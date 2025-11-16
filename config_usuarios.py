"""
Configuração de Usuários (Produção)
Desenvolvido por: Marcio Góes do Nascimento

Este arquivo PODE ser commitado porque usa apenas variáveis de ambiente.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Senhas vindas de variáveis de ambiente
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
MARCIO_PASSWORD = os.getenv("MARCIO_PASSWORD")

# Verificar se variáveis estão configuradas
if not ADMIN_PASSWORD or not MARCIO_PASSWORD:
    raise ValueError(
        "❌ ERRO: Variáveis de ambiente não configuradas!\n"
        "Configure ADMIN_PASSWORD e MARCIO_PASSWORD no Railway."
    )

USUARIOS = {
    "admin": {
        "senha": ADMIN_PASSWORD,
        "nome": "Administrador",
        "email": "admin@rag.com"
    },
    "marcio": {
        "senha": MARCIO_PASSWORD,
        "nome": "Marcio Góes do Nascimento",
        "email": "marcio@rag.com"
    }
}

# Configurações de Segurança
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "❌ ERRO: SECRET_KEY não configurada!\n"
        "Configure SECRET_KEY no Railway."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

# Configurações do Ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
IS_PRODUCTION = ENVIRONMENT == "production"

# Log de status
if IS_PRODUCTION:
    print("✅ MODO PRODUÇÃO - Variáveis de ambiente carregadas")
else:
    print("⚠️  MODO DESENVOLVIMENTO")
