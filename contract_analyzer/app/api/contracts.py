from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security import get_current_user
from typing import Annotated
from app.services.file_parser import extract_text
from app.services.ai_service import GROQ_ENABLED, extract_contract_info_groq
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.contract import Contract
from app.schemas.contracts import ContractUpdate



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()

# Tipos de arquivos permitidos
ALLOWED_EXTENSIONS = [".pdf", ".docx"]


@router.post("/contracts/upload")
async def upload_contract(
    file: Annotated[UploadFile, File(..., description="Arquivo .pdf ou .docx do contrato")],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Faz upload de um contrato, extrai o texto e simula análise por IA.
    """
    filename = file.filename
    extension = filename.lower().split(".")[-1]

    if f".{extension}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado: .{extension}. Apenas PDF e DOCX são permitidos.",
        )

    # Verifica se o nome do arquivo já existe no banco
    existing_contract = db.query(Contract).filter(Contract.filename == filename).first()
    if existing_contract:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um contrato com o nome de arquivo '{filename}'. Por favor, escolha outro nome."
        )

    # Lê o conteúdo do arquivo
    content = await file.read()

    try:
        # Extrai o texto do arquivo
        extracted_text = extract_text(content, f".{extension}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if GROQ_ENABLED:
        try:
            # Faz a extração usando a IA Groq
            analysis_result = extract_contract_info_groq(extracted_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar o contrato com a IA: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA (Groq) não está habilitado. Configure a chave API para usar esta funcionalidade."
        )

    # Salvar contrato no banco
    db_contract = Contract(
        filename=filename,
        uploaded_by=current_user.id,  # agora usa o id real do usuário logado
        nomes_partes="; ".join(analysis_result["nomes_partes"]),
        valores_monetarios="; ".join(analysis_result["valores_monetarios"]),
        obrigacoes_principais="\n".join(analysis_result["obrigacoes_principais"]),
        dados_adicionais=analysis_result["dados_adicionais"],
        clausulas_rescisao="; ".join(analysis_result["clausulas_rescisao"])
    )

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return {
        "id": db_contract.id,
        "filename": filename,
        "uploaded_by": current_user.username,
        "analysis": analysis_result,
        "message": "Contrato salvo no banco e analisado com sucesso!"
    }


@router.get("/contracts/by-name/{contract_name}")
def get_contract_by_name(
    contract_name: str,
    current_user: dict = Depends(get_current_user),  # Protege com JWT
    db: Session = Depends(get_db)
):
    """
    Busca um contrato pelo nome do arquivo e retorna suas informações.
    """
    contract = db.query(Contract).filter(Contract.filename == contract_name).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contrato com nome '{contract_name}' não encontrado."
        )

    return {
        "id": contract.id,
        "filename": contract.filename,
        "uploaded_by": contract.uploaded_by,
        "nomes_partes": contract.nomes_partes,
        "valores_monetarios": contract.valores_monetarios,
        "obrigacoes_principais": contract.obrigacoes_principais,
        "dados_adicionais": contract.dados_adicionais,
        "clausulas_rescisao": contract.clausulas_rescisao
    }


@router.get("/contracts/{contract_id}")
def get_contract_by_id(
    contract_id: int,
    current_user: dict = Depends(get_current_user),  # Protegido com JWT
    db: Session = Depends(get_db)
):
    """
    Busca um contrato pelo ID e retorna suas informações.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contrato com ID '{contract_id}' não encontrado."
        )

    return {
        "id": contract.id,
        "filename": contract.filename,
        "uploaded_by": contract.uploaded_by,
        "nomes_partes": contract.nomes_partes,
        "valores_monetarios": contract.valores_monetarios,
        "obrigacoes_principais": contract.obrigacoes_principais,
        "dados_adicionais": contract.dados_adicionais,
        "clausulas_rescisao": contract.clausulas_rescisao
    }


@router.get("/contracts")
def list_all_contracts(
    current_user: dict = Depends(get_current_user),  # Protegido com JWT
    db: Session = Depends(get_db)
):
    """
    Lista todos os contratos salvos no banco de dados.
    """
    contracts = db.query(Contract).all()

    if not contracts:
        raise HTTPException(status_code=404, detail="Nenhum contrato encontrado.")

    # Monta a lista com os contratos
    contract_list = [
        {
            "id": c.id,
            "filename": c.filename,
            "uploaded_by": c.uploaded_by,
            "nomes_partes": c.nomes_partes,
            "valores_monetarios": c.valores_monetarios,
            "obrigacoes_principais": c.obrigacoes_principais,
            "dados_adicionais": c.dados_adicionais,
            "clausulas_rescisao": c.clausulas_rescisao
        }
        for c in contracts
    ]

    return {"contracts": contract_list, "total": len(contract_list)}


@router.put("/contracts/{contract_id}")
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    current_user: dict = Depends(get_current_user),  # Protegido com JWT
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de um contrato pelo ID.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contrato com ID '{contract_id}' não encontrado."
        )

    # Atualiza somente os campos enviados no JSON
    update_data = contract_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract) # O refresh apenas recarrega o objeto do banco após o commit.

    return {
        "message": f"Contrato com ID '{contract_id}' atualizado com sucesso!",
        "updated_contract": {
            "id": contract.id,
            "filename": contract.filename,
            "nomes_partes": contract.nomes_partes,
            "valores_monetarios": contract.valores_monetarios,
            "obrigacoes_principais": contract.obrigacoes_principais,
            "dados_adicionais": contract.dados_adicionais,
            "clausulas_rescisao": contract.clausulas_rescisao,
        }
    }


@router.delete("/contracts/{contract_id}")
def delete_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user),  # Protegido com JWT
    db: Session = Depends(get_db)
):
    """
    Deleta um contrato pelo nome do arquivo.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contrato com ID '{contract_id}' não encontrado."
        )

    db.delete(contract)
    db.commit()

    return {
        "message": f"Contrato com ID '{contract_id}' excluído com sucesso!"
    }


# -----------------------------------------------------
# Rota de teste protegida com JWT (DEBUG)
# -----------------------------------------------------
# @router.get("/contracts/protected")
# def protected_route(current_user: dict = Depends(get_current_user)):
#     """
#     Rota protegida para testar autenticação JWT (uso interno).
#     """
#     return {
#         "message": f"Olá, {current_user['username']}! Você está autenticado.",
#         "user": current_user
#     }

