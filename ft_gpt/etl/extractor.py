import ftplib
import logging
import os
from pathlib import Path

from ft_gpt import constants, utils


class Extractor:
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

            dl_folder_path = f"{constants.DATA_DIR_XML_RAW}"
            if not os.path.exists(f"{dl_folder_path}"):
                os.makedirs(dl_folder_path)
                logging.info(f"Folder '{dl_folder_path}' was created.")

                # Initialize empty list so that later check is correct
                existing_files = []
            else:
                logging.info(f"Folder '{dl_folder_path}' already exists.")

                # Extract file names to check if they already exist later
                existing_files = os.listdir(dl_folder_path)

            ftp.cwd(folder)
            files = ftp.nlst()
            for file in files:
                if file in existing_files:
                    logging.info(f"{file} already exists in {dl_folder_path}.")
                else:
                    file_name = f"{dl_folder_path}/{file}"
                    with open(file_name, "wb") as f:
                        # Use FTP's RETR command to download the file
                        ftp.retrbinary(f"RETR {file}", f.write)
                        logging.warning(f"Downloaded {file} to {dl_folder_path}.")

            # Return up
            ftp.cwd("..")

        logging.info("Extraction complete.")
        logging.info("Closing ftp connection.")
        ftp.quit()
        logging.info("ftp connection closed.")

    def generate_overview_doc(self):
        dates = utils.get_dates_of_sittings()
        overview_path = Path(f"{constants.DATA_DIR}overblik.txt").expanduser()
        with open(overview_path, "w") as f:
            f.write("Møder er blevet afholdt på følgende datoer:\n\n")

        for i in dates:
            with open(overview_path, "a") as f:
                f.write(f"{i}, {utils.convert_date(i)}\n")

    def run(self):
        logging.basicConfig(level=logging.WARN)
        self.extract()
        self.generate_overview_doc()


if __name__ == "__main__":
    e = Extractor()
    e.run()
