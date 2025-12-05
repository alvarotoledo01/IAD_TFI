from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Base Schemas
class ZonaBase(BaseModel):
    nombre: str
    latitud: float
    longitud: float

class Zona(ZonaBase):
    id: int
    class Config:
        from_attributes = True

class DoctorBase(BaseModel):
    nombre: str
    especialidad: str
    disponible: bool

class Doctor(DoctorBase):
    id: int
    hospital_id: int
    class Config:
        from_attributes = True

class HospitalBase(BaseModel):
    nombre: str
    capacidad_total: int
    ocupacion_actual: int
    tiene_suero_antiescorpionico: bool
    tiene_unidad_trauma: bool
    tiene_cardiologia: bool
    tiene_pediatria: bool
    tiene_unidad_quemados: bool
    latitud: float
    longitud: float

class Hospital(HospitalBase):
    id: int
    zona_id: int
    doctores: List[Doctor] = []
    class Config:
        from_attributes = True

class VehiculoBase(BaseModel):
    nombre: str
    tipo: str
    estado: str
    latitud: float
    longitud: float

class Vehiculo(VehiculoBase):
    id: int
    zona_id: int
    class Config:
        from_attributes = True

class EmergenciaBase(BaseModel):
    tipo: str
    descripcion: str
    zona_id: int
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class EmergenciaCreate(EmergenciaBase):
    pass

class Emergencia(EmergenciaBase):
    id: int
    estado: str
    vehiculo_asignado_id: Optional[int] = None
    hospital_asignado_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ActividadBase(BaseModel):
    agente: str
    tipo: str
    descripcion: str

class Actividad(ActividadBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class SystemState(BaseModel):
    emergencias: List[Emergencia]
    hospitales: List[Hospital]
    vehiculos: List[Vehiculo]
    actividades: List[Actividad]

