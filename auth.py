"""
Sistema de Autenticação JWT
Desenvolvido por: Marcio Góes do Nascimento
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config_usuarios import USUARIOS, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha está correta"""
    return senha_plana == senha_hash  # Simplificado para demo


def autenticar_usuario(username: str, password: str):
    """Autentica um usuário"""
    usuario = USUARIOS.get(username)
    if not usuario:
        return False
    if not verificar_senha(password, usuario["senha"]):
        return False
    return usuario


def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica se o token é válido"""
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# Dependência para rotas protegidas
def usuario_atual(username: str = Depends(verificar_token)):
    """Retorna o usuário atual autenticado"""
    usuario = USUARIOS.get(username)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"username": username, **usuario}
