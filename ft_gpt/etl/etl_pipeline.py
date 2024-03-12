import os

from ft_gpt import constants


class ETLPipeline:

    def load(self):
        self._create_index()
        """
        Push into remote storage
        """

        pass

    def run(self):
        # self.extract()
        self.transform()
        self.load()


if __name__ == "__main__":
    p = ETLPipeline()
    nodes = p.run()
