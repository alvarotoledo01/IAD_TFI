export interface Zona {
  id: number;
  nombre: string;
  latitud: number;
  longitud: number;
}

export interface Doctor {
  id: number;
  nombre: string;
  especialidad: string;
  disponible: boolean;
}

export interface Hospital {
  id: number;
  nombre: string;
  zona_id: number;
  capacidad_total: number;
  ocupacion_actual: number;
  tiene_suero_antiescorpionico: boolean;
  tiene_unidad_trauma: boolean;
  tiene_cardiologia: boolean;
  tiene_pediatria: boolean;
  tiene_unidad_quemados: boolean;
  latitud: number;
  longitud: number;
  doctores: Doctor[];
}

export interface Vehiculo {
  id: number;
  nombre: string;
  tipo: string;
  zona_id: number;
  estado: string;
  latitud: number;
  longitud: number;
}

export interface Emergencia {
  id: number;
  tipo: string;
  descripcion: string;
  zona_id: number;
  latitud?: number;
  longitud?: number;
  estado: string;
  vehiculo_asignado_id?: number;
  hospital_asignado_id?: number;
  created_at: string;
}

export interface Actividad {
  id: number;
  agente: string;
  tipo: string;
  descripcion: string;
  timestamp: string;
}

export interface SystemState {
  emergencias: Emergencia[];
  hospitales: Hospital[];
  vehiculos: Vehiculo[];
  actividades: Actividad[];
}

