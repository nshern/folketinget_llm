import os

from llama_index.core import (
    ServiceContext,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    service_context,
)
from llama_index.core.schema import NodeRelationship, RelatedNodeInfo, TextNode
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from ft_gpt import constants, settings, utils


class Loader:
    def _extract_data(self):
        print("Parsing data...")
        files = os.listdir(constants.DATA_DIR_XML_RAW)
        docs = {}
        for file in files:
            docs[file] = {}
            abs_file_raw = f"{constants.DATA_DIR_XML_RAW}{file}"
            date = utils.extract_date_from_xml(abs_file_raw)
            docs[file]["date"] = date

            abs_file_parsed = f"{constants.DATA_DIR_XML_PARSED}{file}.md"
            with open(abs_file_parsed) as f:
                text = f.read()
                docs[file]["text"] = text

        print("Finished parsing data..")
        return docs

    # TODO: Set date range parameter
    def _create_nodes(self):
        nodes = []
        current_id = 0
        docs = self._extract_data()

        print("Creating nodes..")
        for key, val in docs.items():
            lines = val["text"].split("\n")
            for line in lines:
                speaker = str(line.split(":", 1)[0]).replace("**", "").strip()
                content = line.split(":", 1)[-1].strip()
                file = str(key).split(".")[0].strip()
                date = val["date"].strip()

                # NOTE: Hacked filtering on date range
                # NOTE: Filtered should occur before this point
                if str(date).startswith("2023"):
                    node = TextNode(
                        text=content,
                        metadata={"speaker": speaker, "date": date, "file": file},  # type: ignore
                    )

                    current_id = current_id + 1
                    node.id_ = str(current_id)

                    node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                        node_id=str(current_id + 1)
                    )
                    node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                        node_id=str(current_id - 1)
                    )

                    nodes.append(node)

            self.nodes = nodes

    def _create_index(self):
        openai_llm = OpenAI(
            model="gpt-4-0125-preview",
            temperature=0.7,
            max_tokens=128000,  # Adjust based on your needs, up to the model's limit
            api_key="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",
            api_base="https://api.openai.com",
            api_version="v1",
        )
        Settings.llm = openai_llm
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")
        if os.path.isdir(constants.PERSIST_DIR):
            print("Storage exists")
            print("Loading storage")
            storage_context = StorageContext.from_defaults(
                persist_dir=constants.PERSIST_DIR
            )
            self.index = load_index_from_storage(storage_context)
        else:
            nodes = self.nodes
            print("No storage")
            print("Creating index")
            index = VectorStoreIndex(nodes=nodes)
            index.storage_context.persist(persist_dir=constants.PERSIST_DIR)

    def run(self):
        # print(Settings.llm)
        self._create_nodes()
        self._create_index()


if __name__ == "__main__":
    loader = Loader()
    loader.run()
