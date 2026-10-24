import time

import streamlit as st

from chatbot import FAQChatbot

st.set_page_config(page_title="Nova Market Assistant", page_icon="🛍️", layout="centered")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.5rem; padding-bottom: 6rem; max-width: 780px; }

    .hero {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 55%, #06B6D4 100%);
        border-radius: 20px; padding: 1.8rem 2rem; color: white; text-align: center;
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.28); margin-bottom: 1.4rem;
    }
    .hero h1 { margin: 0; font-size: 1.9rem; font-weight: 700; color: white; }
    .hero p { margin: .45rem 0 0 0; font-size: 1rem; opacity: .92; color: white; }

    .section-label {
        font-size: .78rem; font-weight: 600; letter-spacing: .06em;
        text-transform: uppercase; color: #6B7280; margin: .8rem 0 .4rem 0;
    }

    div[data-testid="stChatMessage"] {
        background: #FFFFFF; border: 1.5px solid #E5E7EB; border-radius: 16px;
        padding: .9rem 1.1rem; margin-bottom: .7rem;
        box-shadow: 0 4px 14px rgba(17, 24, 39, .05);
    }

    .pill {
        display: inline-block; padding: .15rem .65rem; margin: .35rem .4rem 0 0;
        border-radius: 999px; font-size: .74rem; font-weight: 600;
        background: #EEF2FF; color: #4338CA;
    }
    .pill-muted { background: #F3F4F6; color: #4B5563; }
    .pill-warn { background: #FEF3C7; color: #92400E; }

    .stButton > button {
        border-radius: 12px; font-weight: 500; padding: .6rem .9rem;
        border: 1.5px solid #E5E7EB; background: #FFFFFF; transition: all .15s ease;
    }
    .stButton > button:hover { border-color: #4F46E5; color: #4F46E5; transform: translateY(-1px); }

    div[data-testid="stChatInput"] { border-radius: 16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

QUICK_QUESTIONS = [
    "How can I track my order?",
    "What is your return policy?",
    "How much does shipping cost?",
    "What payment methods do you accept?",
    "How do I reset my password?",
    "Do you ship internationally?",
]

WELCOME = (
    "Hi! I'm the Nova Market assistant. Ask me about orders, delivery, payments, "
    "returns or your account, or pick a question below."
)


@st.cache_resource
def load_bot():
    return FAQChatbot()


bot = load_bot()


# ---------- Conversation state ----------
def init_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME, "meta": None, "animate": False}
    ]


def ask(question):
    """Called when the user clicks a suggested question."""
    st.session_state.pending = question


def stream_text(text):
    """Yield the text word by word to create a typing effect."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def answer_to(text):
    st.session_state.messages.append({"role": "user", "content": text})
    result = bot.get_answer(text)
    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "meta": result, "animate": True}
    )


if "messages" not in st.session_state:
    init_chat()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### About this demo")
    st.write(
        f"**{bot.company}** is a *fictional* online store created to demonstrate "
        "an FAQ chatbot."
    )
    st.markdown("**How it works**")
    st.write(
        "1. Your question is cleaned with NLTK (tokenization, stop words, lemmatization).\n"
        "2. It is converted into numbers with TF-IDF.\n"
        "3. Cosine similarity finds the closest FAQ.\n"
        "4. If nothing is close enough, the bot says so instead of guessing."
    )
    st.caption(f"{len(bot.faqs)} FAQs · {len(bot.phrasings)} question variants")
    st.button("🗑️ Clear conversation", on_click=init_chat, use_container_width=True)

# ---------- Header ----------
st.markdown(
    f"""
    <div class="hero">
        <h1>🛍️ {bot.company} Assistant</h1>
        <p>Instant answers about orders, delivery, payments and returns.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- New message (typed or clicked) ----------
pending = st.session_state.pop("pending", None)
typed = st.chat_input("Ask a question about orders, delivery, payments...")
new_text = pending or typed
if new_text:
    answer_to(new_text)

# ---------- Conversation ----------
for message in st.session_state.messages:
    avatar = "🛍️" if message["role"] == "assistant" else "🧑"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("animate"):
            st.write_stream(stream_text(message["content"]))
            message["animate"] = False
        else:
            st.markdown(message["content"])

        meta = message.get("meta")
        if meta:
            if meta["confident"]:
                pills = (
                    f'<span class="pill">{meta["category"]}</span>'
                    f'<span class="pill pill-muted">Confidence {meta["score"]:.0%}</span>'
                )
            else:
                pills = '<span class="pill pill-warn">Not sure</span>'
            st.markdown(pills, unsafe_allow_html=True)

# ---------- Quick replies and suggestions ----------
messages = st.session_state.messages
if len(messages) == 1:
    st.markdown('<div class="section-label">Popular questions</div>', unsafe_allow_html=True)
    columns = st.columns(2)
    for i, question in enumerate(QUICK_QUESTIONS):
        columns[i % 2].button(
            question, key=f"quick_{i}", on_click=ask, args=(question,), use_container_width=True
        )
else:
    last_meta = messages[-1].get("meta")
    if last_meta and not last_meta["confident"] and last_meta["suggestions"]:
        st.markdown('<div class="section-label">Did you mean</div>', unsafe_allow_html=True)
        for j, question in enumerate(last_meta["suggestions"]):
            st.button(
                question, key=f"suggestion_{len(messages)}_{j}", on_click=ask,
                args=(question,), use_container_width=True,
            )