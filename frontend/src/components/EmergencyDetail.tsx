import React from 'react';
import { Emergencia, Hospital, Vehiculo } from '../types';

interface Props {
  emergencia: Emergencia | null;
  hospitals: Hospital[];
  vehicles: Vehiculo[];
}

export const EmergencyDetail = ({ emergencia, hospitals, vehicles }: Props) => {
  if (!emergencia) {
    return (
      <div className="bg-white p-4 rounded shadow h-64 flex items-center justify-center text-gray-400">
        Selecciona una emergencia para ver detalles
      </div>
    );
  }

  const hospital = hospitals.find(h => h.id === emergencia.hospital_asignado_id);
  const vehicle = vehicles.find(v => v.id === emergencia.vehiculo_asignado_id);

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-lg font-semibold mb-4 border-b pb-2">Detalle: {emergencia.tipo}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="font-medium text-gray-700">Información</h3>
          <p className="text-sm text-gray-600 mt-1">{emergencia.descripcion}</p>
          <div className="mt-2 text-sm">
            <p><strong>Zona ID:</strong> {emergencia.zona_id}</p>
            <p><strong>Estado:</strong> {emergencia.estado}</p>
            <p><strong>Reportado:</strong> {new Date(emergencia.created_at).toLocaleString()}</p>
          </div>
        </div>

        <div>
          <h3 className="font-medium text-gray-700">Recursos Asignados</h3>
          
          <div className="mt-2 p-2 bg-gray-50 rounded border">
            <p className="text-sm font-semibold">Hospital</p>
            {hospital ? (
              <div className="text-sm">
                <p>{hospital.nombre}</p>
                <p className="text-xs text-gray-500">Ocupación: {hospital.ocupacion_actual}/{hospital.capacidad_total}</p>
              </div>
            ) : (
              <p className="text-sm text-yellow-600">Pendiente de asignación</p>
            )}
          </div>

          <div className="mt-2 p-2 bg-gray-50 rounded border">
            <p className="text-sm font-semibold">Vehículo</p>
            {vehicle ? (
              <div className="text-sm">
                <p>{vehicle.nombre} ({vehicle.tipo})</p>
              </div>
            ) : (
              <p className="text-sm text-yellow-600">Pendiente de asignación</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

