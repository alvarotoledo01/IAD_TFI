import React from 'react';
import { Actividad } from '../types';

const getAgentColor = (agent: string) => {
  switch (agent) {
    case 'HospitalAgent': return 'border-green-500 text-green-700';
    case 'VehicleAgent': return 'border-yellow-500 text-yellow-700';
    case 'CoordinatorAgent': return 'border-purple-500 text-purple-700';
    case 'AnalystAgent': return 'border-blue-500 text-blue-700';
    default: return 'border-gray-400 text-gray-700';
  }
};

export const ActivityPanel = ({ actividades }: { actividades: Actividad[] }) => {
  return (
    <div className="bg-white p-4 rounded shadow h-96 overflow-y-auto">
      <h2 className="text-lg font-semibold mb-4 border-b pb-2">Bitácora de Inteligencia Artificial</h2>
      <div className="space-y-4">
        {actividades.length === 0 && <p className="text-gray-400 text-sm italic">Esperando eventos...</p>}
        {actividades.map((act) => {
          const colorClass = getAgentColor(act.agente);
          const borderColor = colorClass.split(' ')[0];
          const textColor = colorClass.split(' ')[1];

          return (
            <div key={act.id} className={`text-sm border-l-4 ${borderColor} pl-3 py-2 bg-gray-50 rounded-r`}>
              <div className="flex justify-between items-center text-xs mb-1">
                <span className={`font-bold uppercase tracking-wide ${textColor}`}>{act.agente}</span>
                <span className="text-gray-400">{new Date(act.timestamp).toLocaleTimeString()}</span>
              </div>
              <p className="text-gray-800 leading-relaxed">{act.descripcion}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

