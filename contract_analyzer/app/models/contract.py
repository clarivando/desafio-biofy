from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    nomes_partes = Column(String(1000), nullable=True)  # Nomes das partes envolvidas separadas por ;
    valores_monetarios = Column(String(500), nullable=True)  # Lista de valores monetários
    obrigacoes_principais = Column(Text, nullable=True)  # Principais obrigações do contrato
    dados_adicionais = Column(Text, nullable=True)  # Dados adicionais importantes como objeto do contrato e vigência
    clausulas_rescisao = Column(Text, nullable=True)  # Texto com cláusulas
