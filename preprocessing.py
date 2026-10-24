import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# NLTK data needed by this module (downloaded automatically if missing)
NLTK_RESOURCES = {
    "punkt_tab": "tokenizers/punkt_tab",
    "stopwords": "corpora/stopwords",
    "wordnet": "corpora/wordnet",
}


def ensure_nltk_data():
    for name, path in NLTK_RESOURCES.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


ensure_nltk_data()

# Negations carry meaning ("I did NOT receive my order"), so we keep them
STOP_WORDS = set(stopwords.words("english")) - {"not", "no", "nor"}
lemmatizer = WordNetLemmatizer()


def tokenize(text):
    """Lowercase the text and split it into words and punctuation marks."""
    tokens = word_tokenize(text.lower())
    # NLTK splits "haven't" into "have" + "n't": turn "n't" back into "not"
    return ["not" if token == "n't" else token for token in tokens]


def remove_stop_words(tokens):
    """Keep only words, without punctuation, numbers or common words (the, is, a...)."""
    return [token for token in tokens if token.isalpha() and token not in STOP_WORDS]


def lemmatize(tokens):
    """Reduce each word to its base form ('boxes' -> 'box', 'arrived' -> 'arrive')."""
    return [lemmatizer.lemmatize(lemmatizer.lemmatize(t, pos="v"), pos="n") for t in tokens]


def preprocess(text):
    """Full cleaning pipeline: returns a list of clean words."""
    return lemmatize(remove_stop_words(tokenize(text)))


def preprocess_to_string(text):
    """Same as preprocess, but returns a single string (used for TF-IDF)."""
    return " ".join(preprocess(text))


if __name__ == "__main__":
    samples = [
        "Where is my package?",
        "My orders haven't arrived yet!",
        "How can I return the boxes?",
        "I did not receive a confirmation email",
        "Do you ship internationally?",
    ]
    for sentence in samples:
        tokens = tokenize(sentence)
        filtered = remove_stop_words(tokens)
        lemmas = lemmatize(filtered)
        print("Original        :", sentence)
        print("1. Tokens       :", tokens)
        print("2. No stop words:", filtered)
        print("3. Lemmas       :", lemmas)
        print()