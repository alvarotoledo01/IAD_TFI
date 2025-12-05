from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Zona(Base):
    __tablename__ = "zonas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    latitud = Column(Float)
    longitud = Column(Float)

    hospitales = relationship("Hospital", back_populates="zona")
    vehiculos = relationship("VehiculoRescate", back_populates="zona")
    emergencias = relationship("Emergencia", back_populates="zona")

class Hospital(Base):
    __tablename__ = "hospitales"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    zona_id = Column(Integer, ForeignKey("zonas.id"))
    capacidad_total = Column(Integer)
    ocupacion_actual = Column(Integer)
    tiene_suero_antiescorpionico = Column(Boolean, default=False)
    tiene_unidad_trauma = Column(Boolean, default=False)
    tiene_cardiologia = Column(Boolean, default=False)
    tiene_pediatria = Column(Boolean, default=False)
    tiene_unidad_quemados = Column(Boolean, default=False)
    latitud = Column(Float)
    longitud = Column(Float)

    zona = relationship("Zona", back_populates="hospitales")
    doctores = relationship("Doctor", back_populates="hospital")
    emergencias = relationship("Emergencia", back_populates="hospital_asignado")

class Doctor(Base):
    __tablename__ = "doctores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    especialidad = Column(String)
    hospital_id = Column(Integer, ForeignKey("hospitales.id"))
    disponible = Column(Boolean, default=True)

    hospital = relationship("Hospital", back_populates="doctores")

class VehiculoRescate(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    tipo = Column(String) # ambulancia, helicoptero, etc.
    zona_id = Column(Integer, ForeignKey("zonas.id"))
    estado = Column(String, default="disponible") # disponible, en_camino, ocupado
    latitud = Column(Float)
    longitud = Column(Float)

    zona = relationship("Zona", back_populates="vehiculos")
    emergencias = relationship("Emergencia", back_populates="vehiculo_asignado")

class Emergencia(Base):
    __tablename__ = "emergencias"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    descripcion = Column(String)
    zona_id = Column(Integer, ForeignKey("zonas.id"))
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    estado = Column(String, default="activa") # activa, asignada, resuelta
    
    vehiculo_asignado_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=True)
    hospital_asignado_id = Column(Integer, ForeignKey("hospitales.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    zona = relationship("Zona", back_populates="emergencias")
    vehiculo_asignado = relationship("VehiculoRescate", back_populates="emergencias")
    hospital_asignado = relationship("Hospital", back_populates="emergencias")

class Actividad(Base):
    __tablename__ = "actividades"
    id = Column(Integer, primary_key=True, index=True)
    agente = Column(String)
    tipo = Column(String)
    descripcion = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

