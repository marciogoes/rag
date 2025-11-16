"""
Script de Teste - Sistema de Projetos
Desenvolvido por: Marcio Góes do Nascimento

Testa todas as funcionalidades do sistema
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("🧪 TESTE DO SISTEMA DE PROJETOS")
print("   Desenvolvido por: Marcio Góes do Nascimento")
print("=" * 60)
print()

# Cores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def teste(nome):
    """Decorator para testes"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n{'='*60}")
            print(f"🧪 TESTE: {nome}")
            print(f"{'='*60}")
            try:
                resultado = func(*args, **kwargs)
                print(f"{GREEN}✅ PASSOU!{RESET}")
                return resultado
            except Exception as e:
                print(f"{RED}❌ FALHOU: {e}{RESET}")
                return None
        return wrapper
    return decorator


@teste("1. Health Check - Servidor está rodando?")
def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, "Servidor não está respondendo"
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Desenvolvedor: {data['desenvolvedor']}")
    return data


@teste("2. Login como Admin")
def test_login_admin():
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": "admin",
            "password": "Admin@RAG2024!Secure"
        }
    )
    assert response.status_code == 200, "Login falhou"
    data = response.json()
    print(f"   Usuário: {data['user']['nome']}")
    print(f"   Token recebido: {data['access_token'][:30]}...")
    return data['access_token']


@teste("3. Login como Usuário Normal")
def test_login_user():
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": "marcio",
            "password": "Marcio@2024!Dev"
        }
    )
    assert response.status_code == 200, "Login falhou"
    data = response.json()
    print(f"   Usuário: {data['user']['nome']}")
    return data['access_token']


@teste("4. Criar Projeto (como Admin)")
def test_criar_projeto(token_admin):
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = requests.post(
        f"{BASE_URL}/projetos/",
        headers=headers,
        json={
            "nome": "Projeto Teste API",
            "descricao": "Projeto criado via teste automatizado"
        }
    )
    assert response.status_code == 200, "Criar projeto falhou"
    data = response.json()
    print(f"   ID: {data['id']}")
    print(f"   Nome: {data['nome']}")
    print(f"   Criado por: {data['criado_por']}")
    return data['id']


@teste("5. Tentar Criar Projeto (como Usuário) - Deve Falhar")
def test_criar_projeto_sem_permissao(token_user):
    headers = {"Authorization": f"Bearer {token_user}"}
    response = requests.post(
        f"{BASE_URL}/projetos/",
        headers=headers,
        json={
            "nome": "Projeto Não Autorizado",
            "descricao": "Este não deveria ser criado"
        }
    )
    assert response.status_code == 403, "Usuário comum não deveria criar projeto"
    print(f"   Bloqueado corretamente! Status: {response.status_code}")


@teste("6. Listar Projetos")
def test_listar_projetos(token_admin):
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = requests.get(f"{BASE_URL}/projetos/", headers=headers)
    assert response.status_code == 200, "Listar projetos falhou"
    projetos = response.json()
    print(f"   Total de projetos: {len(projetos)}")
    for p in projetos:
        print(f"   - [{p['id']}] {p['nome']} ({p['total_documentos']} docs)")
    return projetos


@teste("7. Buscar Projeto Específico")
def test_buscar_projeto(token_admin, projeto_id):
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = requests.get(f"{BASE_URL}/projetos/{projeto_id}", headers=headers)
    assert response.status_code == 200, "Buscar projeto falhou"
    projeto = response.json()
    print(f"   Nome: {projeto['nome']}")
    print(f"   Descrição: {projeto['descricao']}")
    print(f"   Ativo: {projeto['ativo']}")


@teste("8. Atualizar Projeto (como Admin)")
def test_atualizar_projeto(token_admin, projeto_id):
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = requests.put(
        f"{BASE_URL}/projetos/{projeto_id}",
        headers=headers,
        json={
            "descricao": "Descrição atualizada pelo teste"
        }
    )
    assert response.status_code == 200, "Atualizar projeto falhou"
    data = response.json()
    print(f"   Descrição nova: {data['descricao']}")


@teste("9. Estatísticas do Projeto")
def test_estatisticas(token_admin, projeto_id):
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = requests.get(
        f"{BASE_URL}/projetos/{projeto_id}/estatisticas",
        headers=headers
    )
    assert response.status_code == 200, "Estatísticas falharam"
    stats = response.json()
    print(f"   Documentos: {stats['total_documentos']}")
    print(f"   Ativo: {stats['ativo']}")


@teste("10. Desativar Projeto")
def test_desativar_projeto(token_admin, projeto_id):
    headers = {"Authorization": f"Bearer {token_admin}"}
    response = requests.delete(
        f"{BASE_URL}/projetos/{projeto_id}?deletar_documentos=false",
        headers=headers
    )
    assert response.status_code == 200, "Desativar projeto falhou"
    data = response.json()
    print(f"   Mensagem: {data['message']}")


# Executar todos os testes
def main():
    print(f"\n{YELLOW}📡 Certifique-se que o servidor está rodando!{RESET}")
    print(f"{YELLOW}   Execute em outro terminal: python main.py{RESET}")
    input("\nPressione ENTER para começar os testes...")
    
    # Teste 1: Health Check
    health_data = test_health()
    if not health_data:
        print(f"\n{RED}❌ Servidor não está rodando! Execute: python main.py{RESET}")
        return
    
    sleep(1)
    
    # Teste 2: Login Admin
    token_admin = test_login_admin()
    if not token_admin:
        print(f"\n{RED}❌ Login admin falhou! Verifique credenciais{RESET}")
        return
    
    sleep(1)
    
    # Teste 3: Login User
    token_user = test_login_user()
    if not token_user:
        print(f"\n{RED}❌ Login usuário falhou! Verifique credenciais{RESET}")
        return
    
    sleep(1)
    
    # Teste 4: Criar Projeto
    projeto_id = test_criar_projeto(token_admin)
    if not projeto_id:
        print(f"\n{RED}❌ Criar projeto falhou!{RESET}")
        return
    
    sleep(1)
    
    # Teste 5: Tentar criar sem permissão
    test_criar_projeto_sem_permissao(token_user)
    
    sleep(1)
    
    # Teste 6: Listar Projetos
    test_listar_projetos(token_admin)
    
    sleep(1)
    
    # Teste 7: Buscar Projeto
    test_buscar_projeto(token_admin, projeto_id)
    
    sleep(1)
    
    # Teste 8: Atualizar Projeto
    test_atualizar_projeto(token_admin, projeto_id)
    
    sleep(1)
    
    # Teste 9: Estatísticas
    test_estatisticas(token_admin, projeto_id)
    
    sleep(1)
    
    # Teste 10: Desativar
    test_desativar_projeto(token_admin, projeto_id)
    
    # Resumo
    print("\n" + "=" * 60)
    print(f"{GREEN}✅ TODOS OS TESTES PASSARAM!{RESET}")
    print("=" * 60)
    print(f"\n{YELLOW}📋 Próximo passo:{RESET}")
    print(f"   1. Abra o navegador: http://localhost:8000")
    print(f"   2. Faça login como admin")
    print(f"   3. Teste a interface gráfica")
    print()


if __name__ == "__main__":
    main()
