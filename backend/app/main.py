from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, routes, seed
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

# Seed data if empty
db = SessionLocal()
seed.init_db(db)
db.close()

app = FastAPI(title="SAR Multi-Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "SAR System Backend Running"}

