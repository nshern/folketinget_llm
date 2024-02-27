from ft_gpt.settings import init_settings
from ft_gpt.ingest.create_engine import create_engine


def chat():
    init_settings()
    query_engine = create_engine()

    while True:
        query = input("Q: ")
        response = query_engine.chat(query)
        print(response)


if __name__ == "__main__":
    chat()
