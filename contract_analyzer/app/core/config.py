import os
from dotenv import load_dotenv


# Carrega variáveis do .env
load_dotenv()

# JWT configs
SECRET_KEY = os.getenv("SECRET_KEY", "chave-supersecreta-padrao")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 600))

# Banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

# CORS configs
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")


# Configs do Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")


