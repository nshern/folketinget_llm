from ft_gpt.settings import init_settings
from ft_gpt.ingest.create_engine import create_engine


#     query = input("Q: ")
#     response = query_engine.chat(query)
#     print(response)


if __name__ == "__main__":
    init_settings()
    query_engine = create_engine()
    questions = [
        "Hvornår blev seneste møde afholdt?",
        "Hvad er datospændet på de mødereferater, som du har adgang til?",
        "Hvilken dato blev det første møde afholdt, som du har et referat fra?",
    ]
