from pydantic import BaseModel
from typing import Optional


class ContractUpdate(BaseModel):
    filename: Optional[str] = None
    nomes_partes: Optional[str] = None
    valores_monetarios: Optional[str] = None
    obrigacoes_principais: Optional[str] = None
    dados_adicionais: Optional[str] = None
    clausulas_rescisao: Optional[str] = None