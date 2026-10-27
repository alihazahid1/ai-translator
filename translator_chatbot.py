import streamlit as st
import requests
import base64
import html
import streamlit.components.v1 as components
from gtts import gTTS
from io import BytesIO
import nltk
from nltk.corpus import wordnet

st.set_page_config(
    page_title="LinguaBot AI",
    page_icon="🤖",
    layout="wide",
)

# ---------- STYLING ----------

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 85% 15%, #26365b 0%, transparent 38%),
        linear-gradient(135deg, #101629 0%, #19233d 55%, #11182c 100%);
    color: #f5f7ff;
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}
h1, h2, h3, p, label {
    color: #f5f7ff;
}
div[data-testid="stTextArea"] textarea {
    background: #151f35;
    color: #ffffff;
    border: 1px solid #3d507b;
    border-radius: 13px;
}
/* Selected language value */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #202b43 !important;
    color: #ffffff !important;
    border-radius: 10px;
}

/* Selected text and dropdown arrow */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #ffffff !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}
div.stButton > button {
    background: linear-gradient(90deg, #536fff, #985cff);
    color: #ffffff;
    border: 0;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
}
div.stButton > button:hover {
    border: 1px solid #9cecff;
    color: #ffffff;
}
.panel {
    background: rgba(29, 40, 66, 0.82);
    border: 1px solid rgba(119, 147, 205, 0.28);
    border-radius: 18px;
    padding: 18px;
    min-height: 100px;
    overflow-wrap: anywhere;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.12);
}
.eyebrow {
    color: #9fb6ee;
    font-size: 0.76rem;
    letter-spacing: 0.12em;
    font-weight: 700;
    text-transform: uppercase;
}
.helper {
    color: #aebfe2;
    font-size: 0.88rem;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------- API & LANGUAGES ----------

API_URL = "https://api.mymemory.translated.net/get"

LANGUAGES = {
    "English": "en",
    "Urdu": "ur",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Chinese": "zh-CN",
    "Arabic": "ar",
    "Hindi": "hi",
    "Turkish": "tr",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
}

TTS_LANGUAGES = LANGUAGES.copy()


def translate_text(text, source_code, target_code):
    params = {
        "q": text,
        "langpair": f"{source_code}|{target_code}",
        "mt": 1,
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("responseStatus") != 200:
        raise ValueError(
            data.get("responseDetails", "Translation failed")
        )

    result = data.get("responseData", {}).get("translatedText", "")
    if not result:
        raise ValueError("No translated text returned.")

    return result


def get_synonyms(word):
    synonyms = set()

    # Synonyms are generated for a single English word.
    if not word.isalpha():
        return []

    for syn in wordnet.synsets(word.lower()):
        for lemma in syn.lemmas():
            synonym = lemma.name().replace("_", " ")

            if synonym.lower() != word.lower():
                synonyms.add(synonym)

    return sorted(synonyms)[:10]

def text_to_speech(text, language):
    audio_buffer = BytesIO()
    tts = gTTS(
        text=text,
        lang=TTS_LANGUAGES[language],
        slow=False,
    )
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.getvalue()


# ---------- ROBOT COMPONENT ----------

def show_robot(audio_bytes=None):
    audio_src = ""
    if audio_bytes:
        encoded = base64.b64encode(audio_bytes).decode("utf-8")
        audio_src = f"data:audio/mp3;base64,{encoded}"

    robot_html = r"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    * { box-sizing: border-box; }
    body {
        margin: 0;
        font-family: Arial, sans-serif;
        color: #fff;
        background: transparent;
        text-align: center;
    }
    .stage {
        min-height: 545px;
        padding: 24px 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(127, 160, 229, .22);
        border-radius: 22px;
        background:
          radial-gradient(ellipse at 50% 42%, rgba(73, 108, 190, .34), transparent 58%),
          linear-gradient(155deg, rgba(31, 45, 75, .95), rgba(17, 25, 44, .97));
        box-shadow: 0 18px 45px rgba(0, 0, 0, .2);
        overflow: hidden;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #b9f7e4;
        background: rgba(62, 205, 166, .10);
        border: 1px solid rgba(100, 231, 198, .25);
        padding: 7px 12px;
        border-radius: 30px;
        font-size: 12px;
        margin-bottom: 12px;
    }
    .dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: #65efc4; box-shadow: 0 0 10px #65efc4;
    }
    .robot-wrap {
        position: relative;
        width: 240px;
        height: 295px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 4px auto 0;
    }
    .halo {
        position: absolute;
        width: 235px; height: 235px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(86, 143, 255, .23), rgba(93, 79, 255, .08) 48%, transparent 72%);
        animation: haloPulse 3s ease-in-out infinite;
    }
    .robot {
        position: relative;
        width: 190px;
        height: 235px;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 14px 16px rgba(0, 0, 0, .4));
    }
    .antenna {
        position: absolute; top: 1px; left: 92px;
        width: 7px; height: 31px; border-radius: 10px;
        background: linear-gradient(90deg, #8199bd, #f5fbff, #9bafd0);
    }
    .antenna:after {
        content: ""; position: absolute;
        width: 18px; height: 18px; top: -10px; left: -5px;
        border-radius: 50%; background: #69edff;
        box-shadow: 0 0 19px #52dfff;
        animation: glow 1.6s ease-in-out infinite alternate;
    }
    .ear {
        position: absolute; top: 80px; width: 18px; height: 43px;
        border-radius: 8px;
        background: linear-gradient(90deg, #7189ad, #e7f1ff);
        box-shadow: 0 2px 5px rgba(0,0,0,.2);
    }
    .ear.left { left: 1px; }
    .ear.right { right: 1px; }
    .head {
        position: absolute; top: 26px; left: 5px;
        width: 180px; height: 150px; border-radius: 43px;
        background: linear-gradient(135deg, #fff 0%, #d9e5f7 28%, #a4b8d8 68%, #edf5ff 100%);
        border: 2px solid rgba(255,255,255,.9);
        box-shadow: inset -9px -9px 18px #7286a7, inset 7px 7px 15px #fff;
    }
    .face {
        position: absolute; top: 28px; left: 19px;
        width: 140px; height: 91px; border-radius: 25px;
        background: linear-gradient(145deg, #182743, #070e20);
        box-shadow: inset 0 0 13px #020817, 0 0 0 2px rgba(115, 221, 255, .25);
    }
    .eyes {
        display: flex; justify-content: space-evenly; padding-top: 17px;
    }
    .eye {
        width: 25px; height: 29px; border-radius: 50%;
        background: radial-gradient(circle at 35% 28%, #fff 0%, #9df5ff 22%, #35bfff 58%, #1473ff 100%);
        box-shadow: 0 0 14px #25c5ff;
        animation: blink 4.2s infinite;
    }
    .mouth {
        width: 34px; height: 6px; margin: 10px auto 0;
        border-radius: 50%; background: #66efff;
        box-shadow: 0 0 11px #43dfff;
    }
    .robot.speaking .mouth { animation: talk .16s infinite alternate; }
    .robot.speaking .eye { box-shadow: 0 0 23px #6df5ff; }
    .neck {
        position: absolute; top: 174px; left: 72px;
        width: 46px; height: 15px; border-radius: 6px;
        background: linear-gradient(90deg, #8196b8, #eff7ff, #8498b8);
    }
    .body {
        position: absolute; top: 185px; left: 42px;
        width: 106px; height: 44px; border-radius: 23px 23px 15px 15px;
        background: linear-gradient(135deg, #fff, #b7c9e4 48%, #f3f8ff);
        border: 1px solid #e9f2ff;
        box-shadow: inset -6px -6px 10px #8296b5, inset 5px 5px 9px #fff;
    }
    .chest-light {
        position: absolute; top: 198px; left: 88px;
        width: 14px; height: 8px; border-radius: 8px;
        background: #60eaff; box-shadow: 0 0 12px #60eaff;
    }
    .robot-label {
        font-size: 22px; font-weight: 700; margin-top: 0;
        letter-spacing: .01em;
    }
    .robot-subtitle {
        color: #aebfe2; font-size: 13px; margin-top: 7px;
        line-height: 1.5; max-width: 260px;
    }
    .play {
        margin-top: 19px; width: min(100%, 280px);
        padding: 14px 20px; color: #fff; border: 0;
        border-radius: 14px;
        background: linear-gradient(100deg, #536fff, #8a5bff);
        box-shadow: 0 8px 22px rgba(83, 111, 255, .28);
        font-size: 14px; font-weight: 700; cursor: pointer;
        transition: transform .2s, opacity .2s;
    }
    .play:hover { transform: translateY(-2px); }
    .play:disabled { opacity: .5; cursor: not-allowed; }
    .tip { color: #8599c1; font-size: 11px; margin-top: 12px; }
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(-1deg); }
        50% { transform: translateY(-8px) rotate(1deg); }
    }
    @keyframes blink {
        0%, 44%, 48%, 100% { transform: scaleY(1); }
        46% { transform: scaleY(.08); }
    }
    @keyframes talk {
        from { height: 4px; width: 26px; border-radius: 50%; }
        to { height: 23px; width: 20px; border-radius: 45%; }
    }
    @keyframes glow { from { opacity: .65; } to { opacity: 1; } }
    @keyframes haloPulse {
        0%, 100% { transform: scale(.94); opacity: .7; }
        50% { transform: scale(1.06); opacity: 1; }
    }
    </style>
    </head>
    <body>
      <div class="stage">
        <div class="status-pill"><span class="dot"></span><span id="status">AI ASSISTANT READY</span></div>
        <div class="robot-wrap">
          <div class="halo"></div>
          <div class="robot" id="robot">
            <div class="antenna"></div>
            <div class="ear left"></div><div class="ear right"></div>
            <div class="head">
              <div class="face">
                <div class="eyes"><div class="eye"></div><div class="eye"></div></div>
                <div class="mouth"></div>
              </div>
            </div>
            <div class="neck"></div><div class="body"></div><div class="chest-light"></div>
          </div>
        </div>
        <div class="robot-label">LinguaBot</div>
        <div class="robot-subtitle" id="subtitle">Your personal language assistant.<br>Translate text and I'll speak it for you.</div>
        <audio id="voice" preload="auto" src="ROBOT_AUDIO"></audio>
        <button class="play" id="play" onclick="playVoice()" disabled>Translate text first</button>
        <div class="tip">VOICE OUTPUT · ANIMATED SPEAKING</div>
      </div>
      <script>
        const robot = document.getElementById("robot");
        const audio = document.getElementById("voice");
        const statusText = document.getElementById("status");
        const subtitle = document.getElementById("subtitle");
        const button = document.getElementById("play");
        const hasAudio = Boolean(audio.getAttribute("src"));

        if (hasAudio) {
          button.disabled = false;
          button.textContent = "▶  Speak Translation";
          statusText.textContent = "TRANSLATION READY";
          subtitle.innerHTML = "Your translated text is ready.<br>Press below to hear it.";
        }

        function resetRobot() {
          robot.classList.remove("speaking");
          statusText.textContent = hasAudio ? "TRANSLATION READY" : "AI ASSISTANT READY";
          subtitle.innerHTML = hasAudio
            ? "Your translated text is ready.<br>Press below to hear it."
            : "Your personal language assistant.<br>Translate text and I'll speak it for you.";
          button.textContent = hasAudio ? "▶  Speak Translation" : "Translate text first";
          button.disabled = !hasAudio;
        }

        async function playVoice() {
          if (!hasAudio) return;
          if (!audio.paused) {
            audio.pause();
            audio.currentTime = 0;
            resetRobot();
            return;
          }
          audio.currentTime = 0;
          robot.classList.add("speaking");
          statusText.textContent = "ROBOT SPEAKING";
          subtitle.textContent = "Listen to your translated text.";
          button.textContent = "■  Stop Speaking";
          try {
            await audio.play();
          } catch (error) {
            resetRobot();
            statusText.textContent = "AUDIO PLAYBACK ERROR";
          }
        }

        audio.addEventListener("ended", resetRobot);
        audio.addEventListener("pause", () => {
          if (audio.currentTime === 0 || audio.ended) resetRobot();
        });
      </script>
    </body>
    </html>
    """
    robot_html = robot_html.replace("ROBOT_AUDIO", audio_src)
    components.html(robot_html, height=590, scrolling=False)


# ---------- HEADER ----------

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown("# 🤖 LinguaBot AI")
    st.markdown(
        '<div class="helper">Translate instantly. '
        'Your robot is ready to speak.</div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        '<div style="text-align:right;padding-top:16px;">'
        '<span style="background:#193b3a;color:#91f3d5;'
        'border:1px solid #2b6a61;border-radius:20px;'
        'padding:8px 12px;font-size:12px;">● SYSTEM READY</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------- MAIN TWO-COLUMN LAYOUT ----------

left_col, right_col = st.columns([1.08, 0.92], gap="large")

with left_col:
    st.markdown(
        '<div class="eyebrow">LANGUAGE TRANSLATOR</div>',
        unsafe_allow_html=True,
    )
    st.markdown("## Translate your text")
    st.markdown(
        '<div class="helper">Choose languages, enter your text, '
        'and get your spoken translation.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    source_col, target_col = st.columns([1, 1])

    with source_col:
        source = st.selectbox(
            "Translate from",
            list(LANGUAGES.keys()),
            index=0,
            key="source_language",
        )

    with target_col:
        target = st.selectbox(
            "Translate to",
            list(LANGUAGES.keys()),
            index=1,
            key="target_language_select",
        )




    text = st.text_area(
        "Your text",
        placeholder="Type something you want to translate...",
        height=150,
        max_chars=1000,
        key="input_text",
    )

    st.markdown(
        '<div class="helper">Tip: short, clear sentences usually '
        'produce better translations.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    translate_clicked = st.button(
        "🌐  Translate Text",
        type="primary",
        use_container_width=True,
    )

    if translate_clicked:
        if not text.strip():
            st.warning("Please enter some text.")

        elif source == target:
            st.warning("Choose two different languages.")

        elif len(text.strip().encode("utf-8")) > 500:
            st.warning(
                "Please enter shorter text. MyMemory requests are "
                "limited to 500 bytes in this app."
            )

        else:
            try:
                with st.spinner("Translating and preparing speech..."):
                    translated = translate_text(
                        text.strip(),
                        LANGUAGES[source],
                        LANGUAGES[target],
                    )
                    # Automatically prepare the translated voice.
                    audio_bytes = text_to_speech(translated, target)

                st.session_state["translated"] = translated
                st.session_state["speech_audio"] = audio_bytes
                st.session_state["original_text"] = text.strip()
                st.session_state["result_source"] = source
                st.session_state["result_target"] = target

            except Exception as e:
                st.error(f"Could not complete translation: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="eyebrow">TRANSLATION RESULT</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Your translated text")
    
    # ---------- SYNONYMS ----------
    original_text = st.session_state.get("original_text", "").strip()

    st.markdown("### 🔤 English Synonyms")

    if original_text and source == "English" and len(original_text.split()) == 1:
        synonyms = get_synonyms(original_text)

        if synonyms:
            st.write("Similar words:")
            st.write(" · ".join(synonyms))
        else:
            st.caption("No synonyms found for this word.")
    else:
        st.caption("Enter and translate a single English word to see its synonyms.")


    translated = st.session_state.get("translated")
    if translated:
        st.markdown(
            '<div class="panel">' + html.escape(translated) + '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="helper" style="margin-top:8px;">'
            f'{html.escape(st.session_state.get("result_source", ""))}'
            f' → {html.escape(st.session_state.get("result_target", ""))}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="panel" style="color:#9fb0d3;">'
            'Your translation will appear here after you click '
            '<b>Translate Text</b>.'
            '</div>',
            unsafe_allow_html=True,
        )

with right_col:
    show_robot(st.session_state.get("speech_audio"))

st.markdown(
    '<div style="text-align:center;color:#7185ad;font-size:12px;'
    'padding:20px 0 4px;">Powered by MyMemory Translation API · gTTS</div>',
    unsafe_allow_html=True,
)
