import os
import locale
from pathlib import Path
from datetime import datetime
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
)


FILE_DIR = os.path.dirname(__file__)
PERSIST_DIR = f"{FILE_DIR}/storage"
DATA_DIR = f"{os.path.dirname(FILE_DIR)}/data/text/"

# Configure LLM
Settings.llm = OpenAI(model="gpt-4", temperature=0.1)
Settings.embed_model = OpenAIEmbedding()


def _get_date(s: str):
    return s.split("_")[-2]


def convert_date_format(date_str):
    # Ensure the locale is set to Danish
    # Note: The locale setting might differ based on your operating system.
    # For Linux, it might be 'da_DK.UTF-8'. For Windows, it might be 'danish'.
    try:
        locale.setlocale(
            locale.LC_TIME, "da_DK.UTF-8"
        )  # Try this first if you're on Linux
    except locale.Error:
        try:
            locale.setlocale(
                locale.LC_TIME, "danish"
            )  # Try this if you're on Windows or the above
        except locale.Error as e:
            print(f"Error setting locale: {e}")
            return None

    # Parse the input date string
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Format the date in the desired format
    formatted_date = date_obj.strftime("%-d. %B %Y")

    return formatted_date


def convert_date(date_str):
    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Format the date as desired
    # %d for day, %B for full month name, %Y for year
    formatted_date = date_obj.strftime("%d. %B %Y")

    return formatted_date


def get_dates_of_sittings():

    dates = []

    files = os.listdir(DATA_DIR)

    for file in files:
        if str(file.title()) == "Overblik.Txt":
            continue
        else:
            date_of_sitting = f"{_get_date(file)}"
            dates.append(date_of_sitting)
    # Convert string dates to datetime objects
    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    # Sort the date objects
    date_objects.sort()

    # If you need them back in string format
    sorted_dates = [datetime.strftime(date, "%Y-%m-%d") for date in date_objects]

    res = []

    for i in sorted_dates:
        res.append(i)

    return sorted_dates


def generate_overview_doc():
    dates = get_dates_of_sittings()
    overview_path = Path(f"{DATA_DIR}overblik.txt").expanduser()
    with open(overview_path, "w") as f:
        f.write("Møder er blevet afholdt på følgende datoer:\n\n")

    for i in dates:
        with open(overview_path, "a") as f:
            f.write(f"{i}, {convert_date(i)}\n")


def generate_pre_promt():
    dates_of_sittings = get_dates_of_sittings()

    prompt = (
        "You are a helpful chatbot that answers questions about meeting notes (mødereferater) from the Danish Folketing.\n"
        "You should only answer questions related to this topic.\n"
        "The date today is 24. of February 2024. Every mention of a time and date should be in relation to this piece of information.\n"
        f"You have access to meeting notes from the following dates:\n {dates_of_sittings}\n"
        "You may only communicate in Danish and should refrain entirely from communicating in any other language.\n"
    )

    return prompt


def load_docs():
    """
    Read text files used for the llm
    """

    data_dir = f"{os.path.dirname(FILE_DIR)}/data/text/"

    documents = []
    files = os.listdir(data_dir)

    print("Reading files")
    for file in files:
        try:
            date = _get_date(file)
        except Exception as e:
            print(f"No date were found for file: {file}: {e}")
            date = ""
        date_of_sitting = f"Afholdelsestidspunkt for møde: {date}"
        with open(f"{data_dir}{file}") as f:
            text = f.read()
        title = file.split(".pdf.txt")[0]
        document = Document(text=text, metadata={"title": title, "date": f"[{date_of_sitting}]"})  # type: ignore
        documents.append(document)

    return documents


def parse_nodes(documents):
    node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)
    nodes = node_parser.get_nodes_from_documents(documents)

    return nodes


def create_index():
    if os.path.isdir(PERSIST_DIR):
        print("Storage exists")
        print("Loading storage")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    else:
        docs = load_docs()
        nodes = parse_nodes(docs)
        print("No storage")
        print("Creating index")
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(persist_dir=PERSIST_DIR)

    return index


def create_engine(index):
    memory = ChatMemoryBuffer.from_defaults()
    system_prompt = generate_pre_promt()
    query_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=system_prompt,
    )
    return query_engine


def chat():
    generate_overview_doc()
    index = create_index()
    query_engine = create_engine(index)

    while True:
        query = input("Q: ")
        response = query_engine.chat(query)
        print(response)


if __name__ == "__main__":
    questions = [
        "Hvornår blev seneste møde afholdt?",
        "Hvad er datospændet på de mødereferater, som du har adgang til?",
        "Hvilken dato blev det første møde afholdt, som du har et referat fra?",
    ]
    chat()
