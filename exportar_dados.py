# 📤 Guia de Exportação RAG

Este guia explica como **exportar a estrutura RAG** para usar em outros chatbots e sistemas.

---

## 🎯 Cenários de Uso

### 1. **Usar em outro chatbot Python** (Make.com, n8n, Bubble.io)
### 2. **Integrar com plataformas no-code** (Zapier, Integromat)
### 3. **Usar em aplicações Node.js, PHP, Java, etc**
### 4. **Migrar para outro banco vetorial** (Pinecone, Weaviate, Qdrant)

---

## 📦 Opção 1: Copiar o Banco Vetorial ChromaDB

O banco vetorial está em:
```
C:\Users\marci\OneDrive\Documentos\Projetos\rag\chroma_db\
```

### ✅ Vantagens:
- Plug and play
- Todos os embeddings já calculados
- Funciona offline

### 📋 Como usar:

**1. Copiar a pasta completa:**
```bash
# Copiar para outro projeto
xcopy /E /I chroma_db C:\outro\projeto\chroma_db
```

**2. No outro projeto Python:**
```python
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings

# Conectar ao banco
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("documents")

# Fazer busca
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

query_embedding = embeddings.embed_query("sua pergunta")
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print(results)
```

---

## 🔌 Opção 2: API de Consulta (Para qualquer linguagem)

Criamos um arquivo **`api_consulta.py`** que roda uma API simples.

### Como usar:

**1. Iniciar a API (em outro terminal):**
```powershell
python api_consulta.py
```

**2. Fazer consultas de QUALQUER linguagem:**

#### JavaScript/Node.js:
```javascript
const response = await fetch('http://localhost:8001/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: "qual o conteúdo sobre X?",
        n_results: 3
    })
});

const data = await response.json();
console.log(data.results);
```

#### Python:
```python
import requests

response = requests.post('http://localhost:8001/search', json={
    'query': 'qual o conteúdo sobre X?',
    'n_results': 3
})

results = response.json()['results']
```

#### PHP:
```php
$ch = curl_init('http://localhost:8001/search');
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'query' => 'qual o conteúdo sobre X?',
    'n_results' => 3
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = json_decode(curl_exec($ch), true);
print_r($response['results']);
```

#### cURL (Terminal):
```bash
curl -X POST "http://localhost:8001/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "sua pergunta", "n_results": 3}'
```

---

## 🌐 Opção 3: Exportar para JSON/CSV

Se você quer os dados em formato portável:

<function_calls>
<invoke name="Filesystem:write_file">
<parameter name="content">"""
Script para exportar dados do ChromaDB para JSON
"""
import json
import csv
from rag_engine import RAGEngine

def exportar_para_json(output_file="documentos_exportados.json"):
    """Exporta todos os documentos para JSON"""
    rag = RAGEngine(persist_directory="./chroma_db")
    
    # Pega todos os dados
    results = rag.collection.get()
    
    dados_exportados = {
        'total_documentos': len(set([m.get('doc_id') for m in results['metadatas']])),
        'total_chunks': len(results['ids']),
        'documentos': []
    }
    
    for i in range(len(results['ids'])):
        dados_exportados['documentos'].append({
            'id': results['ids'][i],
            'conteudo': results['documents'][i],
            'metadata': results['metadatas'][i] if results['metadatas'] else {}
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dados_exportados, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exportado para {output_file}")
    print(f"📊 Total: {dados_exportados['total_chunks']} chunks")

def exportar_para_csv(output_file="documentos_exportados.csv"):
    """Exporta todos os documentos para CSV"""
    rag = RAGEngine(persist_directory="./chroma_db")
    
    results = rag.collection.get()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Conteudo', 'Arquivo', 'Formato', 'Chunk'])
        
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            writer.writerow([
                results['ids'][i],
                results['documents'][i],
                metadata.get('filename', ''),
                metadata.get('format', ''),
                metadata.get('chunk_index', '')
            ])
    
    print(f"✅ Exportado para {output_file}")

if __name__ == "__main__":
    print("🔄 Exportando dados do ChromaDB...")
    exportar_para_json()
    exportar_para_csv()
    print("\n✅ Exportação concluída!")
