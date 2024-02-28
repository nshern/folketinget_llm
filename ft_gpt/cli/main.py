from ft_gpt.settings import init_settings
from ft_gpt.ingest.create_engine import create_engine


if __name__ == "__main__":
    init_settings()
    query_engine = create_engine()
    print("\n")

    while True:
        query = input("Q: ")

        if query == "reset":
            print("Resetting")
            query_engine.reset()
        else:
            r = query_engine.chat(query)
            print(r.response)
