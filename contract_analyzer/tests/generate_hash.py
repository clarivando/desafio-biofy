from passlib.context import CryptContext

# Cria o contexto com o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Gera o hash da senha "admin123"
hashed_password = pwd_context.hash("admin123")

print(hashed_password)