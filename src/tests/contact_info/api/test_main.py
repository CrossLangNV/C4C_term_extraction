import unittest

from fastapi.testclient import TestClient

from src.contact_info.api.main import app, Label, Sentence
from src.contact_info.classification_contact_info import TypesContactInfo

client = TestClient(app)

TEST_SENTENCE = Sentence(string='test@sentence.com')
TEST_LABEL = Label(name=TypesContactInfo.EMAIL.name)


class TestMain(unittest.TestCase):
    def test_home(self):
        response = client.get("/")

        self.assertEqual(200, response.status_code)
        self.assertEqual({'msg': "Contact information classification API."}, response.json())


class TestClassifierContactType(unittest.TestCase):
    def test_call(self):
        response = client.post("/classify_contact_type",
                               json=TEST_SENTENCE.dict())

        self.assertEqual(200, response.status_code)

        self.assertEqual(TEST_LABEL.dict(), response.json())


class TestClassifierEmail(unittest.TestCase):
    def test_call(self):
        response = client.post("/classify_contact_type/email",
                               json=TEST_SENTENCE.dict())

        self.assertEqual(200, response.status_code)

        self.assertEqual(True, response.json())
