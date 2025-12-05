import React from 'react';
import { Emergencia } from '../types';

interface Props {
  emergencias: Emergencia[];
  onSelect: (e: Emergencia) => void;
  selectedId?: number;
}

export const EmergencyList = ({ emergencias, onSelect, selectedId }: Props) => {
  return (
    <div className="bg-white p-4 rounded shadow h-96 overflow-y-auto">
      <h2 className="text-lg font-semibold mb-4 border-b pb-2">Emergencias Activas</h2>
      <div className="space-y-2">
        {emergencias.length === 0 && <p className="text-gray-500 italic">No hay emergencias activas.</p>}
        {emergencias.map((e) => (
          <div 
            key={e.id} 
            onClick={() => onSelect(e)}
            className={`p-3 rounded cursor-pointer border ${selectedId === e.id ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50 border-gray-200'}`}
          >
            <div className="flex justify-between items-center">
              <span className="font-medium text-gray-800">{e.tipo}</span>
              <span className={`text-xs px-2 py-1 rounded ${
                e.estado === 'asignada' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {e.estado}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1 truncate">{e.descripcion}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

