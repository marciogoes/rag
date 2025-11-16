"""
Exemplo de Integração com Chatbot Externo
Este script mostra como integrar a base RAG com qualquer chatbot
"""

import requests
from typing import List, Dict

class RAGConnector:
    """Conector para usar a base RAG em qualquer chatbot"""
    
    def __init__(self, rag_api_url: str = "http://localhost:8001"):
        """
        Inicializa o conector
        
        Args:
            rag_api_url: URL da API de consulta RAG
        """
        self.rag_api_url = rag_api_url
        
    def buscar_contexto(self, pergunta: str, n_resultados: int = 3) -> List[Dict]:
        """
        Busca contexto relevante nos documentos
        
        Args:
            pergunta: Pergunta do usuário
            n_resultados: Número de documentos a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            response = requests.post(
                f"{self.rag_api_url}/search",
                json={
                    "query": pergunta,
                    "n_results": n_resultados
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Erro ao conectar com RAG: {e}")
            return []
    
    def formatar_contexto(self, resultados: List[Dict]) -> str:
        """
        Formata os resultados em texto para enviar ao LLM
        
        Args:
            resultados: Lista de documentos do RAG
            
        Returns:
            Texto formatado com o contexto
        """
        if not resultados:
            return "Nenhum documento relevante encontrado."
        
        contexto = "📚 Contexto dos documentos:\n\n"
        
        for i, doc in enumerate(resultados, 1):
            arquivo = doc.get('metadata', {}).get('filename', 'Desconhecido')
            conteudo = doc.get('content', '')
            
            contexto += f"[Documento {i}: {arquivo}]\n"
            contexto += f"{conteudo}\n\n"
            contexto += "---\n\n"
        
        return contexto


# ============================================
# EXEMPLO 1: Integração com OpenAI
# ============================================

def exemplo_openai():
    """Exemplo de uso com OpenAI GPT"""
    from openai import OpenAI
    import os
    
    # Inicializa o conector RAG
    rag = RAGConnector()
    
    # Inicializa OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Pergunta do usuário
    pergunta = "Quais são os principais pontos do documento?"
    
    # Busca contexto no RAG
    documentos = rag.buscar_contexto(pergunta)
    contexto = rag.formatar_contexto(documentos)
    
    # Monta o prompt com contexto
    prompt = f"""{contexto}

Pergunta do usuário: {pergunta}

Por favor, responda baseado apenas nas informações dos documentos acima."""
    
    # Chama OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você responde perguntas baseado em documentos fornecidos."},
            {"role": "user", "content": prompt}
        ]
    )
    
    print(response.choices[0].message.content)


# ============================================
# EXEMPLO 2: Integração com Anthropic (Claude)
# ============================================

def exemplo_claude():
    """Exemplo de uso com Claude (Anthropic)"""
    from anthropic import Anthropic
    import os
    
    # Inicializa o conector RAG
    rag = RAGConnector()
    
    # Inicializa Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Pergunta do usuário
    pergunta = "Resuma os pontos principais dos documentos"
    
    # Busca contexto no RAG
    documentos = rag.buscar_contexto(pergunta)
    contexto = rag.formatar_contexto(documentos)
    
    # Monta o prompt
    prompt = f"""{contexto}

Pergunta: {pergunta}"""
    
    # Chama Claude
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    print(message.content[0].text)


# ============================================
# EXEMPLO 3: Webhook para Make.com / Zapier
# ============================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app_webhook = FastAPI()
rag_connector = RAGConnector()

@app_webhook.post("/webhook/make")
async def webhook_make(request: Request):
    """
    Webhook para Make.com / Integromat
    
    Recebe: {"user_message": "pergunta do usuário"}
    Retorna: {"response": "resposta com contexto", "sources": [...]}
    """
    data = await request.json()
    pergunta = data.get('user_message', '')
    
    if not pergunta:
        return JSONResponse({
            "error": "Mensagem vazia"
        }, status_code=400)
    
    # Busca contexto
    documentos = rag_connector.buscar_contexto(pergunta)
    contexto = rag_connector.formatar_contexto(documentos)
    
    # Aqui você pode integrar com qualquer LLM
    # Por simplicidade, retornamos apenas o contexto
    
    return JSONResponse({
        "contexto": contexto,
        "documentos_encontrados": len(documentos),
        "fontes": [
            doc.get('metadata', {}).get('filename', 'Desconhecido')
            for doc in documentos
        ]
    })


# ============================================
# EXEMPLO 4: Integração com LangChain
# ============================================

def exemplo_langchain():
    """Exemplo de uso com LangChain"""
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    
    # Inicializa RAG
    rag = RAGConnector()
    
    def buscar_rag(query: dict) -> str:
        """Busca no RAG e retorna contexto"""
        pergunta = query.get('question', '')
        docs = rag.buscar_contexto(pergunta)
        return rag.formatar_contexto(docs)
    
    # Cria chain
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    template = """Baseado no seguinte contexto:

{context}

Responda a pergunta: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": buscar_rag, "question": RunnablePassthrough()}
        | prompt
        | llm
    )
    
    # Usa a chain
    resposta = chain.invoke({"question": "O que dizem os documentos?"})
    print(resposta.content)


# ============================================
# TESTE SIMPLES
# ============================================

if __name__ == "__main__":
    print("🔍 Testando RAG Connector\n")
    
    # Testa conexão
    rag = RAGConnector()
    
    # Busca teste
    pergunta_teste = "teste"
    print(f"Pergunta: {pergunta_teste}")
    
    resultados = rag.buscar_contexto(pergunta_teste, n_resultados=2)
    
    if resultados:
        print(f"\n✅ Encontrados {len(resultados)} documentos relevantes:")
        for i, doc in enumerate(resultados, 1):
            arquivo = doc.get('metadata', {}).get('filename', 'Desconhecido')
            preview = doc.get('content', '')[:100]
            print(f"\n{i}. {arquivo}")
            print(f"   {preview}...")
    else:
        print("\n❌ Nenhum documento encontrado")
        print("💡 Certifique-se que a API está rodando: python api_consulta.py")
