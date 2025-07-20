from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, contracts, users
from app.database import init_db
#from app.core.config import ALLOWED_ORIGINS


init_db()
app = FastAPI()

# Adiciona CORS
app.add_middleware(
    CORSMiddleware,
    #allow_origins=ALLOWED_ORIGINS,  # Carregado do .env
    allow_origins=["*"],  # Pode ser "*" para testes (permite qualquer origem)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "API de análise de contratos está funcionando!"}