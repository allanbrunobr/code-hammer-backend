from langchain_google_vertexai import VertexAIEmbeddings


class ModelEmbeddings(VertexAIEmbeddings):

    def __init__(self):
        model_name = "textembedding-gecko@003"

        super().__init__(model_name=model_name)
