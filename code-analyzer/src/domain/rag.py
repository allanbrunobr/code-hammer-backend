from typing import List, Any
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

class RAG:

    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        """
               Divide os documentos em partes menores para facilitar o processamento e a recuperação.

               Args:
                   documents (List[Document]): Lista de documentos a serem divididos.

               Returns:
                   List[Document]: Lista de documentos divididos em partes menores.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        docs = text_splitter.split_documents(documents)

        return docs

    @staticmethod
    def vector(documents: List[Document], embeddings: Embeddings) -> Any:
        """
               Cria um vetor de documentos usando embeddings para facilitar a recuperação baseada em similaridade.

               Args:
                   documents (List[Document]): Lista de documentos a serem vetorizados.
                   embeddings (Embeddings): Embeddings usados para a vetorização.

               Returns:
                   Any: Um vetor FAISS contendo os documentos vetorizados.
        """
        vector = FAISS.from_documents(documents=documents, embedding=embeddings)

        return vector

    @staticmethod
    def retriever(documents: List[Document], embeddings: Embeddings):
        """
              Recupera documentos relevantes com base nos embeddings fornecidos.

              Args:
                  documents (List[Document]): Lista de documentos a serem processados e recuperados.
                  embeddings (Embeddings): Embeddings usados para a recuperação dos documentos.

              Returns:
                  Any: Um objeto retriever configurado para recuperar documentos relevantes.
        """
        vector = RAG.vector(documents=RAG.split_documents(documents), embeddings=embeddings)
        retriever = vector.as_retriever()

        return retriever
