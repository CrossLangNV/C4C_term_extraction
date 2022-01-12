import unittest

from src.contact_info.classification_contact_info import classify_email


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
