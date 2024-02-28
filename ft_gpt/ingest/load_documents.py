from ft_gpt import constants, utils
import os
from llama_index.core import Document


def load_docs():
    print("Loading documents...")
    """
    Read text files used for the llm
    """

    data_dir = f"{os.path.dirname(constants.FILE_DIR)}/data/text/"

    documents = []
    files = os.listdir(data_dir)

    print("Reading files")
    for file in files:
        try:
            date = utils.get_date(file)
        except Exception as e:
            print(f"No date were found for file: {file}: {e}")
            date = ""
        date_of_sitting = f"[Afholdelsestidspunkt for møde: {date}]"
        with open(f"{data_dir}{file}") as f:
            text = f.read()

        title = file.split(".pdf.txt")[0]
        if title.startswith("dk_forhandlinger"):
            url = f"https://www.ft.dk/forhandlinger/{title.split('_', 3)[2]}/{title.split('_', 3)[3]}.htm"
        else:
            url = ""
        document = Document(text=text, metadata={"title": title, "date": f"[{date_of_sitting}]", "url": url})  # type: ignore
        documents.append(document)

    return documents
