from pathlib import Path
import tika

tika.initVM()

from tika import parser

def convertToString(filename: Path )-> str:
    
    '''
    Read data from files (.doc, .docx, .pdf, .html) using tika.
    
    :param split_dir: Path. Filename to read.
    :return: str. Parsed content. 
    '''
    
    if filename.endswith(".txt"):
        with open(filename, 'r') as text:
            return text.read()
    if filename.endswith(".docx") or filename.endswith(".doc"):
        return tikaToText(filename)
    if filename.endswith(".pdf"):
        return tikaToText(filename)
    if filename.endswith(".html"):
        return tikaToText(filename)
    
def tikaToText(path_file ):
    parsed = parser.from_file(path_file)
    content = parsed["content"]
    if content:
        return content.strip()