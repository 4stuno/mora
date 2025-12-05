"""
Script para carregar documentos na base de conhecimento.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from rag.vector_store import VectorStore
import json


def load_markdown_documents():
    """Carrega documentos Markdown."""
    documents_dir = os.path.join(os.path.dirname(__file__), "..", "documents", "markdown")
    metadata_file = os.path.join(os.path.dirname(__file__), "..", "documents", "metadata.json")
    
    # Carregar metadados
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    docs = []
    doc_metadata = []
    
    for doc_info in metadata['documents']:
        if doc_info['type'] == 'markdown':
            file_path = os.path.join(documents_dir, doc_info['file'])
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': doc_info['source'],
                        'date': doc_info['date'],
                        'theme': doc_info['theme'],
                        'type': doc_info['type'],
                        'file': doc_info['file']
                    }
                )
                docs.append(doc)
                doc_metadata.append(doc_info)
    
    return docs, doc_metadata


def main():
    """Carrega documentos no vector store."""
    print("Carregando documentos...")
    
    # Carregar documentos
    documents, metadata = load_markdown_documents()
    print(f"Documentos carregados: {len(documents)}")
    
    # Inicializar vector store
    vector_store = VectorStore()
    
    # Adicionar documentos
    print("Indexando documentos...")
    vector_store.add_documents(documents, metadata)
    
    # Salvar
    print("Salvando índice...")
    vector_store.save()
    
    print(f"Índice salvo com {len(vector_store.documents)} chunks")
    print("Concluído!")


if __name__ == "__main__":
    main()

