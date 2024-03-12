import os
import shutil
import xml.etree.ElementTree as ET

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import NodeRelationship, RelatedNodeInfo, TextNode

from ft_gpt import constants


class Transformer:

    def _extract_date_from_xml(self, file):
        res = []
        with open(file, "r") as f:
            xml_data = f.read()
        root = ET.fromstring(xml_data)

        dates = root.findall(".//DateOfSitting")
        res = dates[0].text

        return res

    def _parse_raw_xml_file(self, file):
        res = []
        with open(file, "r") as f:
            xml_data = f.read()
        root = ET.fromstring(xml_data)

        dagsordenspunkter = root.findall(".//DagsordenPunkt")
        id = 0
        for i in dagsordenspunkter:
            id += 1
            tale = i.findall(".//Tale")
            for k in tale:
                firstname = k.find(".//Taler/MetaSpeakerMP/OratorFirstName")
                if firstname is not None:
                    firstname = firstname.text
                lastname = k.find(".//Taler/MetaSpeakerMP/OratorLastName")
                if lastname is not None:
                    lastname = lastname.text
                text_snippet = k.findall(".//TaleSegment/TekstGruppe/Exitus/Linea/Char")
                text = " ".join([i.text for i in text_snippet if i.text is not None])
                line = f"**{firstname} {lastname}**: {text}\n"
                res.append(line)

        return " ".join(res)

    def _parse_raw_xml_files(self):
        try:
            shutil.rmtree(constants.DATA_DIR_XML_PARSED)
            print(f"Directory '{constants.DATA_DIR_XML_PARSED}' has been removed")
        except OSError as error:
            print(f"Error: {error.strerror}")

        if not os.path.exists(constants.DATA_DIR_XML_PARSED):
            os.makedirs(constants.DATA_DIR_XML_PARSED)

        files = os.listdir(constants.DATA_DIR_XML_RAW)
        for file in files:
            parsed_file_title = f"{constants.DATA_DIR_XML_PARSED}{file}.md"
            parsed = self._parse_raw_xml_file(f"{constants.DATA_DIR_XML_RAW}{file}")
            with open(parsed_file_title, "w") as f:
                f.write(parsed)
                print(f"Parsed {parsed_file_title}")

    def _extract_data_from_parsed_files(self):
        print("Parsing data...")
        files = os.listdir(constants.DATA_DIR_XML_RAW)
        docs = {}
        for file in files:
            docs[file] = {}
            abs_file_raw = f"{constants.DATA_DIR_XML_RAW}{file}"
            date = self._extract_date_from_xml(abs_file_raw)
            docs[file]["date"] = date

            abs_file_parsed = f"{constants.DATA_DIR_XML_PARSED}{file}.md"
            with open(abs_file_parsed) as f:
                text = f.read()
                docs[file]["text"] = text

        print("Finished parsing data..")
        return docs

    # NOTE: This part and down should probably go into load
    def _create_nodes(self):
        self._parse_raw_xml_files()
        nodes = []
        current_id = 0
        docs = self._extract_data_from_parsed_files()

        print("Creating nodes..")
        for key, val in docs.items():
            lines = val["text"].split("\n")
            for line in lines:
                speaker = str(line.split(":", 1)[0]).replace("**", "")
                content = line.split(":", 1)[-1]
                file = str(key).split(".")[0]
                date = val["date"]
                node = TextNode(
                    text=content,
                    metadata={"speaker": speaker, "date": date, "file": file},  # type: ignore
                )

                current_id = current_id + 1
                node.id_ = str(current_id)

                # TODO: Add node relationships

                nodes.append(node)

            self.nodes = nodes

    def _create_index(self):
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
            index = VectorStoreIndex(nodes)
            self.index = index.storage_context.persist(
                persist_dir=constants.PERSIST_DIR
            )

    def run(self):
        self._create_nodes()
        self._create_index


if __name__ == "__main__":
    t = Transformer()
    t.run()
