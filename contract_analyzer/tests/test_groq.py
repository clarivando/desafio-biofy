from openai import OpenAI
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configura cliente Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = "https://api.groq.com/openai/v1"

if not GROQ_API_KEY:
    print("Nenhuma chave API do Groq encontrada no .env")
    exit(1)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_API_BASE
)

try:
    print("Enviando prompt de teste para o Groq...")

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": "Resuma este texto: O contrato estabelece as condições para prestação de serviços de TI."}
        ],
        temperature=0.2
    )

    print("\n**Resposta do Groq:**")
    print(response.choices[0].message.content)

except Exception as e:
    print("Erro ao chamar a API do Groq:")
    print(e)
