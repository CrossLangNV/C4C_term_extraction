import requests

UIMA_URL = {"BASE": "http://staging.dgfisma.crosslang.com:8008",  # http://uima:8008
            "HTML2TEXT": "/html2text",
            "TYPESYSTEM": "/html2text/typesystem",
            }

def get_html2text_cas(content_html):
    content_html_text = {
        "text": content_html
    }

    r = requests.post(
        UIMA_URL["BASE"] + UIMA_URL["HTML2TEXT"], json=content_html_text)
    return r.content.decode('utf-8')