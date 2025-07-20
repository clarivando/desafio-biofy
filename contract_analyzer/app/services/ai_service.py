
from openai import OpenAI
from app.core.config import GROQ_API_KEY, GROQ_API_BASE, GROQ_MODEL


# Configura o cliente OpenAI apontando para o Groq
if GROQ_API_KEY:
    groq_client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url=GROQ_API_BASE
    )
    GROQ_ENABLED = True
    print("Groq API configurado com sucesso!")
else:
    groq_client = None
    GROQ_ENABLED = False
    print("Groq API não configurado. Configure a chave no .env.")


def extract_contract_info_groq(contract_text: str) -> dict:
    """
    Extrai informações do contrato usando a API do Groq (LLaMA 3).
    """
    if not GROQ_ENABLED:
        raise RuntimeError("Groq API não está habilitado. Configure a chave no .env.")

    prompt = f"""
    Extraia as seguintes informações do contrato abaixo e retorne exatamente no formato JSON abaixo:
    {{
        "nomes_partes": ["parte1", "parte2"],
        "valores_monetarios": ["R$ 1.000,00", "R$ 50.000,00"],
        "obrigacoes_principais": ["obrigação 1", "obrigação 2"],
        "dados_adicionais": "texto com objeto e vigência do contrato",
        "clausulas_rescisao": "texto com as cláusulas de rescisão"
    }}

    Contrato:
    {contract_text}
    """

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        # Extrai o conteúdo
        result_text = response.choices[0].message.content

        # Força o parsing JSON
        import json
        json_start = result_text.find("{")
        json_end = result_text.rfind("}") + 1
        clean_json = result_text[json_start:json_end]

        return json.loads(clean_json)

    except Exception as e:
        print(f"Erro ao chamar a API do Groq: {e}")
        raise RuntimeError("Erro ao processar o contrato com a IA (Groq).")


def extract_contract_info_mock(contract_text: str) -> dict:
    """
    Simula a extração de informações de um contrato sem usar IA.
    """
    print("Usando MOCK para extrair informações do contrato.")
    return {
        "nomes_partes": ["Empresa X", "Cliente Y"],
        "valores_monetarios": ["R$ 100.000,00", "R$ 50.000,00"],
        "obrigacoes_principais": [
            "Entrega do serviço no prazo de 12 meses.",
            "Pagamento em 5 parcelas iguais com vencimento mensal."
        ],
        "dados_adicionais": "Objeto: Prestação de serviços de consultoria em TI. Vigência: 01/01/2024 a 31/12/2024.\n" + contract_text[:500],
        "clausulas_rescisao": "Contrato pode ser rescindido por qualquer uma das partes mediante aviso prévio de 30 dias."
    }
