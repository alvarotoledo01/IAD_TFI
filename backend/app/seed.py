import random
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal, engine

def init_db(db: Session):
    # Check if data exists
    if db.query(models.Zona).first():
        return

    # Create Zones (San Miguel de Tucuman approx)
    zonas = [
        models.Zona(nombre="Centro", latitud=-26.8300, longitud=-65.2000),
        models.Zona(nombre="Norte", latitud=-26.8100, longitud=-65.2100),
        models.Zona(nombre="Sur", latitud=-26.8500, longitud=-65.1900),
        models.Zona(nombre="Yerba Buena", latitud=-26.8200, longitud=-65.2900), # Nearby
    ]
    db.add_all(zonas)
    db.commit()
    
    zonas = db.query(models.Zona).all()
    z_centro = next(z for z in zonas if z.nombre == "Centro")
    z_norte = next(z for z in zonas if z.nombre == "Norte")
    z_sur = next(z for z in zonas if z.nombre == "Sur")
    z_yb = next(z for z in zonas if z.nombre == "Yerba Buena")

    # Create Hospitals
    hospitales = [
        models.Hospital(
            nombre="Hospital Padilla", 
            zona_id=z_centro.id, 
            capacidad_total=100, 
            ocupacion_actual=random.randint(50, 90),
            tiene_suero_antiescorpionico=True,
            tiene_unidad_trauma=True,
            tiene_cardiologia=True,
            tiene_pediatria=False,
            tiene_unidad_quemados=True,
            latitud=-26.8350, longitud=-65.2050
        ),
        models.Hospital(
            nombre="Hospital de Niños", 
            zona_id=z_centro.id, 
            capacidad_total=80, 
            ocupacion_actual=random.randint(30, 70),
            tiene_suero_antiescorpionico=True,
            tiene_unidad_trauma=True,
            tiene_cardiologia=True,
            tiene_pediatria=True,
            tiene_unidad_quemados=False,
            latitud=-26.8290, longitud=-65.2010
        ),
        models.Hospital(
            nombre="Hospital Avellaneda", 
            zona_id=z_norte.id, 
            capacidad_total=60, 
            ocupacion_actual=random.randint(20, 50),
            tiene_suero_antiescorpionico=False,
            tiene_unidad_trauma=False,
            tiene_cardiologia=True,
            tiene_pediatria=True,
            tiene_unidad_quemados=False,
            latitud=-26.8050, longitud=-65.2150
        ),
        models.Hospital(
            nombre="Hospital Carrillo", 
            zona_id=z_yb.id, 
            capacidad_total=50, 
            ocupacion_actual=random.randint(10, 40),
            tiene_suero_antiescorpionico=True,
            tiene_unidad_trauma=False,
            tiene_cardiologia=False,
            tiene_pediatria=True,
            tiene_unidad_quemados=False,
            latitud=-26.8210, longitud=-65.2850
        )
    ]
    db.add_all(hospitales)
    db.commit()

    # Doctors
    especialidades = ["pediatra", "cardiologo", "traumatologo", "toxicologo", "medicina_interna"]
    for h in hospitales:
        for _ in range(random.randint(3, 6)):
            db.add(models.Doctor(
                nombre=f"Dr. {random.choice(['Perez', 'Gomez', 'Diaz', 'Lopez', 'Martinez'])}",
                especialidad=random.choice(especialidades),
                hospital_id=h.id,
                disponible=random.choice([True, True, False]) # Mostly available
            ))
    db.commit()

    # Vehicles
    vehiculos = [
        models.VehiculoRescate(nombre="Movil-101", tipo="ambulancia", zona_id=z_centro.id, estado="disponible", latitud=-26.8310, longitud=-65.2010),
        models.VehiculoRescate(nombre="Movil-102", tipo="ambulancia_uti", zona_id=z_centro.id, estado="disponible", latitud=-26.8340, longitud=-65.2040),
        models.VehiculoRescate(nombre="Movil-201", tipo="ambulancia", zona_id=z_norte.id, estado="disponible", latitud=-26.8110, longitud=-65.2120),
        models.VehiculoRescate(nombre="Heli-1", tipo="helicoptero", zona_id=z_sur.id, estado="disponible", latitud=-26.8510, longitud=-65.1920),
        models.VehiculoRescate(nombre="Movil-301", tipo="ambulancia", zona_id=z_yb.id, estado="ocupado", latitud=-26.8220, longitud=-65.2860),
    ]
    db.add_all(vehiculos)
    db.commit()

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()

