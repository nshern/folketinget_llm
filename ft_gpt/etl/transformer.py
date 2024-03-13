import os
import shutil
import xml.etree.ElementTree as ET

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

    def run(self):
        self._parse_raw_xml_files()


if __name__ == "__main__":
    t = Transformer()
    t.run()
