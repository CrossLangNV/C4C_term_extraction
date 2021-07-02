import sys
sys.path.append('..')
from utils import launch_term_extraction, get_doc_content, get_batch_data
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auth_key')
    parser.add_argument('--auth_value')
    parser.add_argument('--max_docs')
    parser.add_argument('--city')
    parser.add_argument('--lang')
    parser.add_argument('--output')

    args = parser.parse_args()
    AND = "%20AND%20"
    BASE_URL = "https://solr.cefat4cities.crosslang.com/solr/documents/select?q=acceptance_state:Accepted"
    BASE_CITY = "website:"
    START_ROWS = "&rows=10&start="
    LANG = "language%3A"
    BATCH = 10

    if args.city.lower() == 'brussel':
        ACCEPTED_URL = BASE_URL  + AND + BASE_CITY + args.city + AND + LANG + args.lang + START_ROWS
        print(ACCEPTED_URL)
    else:
        ACCEPTED_URL = BASE_URL  + AND + BASE_CITY + args.city + START_ROWS

    for step in range(0, int(args.max_docs), BATCH):
        batch_url = ACCEPTED_URL + str(step)
        batch_data = get_batch_data(batch_url, args.auth_key, args.auth_value)
        for doc in batch_data['response']['docs']:
            content = get_doc_content(doc)
            with open(args.output, 'a') as wf:
                for line in content:
                    wf.write(line+'\n')
        else:
            continue