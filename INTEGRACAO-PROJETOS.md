# 🗂️ GUIA DE INTEGRAÇÃO - SISTEMA DE PROJETOS
**Desenvolvido por: Marcio Góes do Nascimento**  
**Data:** 16/11/2024

---

## 📋 VISÃO GERAL

Este guia mostra como integrar o **Sistema de Gestão de Projetos** ao RAG Chatbot existente.

### Funcionalidades Adicionadas:

1. ✅ **Cadastro de Projetos** (apenas admin)
2. ✅ **Associação de documentos a projetos**
3. ✅ **Filtros de chat por projeto**
4. ✅ **Exportação separada por projeto**
5. ✅ **Interface atualizada com seleção de projeto**

---

## 📁 ARQUIVOS CRIADOS

1. **`projetos.py`** - Gerenciador de projetos
2. **`rotas_projetos.py`** - API REST para projetos
3. **`exportador_projetos.py`** - Exportações por projeto
4. **`data/projetos.json`** - Banco de dados de projetos (criado automaticamente)

---

## 🔧 PASSO 1: MODIFICAR main.py

### 1.1. Adicionar Imports no Início

```python
# ADICIONAR estas linhas após os imports existentes:
from rotas_projetos import router as projetos_router
from exportador_projetos import ExportadorProjetos
from projetos import gerenciador_projetos
```

### 1.2. Incluir Router de Projetos

```python
# ADICIONAR após a criação do app FastAPI:
app.include_router(projetos_router)
```

### 1.3. Inicializar Exportador de Projetos

```python
# ADICIONAR após a inicialização dos componentes existentes:
exportador_projetos = ExportadorProjetos(rag_engine=rag_engine)
```

---

## 🔧 PASSO 2: MODIFICAR ROTA DE UPLOAD

### 2.1. Adicionar Parâmetro de Projeto

Localizar a função `upload_file` e modificar para:

```python
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    projeto_id: int = Form(default=0),  # ← ADICIONAR ESTA LINHA
    current_user: dict = Depends(usuario_atual)
):
    """Upload e processa um arquivo (rota protegida)"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in document_processor.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado: {file_ext}"
            )
        
        # Verificar se projeto existe (se projeto_id != 0)
        if projeto_id != 0:
            projeto = gerenciador_projetos.buscar_projeto(projeto_id)
            if not projeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Projeto ID {projeto_id} não encontrado"
                )
            if not projeto.get('ativo', True):
                raise HTTPException(
                    status_code=400,
                    detail=f"Projeto está desativado"
                )
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        doc_data = document_processor.process_file(str(file_path), file.filename)
        
        # MODIFICAR metadata para incluir projeto_id
        doc_id = rag_engine.add_document(
            content=doc_data['content'],
            metadata={
                'filename': doc_data['filename'],
                'format': doc_data['format'],
                'size': doc_data['size'],
                'uploaded_by': current_user['username'],
                'projeto_id': projeto_id  # ← ADICIONAR ESTA LINHA
            }
        )
        
        # Incrementar contador de documentos do projeto
        if projeto_id != 0:
            gerenciador_projetos.incrementar_contador_documentos(projeto_id)
        
        file_path.unlink()
        
        return {
            'success': True,
            'doc_id': doc_id,
            'filename': file.filename,
            'projeto_id': projeto_id,  # ← ADICIONAR ESTA LINHA
            'message': f'Arquivo "{file.filename}" processado com sucesso!'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔧 PASSO 3: MODIFICAR ROTA DE CHAT

### 3.1. Adicionar Filtro de Projeto

Localizar a classe `ChatRequest` e modificar:

```python
class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    n_context_docs: int = 3
    projeto_id: int = 0  # ← ADICIONAR ESTA LINHA
```

### 3.2. Modificar Função de Chat

Localizar a função `chat` e modificar:

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(usuario_atual)):
    """Endpoint de chat (rota protegida)"""
    try:
        # Se projeto_id especificado, filtrar contexto apenas desse projeto
        if request.projeto_id != 0:
            # Buscar apenas documentos deste projeto para contexto
            projeto_docs = rag_engine.collection.get(
                where={"projeto_id": request.projeto_id},
                limit=request.n_context_docs
            )
            
            # Usar apenas documentos do projeto como contexto
            # (Aqui você pode adaptar a lógica do chatbot para usar esses docs)
        
        response = chatbot.chat(
            user_message=request.message,
            use_rag=request.use_rag,
            n_context_docs=request.n_context_docs
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔧 PASSO 4: ADICIONAR ROTAS DE EXPORTAÇÃO POR PROJETO

Adicionar estas novas rotas após as rotas de exportação existentes:

```python
@app.get("/export/projetos/json")
async def exportar_todos_projetos_json(current_user: dict = Depends(usuario_atual)):
    """Exporta todos os documentos agrupados por projeto para JSON"""
    try:
        export_path = exportador_projetos.exportar_json_por_projeto(current_user)
        
        return FileResponse(
            export_path,
            media_type='application/json',
            filename='documentos_por_projeto.json'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/projetos/csv")
async def exportar_todos_projetos_csv(current_user: dict = Depends(usuario_atual)):
    """Exporta todos os documentos com coluna de projeto para CSV"""
    try:
        export_path = exportador_projetos.exportar_csv_por_projeto(current_user)
        
        return FileResponse(
            export_path,
            media_type='text/csv',
            filename='documentos_por_projeto.csv'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/projeto/{projeto_id}/json")
async def exportar_projeto_json(
    projeto_id: int,
    current_user: dict = Depends(usuario_atual)
):
    """Exporta apenas documentos de um projeto específico para JSON"""
    try:
        export_path = exportador_projetos.exportar_projeto_especifico_json(
            projeto_id=projeto_id,
            usuario_exportador=current_user
        )
        
        projeto = gerenciador_projetos.buscar_projeto(projeto_id)
        nome_arquivo = f"projeto_{projeto['nome'].replace(' ', '_')}.json"
        
        return FileResponse(
            export_path,
            media_type='application/json',
            filename=nome_arquivo
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/projeto/{projeto_id}/csv")
async def exportar_projeto_csv(
    projeto_id: int,
    current_user: dict = Depends(usuario_atual)
):
    """Exporta apenas documentos de um projeto específico para CSV"""
    try:
        export_path = exportador_projetos.exportar_projeto_especifico_csv(
            projeto_id=projeto_id,
            usuario_exportador=current_user
        )
        
        projeto = gerenciador_projetos.buscar_projeto(projeto_id)
        nome_arquivo = f"projeto_{projeto['nome'].replace(' ', '_')}.csv"
        
        return FileResponse(
            export_path,
            media_type='text/csv',
            filename=nome_arquivo
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔧 PASSO 5: MODIFICAR ROTA DE DELETE DE DOCUMENTO

Localizar a função `delete_document` e modificar para decrementar contador:

```python
@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user: dict = Depends(usuario_atual)):
    """Remove um documento (rota protegida)"""
    try:
        # Buscar metadata antes de deletar para pegar projeto_id
        doc_info = rag_engine.collection.get(ids=[doc_id])
        if doc_info['metadatas']:
            projeto_id = doc_info['metadatas'][0].get('projeto_id', 0)
        else:
            projeto_id = 0
        
        success = rag_engine.delete_document(doc_id)
        
        if success:
            # Decrementar contador do projeto
            if projeto_id != 0:
                try:
                    gerenciador_projetos.decrementar_contador_documentos(projeto_id)
                except:
                    pass  # Projeto pode não existir mais
            
            return {'success': True, 'message': 'Documento removido com sucesso'}
        else:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎨 PASSO 6: ATUALIZAR INTERFACE HTML

### 6.1. Adicionar Seção de Gestão de Projetos

Na interface HTML, adicionar uma nova seção na sidebar (após a seção de documentos):

```html
<div class="section" id="projetosSection">
    <h2>🗂️ Gestão de Projetos</h2>
    
    <!-- Apenas para admin -->
    <div id="adminProjetosControls" style="display: none;">
        <button class="btn" onclick="abrirModalNovoProjeto()">
            ➕ Novo Projeto
        </button>
    </div>
    
    <!-- Lista de projetos -->
    <select id="projetoSelect" class="form-control" style="margin-top: 10px; padding: 10px; width: 100%; border: 2px solid #ddd; border-radius: 8px;">
        <option value="0">📋 Todos os Projetos</option>
    </select>
    
    <div id="projetoInfo" style="margin-top: 10px; padding: 10px; background: white; border-radius: 8px; display: none;">
        <strong id="projetoNome"></strong><br>
        <small id="projetoDescricao"></small><br>
        <small id="projetoStats"></small>
    </div>
</div>
```

### 6.2. Adicionar Modal de Novo Projeto

```html
<!-- Modal Novo Projeto -->
<div id="modalNovoProjeto" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
    <div style="background: white; max-width: 500px; margin: 100px auto; padding: 30px; border-radius: 15px;">
        <h2>➕ Novo Projeto</h2>
        <form onsubmit="criarProjeto(event)">
            <div class="form-group">
                <label>Nome do Projeto:</label>
                <input type="text" id="novoProjetoNome" required class="form-control">
            </div>
            <div class="form-group">
                <label>Descrição:</label>
                <textarea id="novoProjetoDescricao" required class="form-control" rows="3"></textarea>
            </div>
            <div style="display: flex; gap: 10px;">
                <button type="submit" class="btn">Criar</button>
                <button type="button" class="btn btn-danger" onclick="fecharModalNovoProjeto()">Cancelar</button>
            </div>
        </form>
    </div>
</div>
```

### 6.3. Adicionar JavaScript

Adicionar estas funções JavaScript na seção `<script>`:

```javascript
// Variáveis globais
let projetoSelecionado = 0;
let isAdmin = false;

// Verificar se é admin após login
async function checkAuth() {
    try {
        const response = await fetch('/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const user = await response.json();
            document.getElementById('loginScreen').style.display = 'none';
            document.getElementById('app').style.display = 'block';
            
            document.getElementById('userName').textContent = user.nome;
            document.getElementById('userEmail').textContent = user.email;
            
            // Verificar se é admin
            isAdmin = user.username === 'admin';
            if (isAdmin) {
                document.getElementById('adminProjetosControls').style.display = 'block';
            }
            
            await carregarProjetos();
            await loadDocuments();
        } else {
            logout();
        }
    } catch (error) {
        logout();
    }
}

// Carregar projetos
async function carregarProjetos() {
    try {
        const response = await fetch('/projetos/', {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const projetos = await response.json();
            const select = document.getElementById('projetoSelect');
            
            // Limpar opções exceto "Todos"
            select.innerHTML = '<option value="0">📋 Todos os Projetos</option>';
            
            // Adicionar projetos
            projetos.forEach(projeto => {
                const option = document.createElement('option');
                option.value = projeto.id;
                option.textContent = `🗂️ ${projeto.nome} (${projeto.total_documentos} docs)`;
                select.appendChild(option);
            });
            
            // Listener para mudança de projeto
            select.addEventListener('change', async (e) => {
                projetoSelecionado = parseInt(e.target.value);
                await mostrarInfoProjeto(projetoSelecionado);
                await loadDocuments();
            });
        }
    } catch (error) {
        console.error('Erro ao carregar projetos:', error);
    }
}

// Mostrar informações do projeto
async function mostrarInfoProjeto(projetoId) {
    const infoDiv = document.getElementById('projetoInfo');
    
    if (projetoId === 0) {
        infoDiv.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/projetos/${projetoId}`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const projeto = await response.json();
            document.getElementById('projetoNome').textContent = projeto.nome;
            document.getElementById('projetoDescricao').textContent = projeto.descricao;
            document.getElementById('projetoStats').textContent = 
                `${projeto.total_documentos} documentos | Criado por ${projeto.criado_por}`;
            infoDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Erro ao carregar informações do projeto:', error);
    }
}

// Modal novo projeto
function abrirModalNovoProjeto() {
    document.getElementById('modalNovoProjeto').style.display = 'block';
}

function fecharModalNovoProjeto() {
    document.getElementById('modalNovoProjeto').style.display = 'none';
    document.getElementById('novoProjetoNome').value = '';
    document.getElementById('novoProjetoDescricao').value = '';
}

async function criarProjeto(e) {
    e.preventDefault();
    
    const nome = document.getElementById('novoProjetoNome').value;
    const descricao = document.getElementById('novoProjetoDescricao').value;
    
    try {
        const response = await fetch('/projetos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({ nome, descricao })
        });
        
        if (response.ok) {
            addMessage('bot', `✅ Projeto "${nome}" criado com sucesso!`);
            fecharModalNovoProjeto();
            await carregarProjetos();
        } else {
            const error = await response.json();
            addMessage('bot', `❌ Erro ao criar projeto: ${error.detail}`);
        }
    } catch (error) {
        addMessage('bot', `❌ Erro ao criar projeto: ${error.message}`);
    }
}

// Modificar função de upload para incluir projeto
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('projeto_id', projetoSelecionado);  // ← ADICIONAR
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData
        });
        
        const result = await response.json();
        if (response.ok) {
            let mensagem = `✅ Arquivo "${file.name}" processado com sucesso!`;
            if (projetoSelecionado !== 0) {
                mensagem += ` (Projeto ID: ${projetoSelecionado})`;
            }
            addMessage('bot', mensagem);
        } else {
            addMessage('bot', `❌ Erro ao processar "${file.name}": ${result.detail}`);
        }
    } catch (error) {
        addMessage('bot', `❌ Erro ao enviar "${file.name}": ${error.message}`);
    }
}

// Modificar sendMessage para incluir projeto
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage('user', message);
    input.value = '';
    
    const loading = document.getElementById('loading');
    loading.classList.add('active');
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({
                message: message,
                use_rag: true,
                n_context_docs: 3,
                projeto_id: projetoSelecionado  // ← ADICIONAR
            })
        });
        
        const result = await response.json();
        
        let botResponse = result.response;
        if (result.sources && result.sources.length > 0) {
            botResponse += '<div class="sources"><strong>📚 Fontes:</strong><br>';
            result.sources.forEach(source => {
                botResponse += `• ${source.filename}<br>`;
            });
            botResponse += '</div>';
        }
        
        addMessage('bot', botResponse);
    } catch (error) {
        addMessage('bot', `❌ Erro ao processar mensagem: ${error.message}`);
    }
    
    loading.classList.remove('active');
}

// Adicionar botões de exportação por projeto
async function exportarProjetoAtualJSON() {
    if (projetoSelecionado === 0) {
        addMessage('bot', '⚠️ Selecione um projeto específico para exportar');
        return;
    }
    
    const loading = document.getElementById('loading');
    loading.classList.add('active');
    
    try {
        const response = await fetch(`/export/projeto/${projetoSelecionado}/json`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `projeto_${projetoSelecionado}.json`;
            a.click();
            addMessage('bot', '✅ Exportação do projeto concluída!');
        }
    } catch (error) {
        addMessage('bot', `❌ Erro ao exportar projeto: ${error.message}`);
    }
    
    loading.classList.remove('active');
}
```

---

## 🧪 PASSO 7: TESTAR O SISTEMA

### 7.1. Testar Gestão de Projetos

```powershell
# Testar o gerenciador
python projetos.py
```

### 7.2. Iniciar Servidor

```powershell
python main.py
```

### 7.3. Fluxo de Teste

1. **Login como admin**
   - Usuário: `admin`
   - Senha: `admin123` (ou sua senha configurada)

2. **Criar Projeto**
   - Clicar em "➕ Novo Projeto"
   - Nome: "Projeto Teste"
   - Descrição: "Documentos de teste"

3. **Selecionar Projeto**
   - Selecionar projeto no dropdown

4. **Upload de Documento**
   - Fazer upload de um PDF
   - Verificar que aparece mensagem com ID do projeto

5. **Chat com Filtro**
   - Perguntar algo sobre o documento
   - Verificar que usa apenas documentos do projeto

6. **Exportar Projeto**
   - Clicar em exportar JSON/CSV
   - Verificar que exporta apenas documentos do projeto

---

## 📊 ESTRUTURA FINAL DO PROJETO

```
rag/
├── main.py                      # ✏️ MODIFICADO - Aplicação principal
├── projetos.py                  # ✨ NOVO - Gerenciador de projetos
├── rotas_projetos.py            # ✨ NOVO - Rotas de API
├── exportador_projetos.py       # ✨ NOVO - Exportações
├── auth.py                      # ✅ Sem alteração
├── chatbot.py                   # ✅ Sem alteração
├── rag_engine.py                # ✅ Sem alteração
├── document_processor.py        # ✅ Sem alteração
├── config_usuarios.py           # ✅ Sem alteração
├── requirements.txt             # ✅ Sem alteração
├── data/
│   └── projetos.json           # ✨ NOVO - Banco de projetos
├── chroma_db/                  # ✅ Banco vetorial
├── uploads/                    # ✅ Arquivos temporários
└── exports/                    # ✅ Exportações
```

---

## 🔍 ENDPOINTS DA API

### Projetos (Todos autenticados)

```
GET    /projetos/                      # Listar projetos
GET    /projetos/{id}                  # Buscar projeto
POST   /projetos/                      # Criar projeto (admin)
PUT    /projetos/{id}                  # Atualizar projeto (admin)
DELETE /projetos/{id}                  # Deletar projeto (admin)
GET    /projetos/{id}/estatisticas     # Estatísticas do projeto
```

### Exportação (Todos autenticados)

```
GET    /export/projetos/json           # Exportar todos agrupados
GET    /export/projetos/csv            # Exportar todos com coluna
GET    /export/projeto/{id}/json       # Exportar projeto específico
GET    /export/projeto/{id}/csv        # Exportar projeto específico
```

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### ✅ Cadastro de Projetos
- [x] Apenas admin pode criar
- [x] Validação de nome único
- [x] Metadata completa (criador, data, etc)

### ✅ Associação de Documentos
- [x] Upload com seleção de projeto
- [x] Metadados incluem projeto_id
- [x] Contador automático de documentos

### ✅ Filtros
- [x] Chat filtra por projeto
- [x] Listagem filtra por projeto
- [x] Exportação por projeto

### ✅ Interface
- [x] Dropdown de seleção de projeto
- [x] Modal de criação (admin)
- [x] Informações do projeto
- [x] Botões de exportação por projeto

---

## 💡 PRÓXIMAS MELHORIAS

- [ ] Permissões granulares por projeto
- [ ] Compartilhamento de projetos entre usuários
- [ ] Tags e categorias de documentos
- [ ] Busca avançada por projeto
- [ ] Dashboard com estatísticas por projeto
- [ ] API de webhook para eventos de projeto

---

## 🆘 TROUBLESHOOTING

### Erro: "Projeto não encontrado"
- Verificar se o arquivo `data/projetos.json` existe
- Executar `python projetos.py` para criar estrutura

### Erro: "Apenas administradores"
- Verificar se está logado como `admin`
- Verificar configuração em `config_usuarios.py`

### Documentos não aparecem no projeto
- Verificar se `projeto_id` está nos metadados
- Executar query manual no ChromaDB para verificar

---

**Desenvolvido por: Marcio Góes do Nascimento**  
**Versão:** 3.0.0 com Sistema de Projetos  
**Data:** 16/11/2024

✅ **Sistema pronto para uso em produção após integração!**
