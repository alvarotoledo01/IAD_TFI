import React, { useState } from 'react';
import { createEmergencia } from '../api';
import { Emergencia } from '../types';

const SCENARIOS = [
  { tipo: "Accidente de Tránsito", desc: "Colisión múltiple en Av. Mate de Luna, dos heridos graves." },
  { tipo: "Picadura Alacrán", desc: "Niño de 5 años picado en zona Norte, síntomas severos." },
  { tipo: "Paro Cardíaco", desc: "Hombre de 60 años desvanecido en plaza pública, zona Sur." },
  { tipo: "Incendio Domiciliario", desc: "Fuego en vivienda unifamiliar, posibles quemados." },
  { tipo: "Traumatismo", desc: "Caída de altura en obra en construcción, Yerba Buena." }
];

export const SimulationPanel = ({ onNewEmergency }: { onNewEmergency: () => void }) => {
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const scenario = SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)];
      const zonaId = Math.floor(Math.random() * 4) + 1; // IDs 1-4 (from seed)
      
      await createEmergencia(scenario.tipo, scenario.desc, zonaId);
      onNewEmergency();
    } catch (error) {
      console.error("Simulation failed", error);
      alert("Error al simular emergencia");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow flex items-center justify-between">
      <div>
        <h3 className="font-semibold text-gray-800">Simulador</h3>
        <p className="text-sm text-gray-500">Genera una emergencia aleatoria para probar el sistema.</p>
      </div>
      <button 
        onClick={handleSimulate}
        disabled={loading}
        className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-medium disabled:opacity-50"
      >
        {loading ? "Generando..." : "Simular Emergencia"}
      </button>
    </div>
  );
};

