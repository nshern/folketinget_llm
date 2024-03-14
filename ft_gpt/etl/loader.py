import os

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
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

    def _create_node(self, content, speaker, file, date, id):
        token_amount = utils.get_token_amount(content)

        node = TextNode(
            text=content,
            metadata={"speaker": speaker, "date": date, "file": file},  # type: ignore
        )

        node.id_ = str(id)

        node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=str(id + 1))
        node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
            node_id=str(id - 1)
        )
        return node

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

                    token_amount = utils.get_token_amount(content)

                    if token_amount >= 8191:
                        print("Splitting chunk...")
                        print(token_amount)
                        content_chunks = utils.split_text(content)
                        for chunk in content_chunks:
                            node = self._create_node(
                                content=chunk,
                                speaker=speaker,
                                file=file,
                                date=date,
                                id=current_id,
                            )

                            nodes.append(node)

                    else:
                        node = self._create_node(
                            content=content,
                            speaker=speaker,
                            file=file,
                            date=date,
                            id=current_id,
                        )

                        nodes.append(node)

            self.nodes = nodes

    def _create_index(self):
        openai_llm = OpenAI(
            model="gpt-4-0125-preview",
            temperature=0.7,
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
            index = VectorStoreIndex(nodes=nodes, show_progress=True)
            index.storage_context.persist(persist_dir=constants.PERSIST_DIR)
            self.index = index

    def run(self):
        # print(Settings.llm)
        self._create_nodes()
        self._create_index()
        # TODO : Create method that pushes vectorstore to remote storage


if __name__ == "__main__":
    loader = Loader()
    loader.run()
