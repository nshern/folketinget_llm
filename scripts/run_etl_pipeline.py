from ft_gpt.etl.extract import extract
from ft_gpt.etl.load import load_docs


def run_pipeline_from_db():
    # Extract documents from database
    # Documents are placed in data dir
    extract()
    docs = load_docs("xml")
