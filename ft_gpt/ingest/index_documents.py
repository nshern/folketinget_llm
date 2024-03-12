import os

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import SimpleNodeParser

from ft_gpt import constants
from ft_gpt.etl.pipeline import ETLPipeline


def parse_nodes(documents):
    node_parser = SimpleNodeParser.from_defaults(chunk_size=1024)
    nodes = node_parser.get_nodes_from_documents(documents)
    print(type(nodes))
    breakpoint()

    return nodes


def create_index(filetype):
    if os.path.isdir(constants.PERSIST_DIR):
        print("Storage exists")
        print("Loading storage")
        storage_context = StorageContext.from_defaults(
            persist_dir=constants.PERSIST_DIR
        )
        index = load_index_from_storage(storage_context)
    else:
        p = ETLPipeline()
        docs = p.transform()
        # docs = load_docs(filetype)
        nodes = parse_nodes(docs)
        print("No storage")
        print("Creating index")
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(persist_dir=constants.PERSIST_DIR)

    return index
