import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing import lemmatize, preprocess, tokenize

FAQ_FILE = Path(__file__).with_name("faq.json")
CONFIDENCE_THRESHOLD = 0.30  # below this score, the bot admits it did not understand
SMALL_TALK_THRESHOLD = 0.70  # greetings must match almost exactly (avoids false matches)

FALLBACK_ANSWER = (
    "I'm sorry, I didn't quite understand your question. Could you rephrase it? "
    "You can ask me about orders, delivery, payments, returns or your account."
)


def prepare(text):
    """Clean a text and return it as a single string of base-form words."""
    words = preprocess(text)
    if words:
        return " ".join(words)
    # Very short questions made only of common words ("Who are you?"):
    # in that case we keep every word instead of returning nothing.
    return " ".join(lemmatize([t for t in tokenize(text) if t.isalpha()]))


class FAQChatbot:
    def __init__(self, faq_file=FAQ_FILE):
        with open(faq_file, encoding="utf-8") as f:
            data = json.load(f)
        self.company = data["company"]
        self.faqs = data["faqs"]

        # One row per question phrasing, remembering which FAQ it belongs to
        self.phrasings = []   # cleaned text of each phrasing
        self.owner = []       # index of the FAQ each phrasing belongs to
        for faq_index, faq in enumerate(self.faqs):
            for question in faq["questions"]:
                self.phrasings.append(prepare(question))
                self.owner.append(faq_index)

        # TF-IDF turns each phrasing into a vector of numbers
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(self.phrasings)

    def get_answer(self, user_text, n_suggestions=3):
        """Return a dictionary describing the best answer for the user's question."""
        cleaned = prepare(user_text)
        scores = [0.0] * len(self.faqs)
        if cleaned:
            query_vector = self.vectorizer.transform([cleaned])
            similarities = cosine_similarity(query_vector, self.matrix)[0]
            # A FAQ gets the score of its best-matching phrasing
            for faq_index, similarity in zip(self.owner, similarities):
                scores[faq_index] = max(scores[faq_index], float(similarity))

        ranking = sorted(range(len(self.faqs)), key=lambda i: scores[i], reverse=True)

        # Pick the best-scoring FAQ that is good enough to be trusted
        best = next((i for i in ranking if scores[i] >= self._threshold(i)), None)
        confident = best is not None
        shown = best if confident else ranking[0]

        return {
            "answer": self.faqs[best]["answer"] if confident else FALLBACK_ANSWER,
            "confident": confident,
            "score": scores[shown],
            "category": self.faqs[best]["category"] if confident else None,
            "matched_question": self.faqs[best]["questions"][0] if confident else None,
            "suggestions": [
                self.faqs[i]["questions"][0]
                for i in ranking[:n_suggestions]
                if scores[i] > 0 and self.faqs[i]["category"] != "Small talk"
            ],
        }

    def _threshold(self, faq_index):
        if self.faqs[faq_index]["category"] == "Small talk":
            return SMALL_TALK_THRESHOLD
        return CONFIDENCE_THRESHOLD


if __name__ == "__main__":
    bot = FAQChatbot()
    print(f"{bot.company} assistant ready ({len(bot.faqs)} FAQs). Type 'quit' to exit.\n")
    while True:
        text = input("You: ").strip()
        if text.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        if not text:
            continue
        result = bot.get_answer(text)
        print(f"Bot: {result['answer']}")
        print(f"     [score {result['score']:.2f} | matched: {result['matched_question']}]")
        if not result["confident"] and result["suggestions"]:
            print("     Did you mean: " + " / ".join(result["suggestions"]))
        print()