"""
Script para gerar SECRET_KEY segura
Desenvolvido por: Marcio Góes do Nascimento
"""

import secrets

print("=" * 60)
print("🔐 GERADOR DE SECRET_KEY SEGURA")
print("   Desenvolvido por: Marcio Góes do Nascimento")
print("=" * 60)
print()

# Gera chave segura
secret_key = secrets.token_urlsafe(32)

print("✅ SECRET_KEY gerada com sucesso!")
print()
print("📋 Copie e cole no seu arquivo .env ou nas variáveis de ambiente:")
print()
print(f"SECRET_KEY={secret_key}")
print()
print("=" * 60)
print("⚠️  IMPORTANTE:")
print("   - NUNCA compartilhe esta chave")
print("   - Use uma chave diferente para cada ambiente")
print("   - Guarde em local seguro")
print("=" * 60)
