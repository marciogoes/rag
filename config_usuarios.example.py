# Configuração de Usuários - EXEMPLO
# Desenvolvido por: Marcio Góes do Nascimento
# 
# INSTRUÇÕES:
# 1. Copie este arquivo para 'config_usuarios.py'
# 2. Configure as variáveis de ambiente ou edite as senhas padrão
# 3. NUNCA commite o arquivo config_usuarios.py no Git!

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Senhas - SEMPRE use variáveis de ambiente em produção!
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "MUDE_ESTA_SENHA")
MARCIO_PASSWORD = os.getenv("MARCIO_PASSWORD", "MUDE_ESTA_SENHA")

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
# ⚠️ GERE UMA NOVA SECRET_KEY usando: python gerar_secret_key.py
SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "GERE_UMA_CHAVE_SEGURA_USANDO_gerar_secret_key.py"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

# Configurações do Ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Avisos de Segurança
if not IS_PRODUCTION:
    print("⚠️  MODO DESENVOLVIMENTO - Use variáveis de ambiente em produção!")
else:
    print("✅ MODO PRODUÇÃO - Variáveis de ambiente carregadas")
    if "GERE_UMA_CHAVE" in SECRET_KEY:
        print("🚨 ERRO CRÍTICO: SECRET_KEY padrão detectada! Sistema não pode iniciar!")
        print("   Execute: python gerar_secret_key.py")
        exit(1)
