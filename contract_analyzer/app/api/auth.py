from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import SessionLocal
from app.models.user import User
from app.schemas.auth import Token, LoginData
from app.core.security import create_access_token
from passlib.context import CryptContext
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/login", response_model=Token)
def login(
    login_data: LoginData,
    db: Session = Depends(get_db)
):
    """
    Autentica o usuário e retorna um token JWT.
    """
    email = login_data.email
    password = login_data.password

    # Busca o usuário no banco pelo e-mail
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se a senha está correta
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # usamos o ID como identificador no token
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
