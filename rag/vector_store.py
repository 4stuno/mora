"""
Módulo para gerenciamento do vector store usando FAISS.
"""
import os
import pickle
from typing import List, Dict, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class VectorStore:
    """Gerenciador do vector store FAISS para busca semântica."""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", 
                 store_path: str = "./data/vector_store"):
        """
        Inicializa o vector store.
        
        Args:
            embedding_model: Nome do modelo de embeddings
            store_path: Caminho para salvar/carregar o índice
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.store_path = store_path
        self.index: Optional[faiss.Index] = None
        self.documents: List[Document] = []
        self.metadata: List[Dict] = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Criar diretório se não existir
        os.makedirs(store_path, exist_ok=True)
        
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Gera embeddings para uma lista de textos."""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.astype('float32')
    
    def add_documents(self, documents: List[Document], metadata: Optional[List[Dict]] = None):
        """
        Adiciona documentos ao vector store.
        
        Args:
            documents: Lista de documentos LangChain
            metadata: Metadados opcionais para cada documento
        """
        # Dividir documentos em chunks
        chunks = []
        chunk_metadata = []
        
        for i, doc in enumerate(documents):
            doc_chunks = self.text_splitter.split_text(doc.page_content)
            for chunk in doc_chunks:
                chunks.append(chunk)
                chunk_meta = doc.metadata.copy() if doc.metadata else {}
                chunk_meta['source_doc_id'] = i
                chunk_meta['chunk_index'] = len(chunks) - 1
                if metadata and i < len(metadata):
                    chunk_meta.update(metadata[i])
                chunk_metadata.append(chunk_meta)
        
        if not chunks:
            return
        
        # Gerar embeddings
        embeddings = self._get_embeddings(chunks)
        dimension = embeddings.shape[1]
        
        # Criar ou atualizar índice FAISS
        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)
        
        # Adicionar ao índice
        self.index.add(embeddings)
        
        # Armazenar documentos e metadados
        for chunk, meta in zip(chunks, chunk_metadata):
            self.documents.append(Document(page_content=chunk, metadata=meta))
            self.metadata.append(meta)
    
    def search(self, query: str, k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Busca documentos similares à query.
        
        Args:
            query: Texto da consulta
            k: Número de resultados a retornar
            filters: Filtros opcionais de metadados
            
        Returns:
            Lista de documentos com scores de similaridade
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Gerar embedding da query
        query_embedding = self._get_embeddings([query])
        
        # Buscar no índice
        k = min(k, len(self.documents))
        distances, indices = self.index.search(query_embedding, k)
        
        # Preparar resultados
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx]
                meta = self.metadata[idx]
                
                # Aplicar filtros se fornecidos
                if filters:
                    if not all(meta.get(k) == v for k, v in filters.items()):
                        continue
                
                results.append({
                    'document': doc,
                    'score': float(1 / (1 + distance)),  # Converter distância em score
                    'metadata': meta,
                    'distance': float(distance)
                })
        
        return results
    
    def save(self):
        """Salva o índice e documentos em disco."""
        if self.index is None:
            return
        
        # Salvar índice FAISS
        faiss.write_index(self.index, os.path.join(self.store_path, "index.faiss"))
        
        # Salvar documentos e metadados
        with open(os.path.join(self.store_path, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)
        
        with open(os.path.join(self.store_path, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)
    
    def load(self):
        """Carrega o índice e documentos do disco."""
        index_path = os.path.join(self.store_path, "index.faiss")
        docs_path = os.path.join(self.store_path, "documents.pkl")
        meta_path = os.path.join(self.store_path, "metadata.pkl")
        
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        
        if os.path.exists(docs_path):
            with open(docs_path, "rb") as f:
                self.documents = pickle.load(f)
        
        if os.path.exists(meta_path):
            with open(meta_path, "rb") as f:
                self.metadata = pickle.load(f)

