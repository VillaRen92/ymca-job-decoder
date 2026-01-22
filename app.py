import streamlit as st
import re
from collections import Counter
from pypdf import PdfReader
from docx import Document

# --- CONFIGURATION & BRANDING ---
st.set_page_config(
    page_title="YMCA Job Decoder",
    page_icon="🔴",
    layout="wide",  # Changed to wide for a dashboard feel
    initial_sidebar_state="collapsed"
)

# --- CSS HACKS: HIDE MENU & BEAUTIFY ---
st.markdown(
    """
    <style>
    /* HIDE STREAMLIT MENU & FOOTER */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Background to White */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    
    /* Headings in YMCA Red */
    h1, h2, h3, h4, span[data-testid="stMetricLabel"] {
        color: #C41230 !important;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Custom Button Styling */
    div.stButton > button {
        background-color: #C41230;
        color: white;
        border: none;
        font-weight: bold;
        font-size: 18px;
        padding: 15px 30px;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #A00F28;
        transform: translateY(-2px);
        box-shadow: 0px 6px 8px rgba(0,0,0,0.2);
    }

    /* Input Field Styling */
    .stTextArea textarea {
        border: 2px solid #eee;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #C41230;
        box-shadow: 0 0 0 1px #C41230;
    }

    /* Success/Warning Boxes */
    div[data-baseweb="notification"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MULTI-LANGUAGE CONTENT ---
CONTENT = {
    "English": {
        "title": "ATS Job Decoder",
        "subtitle": "Beat the bots. Get hired.",
        "instructions": "1. Upload your resume.\n2. Paste the job description.\n3. Add 'Power Keywords' you really want to highlight.",
        "resume_col": "Your Resume",
        "jd_col": "Job Description",
        "power_col": "Power Keywords (Optional)",
        "power_desc": "Enter specific high-value skills (comma separated) you want to ensure are found (e.g., 'Python, Bilingual, First Aid').",
        "button": "ANALYZE MATCH",
        "match_score": "ATS Match Score",
        "missing_header": "⚠️ Critical Missing Keywords",
        "power_hit": "✅ Power Keyword Found:",
        "power_miss": "❌ Power Keyword Missing:",
        "advice_high": "Excellent! Your resume speaks the same language as this job post.",
        "advice_mid": "Good start. Add the missing keywords below to boost your chances.",
        "advice_low": "Risk of rejection. The ATS might filter you out. Rewrite using the keywords below."
    },
    "Español (Spanish)": {
        "title": "Decodificador de Empleo",
        "subtitle": "Vence a los bots. Consigue el trabajo.",
        "instructions": "1. Sube tu CV.\n2. Pega la oferta de trabajo.\n3. Añade 'Palabras Clave' importantes.",
        "resume_col": "Tu Currículum",
        "jd_col": "Descripción del Trabajo",
        "power_col": "Palabras Clave (Opcional)",
        "power_desc": "Ingresa habilidades específicas (separadas por comas) que quieres asegurar (ej. 'Español, Licencia, Ventas').",
        "button": "ANALIZAR COINCIDENCIA",
        "match_score": "Puntuación de Coincidencia",
        "missing_header": "⚠️ Palabras Clave Faltantes",
        "power_hit": "✅ Palabra Clave Encontrada:",
        "power_miss": "❌ Palabra Clave Faltante:",
        "advice_high": "¡Excelente! Tu currículum habla el mismo idioma que esta oferta.",
        "advice_mid": "Buen comienzo. Añade las palabras faltantes para mejorar.",
        "advice_low": "Riesgo de rechazo. El sistema podría filtrarte. Reescribe usando las palabras abajo."
    },
     "العربية (Arabic)": {
        "title": "فك شفرة الوظائف",
        "subtitle": "تغلب على الروبوتات. احصل على الوظيفة.",
        "instructions": "1. حمل سيرتك الذاتية.\n2. الصق وصف الوظيفة.\n3. أضف 'كلمات مفتاحية' مهمة.",
        "resume_col": "سيرتك الذاتية",
        "jd_col": "وصف الوظيفة",
        "power_col": "كلمات مفتاحية قوية (اختياري)",
        "power_desc": "أدخل مهارات محددة (مفصولة بفواصل) تريد التأكد من وجودها.",
        "button": "تحليل التطابق",
        "match_score": "درجة التطابق",
        "missing_header": "⚠️ كلمات مفتاحية مفقودة",
        "power_hit": "✅ كلمة موجودة:",
        "power_miss": "❌ كلمة مفقودة:",
        "advice_high": "ممتاز! سيرتك الذاتية تتحدث نفس لغة هذا الإعلان.",
        "advice_mid": "بداية جيدة. أضف الكلمات المفقودة أدناه لتحسين فرصك.",
        "advice_low": "خطر الرفض. قد يقوم النظام بتصفيته. أعد الكتابة باستخدام الكلمات أدناه."
    },
     "简体中文 (Simplified Chinese)": {
        "title": "职位解码器",
        "subtitle": "战胜机器筛选，获得录用。",
        "instructions": "1. 上传简历。\n2. 粘贴职位描述。\n3. 添加关键“强力词”。",
        "resume_col": "您的简历",
        "jd_col": "职位描述",
        "power_col": "强力关键词 (可选)",
        "power_desc": "输入您希望确保被发现的特定高价值技能（用逗号分隔）。",
        "button": "分析匹配度",
        "match_score": "ATS 匹配得分",
        "missing_header": "⚠️ 缺失的关键关键词",
        "power_hit": "✅ 关键词已找到:",
        "power_miss": "❌ 关键词缺失:",
        "advice_high": "太棒了！您的简历与该职位非常匹配。",
        "advice_mid": "良好的开端。添加下面的缺失关键词以提高分数。",
        "advice_low": "被拒绝的风险。系统可能会过滤掉您。请使用下面的关键词重写。"
    }
}

# --- HELPER FUNCTIONS ---
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text

def get_tokens(text):
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
    except Exception:
        return ""

def extract_text_from_docx(file):
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return ""

# --- MAIN APP UI ---

# HEADER
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("image_0.png", width=120)
    except FileNotFoundError:
        st.write("🔴")
with col_title:
    # Default to English for initial load
    lang_select = st.selectbox("Language / Idioma / اللغة / 语言", list(CONTENT.keys()), label_visibility="collapsed")
    txt = CONTENT[lang_select]
    st.markdown(f"# {txt['title']}")
    st.markdown(f"**{txt['subtitle']}**")

st.write("---")

# INPUT SECTION
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📄 {txt['resume_col']}")
    upload_tab, paste_tab = st.tabs(["📁 Upload", "✍️ Paste"])
    
    resume_text = ""
    with upload_tab:
        uploaded_file = st.file_uploader("Upload Resume", type=['pdf', 'docx'], label_visibility="collapsed")
        if uploaded_file:
            if uploaded_file.name.endswith('.pdf'):
                resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                resume_text = extract_text_from_docx(uploaded_file)
            
            if resume_text:
                st.success("✅ File Loaded")
            else:
                st.error("❌ Error reading file")

    with paste_tab:
        pasted_resume = st.text_area("Paste Resume", height=200, label_visibility="collapsed")
        if not resume_text: # Prefer upload if both exist
            resume_text = pasted_resume

with col2:
    st.subheader(f"📋 {txt['jd_col']}")
    jd_text = st.text_area("Paste JD", height=250, label_visibility="collapsed", placeholder="Paste the full job description here...")

# POWER KEYWORDS SECTION
st.markdown("### 🚀 " + txt['power_col'])
power_input = st.text_input(txt['power_desc'], placeholder="e.g. Python, Leadership, CPR")

# ACTION BUTTON
st.write("")
analyze_btn = st.button(txt['button'], use_container_width=True)

# ANALYSIS LOGIC
if analyze_btn:
    if not resume_text or not jd_text:
        st.error("Please provide both a resume and a job description.")
    else:
        # 1. Standard Token Matching
        resume_tokens = get_tokens(resume_text)
        jd_tokens = get_tokens(jd_text)
        
        common_words = {"the", "and", "for", "that", "this", "with", "you", "are", "work", "will", "can", "team", "skills", "experience", "job", "role"}
        filtered_jd_tokens = jd_tokens - common_words
        
        shared = filtered_jd_tokens.intersection(resume_tokens)
        missing = list(filtered_jd_tokens - resume_tokens)
        
        # Calculate Score
        if len(filtered_jd_tokens) > 0:
            score = int((len(shared) / len(filtered_jd_tokens)) * 100)
        else:
            score = 0
            
        # 2. Power Keyword Matching
        power_results = []
        if power_input:
            power_words = [p.strip() for p in power_input.split(",") if p.strip()]
            for pw in power_words:
                # Simple case-insensitive substring search
                if pw.lower() in resume_text.lower():
                    power_results.append((True, pw))
                else:
                    power_results.append((False, pw))

        # --- DISPLAY RESULTS DASHBOARD ---
        st.markdown("---")
        
        # Score Card
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(f"<h2 style='text-align: center;'>{txt['match_score']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin: -20px 0;'>{score}%</h1>", unsafe_allow_html=True)
            
            if score > 80:
                st.success(txt['advice_high'])
            elif score > 50:
                st.warning(txt['advice_mid'])
            else:
                st.error(txt['advice_low'])

        # Power Keywords Check
        if power_results:
            st.markdown("#### Power Keyword Check")
            p_cols = st.columns(len(power_results))
            for idx, (found, word) in enumerate(power_results):
                with p_cols[idx % 3]: # Wrap columns if many
                    if found:
                        st.markdown(f"<div style='padding:10px; background:#e6fffa; border:1px solid #38b2ac; border-radius:5px; color:#2c7a7b'><b>✓ {word}</b></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding:10px; background:#fff5f5; border:1px solid #fc8181; border-radius:5px; color:#c53030'><b>✕ {word}</b></div>", unsafe_allow_html=True)
            st.write("")

        # Missing Keywords Tags
        st.subheader(txt['missing_header'])
        if missing:
            # Sort missing by length (simple heuristic for complexity) or alpha
            missing.sort()
            
            # Display visually as "chips"
            html_tags = ""
            for word in missing[:40]: # Limit to top 40 to avoid wall of text
                html_tags += f"""
                <span style='
                    display: inline-block;
                    background-color: #f1f3f5;
                    color: #495057;
                    padding: 5px 12px;
                    margin: 4px;
                    border-radius: 20px;
                    font-weight: 500;
                    border: 1px solid #dee2e6;
                '>{word}</span>
                """
            st.markdown(html_tags, unsafe_allow_html=True)
            if len(missing) > 40:
                st.caption(f"...and {len(missing)-40} more generic terms.")
        else:
             st.balloons()
             st.success("Perfect Match!")

# FOOTER
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>YMCA of Niagara • Youth Employment Services • Shine On</div>", unsafe_allow_html=True)
