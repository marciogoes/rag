"""
Script para Limpar Dados de Teste
Desenvolvido por: Marcio Góes do Nascimento

Remove todos os projetos de teste para começar do zero
"""

import os
import json

print("=" * 60)
print("🗑️  LIMPAR DADOS DE TESTE")
print("   Desenvolvido por: Marcio Góes do Nascimento")
print("=" * 60)
print()

arquivo_projetos = "data/projetos.json"

if os.path.exists(arquivo_projetos):
    print(f"📋 Arquivo encontrado: {arquivo_projetos}")
    
    # Ler projetos atuais
    with open(arquivo_projetos, 'r', encoding='utf-8') as f:
        projetos = json.load(f)
    
    print(f"   Total de projetos: {len(projetos)}")
    
    # Confirmar
    resposta = input("\n⚠️  Deseja DELETAR todos os projetos? (s/n): ")
    
    if resposta.lower() == 's':
        # Limpar
        with open(arquivo_projetos, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        print("\n✅ Todos os projetos foram removidos!")
        print("   Arquivo limpo e pronto para novos testes")
    else:
        print("\n❌ Operação cancelada")
else:
    print(f"⚠️  Arquivo não encontrado: {arquivo_projetos}")
    print("   Nada para limpar")

print()
print("=" * 60)
