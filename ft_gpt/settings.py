from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


def init_settings():
    print("Initializing settings...")
    Settings.llm = OpenAI(model="gpt-4", temperature=0.1)
    Settings.embed_model = OpenAIEmbedding()
