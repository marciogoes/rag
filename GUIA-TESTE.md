# 🧪 GUIA DE TESTE PRÁTICO
**Marcio Góes do Nascimento** | 16/11/2024

---

## ⚡ TESTE RÁPIDO (5 MINUTOS)

### PASSO 1: Teste Isolado do Gerenciador

```powershell
cd "C:\Users\marci\OneDrive\Documentos\GitHub\rag"
python projetos.py
```

**Resultado esperado:**
```
============================================================
🗂️  TESTE DO SISTEMA DE PROJETOS
   Desenvolvido por: Marcio Góes do Nascimento
============================================================

✅ Projeto 'Projeto Teste' criado com sucesso! ID: 1

📋 Projeto criado: {'id': 1, 'nome': 'Projeto Teste', ...}

📋 Projetos cadastrados:
  - [1] Projeto Teste: Projeto de teste do sistema

✅ Sistema de projetos funcionando corretamente!
```

---

### PASSO 2: Teste do Servidor com API de Projetos

**Terminal 1** (Servidor):
```powershell
cd "C:\Users\marci\OneDrive\Documentos\GitHub\rag"
python servidor_teste.py
```

**Terminal 2** (Testes):
```powershell
cd "C:\Users\marci\OneDrive\Documentos\GitHub\rag"
python teste_sistema.py
```

**Resultado esperado:**
```
============================================================
🧪 TESTE DO SISTEMA DE PROJETOS
   Desenvolvido por: Marcio Góes do Nascimento
============================================================

============================================================
🧪 TESTE: 1. Health Check - Servidor está rodando?
============================================================
   Status: healthy
   Desenvolvedor: Marcio Góes do Nascimento
✅ PASSOU!

============================================================
🧪 TESTE: 2. Login como Admin
============================================================
   Usuário: Administrador
   Token recebido: eyJhbGciOiJIUzI1NiIsInR5cCI6...
✅ PASSOU!

[... mais testes ...]

============================================================
✅ TODOS OS TESTES PASSARAM!
============================================================
```

---

### PASSO 3: Teste Manual via Navegador

1. **Abrir navegador:**
   ```
   http://localhost:8000/docs
   ```

2. **Testar endpoints:**
   - Expandir `/login` → Try it out
   - Body:
     ```json
     {
       "username": "admin",
       "password": "Admin@RAG2024!Secure"
     }
     ```
   - Execute
   - Copiar o `access_token`

3. **Autorizar requisições:**
   - Clicar no botão "Authorize" (cadeado)
   - Colar: `Bearer SEU_TOKEN_AQUI`
   - Clicar "Authorize"

4. **Testar criar projeto:**
   - Expandir `POST /projetos/` → Try it out
   - Body:
     ```json
     {
       "nome": "Meu Primeiro Projeto",
       "descricao": "Teste via Swagger"
     }
     ```
   - Execute

5. **Listar projetos:**
   - Expandir `GET /projetos/` → Try it out
   - Execute
   - Ver lista de projetos

---

## 🔧 TESTE COMPLETO (30 MINUTOS)

Se quiser testar a integração completa com interface:

### PASSO 1: Fazer Backup

```powershell
# Backup do main.py original
copy main.py main.py.backup
```

### PASSO 2: Aplicar Integrações

Siga o guia: `INTEGRACAO-PROJETOS.md`

### PASSO 3: Testar Interface

```powershell
python main.py
```

Abrir: http://localhost:8000

**Testar:**
- ✅ Login como admin
- ✅ Ver seção de projetos
- ✅ Criar novo projeto
- ✅ Selecionar projeto
- ✅ Upload de arquivo
- ✅ Chat filtrado por projeto
- ✅ Exportar por projeto

---

## 📋 CHECKLIST DE TESTES

### Gerenciador (projetos.py)
- [ ] Executa sem erros
- [ ] Cria projeto de teste
- [ ] Lista projetos
- [ ] Arquivo `data/projetos.json` é criado

### API (servidor_teste.py)
- [ ] Servidor inicia na porta 8000
- [ ] Health check responde
- [ ] Login admin funciona
- [ ] Login user funciona
- [ ] Criar projeto funciona
- [ ] Listar projetos funciona
- [ ] User comum não pode criar projeto

### Testes Automatizados (teste_sistema.py)
- [ ] Todos os 10 testes passam
- [ ] Nenhum erro crítico
- [ ] Mensagem de sucesso final

### Interface Swagger
- [ ] Abre /docs corretamente
- [ ] Login funciona
- [ ] Autorização funciona
- [ ] Criar projeto funciona
- [ ] Listar projetos funciona

---

## 🆘 PROBLEMAS COMUNS

### Erro: "ModuleNotFoundError: No module named 'rotas_projetos'"

**Solução:**
```powershell
# Verificar se arquivo existe
dir rotas_projetos.py

# Se não existir, foi criado. Deve estar lá!
```

### Erro: "Cannot connect to server"

**Solução:**
```powershell
# Verificar se servidor está rodando
# Deve ter um terminal aberto com: python servidor_teste.py
```

### Erro: "401 Unauthorized"

**Solução:**
```powershell
# Verificar credenciais:
# Admin: admin / Admin@RAG2024!Secure
# User:  marcio / Marcio@2024!Dev
```

### Erro: "Arquivo projetos.json não encontrado"

**Solução:**
```powershell
# Executar uma vez para criar:
python projetos.py
```

---

## 🎯 RESULTADOS ESPERADOS

### ✅ SUCESSO - Você deve ver:

1. **Gerenciador:**
   - Projeto criado
   - Arquivo JSON gerado
   - Mensagem de sucesso

2. **API:**
   - Servidor rodando
   - Endpoints respondendo
   - Autenticação funcionando

3. **Testes:**
   - 10/10 testes passando
   - Permissões funcionando
   - CRUD completo operacional

---

## 📞 PRÓXIMOS PASSOS

### Se os testes passaram:

1. **Integrar ao main.py** (2h)
   - Seguir `INTEGRACAO-PROJETOS.md`

2. **Testar interface completa** (30 min)
   - Upload com projeto
   - Chat filtrado
   - Exportações

3. **Corrigir segurança** (30 min)
   - Seguir `ACOES-CORRETIVAS.md`

4. **Deploy** (30 min)
   - Railway/Render

---

## 🚀 COMANDOS RESUMIDOS

```powershell
# 1. Teste simples
python projetos.py

# 2. Servidor de teste
python servidor_teste.py

# 3. Em outro terminal - Testes automatizados
python teste_sistema.py

# 4. Abrir navegador
start http://localhost:8000/docs
```

---

**💻 Desenvolvido por: Marcio Góes do Nascimento**  
**🧪 Guia de Teste v1.0**

**Está tudo pronto! É só executar os comandos acima! 🚀**
