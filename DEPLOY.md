# 🚀 GUIA DE DEPLOY EM PRODUÇÃO
**Desenvolvido por: Marcio Góes do Nascimento**

Este guia te leva do desenvolvimento para produção em 30 minutos!

---

## 📋 PRÉ-REQUISITOS

Antes de começar, você precisa:

✅ Conta no GitHub (gratuita)  
✅ Conta no Railway/Render (gratuita)  
✅ Chave da API Anthropic  
✅ Git instalado no seu computador  

---

## 🎯 MÉTODO 1: RAILWAY.APP (RECOMENDADO - 15 MIN)

### Passo 1: Criar Repositório no GitHub

**1.1. Acesse:** https://github.com/new

**1.2. Configure:**
- Repository name: `rag-chatbot-claude`
- Description: `Sistema RAG com Claude - Desenvolvido por Marcio Góes do Nascimento`
- Private ✅ (recomendado)
- Clique em "Create repository"

**1.3. No seu computador (PowerShell):**

```powershell
# Entre na pasta do projeto
cd "C:\Users\marci\OneDrive\Documentos\GitHub\rag"

# Inicialize o Git
git init

# Adicione todos os arquivos
git add .

# Primeiro commit
git commit -m "Sistema RAG com Claude - Desenvolvido por Marcio Góes do Nascimento"

# Conecte com GitHub (substitua SEU-USUARIO pelo seu usuário)
git remote add origin https://github.com/SEU-USUARIO/rag-chatbot-claude.git

# Envie para o GitHub
git branch -M main
git push -u origin main
```

---

### Passo 2: Deploy no Railway

**2.1. Acesse:** https://railway.app/

**2.2. Faça login com GitHub**

**2.3. Clique em "New Project"**

**2.4. Selecione "Deploy from GitHub repo"**

**2.5. Escolha o repositório `rag-chatbot-claude`**

**2.6. Railway vai detectar automaticamente que é Python!**

---

### Passo 3: Configurar Variáveis de Ambiente

**3.1. No Railway, clique na aba "Variables"**

**3.2. Adicione as seguintes variáveis:**

```
ANTHROPIC_API_KEY=[SUA_CHAVE_ANTHROPIC_AQUI]

SECRET_KEY=[RESULTADO_DO_gerar_secret_key.py]

ENVIRONMENT=production

ADMIN_PASSWORD=[SUA_SENHA_ADMIN_FORTE]

MARCIO_PASSWORD=[SUA_SENHA_USER_FORTE]

ACCESS_TOKEN_EXPIRE_MINUTES=480
```

**⚠️ IMPORTANTE:** 
- Gere sua chave em: https://console.anthropic.com/settings/keys
- Gere SECRET_KEY forte com: `python gerar_secret_key.py`
- Use senhas FORTES

**3.3. Clique em "Deploy"**

---

### Passo 4: Obter URL e Testar

**4.1. Railway vai gerar uma URL automática:**
```
https://rag-chatbot-claude-production.up.railway.app
```

**4.2. Acesse a URL e faça login!**

**4.3. Configure domínio personalizado (opcional):**
- Settings → Domains → Add Custom Domain

---

## 🎯 MÉTODO 2: RENDER.COM (15 MIN)

### Passo 1: Mesmos passos do GitHub acima

### Passo 2: Deploy no Render

**2.1. Acesse:** https://render.com/

**2.2. New → Web Service**

**2.3. Conecte com GitHub e selecione o repo**

**2.4. Configure:**
- Name: `rag-chatbot-claude`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**2.5. Adicione variáveis de ambiente (mesmas do Railway)**

**2.6. Clique em "Create Web Service"**

---

## 🔒 CHECKLIST DE SEGURANÇA

Antes de ir para produção, verifique:

### Essencial:
- [ ] SECRET_KEY forte e única gerada
- [ ] Senhas fortes para todos os usuários
- [ ] HTTPS ativado (SSL/TLS)
- [ ] Variáveis de ambiente configuradas
- [ ] .env não commitado no Git
- [ ] CORS configurado corretamente

### Recomendado:
- [ ] Backup automático do ChromaDB
- [ ] Monitoramento de erros (Sentry)
- [ ] Rate limiting nas APIs
- [ ] Logs configurados

---

## 📊 MONITORAMENTO

### Logs no Railway/Render:
- Acesse a aba "Logs" no painel
- Configure alertas de erro

---

## 🔄 ATUALIZAÇÕES

### Railway/Render (automático):
```powershell
# Local
git add .
git commit -m "Atualização do sistema"
git push

# Deploy automático acontece!
```

---

## 💰 CUSTOS ESTIMADOS

| Plataforma | Custo/mês | Recursos |
|------------|-----------|----------|
| Railway (Free) | $0 | 500h, $5 crédito |
| Railway (Pro) | $20 | Ilimitado |
| Render (Free) | $0 | Hiberna após inatividade |
| Render (Starter) | $7 | Sempre ativo |
| DigitalOcean | $6 | 1GB RAM, 25GB SSD |

---

## 🎉 PRONTO!

Seu sistema RAG está em produção!

**URLs úteis:**
- Aplicação: `https://seu-dominio.com`
- Docs API: `https://seu-dominio.com/docs`
- Health Check: `https://seu-dominio.com/health`

---

**Sistema desenvolvido por: Marcio Góes do Nascimento**  
**Versão:** 2.0.0 Production Ready  
**Suporte:** Via GitHub Issues
