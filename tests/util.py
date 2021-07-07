from spacy.tokens import Doc, Span
from spacy.attrs import POS, HEAD, DEP

#from https://github.com/explosion/spaCy/blob/f22704621ef5d136e00a47068288bf55f666716d/spacy/tests/util.py#L29
def get_doc(vocab, words=[], pos=None, heads=None, deps=None, tags=None, ents=None):
    """Create Doc object from given vocab, words and annotations."""
    pos = pos or [""] * len(words)
    tags = tags or [""] * len(words)
    heads = heads or [0] * len(words)
    deps = deps or [""] * len(words)
    for value in deps + tags + pos:
        vocab.strings.add(value)

    doc = Doc(vocab, words=words)
    attrs = doc.to_array([POS, HEAD, DEP])
    for i, (p, head, dep) in enumerate(zip(pos, heads, deps)):
        attrs[i, 0] = doc.vocab.strings[p]
        attrs[i, 1] = head
        attrs[i, 2] = doc.vocab.strings[dep]
    doc.from_array([POS, HEAD, DEP], attrs)
    if ents:
        doc.ents = [
            Span(doc, start, end, label=doc.vocab.strings[label])
            for start, end, label in ents
        ]
    if tags:
        for token in doc:
            token.tag_ = tags[token.i]
    return doc