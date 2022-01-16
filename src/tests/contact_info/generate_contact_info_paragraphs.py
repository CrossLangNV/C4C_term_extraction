import os
import random

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "../../..",
                           r"DATA/processed_training_data_adress_detection",
                           r"processed_training_data_adress_detection")

FILENAME1 = "adress_tel_FR.FR_EN.txt"
FILENAME2 = "adress_tel_NL.NL_EN.txt"


def main():
    """
    This is not really a test, but a convenient way to build a small list of the different contact info data.

    Returns:

    """

    # Open all address_tel... data (both from Dutch and French sources)
    # and scramble randomly to go over them one by one.

    def get_paragraphs(filename):
        with open(filename, 'r') as file:
            # removes the &nbsp (non-breakable spaces)
            # TODO contact Arne to discuss that sometimes nbsp seems to be used as newline,
            #  while other times (like in telephone numbers) it seems to be used just as a regular space.
            return file.read().replace("\xa0", " ").splitlines()

    l1 = get_paragraphs(os.path.join(DATA_FOLDER, FILENAME1))
    l2 = get_paragraphs(os.path.join(DATA_FOLDER, FILENAME2))

    l = l1 + l2

    def scrambled(orig, seed=314):
        dest = orig[:]
        if seed:
            random.seed(seed)
        random.shuffle(dest)
        return dest

    l_shuffle = scrambled(l)

    for i, s in enumerate(l_shuffle):
        print(s)
        # _ = input(f"#{i}. Press enter to continue:")
        # last_input = _


if __name__ == '__main__':
    main()
