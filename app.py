import streamlit as st
import re
from collections import Counter

# --- CONFIGURATION & BRANDING ---
st.set_page_config(
    page_title="YMCA Job Decoder",
    page_icon="🔴",
    layout="centered"
)

# Custom CSS to enforce YMCA Red and White theme
# YMCA Red approx hex: #C41230
st.markdown(
    """
    <style>
    /* Main Background to White */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    /* Headings in YMCA Red */
    h1, h2, h3, span[data-testid="stMetricLabel"] {
        color: #C41230 !important;
    }
    /* Custom Button Styling - Red Button, White Text */
    div.stButton > button {
        background-color: #C41230;
        color: white;
        border: none;
        font-weight: bold;
        padding: 10px 24px;
    }
    div.stButton > button:hover {
        background-color: #A00F28; /* Slightly darker red on hover */
        color: white;
    }
    /* Metric Value styling */
    span[data-testid="stMetricValue"] {
       color: #C41230;
    }
    /* Helper text for transliteration */
    .translit {
        font-style: italic;
        color: #666666;
        font-size: 0.9em;
        margin-top: -10px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MULTI-LANGUAGE CONTENT DICTIONARY ---
# Includes native script and English transliteration (phonetics)
CONTENT = {
    "English": {
        "instructions": "Instructions: Paste your resume on the left and the job posting on the right.",
        "translit": "(Instructions: Paste your resume on the left and the job posting on the right.)",
        "resume_label": "Your Resume text",
        "jd_label": "Job Description text",
        "button": "DECODE MY RESUME",
        "results_title": "Your Results",
        "missing_title": "Missing Keywords (Add these to your resume!)",
        "match_label": "Match Score"
    },
    "Español (Spanish)": {
        "instructions": "Instrucciones: Pegue su currículum a la izquierda y la oferta de trabajo a la derecha.",
        "translit": "(Instrucciones: Pe-ge su cu-rri-cu-lum a la iz-kier-da y la o-fer-ta de tra-ba-jo a la de-re-cha.)",
        "resume_label": "Texto de su currículum",
        "jd_label": "Texto de la descripción del trabajo",
        "button": "DECODIFICAR MI CURRÍCULUM",
        "results_title": "Sus Resultados",
        "missing_title": "Palabras clave faltantes (¡Agréguelas a su currículum!)",
        "match_label": "Puntuación de coincidencia"
    },
    "العربية (Arabic)": {
        "instructions": "التعليمات: الصق سيرتك الذاتية على اليسار وإعلان الوظيفة على اليمين.",
        "translit": "(Al-ta'leemat: Ilsaq seeratak al-thatia ala al-yassar wa i'lan al-wazifa ala al-yameen.)",
        "resume_label": "نص سيرتك الذاتية",
        "jd_label": "نص الوصف الوظيفي",
        "button": "فك شفرة سيرتي الذاتية",
        "results_title": "نتائجك",
        "missing_title": "كلمات مفتاحية مفقودة (أضفها إلى سيرتك الذاتية!)",
        "match_label": "درجة التطابق"
    },
    "Українська (Ukrainian)": {
        "instructions": "Інструкції: Вставте своє резюме ліворуч, а опис вакансії - праворуч.",
        "translit": "(Instruktsiyi: Vstavte svoye rezyume livoruch, a opys vakansiyi - pravoruch.)",
        "resume_label": "Текст вашого резюме",
        "jd_label": "Текст опису вакансії",
        "button": "РОЗШИФРУВАТИ МОЄ РЕЗЮМЕ",
        "results_title": "Ваші результати",
        "missing_title": "Відсутні ключові слова (Додайте їх до свого резюме!)",
        "match_label": "Оцінка відповідності"
    },
    "简体中文 (Simplified Chinese)": {
        "instructions": "说明：将您的简历粘贴在左侧，将职位描述粘贴在右侧。",
        "translit": "(Shuōmíng: Jiāng nín de jiǎnlì zhāntiē zài zuǒcè, jiāng zhíwèi miáoshù zhāntiē zài yòucè.)",
        "resume_label": "您的简历文本",
        "jd_label": "职位描述文本",
        "button": "解码我的简历",
        "results_title": "您的结果",
        "missing_title": "缺失的关键词 (将这些添加到您的简历中！)",
        "match_label": "匹配得分"
    }
}


# --- HELPER FUNCTIONS ---
def clean_text(text):
    """Cleans text by lowercasing and removing non-alphanumeric characters."""
    text = text.lower()
    # Replace non-alphanumeric characters with spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text

def get_tokens(text):
    """Splits text into individual words (tokens)."""
    cleaned = clean_text(text)
    tokens = cleaned.split()
    # Filter out very short words to reduce noise (optional but helpful)
    return set([t for t in tokens if len(t) > 2])

# --- MAIN APP LAYOUT ---

# 1. Header and Logo
col1, col2, col3 = st.columns([1,2,1])
with col2:
    # Displaying the uploaded logo centrally
    try:
        st.image("image_0.png", use_column_width=True)
    except FileNotFoundError:
        st.error("Logo image not found. Please ensure 'image_0.png' is in the same folder as this script.")

st.markdown("<h1 style='text-align: center;'>Job Description Decoder</h1>", unsafe_allow_html=True)
st.markdown("---")

# 2. Language Selection
lang_options = list(CONTENT.keys())
selected_lang = st.selectbox("🌐 Select Language / Seleccione el idioma / اختر اللغة", lang_options)
text_data = CONTENT[selected_lang]

# 3. Instructions with Transliteration
st.info(f"**{text_data['instructions']}**")
st.markdown(f"<div class='translit'>{text_data['translit']}</div>", unsafe_allow_html=True)


# 4. Input Areas (Two Columns)
col_res, col_jd = st.columns(2)

with col_res:
    st.subheader("👤 RÉSUMÉ")
    resume_text = st.text_area(text_data['resume_label'], height=300, placeholder="Paste resume here...")

with col_jd:
    st.subheader("📋 JOB POSTING")
    jd_text = st.text_area(text_data['jd_label'], height=300, placeholder="Paste job description here...")

# 5. The Decode Button
st.write("") # Spacer
decode_button = st.button(text_data['button'], use_container_width=True)

# 6. Logic and Results Display
if decode_button:
    if not resume_text or not jd_text:
        st.error("Please paste text into both boxes to decode.")
    else:
        # Process texts
        resume_tokens = get_tokens(resume_text)
        jd_tokens = get_tokens(jd_text)

        # Calculate Matches
        # Find words that are in JD but NOT in Resume
        missing_keywords = list(jd_tokens - resume_tokens)
        missing_keywords.sort()
        
        # Calculate Score based on how many unique JD words exist in the resume
        shared_keywords = jd_tokens.intersection(resume_tokens)
        
        if len(jd_tokens) > 0:
            match_score = int((len(shared_keywords) / len(jd_tokens)) * 100)
        else:
            match_score = 0

        # --- DISPLAY RESULTS ---
        st.markdown("---")
        st.header(text_data['results_title'])

        # Display Score Metric
        col_score, col_msg = st.columns([1,2])
        with col_score:
            st.metric(label=text_data['match_label'], value=f"{match_score}%")
        
        with col_msg:
            if match_score > 80:
                st.success("🌟 Great match! You are ready to apply.")
            elif match_score > 50:
                st.warning("⚠️ Good start. Add the missing keywords to improve your score.")
            else:
                st.error("🛑 Low match. You need to tailor your resume significantly for this job.")

        # Display Missing Keywords
        st.subheader(text_data['missing_title'])
        if missing_keywords:
            # Display as chips/tags using standard streamlit elements
            # We create a formatted string of tags
            tags_html = ""
            for word in missing_keywords:
                 tags_html += f"<span style='background-color: #f0f2f6; border: 1px solid #C41230; color: #C41230; padding: 5px 10px; margin: 3px; border-radius: 15px; display: inline-block;'>{word}</span>"
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
             st.balloons()
             st.success("Incredible! You aren't missing any significant keywords from this job description.")

# Footer
st.markdown("---")
st.caption("YMCA of Niagara Youth Employment Services. Shine On.")
