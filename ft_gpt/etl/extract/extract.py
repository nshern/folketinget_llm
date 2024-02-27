import os
import ftplib

# FTP server details
FTP_HOST = "oda.ft.dk"
FTP_DIR = "ODAXML/Referat/samling"

FILE_DIR = os.path.dirname(__file__)
DL_DIR = f"{FILE_DIR}/../data/xml"


def extract():
    # Connect to the FTP server
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login()  # login anonymously

    ftp.cwd(FTP_DIR)
    folders = ftp.nlst()

    for folder in folders:

        # We check if folder exists in download folder.
        # If it does not exist we create it.
        # This give structure to data in downlolad folder.

        dl_folder_path = f"{DL_DIR}/{folder}"
        if not os.path.exists(dl_folder_path):
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
