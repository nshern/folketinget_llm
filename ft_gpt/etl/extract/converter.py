
import os
from pathlib import Path

from tqdm import tqdm
from weasyprint import HTML

# Supress logging from weasyprint as to get a clean tqdm progress bar
logging.getLogger('fontTools').setLevel(logging.CRITICAL)


def _get_htm_files(dir):
    htm_files = []
    for i in os.listdir(dir):
        if str(i).endswith(".htm"):
            htm_files.append(Path(i))

    return htm_files

def _remove_file(file):
    os.remove(file)


def convert_file_to_pdf(file):
    output_filename = f"data/{str(file).split(".")[0]}.pdf"
    input_filename = f"data/{file}"
    HTML(input_filename).write_pdf(output_filename)
    _remove_file(input_filename)

def convert_files_to_pdf(dir):
    print("Converting html files to pdf...")
    files = _get_htm_files(dir)
    for i in tqdm(files):
        convert_file_to_pdf(i)

if __name__ == "__main__":
    convert_files_to_pdf("data")


