import spacy

class Classifier:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_sm")

    def classify_query(self, query):
        semantic_triggers = ["comment", "pourquoi", "quel", "quelle", "quels", "quelles", "où", "qui", "peut", "est-ce",
                             "combien"]

        if "?" in query or any(query.lower().startswith(w) for w in semantic_triggers):
            return "SEMANTIC"

        doc = self.nlp(query)
        verb_count = sum(1 for token in doc if token.pos_ in ["VERB", "AUX"])
        noun_count = sum(1 for token in doc if token.pos_ == "NOUN")
        token_len = len(doc)

        if verb_count > 0 and (verb_count / (noun_count + 1)) > 0.5 and token_len > 3:
            return "SEMANTIC"

        return "FULL_TEXT"
