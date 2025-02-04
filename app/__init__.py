from fastapi import FastAPI
from .db.conec import DATABASE_URL, BACKEND_SERVER
from sqlalchemy import create_engine
from .funciones.funcions import what_is_his_weight, calculate, average_dog_weight
from .models.agent import factory
from fastapi.middleware.cors import CORSMiddleware

agent = factory("gemini")
engine = create_engine(DATABASE_URL)
app = FastAPI(servers=[{"url": BACKEND_SERVER}])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes limitar esto a los dominios que desees
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (incluyendo OPTIONS)
    allow_headers=["*"],  # Permite todos los encabezados
)


prompt = """ En este lugar va el prompt para el agente

""".strip()


# These are known actions
known_actions = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight,
    "what is his weigth" : what_is_his_weight
}

from .routes import route_human