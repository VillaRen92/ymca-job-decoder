import streamlit as st
import re
from collections import Counter
from pypdf import PdfReader
from docx import Document

# --- CONFIGURATION & BRANDING ---
st.set_page_config(
    page_title="YMCA Job Decoder",
    page_icon="🔴",
    layout="centered"
)

# Custom CSS to enforce YMCA Red and White theme
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
        background-color: #A00F28;
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
CONTENT = {
    "English": {
        "instructions": "Instructions: Upload your resume on the left and paste the job posting on the right.",
        "translit": "(Instructions: Upload your resume on the left and paste the job posting on the right.)",
        "resume_label": "Your Resume",
        "jd_label": "Job Description text",
        "button": "DECODE MY RESUME",
        "results_title": "Your Results",
        "missing_title": "Missing Keywords (Add these to your resume!)",
        "match_label": "Match Score",
        "upload_label": "Upload PDF or Word Doc",
        "paste_label": "Paste Text"
    },
    "Español (Spanish)": {
        "instructions": "Instrucciones: Suba su currículum a la izquierda y pegue la oferta de trabajo a la derecha.",
        "translit": "(Instrucciones: Su-ba su cu-rri-cu-lum a la iz-kier-da y pe-ge la o-fer-ta de tra-ba-jo a la de-re-cha.)",
        "resume_label": "Su currículum",
        "jd_label": "Texto de la descripción del trabajo",
        "button": "DECODIFICAR MI CURRÍCULUM",
        "results_title": "Sus Resultados",
        "missing_title": "Palabras clave faltantes (¡Agréguelas a su currículum!)",
        "match_label": "Puntuación de coincidencia",
        "upload_label": "Subir PDF o Word",
        "paste_label": "Pegar texto"
    },
    "العربية (Arabic)": {
        "instructions": "التعليمات: حمل سيرتك الذاتية على اليسار والصق إعلان الوظيفة على اليمين.",
        "translit": "(Al-ta'leemat: Hammil seeratak al-thatia ala al-yassar wa i'lan al-wazifa ala al-yameen.)",
        "resume_label": "سيرتك الذاتية",
        "jd_label": "نص الوصف الوظيفي",
        "button": "فك شفرة سيرتي الذاتية",
        "results_title": "نتائجك",
        "missing_title": "كلمات مفتاحية مفقودة (أضفها إلى سيرتك الذاتية!)",
        "match_label": "درجة التطابق",
        "upload_label": "تحميل PDF أو Word",
        "paste_label": "لصق النص"
    },
     "Українська (Ukrainian)": {
        "instructions": "Інструкції: Завантажте своє резюме ліворуч, а опис вакансії вставте праворуч.",
        "translit": "(Instruktsiyi: Zavantazhte svoye rezyume livoruch, a opys vakansiyi vstavte pravoruch.)",
        "resume_label": "Ваше резюме",
        "jd_label": "Текст опису вакансії",
        "button": "РОЗШИФРУВАТИ МОЄ РЕЗЮМЕ",
        "results_title": "Ваші результати",
        "missing_title": "Відсутні ключові слова (Додайте їх до свого резюме!)",
        "match_label": "Оцінка відповідності",
        "upload_label": "Завантажити PDF або Word",
        "paste_label": "Вставити текст"
    },
    "简体中文 (Simplified Chinese)": {
        "instructions": "说明：在左侧上传您的简历，在右侧粘贴职位描述。",
        "translit": "(Shuōmíng: Zài zuǒcè shàngchuán nín de jiǎnlì, zài yòucè zhāntiē zhíwèi miáoshù.)",
        "resume_label": "您的简历",
        "jd_label": "职位描述文本",
        "button": "解码我的简历",
        "results_title": "您的结果",
        "missing_title": "缺失的关键词 (将这些添加到您的简历中！)",
        "match_label": "匹配得分",
        "upload_label": "上传 PDF 或 Word",
        "paste_label": "粘贴文本"
    }
}


# --- HELPER FUNCTIONS ---
def clean_text(text):
    """Cleans text by lowercasing and removing non-alphanumeric characters."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text

def get_tokens(text):
    """Splits text into individual words (tokens)."""
    cleaned = clean_text(text)
    tokens = cleaned.split()
    return set([t for t in tokens if len(t) > 2])

def extract_text_from_pdf(file):
    try:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading Docx: {e}"

# --- MAIN APP LAYOUT ---

# 1. Header and Logo
col1, col2, col3 = st.columns([1,2,1])
with col2:
    try:
        st.image("image_0.png", use_column_width=True)
    except FileNotFoundError:
        st.error("Logo not found.")

st.markdown("<h1 style='text-align: center;'>Job Description Decoder</h1>", unsafe_allow_html=True)
st.markdown("---")

# 2. Language Selection
lang_options = list(CONTENT.keys())
selected_lang = st.selectbox("🌐 Select Language / Seleccione el idioma / اختر اللغة", lang_options)
text_data = CONTENT[selected_lang]

# 3. Instructions
st.info(f"**{text_data['instructions']}**")
st.markdown(f"<div class='translit'>{text_data['translit']}</div>", unsafe_allow_html=True)

# 4. Input Areas
col_res, col_jd = st.columns(2)

resume_text = ""

with col_res:
    st.subheader(f"👤 {text_data['resume_label']}")
    # Toggle for Upload vs Paste
    input_method = st.radio("Input Method", [text_data['upload_label'], text_data['paste_label']], label_visibility="collapsed")
    
    if input_method == text_data['paste_label']:
        resume_text = st.text_area("Paste here", height=250, placeholder="Paste text...", label_visibility="collapsed")
    else:
        uploaded_file = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                with st.spinner('Reading PDF...'):
                    resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                with st.spinner('Reading Word Doc...'):
                    resume_text = extract_text_from_docx(uploaded_file)
            
            if resume_text:
                st.success("File loaded!")
            else:
                st.error("Could not extract text. Try pasting it instead.")

with col_jd:
    st.subheader(f"📋 {text_data['jd_label']}")
    # Spacer to align with the radio button offset on the left
    st.write("") 
    st.write("") 
    st.write("") 
    jd_text = st.text_area("Paste JD here", height=250, placeholder="Paste job description...", label_visibility="collapsed")

# 5. Decode Button
st.write("") 
decode_button = st.button(text_data['button'], use_container_width=True)

# 6. Logic and Results
if decode_button:
    if not resume_text or not jd_text:
        st.error("Please provide both a resume and a job description.")
    else:
        resume_tokens = get_tokens(resume_text)
        jd_tokens = get_tokens(jd_text)

        missing_keywords = list(jd_tokens - resume_tokens)
        missing_keywords.sort()
        
        shared_keywords = jd_tokens.intersection(resume_tokens)
        
        if len(jd_tokens) > 0:
            match_score = int((len(shared_keywords) / len(jd_tokens)) * 100)
        else:
            match_score = 0

        st.markdown("---")
        st.header(text_data['results_title'])

        col_score, col_msg = st.columns([1,2])
        with col_score:
            st.metric(label=text_data['match_label'], value=f"{match_score}%")
        
        with col_msg:
            if match_score > 80:
                st.success("🌟 Great match! You are ready to apply.")
            elif match_score > 50:
                st.warning("⚠️ Good start. Add the missing keywords to improve your score.")
            else:
                st.error("🛑 Low match. You need to tailor your resume significantly.")

        st.subheader(text_data['missing_title'])
        if missing_keywords:
            tags_html = ""
            for word in missing_keywords:
                 tags_html += f"<span style='background-color: #f0f2f6; border: 1px solid #C41230; color: #C41230; padding: 5px 10px; margin: 3px; border-radius: 15px; display: inline-block;'>{word}</span>"
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
             st.balloons()
             st.success("Incredible! You aren't missing any significant keywords.")

st.markdown("---")
st.caption("YMCA of Niagara Youth Employment Services. Shine On.")
