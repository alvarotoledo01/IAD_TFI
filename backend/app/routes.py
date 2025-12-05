from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
import json

from . import models, schemas, database, agents

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

import time

@router.post("/emergencias", response_model=schemas.Emergencia)
def crear_emergencia(emergencia: schemas.EmergenciaCreate, db: Session = Depends(get_db)):
    print(f"\n[SAR] --- NUEVA EMERGENCIA: {emergencia.tipo} ---", flush=True)
    # 1. Create Emergency
    db_emergencia = models.Emergencia(**emergencia.dict())
    db.add(db_emergencia)
    db.commit()
    db.refresh(db_emergencia)

    # Initial Activity
    act_init = models.Actividad(
        agente="SensorEmergencias",
        tipo="emergencia_creada",
        descripcion=f"Nueva emergencia reportada: {emergencia.tipo} en zona {emergencia.zona_id}"
    )
    db.add(act_init)
    db.commit()

    # 2. Agent Orchestration
    agent_sys = agents.AgentSystem(db)
    
    # Get candidates
    hospitales = db.query(models.Hospital).all()
    vehiculos = db.query(models.VehiculoRescate).filter(models.VehiculoRescate.estado == "disponible").all()

    print(f"\n{'='*10} AGENT: HOSPITAL {'='*10}", flush=True)
    print(f"[SAR] Ejecutando HospitalAgent con {len(hospitales)} candidatos...", flush=True)
    # A. Hospital Agent
    hosp_proposals = agent_sys.run_hospital_agent(db_emergencia, hospitales)
    print(f"[SAR] HospitalAgent propuso: {len(hosp_proposals)} opciones.", flush=True)
    
    time.sleep(2) # Rate limit spacing

    print(f"\n{'='*10} AGENT: VEHICLE {'='*10}", flush=True)
    print(f"[SAR] Ejecutando VehicleAgent con {len(vehiculos)} candidatos...", flush=True)
    # B. Vehicle Agent
    veh_proposals = agent_sys.run_vehicle_agent(db_emergencia, vehiculos)
    print(f"[SAR] VehicleAgent propuso: {len(veh_proposals)} opciones.", flush=True)

    time.sleep(2) # Rate limit spacing

    print(f"\n{'='*10} AGENT: COORDINATOR {'='*10}", flush=True)
    print(f"[SAR] Ejecutando CoordinatorAgent...", flush=True)
    # C. Coordinator Agent
    decision = agent_sys.run_coordinator_agent(db_emergencia, hosp_proposals, veh_proposals)
    print(f"[SAR] Decision Final: {json.dumps(decision)}", flush=True)

    time.sleep(2) # Rate limit spacing

    # Apply Decision
    h_id = decision.get("hospital_id")
    v_id = decision.get("vehiculo_id")
    justificacion = decision.get("justificacion", "Sin justificación")

    if h_id:
        db_emergencia.hospital_asignado_id = h_id
    if v_id:
        db_emergencia.vehiculo_asignado_id = v_id
        # Update vehicle status
        veh = db.query(models.VehiculoRescate).filter(models.VehiculoRescate.id == v_id).first()
        if veh:
            veh.estado = "en_camino"
    
    if h_id or v_id:
        db_emergencia.estado = "asignada"
    
    db.commit()
    db.refresh(db_emergencia)

    print(f"\n{'='*10} AGENT: ANALYST {'='*10}", flush=True)
    print(f"[SAR] Generando analisis (AnalystAgent)...", flush=True)
    # D. Analyst Agent
    activities = agent_sys.run_analyst_agent(db_emergencia, decision, hosp_proposals, veh_proposals)
    
    # Save activities
    for act in activities:
        print(f"[SAR] Actividad registrada: {act.get('agente')} - {act.get('descripcion')[:50]}...", flush=True)
        db_act = models.Actividad(
            agente=act.get("agente", "System"),
            tipo=act.get("tipo", "info"),
            descripcion=act.get("descripcion", "")
        )
        db.add(db_act)
    
    db.commit()
    print(f"[SAR] --- PROCESO COMPLETADO ---\n")
    
    return db_emergencia

@router.get("/estado", response_model=schemas.SystemState)
def get_estado(db: Session = Depends(get_db)):
    emergencias = db.query(models.Emergencia).filter(models.Emergencia.estado != "resuelta").all()
    hospitales = db.query(models.Hospital).all()
    vehiculos = db.query(models.VehiculoRescate).all()
    # Limit activities to last 30
    actividades = db.query(models.Actividad).order_by(models.Actividad.timestamp.desc()).limit(30).all()
    
    return {
        "emergencias": emergencias,
        "hospitales": hospitales,
        "vehiculos": vehiculos,
        "actividades": actividades
    }
