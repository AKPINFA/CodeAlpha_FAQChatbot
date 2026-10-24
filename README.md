&#x20;FAQ Chatbot



!\[FAQ Chatbot](screenshots/banner.png)



A chatbot that answers frequently asked questions using Natural Language Processing. It finds the FAQ entry that is closest to the user's question and returns its answer. The demo is built around \*\*Nova Market\*\*, a fictional online store.



&#x20;Features



\- Understands questions written in different ways ("Where is my package?", "Track my parcel")

\- Text preprocessing with \*\*NLTK\*\*: tokenization, stop-word removal and lemmatization

\- Matching with \*\*TF-IDF\*\* and \*\*cosine similarity\*\* (scikit-learn)

\- \*\*Confidence score\*\* for every answer, and a polite fallback when the bot is not sure

\- Suggested questions when the question is not understood

\- Modern chat interface built with Streamlit: typing effect, quick replies, category and confidence badges

\- Easy to adapt: all the content lives in one JSON file (`faq.json`)



&#x20;Screenshot



!\[App screenshot](screenshots/demo.png)



&#x20;How it works



1\. \*\*Preprocessing\*\* (`preprocessing.py`): the question is lowercased and split into words, common words ("the", "is"...) and punctuation are removed, and each word is reduced to its base form ("boxes" becomes "box"). Negations such as "not" are kept because they change the meaning.

2\. \*\*Vectorization\*\* (`chatbot.py`): every question of the FAQ is turned into a vector of numbers with TF-IDF. Rare words weigh more than frequent ones.

3\. \*\*Matching\*\*: cosine similarity compares the user's question with all the FAQ questions. The FAQ with the highest score is selected.

4\. \*\*Confidence check\*\*: if the best score is below a threshold, the bot says it did not understand instead of guessing. Greetings use a stricter threshold to avoid false matches.



Each FAQ entry has several phrasings of the same question, which helps the bot recognize synonyms and different formulations.



&#x20;Tech stack



| Purpose | Library |

|---|---|

| Text preprocessing | \[NLTK](https://www.nltk.org) |

| Vectorization and similarity | \[scikit-learn](https://scikit-learn.org) |

| User interface | \[Streamlit](https://streamlit.io) |



&#x20;Getting started



&#x20;Prerequisites



\- Python 3.10 or newer

\- An internet connection the first time (NLTK language data is downloaded automatically)



&#x20;Installation



```bash

git clone https://github.com/AKPINFA/CodeAlpha\_FAQChatbot.git

cd CodeAlpha\_FAQChatbot



python -m venv venv

\# Windows

venv\\Scripts\\activate

\# macOS / Linux

source venv/bin/activate



pip install -r requirements.txt

```



&#x20;Run the web app



```bash

streamlit run app.py

```



&#x20;Or chat in the terminal



```bash

python chatbot.py

```



&#x20;Use your own FAQ



Edit `faq.json`. Each entry looks like this:



```json

{"id": 1, "category": "Orders",

&#x20;"questions": \["How can I track my order?", "Where is my package?"],

&#x20;"answer": "Open My Orders in your account and click Track."}

```



Add several phrasings in `questions`: the more ways users can ask the same thing, the better the matching.



&#x20;Project structure



```

.

|-- app.py            # Streamlit chat interface

|-- chatbot.py        # TF-IDF matching and confidence logic

|-- preprocessing.py  # NLTK text cleaning

|-- faq.json          # FAQ content (questions and answers)

|-- requirements.txt  # Python dependencies

|-- .streamlit/

|   `-- config.toml   # Theme settings

`-- screenshots/      # README images

```



&#x20;Limitations



\- The bot matches words, not meaning: it cannot understand synonyms that are not present in the FAQ. Adding phrasings to `faq.json` fixes this.

\- It only answers questions covered by the FAQ.

\- Nova Market is fictional: all prices, delays and contact details are invented for the demo.



&#x20;Author



Created by \[AKPINFA](https://github.com/AKPINFA).

