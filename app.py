import streamlit as st
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
import re
import numpy as np

# 1. UI STYLING
st.set_page_config(page_title="Universal AI Assistant", layout="wide", page_icon="✨")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .summary-card { 
        padding: 15px; margin: 10px 0; border-radius: 8px; 
        border-left: 5px solid #4A90E2; background: #fdfdfd;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .section-header { font-size: 22px; font-weight: bold; color: #1E3A8A; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Universal Smart Assistant")
st.caption("Instant audio summaries for Theory, Personal, or Technical PDFs.")

# 2. LANGUAGE SELECTION
# Verified dictionary formatting to prevent SyntaxErrors
indian_languages = {
   "Kannada": "kn",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Urdu": "ur",
    "Odia": "or"
}

target_lang_name = st.sidebar.selectbox("🎯 Select Language", list(indian_languages.keys()))
target_lang_code = indian_languages[target_lang_name]

# 3. INSTANT UPLOADER
uploaded_file = st.file_uploader("📂 Drop any PDF here", type="pdf")

if uploaded_file:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        with st.spinner(f"🚀 Creating your {target_lang_name} summary..."):
            # Step 1: Text Extraction
            raw_text = ""
            for page in doc:
                raw_text += page.get_text("text") + " "

            # Step 2: Content Cleaning
            sentences = re.split(r'(?<=[.!?]) +', raw_text)
            clean_sentences = [s.strip() for s in sentences if len(s.split()) > 10]

            if len(clean_sentences) > 5:
                translator = GoogleTranslator(source='auto', target=target_lang_code)
                
                # Step 3: UNIVERSAL CATEGORIES
                categories = [
                    ("👤", "Main Overview"),
                    ("🔍", "Important Details"),
                    ("💡", "Key Insights"),
                    ("⚙️", "How it Works"),
                    ("📌", "Main Highlights"),
                    ("🚀", "Practical Use"),
                    ("⚖️", "Critical Points"),
                    ("📝", "Observations"),
                    ("✨", "Key Takeaways"),
                    ("✅", "Conclusion")
                ]

                # Step 4: Map content to Categories
                num_cat = len(categories)
                indices = np.linspace(0, len(clean_sentences)-1, num_cat * 2, dtype=int)
                
                final_md = f"## 📘 {target_lang_name} Summary\n\n"
                audio_text = ""

                for i, (emoji, cat_name) in enumerate(categories):
                    # Translate category header
                    t_cat = translator.translate(cat_name)
                    final_md += f"<div class='section-header'>{emoji} {t_cat}</div>\n"
                    
                    # Pull 2 points per category
                    start_ptr = i * 2
                    for j in range(start_ptr, start_ptr + 2):
                        if j < len(indices):
                            p = clean_sentences[indices[j]]
                            t_p = translator.translate(p)
                            final_md += f"<div class='summary-card'>{t_p}</div>\n"
                            audio_text += f"{t_p}. "

                # --- STEP 5: DISPLAY RESULTS ---
                st.divider()
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.markdown(final_md, unsafe_allow_html=True)

                with col2:
                    st.info("### 🎧 Audio Lecture")
                    audio_stream = io.BytesIO()
                    gTTS(text=audio_text, lang=target_lang_code).write_to_fp(audio_stream)
                    audio_stream.seek(0)
                    
                    st.audio(audio_stream, format="audio/mp3")
                    st.download_button("📥 Save MP3", audio_stream, "lecture.mp3", "audio/mp3")

            else:
                st.error("Not enough text found in this PDF.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")

else:
    st.info("👋 Upload a PDF to see the magic!")