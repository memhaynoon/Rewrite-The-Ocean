###Rewrite the Ocean###
import streamlit as st
import random
import time
import json
import base64

REVIEW_SECONDS = 30    # time to look at the letters before typing
INPUT_SECONDS = 15    # time allowed to type a word

st.set_page_config(page_title="Rewrite The Ocean", page_icon="🪸")
st.title("🪸 Rewrite The Ocean 🪸")
st.header("Presented by Mutahhar Nazir")
#st.subheader("The Bush School")

st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmswYXJkbTVtdmU3cTZqb3ltMXZxbmd1czUyOW1hNDB2YXdxaWI3ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3diXKYoAiX6qY64M/giphy.gif")

# ---------- Background: ocean-blue color + wallpaper.jpg ----------
@st.cache_data
def get_base64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    wallpaper_base64 = get_base64_file("wallpaper.jpg")
    background_css = f"""
    <style>
    .stApp {{
        background-color: #C0E6F5;
        background-image: linear-gradient(rgba(0, 60, 90, 0.15), rgba(0, 60, 90, 0.15)),
                           url("data:image/jpg;base64,{wallpaper_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
except FileNotFoundError:
    # Falls back to just the ocean-blue color if wallpaper.jpg isn't found
    background_css = """
    <style>
    .stApp {
        background-color: #C0E6F5;
    }
    </style>
    """

st.markdown(background_css, unsafe_allow_html=True)


# ---------- Rules: shown at all times, on every phase ----------
with st.sidebar:
    st.header("🪸 Rewrite The Ocean")
    st.markdown("""
    **Rules:**
    - The total number of letters will be 9.
    - You may choose between 3 and 5 vowels (the rest will be consonants).
    - Your aim is to make the longest possible word.
    - If the word you enter is related to the ocean, you get bonus points.
    - The score is tripled if you make a word using all nine letters.
    """)


# ---------- Load dictionary once per session ----------
@st.cache_data
def load_dictionary():
    with open("dictionary.json", "r", encoding="utf-8") as file:
        return json.load(file)

try:
    dictionary = load_dictionary()
except FileNotFoundError:
    st.error("dictionary.json not found. Make sure it's in the same folder/repo as this app.")
    st.stop()


# ---------- Session state defaults ----------
defaults = {
    "phase": "start",
    "rounds": 1,
    "rounds_completed": 0,
    "score": 0,
    "display": [],
    "review_start": None,
    "word_start": None,
    "round_result": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def generate_letters(vowel_amount):
    consonant_amount = 9 - vowel_amount
    vowels = ["e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "a", "a", "a","a", "a", "a", "a", "a", "a", "i", "i", "i", "i", "i", "i", "i", "i", "i", "o", "o", "o", "o", "o", "o", "o", "o", "u", "u", "u", "u"]
    consonants = [ "n", "n", "n", "n", "n", "n", "r", "r", "r", "r", "r", "r", "t", "t", "t", "t", "t", "t", "d", "d", "d", "d", "l", "l", "l", "l", "s", "s", "s", "s", "g", "g", "g", "b", "b", "c", "c", "f", "f", "h", "h", "m", "m", "p", "p", "v", "v", "w", "w", "y", "y", "k", "j", "x", "q", "z"
]

    vowels_decided = [random.choice(vowels) for _ in range(5)]
    consonants_decided = [random.choice(consonants) for _ in range(6)]

    display = [vowels_decided[0], consonants_decided[0]]
    display += vowels_decided[1:vowel_amount]
    display += consonants_decided[1:consonant_amount]
    return display


def score_word(word, display):
    """Ports the original scoring/dictionary/ocean-bonus logic."""
    definition = None
    if word:
        definition = dictionary.get(word.lower()) or dictionary.get(word.capitalize())

    answer_check = list(word.lower()) if word else []
    possible_score = len(answer_check)
    cancel = possible_score > 9
    lettersarenine = possible_score == 9

    errors = 0
    if not definition:
        errors += possible_score

    # Ocean-related bonus
    ocean_related = False
    bonus_points = 0
    if definition:
        for kw in ["ocean", "sea", "beach", "reef", "sailor"]:
            if kw in definition:
                ocean_related = True
        if ocean_related:
            if possible_score < 4:
                bonus_points = 1
            elif possible_score < 6:
                bonus_points = 2
            elif possible_score < 7:
                bonus_points = 3
            else:
                bonus_points = 4

    # Check letters were actually available in the display set
    display_copy = display.copy()
    letter_errors = []
    for letter in answer_check:
        if letter in display_copy:
            display_copy.remove(letter)
        else:
            letter_errors.append(f"You used '{letter}' too many times.")
            errors += 1

    if lettersarenine:
        possible_score *= 3

    possible_score -= errors
    round_score = 0 if cancel else possible_score + bonus_points

    return {
        "word": word,
        "definition": definition,
        "ocean_related": ocean_related,
        "bonus_points": bonus_points,
        "letter_errors": letter_errors,
        "round_score": round_score,
        "cancel": cancel,
    }


# ==================== PHASE: start ====================
if st.session_state.phase == "start":
    st.title("Ready to play?")

    rounds = st.number_input("How many rounds would you like to play?",
                              min_value=1, value=1, step=1)
    
    if st.button("Start Game"):
        st.session_state.rounds = rounds
        st.session_state.rounds_completed = 0
        st.session_state.score = 0
        st.session_state.phase = "vowel_input"
        st.rerun()


# ==================== PHASE: vowel_input ====================
elif st.session_state.phase == "vowel_input":
    st.subheader(f"Round {st.session_state.rounds_completed + 1} of {st.session_state.rounds}")
    st.write(f"Score so far: {st.session_state.score}")

    vowel_amount = st.number_input("How many vowels do you want? (3-5)",
                                    min_value=3, max_value=5, value=3, step=1)

    
    st.session_state.display = generate_letters(vowel_amount)
    st.session_state.phase = "review"
    st.session_state.review_start = time.time()
    st.rerun()


# ==================== PHASE: review ====================
elif st.session_state.phase == "review":
    st.subheader("These are your letters:")
    st.markdown(f"## {'  '.join(st.session_state.display).upper()}")

    elapsed = time.time() - st.session_state.review_start
    remaining = REVIEW_SECONDS - elapsed

    timer_placeholder = st.empty()

    if remaining > 0:
        timer_placeholder.info(f"You have {int(remaining) + 1}s to think of the longest word")
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.phase = "word_input"
        st.session_state.word_start = time.time()
        st.rerun()


# ==================== PHASE: word_input ====================
elif st.session_state.phase == "word_input":
    st.subheader("Type your longest word:")
    st.write(f"Letters: {'  '.join(st.session_state.display).upper()}")

    user_input = st.text_input("Your word", key="word_box")
    submit = st.button("Submit")

    elapsed = time.time() - st.session_state.word_start
    remaining = INPUT_SECONDS - elapsed

    timer_placeholder = st.empty()

    finalize = submit or remaining <= 0

    if finalize:
        typed = st.session_state.get("word_box", "").strip()
        word = typed if typed else None
        st.session_state.round_result = score_word(word or "", st.session_state.display)
        st.session_state.score += st.session_state.round_result["round_score"]
        st.session_state.rounds_completed += 1
        st.session_state.phase = "result"
        st.rerun()
    else:
        timer_placeholder.warning(f"Time left: {int(remaining) + 1}s")
        time.sleep(1)
        st.rerun()


# ==================== PHASE: result ====================
elif st.session_state.phase == "result":
    result = st.session_state.round_result

    st.subheader("Round Result")

    if not result["word"]:
        st.write("You did not enter a word.")
    else:
        st.write(f"Your word: **{result['word']}**")
        if result["definition"]:
            st.success(f"Definition: {result['definition']}")
        else:
            st.error(f"'{result['word']}' is not in the dictionary.")

        if result["ocean_related"]:
            st.info(f"Related to the ocean! (+{result['bonus_points']} bonus)")

        for err in result["letter_errors"]:
            st.warning(err)

    # st.session_state.score += result["round_score"]
    # st.session_state.rounds_completed += 1

    st.write(f"Round score: {result['round_score']}")
    st.write(f"Total score: {st.session_state.score}")

    if st.session_state.rounds_completed < st.session_state.rounds:
        if st.button("Next Round"):
            st.session_state.phase = "vowel_input"
            st.rerun()
    else:
        if st.button("See Final Score"):
            st.session_state.phase = "final"
            st.rerun()


# ==================== PHASE: final ====================
elif st.session_state.phase == "final":
    st.title("Game Over")
    st.write(f"Your final score is **{st.session_state.score}**.")

    if st.button("Play Again"):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()
