import spacy

nlp = spacy.load("fr_core_news_sm")


def classify_query(query):
    doc = nlp(query)
    verb_count = sum(1 for token in doc if token.pos_ in ["VERB", "AUX"])
    det_count = sum(1 for token in doc if token.pos_ == "DET")
    punc_count = sum(1 for token in doc if token.pos_ == "PUNCT")
    adj_count = sum(1 for token in doc if token.pos_ == "ADJ")
    noun_count = sum(1 for token in doc if token.pos_ in "NOUN")

    if (verb_count + det_count + punc_count + adj_count) >= noun_count:
        return "semantic"
    else:
        return "keyword"

if __name__ == "__main__":
    user_query = "Quel est le prix de la meuleuse ?"
    classification = classify_query(user_query)
    print(f"Classification: {classification}")