# 🚨 AÇÕES CORRETIVAS - ANTES DE COLOCAR EM PRODUÇÃO
**Desenvolvido por: Marcio Góes do Nascimento**

---

## ⚠️ CRÍTICO - FAÇA AGORA!

### 1. ⚠️ REVOGAR E GERAR NOVA CHAVE API

**PROBLEMA:** Sua chave API Anthropic estava exposta em vários arquivos

**AÇÃO:**
1. Acesse: https://console.anthropic.com/settings/keys
2. REVOGUE a chave atual (se ainda não fez)
3. Gere uma NOVA chave API
4. Guarde em local seguro (gerenciador de senhas)
5. **NUNCA** commite a chave no Git!

---

### 2. 🔐 GERAR SECRET_KEY FORTE

```powershell
cd "C:\Users\marci\OneDrive\Documentos\GitHub\rag"
python gerar_secret_key.py
```

Copie o resultado e guarde em local seguro!

---

### 3. 🗑️ REMOVER CREDENCIAIS DO GIT

```powershell
# O GitHub já bloqueou o push - CORRETO!
# Agora precisamos limpar os arquivos locais

# 1. Resetar último commit (se ainda não foi enviado)
git reset HEAD~1

# 2. Limpar arquivos problemáticos
notepad CHECKLIST-DEPLOY.md
notepad DEPLOY.md
notepad .env.production

# 3. Remover TODAS as chaves API dos arquivos
# Substituir por: [SUA_CHAVE_AQUI]
```

---

### 4. ✏️ LIMPAR ARQUIVOS DE DOCUMENTAÇÃO

**Arquivos que precisam ser limpos:**

1. **CHECKLIST-DEPLOY.md**
   - Remover qualquer chave API
   - Substituir por: `[SUA_CHAVE_ANTHROPIC_AQUI]`

2. **DEPLOY.md**
   - Verificar e remover qualquer chave

3. **ACOES-CORRETIVAS.md** (este arquivo)
   - Remover referências a chaves

4. **.env.production**
   - NUNCA commitar este arquivo!
   - Está no .gitignore

---

### 5. 📝 VERIFICAR .gitignore

Certifique-se que estes arquivos estão no `.gitignore`:

```
# Configuração de produção
.env
.env.local
.env.production
.env.*.local

# Credenciais
CREDENCIAIS.md
config_usuarios.py

# Dados sensíveis
chroma_db/
uploads/
exports/
data/projetos.json

# Logs
*.log
logs/
```

---

### 6. 🔄 COMMIT CORRIGIDO

Depois de limpar todos os arquivos:

```powershell
# Ver o que mudou
git status

# Adicionar arquivos limpos
git add .

# Commit SEM credenciais
git commit -m "🔒 Adiciona sistema de projetos (sem credenciais)"

# Push - agora vai funcionar!
git push origin main
```

---

## ✅ CONFIGURAR VARIÁVEIS DE AMBIENTE

**No Railway/Render, configure:**

```bash
ANTHROPIC_API_KEY=[NOVA_CHAVE_GERADA]
SECRET_KEY=[RESULTADO_DO_gerar_secret_key.py]
ENVIRONMENT=production
ADMIN_PASSWORD=[SENHA_FORTE]
MARCIO_PASSWORD=[SENHA_FORTE]
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

**NUNCA coloque credenciais no código!**

---

## 📋 CHECKLIST DE CORREÇÃO

### Antes de tentar push novamente:
- [ ] Limpar CHECKLIST-DEPLOY.md (remover chave API)
- [ ] Limpar DEPLOY.md (verificar)
- [ ] Limpar ACOES-CORRETIVAS.md (este arquivo)
- [ ] Verificar .env.production não está no commit
- [ ] Verificar CREDENCIAIS.md não está no commit
- [ ] .gitignore atualizado
- [ ] Testar: `git status` (não deve mostrar arquivos sensíveis)

### Ao fazer push:
- [ ] GitHub não deve bloquear
- [ ] Nenhum segredo detectado
- [ ] Push bem-sucedido

---

## 🆘 SE O PUSH AINDA FOR BLOQUEADO

1. **Verificar qual arquivo tem o segredo:**
   - GitHub mostra o arquivo e linha
   
2. **Editar o arquivo específico**
   
3. **Adicionar ao stage:**
   ```powershell
   git add [arquivo_corrigido]
   ```
   
4. **Commit novamente:**
   ```powershell
   git commit -m "🔒 Remove credencial de [arquivo]"
   ```
   
5. **Tentar push novamente**

---

## 💡 BOAS PRÁTICAS

### ✅ SEMPRE FAÇA:
- Use variáveis de ambiente (.env)
- Adicione .env no .gitignore
- Use arquivos .example sem credenciais
- Configure secrets no Railway/Render

### ❌ NUNCA FAÇA:
- Commitar chaves API
- Commitar senhas
- Commitar arquivos .env
- Colocar credenciais em documentação

---

**Data de criação:** 16/11/2024  
**Autor:** Marcio Góes do Nascimento  
**Status:** 🚨 CRÍTICO - Corrigir antes de push!
