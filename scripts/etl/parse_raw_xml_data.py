from ft_gpt import constants
from ft_gpt.etl.pipeline import ETLPipeline

p = ETLPipeline()

# files = [
#     "20231_M58_helemoedet.xml",
#     "20231_M59_helemoedet.xml",
#     "20231_M51_helemoedet.xml",
#     "20231_M52_helemoedet.xml",
# ]
#
# for file in files:
#     data = p.parse_xml(f"{constants.DATA_DIR_XML_RAW}{file}")
#     with open(f"{str(file)}.md", "w") as f:
#         f.write(data)

p.parse_all_xml()
