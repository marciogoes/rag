import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document as LangchainDocument


class RAGEngine:
    """Motor de Retrieval Augmented Generation"""
    
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "documents",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa o motor RAG
        
        Args:
            persist_directory: Diretório para persistir o banco vetorial
            collection_name: Nome da coleção no ChromaDB
            embedding_model: Modelo de embeddings a ser usado
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Cria diretório se não existir
        os.makedirs(persist_directory, exist_ok=True)
        
        # Inicializa embeddings
        print("Carregando modelo de embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Inicializa ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Tenta obter a coleção existente ou criar uma nova
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Coleção '{collection_name}' carregada com {self.collection.count()} documentos")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Nova coleção '{collection_name}' criada")
        
        # Inicializa text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def add_document(self, 
                     content: str, 
                     metadata: Dict[str, Any]) -> str:
        """
        Adiciona um documento ao banco vetorial
        
        Args:
            content: Conteúdo textual do documento
            metadata: Metadados do documento (filename, format, etc)
            
        Returns:
            ID do documento adicionado
        """
        if not content or not content.strip():
            raise ValueError("Conteúdo do documento está vazio")
        
        # Divide o documento em chunks
        chunks = self.text_splitter.split_text(content)
        
        if not chunks:
            raise ValueError("Não foi possível dividir o documento em chunks")
        
        # Gera ID único para o documento
        doc_id = str(uuid.uuid4())
        
        # Prepara os dados para inserção
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            
            # Adiciona informações do chunk aos metadados
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'doc_id': doc_id,
                'chunk_index': i,
                'total_chunks': len(chunks)
            })
            metadatas.append(chunk_metadata)
        
        # Gera embeddings e adiciona ao ChromaDB
        embeddings_list = self.embeddings.embed_documents(documents)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings_list,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Documento '{metadata.get('filename', 'unknown')}' adicionado com {len(chunks)} chunks")
        
        return doc_id
    
    def search(self, 
               query: str, 
               n_results: int = 5,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes para uma query
        
        Args:
            query: Texto da busca
            n_results: Número de resultados a retornar
            filter_metadata: Filtros opcionais para metadados
            
        Returns:
            Lista de documentos relevantes com scores
        """
        if not query or not query.strip():
            raise ValueError("Query de busca está vazia")
        
        # Gera embedding da query
        query_embedding = self.embeddings.embed_query(query)
        
        # Busca no ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Formata os resultados
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None,
                    'id': results['ids'][0][i] if results['ids'] else None
                })
        
        return formatted_results
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Remove um documento do banco vetorial
        
        Args:
            doc_id: ID do documento a ser removido
            
        Returns:
            True se removido com sucesso
        """
        try:
            # Busca todos os chunks do documento
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Documento {doc_id} removido ({len(results['ids'])} chunks)")
                return True
            
            return False
        except Exception as e:
            print(f"Erro ao remover documento: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Lista todos os documentos únicos no banco
        
        Returns:
            Lista de documentos com seus metadados
        """
        try:
            # Pega todos os registros
            results = self.collection.get()
            
            if not results['metadatas']:
                return []
            
            # Agrupa por doc_id
            docs_dict = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('doc_id')
                if doc_id and doc_id not in docs_dict:
                    docs_dict[doc_id] = {
                        'doc_id': doc_id,
                        'filename': metadata.get('filename', 'unknown'),
                        'format': metadata.get('format', 'unknown'),
                        'size': metadata.get('size', 0),
                        'chunks': metadata.get('total_chunks', 0)
                    }
            
            return list(docs_dict.values())
        except Exception as e:
            print(f"Erro ao listar documentos: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            total_chunks = self.collection.count()
            documents = self.list_documents()
            
            return {
                'total_documents': len(documents),
                'total_chunks': total_chunks,
                'collection_name': self.collection_name,
                'embedding_model': self.embeddings.model_name
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def clear_all(self) -> bool:
        """
        Remove todos os documentos do banco
        
        Returns:
            True se removido com sucesso
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("Banco de dados limpo com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao limpar banco: {e}")
            return False
