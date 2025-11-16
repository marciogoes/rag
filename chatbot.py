from typing import List, Dict, Any, Optional
import os
from rag_engine import RAGEngine


class RAGChatbot:
    """Chatbot com capacidades de RAG usando Claude (Anthropic)"""
    
    def __init__(self, rag_engine: RAGEngine, llm_provider: str = "anthropic"):
        """
        Inicializa o chatbot
        
        Args:
            rag_engine: Instância do motor RAG
            llm_provider: Provedor do LLM (anthropic, openai, local)
        """
        self.rag_engine = rag_engine
        self.llm_provider = llm_provider
        self.conversation_history = []
        
        # Inicializa o LLM baseado no provedor
        self._init_llm()
    
    def _init_llm(self):
        """Inicializa o modelo de linguagem"""
        if self.llm_provider == "anthropic":
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    print("⚠️ ANTHROPIC_API_KEY não configurada. Configure para usar o chatbot.")
                    self.llm = None
                else:
                    self.llm = Anthropic(api_key=api_key)
                    print("✓ Claude (Anthropic) LLM inicializado")
            except ImportError:
                print("⚠️ Biblioteca Anthropic não instalada")
                self.llm = None
        elif self.llm_provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("⚠️ OPENAI_API_KEY não configurada. Configure para usar o chatbot.")
                    self.llm = None
                else:
                    self.llm = OpenAI(api_key=api_key)
                    print("✓ OpenAI LLM inicializado")
            except ImportError:
                print("⚠️ Biblioteca OpenAI não instalada")
                self.llm = None
        else:
            print(f"⚠️ Provedor '{self.llm_provider}' não implementado ainda")
            self.llm = None
    
    def chat(self, 
             user_message: str, 
             use_rag: bool = True,
             n_context_docs: int = 3) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e gera uma resposta
        
        Args:
            user_message: Mensagem do usuário
            use_rag: Se deve usar RAG para buscar contexto
            n_context_docs: Número de documentos de contexto a buscar
            
        Returns:
            Dicionário com resposta e metadados
        """
        if not user_message or not user_message.strip():
            return {
                'response': 'Por favor, envie uma mensagem válida.',
                'sources': [],
                'error': 'empty_message'
            }
        
        # Busca contexto relevante se RAG estiver ativado
        context_docs = []
        if use_rag:
            try:
                context_docs = self.rag_engine.search(
                    query=user_message,
                    n_results=n_context_docs
                )
            except Exception as e:
                print(f"Erro ao buscar contexto: {e}")
        
        # Prepara o contexto para o LLM
        context_text = ""
        sources = []
        
        if context_docs:
            context_text = "\n\n---\n\n".join([
                f"Documento: {doc['metadata'].get('filename', 'unknown')}\n{doc['content']}"
                for doc in context_docs
            ])
            
            sources = [
                {
                    'filename': doc['metadata'].get('filename', 'unknown'),
                    'chunk_index': doc['metadata'].get('chunk_index', 0),
                    'relevance_score': 1 - doc['distance'] if doc['distance'] else None
                }
                for doc in context_docs
            ]
        
        # Gera resposta com o LLM
        if self.llm is None:
            # Modo de demonstração sem LLM
            if context_docs:
                response = self._generate_demo_response(user_message, context_docs)
            else:
                response = (
                    "⚠️ LLM não configurado. Configure ANTHROPIC_API_KEY para usar o chatbot.\n\n"
                    "No modo de demonstração, mostrando documentos relevantes encontrados..."
                )
        else:
            response = self._generate_llm_response(user_message, context_text)
        
        return {
            'response': response,
            'sources': sources,
            'context_used': len(context_docs),
            'rag_enabled': use_rag
        }
    
    def _generate_demo_response(self, query: str, context_docs: List[Dict]) -> str:
        """Gera uma resposta de demonstração sem LLM"""
        response = f"📚 Encontrei {len(context_docs)} documento(s) relevante(s) para sua pergunta:\n\n"
        
        for i, doc in enumerate(context_docs, 1):
            filename = doc['metadata'].get('filename', 'unknown')
            content_preview = doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
            
            response += f"{i}. **{filename}**\n"
            response += f"   {content_preview}\n\n"
        
        response += "\n💡 Configure sua ANTHROPIC_API_KEY para obter respostas completas do Claude."
        
        return response
    
    def _generate_llm_response(self, user_message: str, context_text: str) -> str:
        """Gera resposta usando o LLM"""
        try:
            # Prepara o prompt com contexto
            if self.llm_provider == "anthropic":
                return self._generate_anthropic_response(user_message, context_text)
            elif self.llm_provider == "openai":
                return self._generate_openai_response(user_message, context_text)
            else:
                return "Provedor de LLM não configurado corretamente."
                
        except Exception as e:
            print(f"Erro ao gerar resposta do LLM: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"
    
    def _generate_anthropic_response(self, user_message: str, context_text: str) -> str:
        """Gera resposta usando Claude (Anthropic)"""
        system_prompt = """Você é um assistente útil que responde perguntas baseado em documentos fornecidos.

Suas responsabilidades:
1. Use APENAS as informações dos documentos fornecidos para responder
2. Se a resposta não estiver nos documentos, diga claramente que não encontrou a informação
3. Cite os documentos quando relevante
4. Seja conciso mas completo
5. Responda em português do Brasil"""
        
        if context_text:
            user_prompt = f"""Contexto dos documentos:

{context_text}

---

Pergunta do usuário: {user_message}

Por favor, responda baseado apenas nas informações dos documentos acima."""
        else:
            user_prompt = f"""Não foram encontrados documentos relevantes para esta pergunta.

Pergunta do usuário: {user_message}

Por favor, informe educadamente que você não possui informações suficientes nos documentos disponíveis para responder essa pergunta."""
        
        # Chama a API da Anthropic
        message = self.llm.messages.create(
            model="claude-sonnet-4-20250514",  # Modelo mais recente
            max_tokens=2000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return message.content[0].text
    
    def _generate_openai_response(self, user_message: str, context_text: str) -> str:
        """Gera resposta usando OpenAI (mantido para compatibilidade)"""
        system_prompt = """Você é um assistente útil que responde perguntas baseado em documentos fornecidos.
Suas responsabilidades:
1. Use APENAS as informações dos documentos fornecidos para responder
2. Se a resposta não estiver nos documentos, diga claramente que não encontrou a informação
3. Cite os documentos quando relevante
4. Seja conciso mas completo
5. Responda em português do Brasil"""
        
        if context_text:
            user_prompt = f"""Contexto dos documentos:

{context_text}

---

Pergunta do usuário: {user_message}

Por favor, responda baseado apenas nas informações dos documentos acima."""
        else:
            user_prompt = f"""Não foram encontrados documentos relevantes para esta pergunta.

Pergunta do usuário: {user_message}

Por favor, informe educadamente que você não possui informações suficientes nos documentos disponíveis para responder essa pergunta."""
        
        # Chama a API do OpenAI
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def clear_history(self):
        """Limpa o histórico de conversação"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Retorna o histórico de conversação"""
        return self.conversation_history.copy()
