from ft_gpt import constants, utils
from pathlib import Path


def generate_overview_doc():
    dates = utils.get_dates_of_sittings()
    overview_path = Path(f"{constants.DATA_DIR}overblik.txt").expanduser()
    with open(overview_path, "w") as f:
        f.write("Møder er blevet afholdt på følgende datoer:\n\n")

    for i in dates:
        with open(overview_path, "a") as f:
            f.write(f"{i}, {utils.convert_date(i)}\n")
