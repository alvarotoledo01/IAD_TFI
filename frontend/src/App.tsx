import React, { useEffect, useState } from 'react';
import { DashboardHeader } from './components/DashboardHeader';
import { EmergencyList } from './components/EmergencyList';
import { EmergencyDetail } from './components/EmergencyDetail';
import { ActivityPanel } from './components/ActivityPanel';
import { SimulationPanel } from './components/SimulationPanel';
import { getSystemState } from './api';
import { SystemState, Emergencia } from './types';

function App() {
  const [state, setState] = useState<SystemState>({
    emergencias: [],
    hospitales: [],
    vehiculos: [],
    actividades: []
  });
  const [selectedEmergency, setSelectedEmergency] = useState<Emergencia | null>(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const fetchData = async () => {
    try {
      const data = await getSystemState();
      setState(data);
      setLastUpdated(new Date());
      
      // If selected emergency exists, update its data from the new list
      if (selectedEmergency) {
        const updated = data.emergencias.find(e => e.id === selectedEmergency.id);
        if (updated) {
          setSelectedEmergency(updated);
        }
      }
    } catch (error) {
      console.error("Error fetching state", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []); // No polling, just initial fetch

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <DashboardHeader lastUpdated={lastUpdated} />
      
      <main className="flex-1 p-4 container mx-auto max-w-7xl space-y-4">
        
        <SimulationPanel onNewEmergency={fetchData} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Col: List & Detail */}
          <div className="lg:col-span-2 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <EmergencyList 
                emergencias={state.emergencias} 
                onSelect={setSelectedEmergency} 
                selectedId={selectedEmergency?.id} 
              />
              <ActivityPanel actividades={state.actividades} />
            </div>
            
            <EmergencyDetail 
              emergencia={selectedEmergency} 
              hospitals={state.hospitales} 
              vehicles={state.vehiculos} 
            />
          </div>

          {/* Right Col: Maybe Map later, for now we can just put stats or leave empty/expand detail */}
          {/* Actually, user wanted Activity Panel prominently. I put it above. */}
          {/* Let's put a simple stats summary here or just use the space for now. */}
          <div className="bg-white p-4 rounded shadow">
             <h3 className="font-semibold mb-2">Resumen de Recursos</h3>
             <div className="space-y-4">
                <div>
                  <h4 className="text-sm text-gray-500 uppercase">Hospitales</h4>
                  {state.hospitales.map(h => (
                    <div key={h.id} className="flex justify-between text-sm mt-1 border-b pb-1">
                      <span>{h.nombre}</span>
                      <span className={h.ocupacion_actual > h.capacidad_total * 0.9 ? 'text-red-500' : 'text-green-600'}>
                        {h.ocupacion_actual}/{h.capacidad_total} oc.
                      </span>
                    </div>
                  ))}
                </div>
                <div>
                  <h4 className="text-sm text-gray-500 uppercase">Vehículos Disponibles</h4>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {state.vehiculos.map(v => (
                      <span key={v.id} className={`text-xs px-2 py-1 rounded ${v.estado === 'disponible' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'}`}>
                        {v.nombre}
                      </span>
                    ))}
                  </div>
                </div>
             </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App

