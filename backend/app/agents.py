import os
import json
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import models

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"

class AgentSystem:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(
            base_url=BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.model = os.getenv("LLM_MODEL", DEFAULT_MODEL)

    def _call_llm(self, system_prompt: str, user_prompt: str, agent_name: str = "Agent") -> str:
        if not OPENROUTER_API_KEY:
            print(f"[{agent_name}] WARNING: OPENROUTER_API_KEY not set. Using dummy response.", flush=True)
            return "{}" 
        
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            print(f"[{agent_name}] Calling LLM ({self.model})... (Attempt {attempt+1}/{max_retries})", flush=True)
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    # timeout=30.0, # 30 second timeout
                )
                response = completion.choices[0].message.content
                print(f"[{agent_name}] Response received (len={len(response)}).", flush=True)
                return response
            except Exception as e:
                error_str = str(e)
                print(f"[{agent_name}] LLM Error: {error_str}", flush=True)
                
                # Check for Rate Limit (429)
                if "429" in error_str:
                    # Increase wait time significantly for 429s
                    wait_time = base_delay * (3 ** attempt) # More aggressive backoff
                    print(f"[{agent_name}] Rate limit hit (429). Retrying in {wait_time}s...", flush=True)
                    time.sleep(wait_time)
                    continue
                
                # Check for Bad Request (400) - Provider errors
                if "400" in error_str:
                     print(f"[{agent_name}] Bad Request (400). Retrying without parameters...", flush=True)
                     try:
                        # Retry naked call (risky but worth a shot for free providers)
                        # Or switch to a simpler prompt structure if complex JSON is failing
                        completion = self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ]
                        )
                        response = completion.choices[0].message.content
                        print(f"[{agent_name}] Response received on retry (len={len(response)}).", flush=True)
                        return response
                     except Exception as e2:
                        print(f"[{agent_name}] Retry failed: {e2}", flush=True)
                        return "{}"

                # Other errors, break
                return "{}"
        
        return "{}"

    def _clean_json(self, text: str) -> str:
        # Attempt to extract JSON from code blocks or raw text
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()

    def run_hospital_agent(self, emergencia: models.Emergencia, hospitales: List[models.Hospital]) -> List[Dict]:
        print(f"[HospitalAgent] Iniciando análisis para emergencia: {emergencia.tipo}")
        # Prepare data context
        hosp_data = []
        for h in hospitales:
            docs = [d.especialidad for d in h.doctores if d.disponible]
            hosp_data.append({
                "id": h.id,
                "nombre": h.nombre,
                "zona_id": h.zona_id,
                "ocupacion": f"{h.ocupacion_actual}/{h.capacidad_total}",
                "recursos": {
                    "antiescorpionico": h.tiene_suero_antiescorpionico,
                    "trauma": h.tiene_unidad_trauma,
                    "cardiologia": h.tiene_cardiologia,
                    "pediatria": h.tiene_pediatria,
                    "quemados": h.tiene_unidad_quemados
                },
                "doctores_disponibles": docs
            })
        
        emergencia_data = {
            "tipo": emergencia.tipo,
            "descripcion": emergencia.descripcion,
            "zona_id": emergencia.zona_id
        }

        system_prompt = """Eres el HospitalAgent. Tu tarea es analizar una emergencia y una lista de hospitales candidatos.
        Debes proponer qué hospitales pueden atenderla basándote en sus recursos, especialidades médicas disponibles y ocupación.
        
        REGLA DE ORO: Siempre debes proponer AL MENOS UN hospital si hay alguno con cupo, aunque no sea perfecto.
        Es una emergencia, peor es no tener hospital.
        
        Salida requerida (JSON puro):
        {
            "hospital_proposals": [
                {
                    "hospital_id": int,
                    "acepta": bool,
                    "prioridad": float (0.0-1.0),
                    "motivo": "breve explicacion",
                    "ocupacion_proyectada": int
                }
            ]
        }
        No incluyas markdown ni texto extra."""

        user_prompt = f"Emergencia: {json.dumps(emergencia_data)}\nHospitales: {json.dumps(hosp_data)}"
        
        raw = self._call_llm(system_prompt, user_prompt, "HospitalAgent")
        try:
            data = json.loads(self._clean_json(raw))
            proposals = data.get("hospital_proposals", [])
            print(f"[HospitalAgent] Generadas {len(proposals)} propuestas.")
            return proposals
        except Exception as e:
            print(f"[HospitalAgent] Error parsing response: {e}")
            return []

    def run_vehicle_agent(self, emergencia: models.Emergencia, vehiculos: List[models.VehiculoRescate]) -> List[Dict]:
        print(f"[VehicleAgent] Iniciando búsqueda de vehículos...")
        veh_data = []
        for v in vehiculos:
            veh_data.append({
                "id": v.id,
                "nombre": v.nombre,
                "tipo": v.tipo,
                "estado": v.estado,
                "zona_id": v.zona_id
            })
        
        emergencia_data = {
            "tipo": emergencia.tipo,
            "descripcion": emergencia.descripcion,
            "zona_id": emergencia.zona_id
        }

        system_prompt = """Eres el VehicleAgent. Analiza la emergencia y los vehículos disponibles.
        
        CRITERIOS DE ASIGNACIÓN (IMPORTANTE):
        1. FLEXIBILIDAD TOTAL: Tu objetivo es ENVIAR ALGO. No te pongas exquisito con requisitos técnicos.
        2. TIPOS: "ambulancia" sirve para TODO. "ambulancia_uti" es mejor para casos graves, pero la normal sirve. "helicoptero" es para lejanía o gravedad extrema.
        3. PROHIBIDO rechazar vehículos por falta de equipamiento que no esté explícito en los datos (ej: NO inventes que falta "ventilador pediátrico").
        4. Si el vehículo está "disponible", PROPONLO. Dale prioridad alta si está en la misma zona, media si está cerca.
        
        Salida requerida (JSON puro):
        {
            "vehicle_proposals": [
                {
                    "vehiculo_id": int,
                    "acepta": bool,
                    "prioridad": float (0.0-1.0),
                    "eta_min": float,
                    "motivo": "breve explicacion"
                }
            ]
        }
        No incluyas markdown."""

        user_prompt = f"Emergencia: {json.dumps(emergencia_data)}\nVehiculos: {json.dumps(veh_data)}"

        raw = self._call_llm(system_prompt, user_prompt, "VehicleAgent")
        try:
            data = json.loads(self._clean_json(raw))
            proposals = data.get("vehicle_proposals", [])
            print(f"[VehicleAgent] Generadas {len(proposals)} propuestas.")
            return proposals
        except Exception as e:
            print(f"[VehicleAgent] Error parsing response: {e}")
            return []

    def run_coordinator_agent(self, emergencia: models.Emergencia, hosp_proposals: List[Dict], veh_proposals: List[Dict]) -> Dict:
        print(f"[CoordinatorAgent] Recibiendo propuestas: {len(hosp_proposals)} hospitales, {len(veh_proposals)} vehículos.")
        emergencia_data = {
            "tipo": emergencia.tipo,
            "descripcion": emergencia.descripcion
        }
        
        system_prompt = """Eres el CoordinatorAgent. Tu misión es tomar la decisión FINAL.
        Recibes propuestas de hospitales y vehículos. Debes elegir la mejor combinación.
        
        REGLA: Si recibes propuestas con acepta=true, DEBES elegir una. No dejes null a menos que las listas estén vacías.
        Prioriza la vida del paciente: Cualquier asignación es mejor que ninguna.
        
        Salida requerida (JSON puro):
        {
            "decision": {
                "hospital_id": int | null,
                "vehiculo_id": int | null,
                "justificacion": "explicacion final de la decision"
            }
        }
        """
        
        user_prompt = f"""Emergencia: {json.dumps(emergencia_data)}
        Propuestas Hospitales: {json.dumps(hosp_proposals)}
        Propuestas Vehiculos: {json.dumps(veh_proposals)}"""

        raw = self._call_llm(system_prompt, user_prompt, "CoordinatorAgent")
        try:
            data = json.loads(self._clean_json(raw))
            decision = data.get("decision", {})
            print(f"[CoordinatorAgent] Decisión tomada: Hospital {decision.get('hospital_id')}, Vehiculo {decision.get('vehiculo_id')}")
            return decision
        except Exception as e:
            print(f"[CoordinatorAgent] Error parsing response: {e}")
            return {}

    def run_analyst_agent(self, emergencia: models.Emergencia, decision: Dict, hosp_proposals: List[Dict], veh_proposals: List[Dict]) -> List[Dict]:
        print("[AnalystAgent] Generando reporte de actividad...")
        emergencia_data = {
            "tipo": emergencia.tipo,
            "descripcion": emergencia.descripcion
        }

        system_prompt = """Eres el AnalystAgent. Genera un reporte de actividad DETALLADO para el dashboard.
        Tu objetivo es contar la historia de CÓMO interactuaron los agentes.
        
        Genera EXACTAMENTE 3 entradas en orden cronológico:
        
        1. Una entrada para HospitalAgent: Explica qué hospitales consideró y cuál propuso como mejor opción y por qué. Menciona nombres de hospitales.
        2. Una entrada para VehicleAgent: Explica qué vehículos analizó y cuál sugirió por cercanía o tipo. Menciona nombres de vehículos.
        3. Una entrada para CoordinatorAgent: Explica la decisión final, justificando por qué esa combinación de hospital+vehículo es la mejor para esta emergencia específica.

        Usa lenguaje natural, técnico pero accesible. Ejemplo: "El HospitalAgent analizó 3 opciones y descartó el Hospital X por falta de unidad de trauma..."
        
        Salida requerida (JSON puro):
        {
            "activity_descriptions": [
                {
                    "agente": "HospitalAgent",
                    "tipo": "propuesta",
                    "descripcion": "..."
                },
                {
                    "agente": "VehicleAgent",
                    "tipo": "propuesta",
                    "descripcion": "..."
                },
                {
                    "agente": "CoordinatorAgent",
                    "tipo": "decision",
                    "descripcion": "..."
                }
            ]
        }
        """

        user_prompt = f"""Emergencia: {json.dumps(emergencia_data)}
        Propuestas Hospitales: {json.dumps(hosp_proposals)}
        Propuestas Vehiculos: {json.dumps(veh_proposals)}
        Decision Final: {json.dumps(decision)}"""

        raw = self._call_llm(system_prompt, user_prompt, "AnalystAgent")
        try:
            data = json.loads(self._clean_json(raw))
            activities = data.get("activity_descriptions", [])
            print(f"[AnalystAgent] Reporte generado con {len(activities)} entradas.")
            return activities
        except Exception as e:
            print(f"[AnalystAgent] Error parsing response: {e}")
            return []