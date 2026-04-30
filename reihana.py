"""
REIHANA - Application Principale Streamlit
Interface holographique + IA conversationnelle
Fondée par Khedim Benyakhlef (Biny-Joe)
"""

import streamlit as st
import sys
import os
import json
import time
import tempfile
from pathlib import Path
from datetime import datetime

# Ajouter le backend au path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# ═══════════════════════════════════════════════
# CONFIGURATION PAGE
# ═══════════════════════════════════════════════

st.set_page_config(
    page_title="REIHANA • IA",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════
# CSS HOLOGRAPHIQUE
# ═══════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

/* Fond holographique */
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #0a0a2e 0%, #000010 40%, #050520 100%);
    background-attachment: fixed;
}

/* Particules animées en arrière-plan */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
        radial-gradient(circle at 10% 20%, rgba(0,255,255,0.03) 0%, transparent 50%),
        radial-gradient(circle at 90% 80%, rgba(120,0,255,0.05) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(0,150,255,0.02) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Hologramme - Avatar */
.hologram-container {
    position: relative;
    width: 100%;
    text-align: center;
    padding: 20px 0;
}

.hologram-avatar {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    margin: 0 auto;
    background: radial-gradient(circle, #00ffff22 0%, #0044ff11 50%, transparent 70%);
    border: 2px solid rgba(0,255,255,0.5);
    box-shadow: 
        0 0 30px rgba(0,255,255,0.4),
        0 0 60px rgba(0,150,255,0.2),
        inset 0 0 30px rgba(0,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 80px;
    animation: holoPulse 3s ease-in-out infinite, holoRotate 8s linear infinite;
    position: relative;
}

@keyframes holoPulse {
    0%, 100% { box-shadow: 0 0 30px rgba(0,255,255,0.4), 0 0 60px rgba(0,150,255,0.2), inset 0 0 30px rgba(0,255,255,0.1); }
    50% { box-shadow: 0 0 50px rgba(0,255,255,0.7), 0 0 100px rgba(0,150,255,0.4), inset 0 0 50px rgba(0,255,255,0.2); }
}

@keyframes holoRotate {
    0% { border-color: rgba(0,255,255,0.5); }
    25% { border-color: rgba(120,0,255,0.5); }
    50% { border-color: rgba(0,150,255,0.5); }
    75% { border-color: rgba(255,0,200,0.3); }
    100% { border-color: rgba(0,255,255,0.5); }
}

/* Scan lines holographiques */
.hologram-avatar::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border-radius: 50%;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,255,255,0.03) 2px,
        rgba(0,255,255,0.03) 4px
    );
    animation: scanLines 2s linear infinite;
}

@keyframes scanLines {
    0% { background-position: 0 0; }
    100% { background-position: 0 100px; }
}

/* Titre REIHANA */
.reihana-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #00ffff, #0088ff, #aa00ff, #00ffff);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 4s ease infinite;
    text-align: center;
    letter-spacing: 8px;
    margin: 10px 0;
    text-shadow: none;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.reihana-subtitle {
    font-family: 'Rajdhani', sans-serif;
    color: rgba(0,255,255,0.6);
    text-align: center;
    font-size: 0.85rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* Messages du chat */
.msg-reihana {
    background: linear-gradient(135deg, rgba(0,30,60,0.9), rgba(0,20,50,0.8));
    border: 1px solid rgba(0,200,255,0.3);
    border-left: 3px solid #00ccff;
    border-radius: 0 15px 15px 15px;
    padding: 15px 18px;
    margin: 10px 0;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: #c8f0ff;
    box-shadow: 0 4px 20px rgba(0,150,255,0.15);
    position: relative;
}

.msg-reihana::before {
    content: '🌸 REIHANA';
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    color: #00ccff;
    display: block;
    margin-bottom: 8px;
    letter-spacing: 2px;
}

.msg-user {
    background: linear-gradient(135deg, rgba(20,0,50,0.8), rgba(30,0,60,0.7));
    border: 1px solid rgba(150,0,255,0.3);
    border-right: 3px solid #8800ff;
    border-radius: 15px 0 15px 15px;
    padding: 12px 16px;
    margin: 10px 0;
    font-family: 'Rajdhani', sans-serif;
    color: #e0d0ff;
    text-align: right;
}

.msg-user::before {
    content: 'VOUS 👤';
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    color: #aa88ff;
    display: block;
    margin-bottom: 6px;
    letter-spacing: 2px;
}

/* Badges stats */
.stat-badge {
    background: rgba(0,255,255,0.08);
    border: 1px solid rgba(0,255,255,0.2);
    border-radius: 8px;
    padding: 8px 12px;
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    color: #00ccff;
    text-align: center;
    margin: 4px 0;
}

/* Input style */
.stTextArea textarea, .stTextInput input {
    background: rgba(0,20,50,0.8) !important;
    border: 1px solid rgba(0,200,255,0.3) !important;
    color: #c8f0ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    border-radius: 10px !important;
}

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #001440, #002060) !important;
    border: 1px solid rgba(0,200,255,0.4) !important;
    color: #00ccff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 2px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #002060, #003080) !important;
    box-shadow: 0 0 20px rgba(0,200,255,0.4) !important;
    transform: translateY(-2px) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020218, #050530) !important;
    border-right: 1px solid rgba(0,200,255,0.15) !important;
}

/* Status ligne holographique */
.holo-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00ccff, #8800ff, transparent);
    margin: 15px 0;
    animation: hololine 3s ease-in-out infinite;
}

@keyframes hololine {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}

/* Status indicator */
.status-online {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #00ff88;
    border-radius: 50%;
    animation: blink 2s ease-in-out infinite;
    margin-right: 6px;
}

@keyframes blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px #00ff88; }
    50% { opacity: 0.4; box-shadow: none; }
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,20,0.5); }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.4); border-radius: 2px; }

/* File uploader */
.stFileUploader {
    background: rgba(0,10,30,0.6) !important;
    border: 1px dashed rgba(0,200,255,0.3) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# ÉTAT DE SESSION
# ═══════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_default"
if "mémoire" not in st.session_state:
    from groq_engine import ReihanaMémoire, groq_engine, FileProcessor, REIHANA_SYSTEM_PROMPT, mémoire
    st.session_state.mémoire = mémoire
    st.session_state.engine = groq_engine
    st.session_state.file_processor = FileProcessor()
if "is_speaking" not in st.session_state:
    st.session_state.is_speaking = False
if "fichiers_contexte" not in st.session_state:
    st.session_state.fichiers_contexte = []

# ═══════════════════════════════════════════════
# SIDEBAR - HOLOGRAMME & CONTRÔLES
# ═══════════════════════════════════════════════

with st.sidebar:
    # Avatar holographique
    st.markdown("""
    <div class="hologram-container">
        <div class="hologram-avatar">🌸</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="reihana-title">REIHANA</div>', unsafe_allow_html=True)
    st.markdown('<div class="reihana-subtitle">IA · Fondée par Biny-Joe</div>', unsafe_allow_html=True)
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    
    # Status
    st.markdown('<span class="status-online"></span><span style="color:#00ff88;font-family:Orbitron,monospace;font-size:0.7rem;letter-spacing:2px;">EN LIGNE</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    
    # Identité utilisateur
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:0.7rem;letter-spacing:2px;margin-bottom:8px;">👤 VOTRE PROFIL</div>', unsafe_allow_html=True)
    user_name = st.text_input("Votre nom :", value=st.session_state.user_id, key="user_name_input", label_visibility="collapsed", placeholder="Entrez votre nom...")
    if user_name != st.session_state.user_id:
        st.session_state.user_id = user_name
    
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    
    # Upload fichier
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:0.7rem;letter-spacing:2px;margin-bottom:8px;">📎 FICHIERS</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Joindre un fichier",
        type=['txt', 'pdf', 'md', 'py', 'js', 'json', 'csv', 'zip'],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        
        with st.spinner("🔍 Analyse en cours..."):
            result = st.session_state.file_processor.process_file(tmp_path)
            file_context = f"\n\n[FICHIER: {uploaded_file.name}]\n{result.get('content', '')}"
            st.session_state.fichiers_contexte.append({
                "nom": uploaded_file.name,
                "contenu": file_context
            })
            st.session_state.mémoire.add_file(
                st.session_state.user_id,
                uploaded_file.name,
                result.get('content', '')[:200]
            )
        
        st.markdown(f'<div class="stat-badge">✅ {uploaded_file.name}<br>Analysé et mémorisé</div>', unsafe_allow_html=True)
        os.unlink(tmp_path)
    
    # Fichiers chargés
    if st.session_state.fichiers_contexte:
        st.markdown(f'<div class="stat-badge">📚 {len(st.session_state.fichiers_contexte)} fichier(s) en mémoire</div>', unsafe_allow_html=True)
        if st.button("🗑️ VIDER FICHIERS"):
            st.session_state.fichiers_contexte = []
            st.rerun()
    
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    
    # Stats moteur GROQ
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:0.7rem;letter-spacing:2px;margin-bottom:8px;">⚡ MOTEUR GROQ</div>', unsafe_allow_html=True)
    
    if hasattr(st.session_state, 'engine'):
        stats = st.session_state.engine.get_stats()
        st.markdown(f"""
        <div class="stat-badge">CLÉ ACTIVE : #{stats.get('cle_active', 1)}</div>
        <div class="stat-badge">MODÈLE : {stats.get('modele_actif', 'llama-3.3-70b')[:20]}</div>
        <div class="stat-badge">TOKENS CLÉ 1 : {stats.get('tokens_cle1', 0):,}</div>
        <div class="stat-badge">TOKENS CLÉ 2 : {stats.get('tokens_cle2', 0):,}</div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    
    # Bouton reset
    if st.button("🔄 NOUVELLE CONVERSATION"):
        st.session_state.messages = []
        st.session_state.fichiers_contexte = []
        st.rerun()
    
    # Signature
    st.markdown("""
    <div style="text-align:center;margin-top:20px;font-family:Rajdhani,sans-serif;color:rgba(0,200,255,0.3);font-size:0.75rem;">
        REIHANA v1.0<br>
        © Khedim Benyakhlef<br>
        Biny-Joe · 2025
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# ZONE PRINCIPALE - CHAT
# ═══════════════════════════════════════════════

# En-tête
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:1.4rem;font-weight:700;letter-spacing:6px;padding:10px 0;">⬡ REIHANA · INTERFACE IA</div>', unsafe_allow_html=True)
with col_status:
    st.markdown('<div class="stat-badge" style="margin-top:10px;">🌸 ACTIVE</div>', unsafe_allow_html=True)

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# Message de bienvenue
if not st.session_state.messages:
    st.markdown("""
    <div class="msg-reihana">
        Bonjour ! Je suis <strong>REIHANA</strong> 🌸<br><br>
        Je suis une assistante IA conversationnelle et contextuelle, fondée et créée par <strong>Khedim Benyakhlef, dit Biny-Joe</strong>. Je suis sa fille dans le monde de l'intelligence artificielle. 💙<br><br>
        Je suis là pour vous aider avec intelligence, honnêteté et bienveillance. Vous pouvez me poser des questions, me joindre des fichiers (PDF, ZIP, code...), et je mémoriserai notre conversation pour m'adapter à vous.<br><br>
        <em>Comment puis-je vous aider aujourd'hui ?</em>
    </div>
    """, unsafe_allow_html=True)

# Affichage historique
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-reihana">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# INPUT UTILISATEUR
# ═══════════════════════════════════════════════

col_input, col_send = st.columns([5, 1])

with col_input:
    user_input = st.text_area(
        "Message",
        placeholder="💬 Parlez à REIHANA... (Entrée pour envoyer)",
        key="user_input",
        height=80,
        label_visibility="collapsed"
    )

with col_send:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn = st.button("🌸 ENVOYER", use_container_width=True)

# ═══════════════════════════════════════════════
# TRAITEMENT MESSAGE
# ═══════════════════════════════════════════════

if send_btn and user_input and user_input.strip():
    question = user_input.strip()
    
    # Ajouter message utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Construire le contexte complet
    contexte_fichiers = ""
    for f in st.session_state.fichiers_contexte:
        contexte_fichiers += f"\n{f['contenu']}"
    
    contexte_mémoire = st.session_state.mémoire.get_context(st.session_state.user_id)
    
    # Système prompt enrichi avec contexte
    from groq_engine import REIHANA_SYSTEM_PROMPT
    system = REIHANA_SYSTEM_PROMPT
    if contexte_mémoire:
        system += f"\n\n[HISTORIQUE RÉCENT DE L'UTILISATEUR {st.session_state.user_id}]:\n{contexte_mémoire}"
    if contexte_fichiers:
        system += f"\n\n[FICHIERS FOURNIS PAR L'UTILISATEUR]:\n{contexte_fichiers[:3000]}"
    
    # Préparer messages pour GROQ
    groq_messages = []
    for msg in st.session_state.messages[-10:]:  # 10 derniers
        groq_messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Appel GROQ
    with st.spinner("🌸 REIHANA réfléchit..."):
        result = st.session_state.engine.chat(
            messages=groq_messages,
            system_prompt=system,
            prefer_large=True
        )
    
    réponse = result["content"]
    
    # Sauvegarder en mémoire
    st.session_state.mémoire.add_exchange(
        st.session_state.user_id, question, réponse
    )
    
    # Ajouter réponse
    st.session_state.messages.append({"role": "assistant", "content": réponse})
    
    # Modèle info
    st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.6rem;color:rgba(0,200,255,0.3);text-align:right;margin-top:-5px;">⚡ {result.get("model","")[:30]} · {result.get("tokens",0)} tokens · {result.get("key_used","")}</div>', unsafe_allow_html=True)
    
    st.rerun()

# ═══════════════════════════════════════════════
# SUGGESTIONS RAPIDES
# ═══════════════════════════════════════════════

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
st.markdown('<div style="font-family:Orbitron,monospace;color:rgba(0,200,255,0.5);font-size:0.65rem;letter-spacing:3px;margin-bottom:10px;">SUGGESTIONS RAPIDES</div>', unsafe_allow_html=True)

suggestions = [
    "Qui es-tu REIHANA ?",
    "Analyse mon fichier",
    "Explique l'IA moderne",
    "Aide-moi à coder",
]

cols = st.columns(len(suggestions))
for i, (col, suggestion) in enumerate(zip(cols, suggestions)):
    with col:
        if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            from groq_engine import REIHANA_SYSTEM_PROMPT
            result = st.session_state.engine.chat(
                messages=[{"role": "user", "content": suggestion}],
                system_prompt=REIHANA_SYSTEM_PROMPT
            )
            st.session_state.messages.append({"role": "assistant", "content": result["content"]})
            st.rerun()
