import ftplib
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from llama_index.core import Document

from ft_gpt import constants, utils


class ETLPipeline:
    def extract(self):
        """
        This method connects to the oda.ft.dk database via ftp and retrieves all meeting notes
        which have not yet been retrieved.
        """
        # FTP server details
        FTP_HOST = "oda.ft.dk"
        FTP_DIR = "ODAXML/Referat/samling"

        # Connect to the FTP server
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login()  # login anonymously

        ftp.cwd(FTP_DIR)
        folders = ftp.nlst()

        for folder in folders:
            # We check if folder exists in download folder.
            # If it does not exist we create it.
            # This give structure to data in downlolad folder.

            # dl_folder_path = f"{DL_DIR}/{folder}"
            dl_folder_path = f"{constants.DATA_DIR_XML_RAW}"
            if not os.path.exists(f"{dl_folder_path}"):
                os.makedirs(dl_folder_path)
                print(f"Folder '{dl_folder_path}' was created.")

                # Initialize empty list so that later check is correct
                existing_files = []
            else:
                print(f"Folder '{dl_folder_path}' already exists.")

                # Extract file names to check if they already exist later
                existing_files = os.listdir(dl_folder_path)

            ftp.cwd(folder)
            files = ftp.nlst()
            for file in files:
                if file in existing_files:
                    print(f"{file} already exists in {dl_folder_path}.")
                else:
                    file_name = f"{dl_folder_path}/{file}"
                    #             print(file_name)
                    with open(file_name, "wb") as f:
                        # Use FTP's RETR command to download the file
                        ftp.retrbinary(f"RETR {file}", f.write)
                        print(f"Downloaded {file} to {dl_folder_path}.")

            # Return up
            ftp.cwd("..")

        print("Extraction complete.")
        print("Closing ftp connection.")
        ftp.quit()
        print("ftp connection closed.")

    def generate_overview_doc(self):
        dates = utils.get_dates_of_sittings()
        overview_path = Path(f"{constants.DATA_DIR}overblik.txt").expanduser()
        with open(overview_path, "w") as f:
            f.write("Møder er blevet afholdt på følgende datoer:\n\n")

        for i in dates:
            with open(overview_path, "a") as f:
                f.write(f"{i}, {utils.convert_date(i)}\n")

    def _parse_xml(self, file):
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
                # print(f"{k.find(".//MetaSpeakerMP/OratorFirstName").text} {k.find(".//MetaSpeakerMP/OratorLastName").text}")
                firstname = k.find(".//Taler/MetaSpeakerMP/OratorFirstName")
                if firstname is not None:
                    firstname = firstname.text
                lastname = k.find(".//Taler/MetaSpeakerMP/OratorLastName")
                if lastname is not None:
                    lastname = lastname.text
                # tekstgrupper = k.find_all(k.findall("./"))
                text_snippet = k.findall(".//TaleSegment/TekstGruppe/Exitus/Linea/Char")
                text = " ".join([i.text for i in text_snippet if i.text is not None])
                line = f"**{firstname} {lastname}**: {text}\n"
                res.append(line)

        return " ".join(res)

    # TODO: Should check if data is already parsed
    def _parse_all_xml(self):
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
            parsed = self._parse_xml(f"{constants.DATA_DIR_XML_RAW}{file}")
            with open(parsed_file_title, "w") as f:
                f.write(parsed)
                print(f"Parsed {parsed_file_title}")

    def _read_documents(self):
        print("Loading documents...")
        """
        Read text files used for the llm
        """

        data_dir = f"{os.path.dirname(constants.FILE_DIR)}/data/xml/parsed/"

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

    def _read_nodes(self):
        # TODO: Check if self.docs exists
        docs = self.docs

    def transform(self):
        self._parse_all_xml()
        self.docs = self._read_documents()

    def load(self):
        """
        Push into remote storage
        """

        pass

    def run(self):
        self.extract()
        self.generate_overview_doc()
        self.transform()


if __name__ == "__main__":
    p = ETLPipeline()
    p.transform()
    print(p.docs)
