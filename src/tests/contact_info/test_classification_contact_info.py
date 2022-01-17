import os
import unittest
from typing import List

from src.contact_info.classification_contact_info import classify_address, classify_email, classify_hours, \
    classify_telephone

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "../../..",
                           r"DATA/contact_info")
FILENAME_ADDRESS = os.path.join(DATA_FOLDER, "address_EN.txt")
FILENAME_EMAIL = os.path.join(DATA_FOLDER, "email_EN.txt")
FILENAME_HOURS = os.path.join(DATA_FOLDER, "hours_EN.txt")
FILENAME_TELEPHONE = os.path.join(DATA_FOLDER, "telephone_EN.txt")
FILENAME_ALL = os.path.join(DATA_FOLDER, "all_txt.txt")


class TestClassifyEmail(unittest.TestCase):
    def test_return(self):
        s = "This is a sentence"
        b = classify_email(s)

        self.assertIsInstance(b, bool)

    def test_correct_prediction(self):

        l_email = [
            "You can reply to no-reply@bot.com or call us on 0123/45.67.89",
            "email@host.io",
        ]

        l_not_email = [
            "you can try to mail us through the post office."
            ""
        ]

        for s in l_email:
            with self.subTest(f"True: {s}"):
                b = classify_email(s)
                self.assertTrue(b)

        for s in l_not_email:
            with self.subTest(f"False: {s}"):
                b = classify_email(s)
                self.assertFalse(b)


class TestClassifyHours(unittest.TestCase):
    def test_correct_prediction(self):

        l_hours = [
            "ouvert aujourd'hui à partir de 9h00.",
            "Openinghours: Today open 10:00 - 19:00 Tomorrow open 10:00 - 19:00",
            "We are open on Sunday.",
        ]

        l_not_hours = [
        ]

        for s in l_hours:
            with self.subTest(f"True: {s}"):
                b = classify_hours(s)
                self.assertTrue(b)

        for s in l_not_hours:
            with self.subTest(f"False: {s}"):
                b = classify_hours(s)
                self.assertFalse(b)


class TestClassifyTelephone(unittest.TestCase):
    def test_correct_prediction(self,
                                country_code="US"):

        l_telephone = [
            "123-456-7890",
            "(123) 456-7890",
            "123 456 7890",
            "123.456.7890",
            "+91 (123) 456-7890"
        ]

        l_not_telephone = [
        ]

        for s in l_telephone:
            with self.subTest(f"True: {s}"):
                b = classify_telephone(s, country_code=country_code)
                self.assertTrue(b)

        for s in l_not_telephone:
            with self.subTest(f"False: {s}"):
                b = classify_telephone(s, country_code=country_code)
                self.assertFalse(b)


class TestClassifyAddress(unittest.TestCase):
    def test_correct_prediction(self
                                ):

        l_address = [
            """Lorem ipsum
            225 E.John Carpenter Freeway,
            Suite 1500 Irving, Texas 75062
            Dorem sit amet
            """,
        ]

        l_not_address = [
        ]

        for s in l_address:
            with self.subTest(f"True: {s}"):
                b = classify_address(s)
                self.assertTrue(b)

        for s in l_not_address:
            with self.subTest(f"False: {s}"):
                b = classify_address(s)
                self.assertFalse(b)

    class TestEvaluation(unittest.TestCase):
        """
    Not really a test, but a way to conglomerate the different evaluations
    """

    def setUp(self) -> None:
        self.address = get_paragraphs(FILENAME_ADDRESS)
        self.email = get_paragraphs(FILENAME_EMAIL)
        self.hours = get_paragraphs(FILENAME_HOURS)
        self.telephone = get_paragraphs(FILENAME_TELEPHONE)
        self.all_text = get_paragraphs(FILENAME_ALL)

    def test_evaluate_email(self):

        self._evaluate_x(method=classify_email, l_gt=self.email)

    def test_evaluate_hours(self):

        self._evaluate_x(method=classify_hours, l_gt=self.hours)

    def test_evaluate_address(self):

        self._evaluate_x(method=classify_address, l_gt=self.address)

    def test_evaluate_telephone(self,
                                country_code="BE"):

        self._evaluate_x(method=lambda s: classify_telephone(s, country_code=country_code),
                         l_gt=self.telephone)

    def _evaluate_x(self,
                    method,
                    l_gt: List[str]):
        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for i, s in enumerate(self.all_text):

            # email:
            b_pred = method(s)
            b_true = s in l_gt

            if b_pred & b_true:
                tp += 1
            elif (not b_pred) & (not b_true):
                tn += 1
            else:
                print(f"#{i}: {s}")

                if b_pred & (not b_true):
                    fp += 1
                elif (not b_pred) & b_true:
                    fn += 1

        a = (tp + tn) / (tp + tn + fp + fn)
        print(f"Accuracy: {a:.1%}%")

        return print_conf(tp, fp, fn, tn)


def print_conf(tp, fp, fn, tn):
    """
    prints the confusion matrix

    Returns:

    """

    print(f"     T\tF")
    print(f"pred {tp}\t{fp}")
    print(f"     {fn}\t{tn}")

    return [[tp, fp],
            [fn, tn]]


def get_paragraphs(filename):
    with open(filename, 'r') as file:
        # removes the &nbsp (non-breakable spaces)
        # TODO contact Arne to discuss that sometimes nbsp seems to be used as newline,
        #  while other times (like in telephone numbers) it seems to be used just as a regular space.
        return file.read().replace("\xa0", " ").splitlines()
