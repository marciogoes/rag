# ✅ CHECKLIST RÁPIDO - COLOCAR EM PRODUÇÃO
**Por: Marcio Góes do Nascimento**

---

## 🎯 MÉTODO RÁPIDO - RAILWAY (15 MINUTOS)

### ANTES DE COMEÇAR:

```powershell
# 1. Gerar SECRET_KEY forte
python gerar_secret_key.py
# Copie o resultado!

# 2. Instalar dependência faltante
pip install python-dotenv

# 3. Testar localmente
python main.py
# Acesse http://localhost:8000 e teste
```

---

### PASSO 1: GITHUB (5 MIN)

```powershell
# 1.1. Criar repo em https://github.com/new
#      Nome: rag-chatbot-claude
#      Private: ✅

# 1.2. No PowerShell, na pasta do projeto:
cd "C:\Users\marci\OneDrive\Documentos\GitHub\rag"

git init
git add .
git commit -m "Sistema RAG - Marcio Góes do Nascimento"
git remote add origin https://github.com/SEU-USUARIO/rag-chatbot-claude.git
git branch -M main
git push -u origin main
```

---

### PASSO 2: RAILWAY (5 MIN)

```
1. Acesse: https://railway.app
2. Login com GitHub
3. New Project → Deploy from GitHub repo
4. Selecione: rag-chatbot-claude
5. Railway detecta Python automaticamente!
```

---

### PASSO 3: VARIÁVEIS DE AMBIENTE (3 MIN)

**No Railway → Variables → Add:**

```
ANTHROPIC_API_KEY
Cole: [SUA_CHAVE_ANTHROPIC_AQUI]

SECRET_KEY
Cole: [RESULTADO_DO_gerar_secret_key.py]

ENVIRONMENT
Digite: production

ADMIN_PASSWORD
Digite: [SUA_SENHA_ADMIN_SEGURA]

MARCIO_PASSWORD
Digite: [SUA_SENHA_USER_SEGURA]
```

**⚠️ IMPORTANTE:**
- Gere sua chave em: https://console.anthropic.com/settings/keys
- Use senhas FORTES e diferentes das padrão
- NUNCA commite credenciais no Git!

---

### PASSO 4: DEPLOY (2 MIN)

```
1. Railway vai fazer deploy automaticamente
2. Aguarde ~2 minutos
3. Clique em "View Logs" para acompanhar
4. Quando terminar, clique em "Generate Domain"
5. Sua URL: https://rag-chatbot-claude-production.up.railway.app
```

---

### PASSO 5: TESTAR! 🎉

```
1. Abra a URL gerada
2. Login:
   - Usuário: admin ou marcio
   - Senha: [sua senha configurada]
3. Faça upload de um documento
4. Pergunte algo ao Claude!
```

---

## ⚡ COMANDOS ÚTEIS

### Atualizar em produção:
```powershell
git add .
git commit -m "Atualização"
git push
# Railway faz deploy automático!
```

### Ver logs:
```
Railway → Seu projeto → Logs
```

### Configurar domínio próprio:
```
Railway → Settings → Domains → Add Custom Domain
```

---

## 🔒 SEGURANÇA - DEPOIS DO DEPLOY

### Obrigatório:
- [ ] SECRET_KEY única gerada
- [ ] HTTPS ativo (Railway faz automaticamente)
- [ ] Senhas fortes configuradas
- [ ] Teste todas as funcionalidades

### Recomendado:
- [ ] Trocar senhas padrão
- [ ] Configurar domínio próprio
- [ ] Configurar backup do ChromaDB
- [ ] Monitorar logs regularmente

---

## 💰 CUSTOS

**Railway:**
- Free: $5/mês de crédito grátis (500h)
- Suficiente para: Testes e uso moderado
- Upgrade: $20/mês (uso ilimitado)

**Se precisar de mais:**
- Render: $7/mês
- DigitalOcean: $6/mês
- AWS Lightsail: $5/mês

---

## 🆘 PROBLEMAS?

### Erro no build:
```
Verifique: requirements.txt está completo?
```

### Erro "Module not found":
```
Railway → Variables → Add:
PYTHONPATH=/app
```

### App não inicia:
```
Railway → Logs
Veja o erro específico
```

### ChromaDB não persiste:
```
Railway → Settings → Volumes
Add: /app/chroma_db
```

---

## 📱 PRÓXIMOS PASSOS

1. ✅ Sistema em produção
2. 🌐 Configurar domínio próprio (opcional)
3. 📊 Monitorar uso e logs
4. 🔄 Fazer backup regular do ChromaDB
5. 👥 Adicionar mais usuários conforme necessário

---

**🎉 PRONTO! SEU SISTEMA ESTÁ NO AR!**

**Desenvolvido por: Marcio Góes do Nascimento**  
**Tempo estimado: 15 minutos**  
**Dificuldade: ⭐ Fácil**
