"""
REIHANA - Application Principale Streamlit v2.0
Interface holographique + IA conversationnelle
Fondée par Khedim Benyakhlef (Biny-Joe)

NOUVEAUTÉS v2.0 :
  ✅ Champ de texte qui se vide après envoi
  ✅ Voix de jeune fille (Web Speech API - voix fr-FR)
  ✅ Hologramme animé bouche qui bouge pendant la parole
  ✅ Boutons ❤️ J'aime / 📋 Copier / 🔄 Régénérer sous chaque réponse
  ✅ Recherche web (DuckDuckGo gratuit)
  ✅ Mode Deep Think (réflexion longue)
"""

import streamlit as st
import sys
import os
import json
import time
import tempfile
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

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

/* ── HOLOGRAMME AVEC BOUCHE ── */
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
    flex-direction: column;
    cursor: pointer;
}

/* Visage SVG dans l'avatar */
.holo-face {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.holo-eyes {
    display: flex;
    gap: 18px;
    margin-top: 10px;
}

.holo-eye {
    width: 10px;
    height: 10px;
    background: #00ffff;
    border-radius: 50%;
    box-shadow: 0 0 6px #00ffff;
    animation: eyeBlink 4s ease-in-out infinite;
}

@keyframes eyeBlink {
    0%, 90%, 100% { transform: scaleY(1); }
    95% { transform: scaleY(0.1); }
}

/* BOUCHE HOLOGRAMME */
.holo-mouth {
    width: 30px;
    height: 10px;
    background: transparent;
    border: 2px solid #00ffff;
    border-top: none;
    border-radius: 0 0 20px 20px;
    margin-top: 8px;
    transition: all 0.1s ease;
    box-shadow: 0 0 8px rgba(0,255,255,0.6);
}

.holo-mouth.talking {
    animation: mouthTalk 0.25s ease-in-out infinite alternate;
}

@keyframes mouthTalk {
    0%  { height: 4px;  border-radius: 0 0 6px 6px; }
    25% { height: 14px; border-radius: 0 0 20px 20px; }
    50% { height: 7px;  border-radius: 0 0 10px 10px; }
    75% { height: 16px; border-radius: 0 0 25px 25px; }
    100%{ height: 5px;  border-radius: 0 0 8px 8px; }
}

/* Scan lines */
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
    pointer-events: none;
}

@keyframes holoPulse {
    0%, 100% { box-shadow: 0 0 30px rgba(0,255,255,0.4), 0 0 60px rgba(0,150,255,0.2), inset 0 0 30px rgba(0,255,255,0.1); }
    50%       { box-shadow: 0 0 50px rgba(0,255,255,0.7), 0 0 100px rgba(0,150,255,0.4), inset 0 0 50px rgba(0,255,255,0.2); }
}

@keyframes holoRotate {
    0%   { border-color: rgba(0,255,255,0.5); }
    25%  { border-color: rgba(120,0,255,0.5); }
    50%  { border-color: rgba(0,150,255,0.5); }
    75%  { border-color: rgba(255,0,200,0.3); }
    100% { border-color: rgba(0,255,255,0.5); }
}

@keyframes scanLines {
    0%   { background-position: 0 0; }
    100% { background-position: 0 100px; }
}

/* Indicateur "parle" sous l'avatar */
.speaking-indicator {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 3px;
    height: 20px;
    margin-top: 6px;
    opacity: 0;
    transition: opacity 0.3s;
}
.speaking-indicator.active { opacity: 1; }
.speaking-indicator span {
    width: 3px;
    background: #00ffff;
    border-radius: 2px;
    animation: wave 0.8s ease-in-out infinite;
}
.speaking-indicator span:nth-child(2) { animation-delay: 0.1s; }
.speaking-indicator span:nth-child(3) { animation-delay: 0.2s; }
.speaking-indicator span:nth-child(4) { animation-delay: 0.3s; }
.speaking-indicator span:nth-child(5) { animation-delay: 0.4s; }

@keyframes wave {
    0%, 100% { height: 4px; }
    50%       { height: 16px; }
}

/* ── TITRES ── */
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
}

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
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

/* ── MESSAGES ── */
.msg-reihana {
    background: linear-gradient(135deg, rgba(0,30,60,0.9), rgba(0,20,50,0.8));
    border: 1px solid rgba(0,200,255,0.3);
    border-left: 3px solid #00ccff;
    border-radius: 0 15px 15px 15px;
    padding: 15px 18px;
    margin: 10px 0 4px 0;
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

/* ── BOUTONS ACTION RÉPONSE ── */
.action-bar {
    display: flex;
    gap: 8px;
    margin: 0 0 14px 4px;
    flex-wrap: wrap;
}

.action-btn {
    background: rgba(0,200,255,0.07);
    border: 1px solid rgba(0,200,255,0.2);
    color: rgba(0,200,255,0.7);
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.78rem;
    padding: 4px 10px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    letter-spacing: 1px;
    text-decoration: none;
}
.action-btn:hover {
    background: rgba(0,200,255,0.15);
    border-color: rgba(0,200,255,0.5);
    color: #00ccff;
    box-shadow: 0 0 10px rgba(0,200,255,0.2);
}
.action-btn.liked {
    background: rgba(255,80,120,0.15);
    border-color: rgba(255,80,120,0.4);
    color: #ff5078;
}

/* ── MODE DEEP THINK ── */
.deep-think-badge {
    background: linear-gradient(135deg, rgba(120,0,255,0.15), rgba(80,0,200,0.1));
    border: 1px solid rgba(150,0,255,0.3);
    border-radius: 6px;
    padding: 4px 10px;
    font-family: 'Orbitron', monospace;
    font-size: 0.62rem;
    color: #aa88ff;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 8px;
}

.web-search-badge {
    background: linear-gradient(135deg, rgba(0,180,100,0.15), rgba(0,120,60,0.1));
    border: 1px solid rgba(0,200,120,0.3);
    border-radius: 6px;
    padding: 4px 10px;
    font-family: 'Orbitron', monospace;
    font-size: 0.62rem;
    color: #00cc88;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 8px;
}

/* ── DIVERS ── */
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

.stTextArea textarea, .stTextInput input {
    background: rgba(0,20,50,0.8) !important;
    border: 1px solid rgba(0,200,255,0.3) !important;
    color: #c8f0ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    border-radius: 10px !important;
}

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

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020218, #050530) !important;
    border-right: 1px solid rgba(0,200,255,0.15) !important;
}

.holo-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00ccff, #8800ff, transparent);
    margin: 15px 0;
    animation: hololine 3s ease-in-out infinite;
}
@keyframes hololine {
    0%, 100% { opacity: 0.4; }
    50%       { opacity: 1; }
}

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
    50%       { opacity: 0.4; box-shadow: none; }
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,20,0.5); }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.4); border-radius: 2px; }

.stFileUploader {
    background: rgba(0,10,30,0.6) !important;
    border: 1px dashed rgba(0,200,255,0.3) !important;
    border-radius: 10px !important;
}

/* Checkbox style */
.stCheckbox label { color: #00ccff !important; font-family: 'Rajdhani', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# JAVASCRIPT : TTS voix jeune fille + bouche
# ═══════════════════════════════════════════════

st.markdown("""
<script>
// ── Variables globales ──
window._reihanaUtterance = null;
window._reihanaVoiceReady = false;

// Charger les voix
function loadVoices() {
    return new Promise(resolve => {
        let voices = speechSynthesis.getVoices();
        if (voices.length > 0) { resolve(voices); return; }
        speechSynthesis.addEventListener('voiceschanged', () => resolve(speechSynthesis.getVoices()), { once: true });
    });
}

// Trouver la meilleure voix jeune fille française
async function getBestGirlVoice() {
    const voices = await loadVoices();
    const preferred = [
        'Google français', 'Microsoft Julie', 'Microsoft Hortense',
        'Amelie', 'Thomas', 'fr-FR-DeniseNeural', 'fr-FR-EloiseNeural'
    ];
    // Essayer voix préférées
    for (let name of preferred) {
        let v = voices.find(v => v.name.includes(name) && v.lang.startsWith('fr'));
        if (v) return v;
    }
    // Fallback : première voix fr-FR
    let frVoice = voices.find(v => v.lang === 'fr-FR');
    if (frVoice) return frVoice;
    // Fallback final : n'importe quelle voix fr
    return voices.find(v => v.lang.startsWith('fr')) || voices[0];
}

// Mettre la bouche en mode "parle"
function setMouthTalking(talking) {
    const mouth = document.getElementById('holo-mouth');
    const indicator = document.getElementById('speaking-indicator');
    if (mouth) mouth.className = talking ? 'holo-mouth talking' : 'holo-mouth';
    if (indicator) indicator.className = talking ? 'speaking-indicator active' : 'speaking-indicator';
}

// Parler
window.reihanaSay = async function(text, btn) {
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        setMouthTalking(false);
        if (btn) btn.textContent = '🔊 Écouter';
        return;
    }
    const voice = await getBestGirlVoice();
    const utter = new SpeechSynthesisUtterance(text);
    utter.voice = voice;
    utter.lang = 'fr-FR';
    utter.rate = 1.05;   // légèrement plus rapide = son jeune
    utter.pitch = 1.6;   // hauteur : plus élevé = voix fille
    utter.volume = 1;

    utter.onstart = () => {
        setMouthTalking(true);
        if (btn) btn.textContent = '⏹ Arrêter';
    };
    utter.onend = utter.onerror = () => {
        setMouthTalking(false);
        if (btn) btn.textContent = '🔊 Écouter';
    };

    window._reihanaUtterance = utter;
    speechSynthesis.speak(utter);
};

// Copier texte
window.reihanaCopy = function(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const orig = btn.textContent;
        btn.textContent = '✅ Copié !';
        setTimeout(() => btn.textContent = orig, 1500);
    });
};

// J'aime
window.reihanaLike = function(btn) {
    btn.classList.toggle('liked');
    btn.textContent = btn.classList.contains('liked') ? '❤️ Aimé' : '❤️ J\'aime';
};
</script>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════

def search_web_duckduckgo(query: str, max_results: int = 3) -> str:
    """Recherche DuckDuckGo (API gratuite, sans clé)."""
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        resp = requests.get(url, timeout=8, headers={"User-Agent": "REIHANA-IA/2.0"})
        data = resp.json()
        results = []
        # Abstract principal
        if data.get("AbstractText"):
            results.append(f"📌 {data['AbstractText']}")
        # RelatedTopics
        for t in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(t, dict) and t.get("Text"):
                results.append(f"• {t['Text'][:200]}")
        if results:
            return "\n".join(results)
        return "Aucun résultat trouvé."
    except Exception as e:
        return f"Erreur recherche web : {e}"


def render_message_with_actions(content: str, msg_idx: int, is_deep: bool = False, web_info: str = ""):
    """Affiche un message REIHANA + barre d'actions interactive."""
    badge = ""
    if is_deep:
        badge = '<div class="deep-think-badge">🧠 DEEP THINK MODE</div>'
    if web_info:
        badge += '<div class="web-search-badge">🌐 RECHERCHE WEB INCLUSE</div>'

    # Échapper pour JS (guillemets simples)
    js_content = content.replace("\\", "\\\\").replace("`", "\\`").replace("'", "\\'")

    st.markdown(f"""
    <div class="msg-reihana">
        {badge}
        {content}
    </div>
    <div class="action-bar">
        <button class="action-btn" onclick="reihanaLike(this)">❤️ J'aime</button>
        <button class="action-btn" onclick="reihanaCopy('{js_content}', this)">📋 Copier</button>
        <button class="action-btn" onclick="reihanaSay('{js_content}', this)">🔊 Écouter</button>
    </div>
    """, unsafe_allow_html=True)

    # Bouton Régénérer (côté Streamlit, car besoin d'appel GROQ)
    if st.button("🔄 Régénérer", key=f"regen_{msg_idx}_{int(time.time()*100) % 10000}"):
        st.session_state.regen_idx = msg_idx
        st.rerun()


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
if "input_value" not in st.session_state:
    st.session_state.input_value = ""
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False
if "deep_think" not in st.session_state:
    st.session_state.deep_think = False
if "web_search_on" not in st.session_state:
    st.session_state.web_search_on = False
if "regen_idx" not in st.session_state:
    st.session_state.regen_idx = None
if "msg_meta" not in st.session_state:
    # dict idx -> {is_deep, web_info}
    st.session_state.msg_meta = {}

# ── GÉRER RÉGÉNÉRATION ──
if st.session_state.regen_idx is not None:
    idx = st.session_state.regen_idx
    st.session_state.regen_idx = None
    # Trouver le message utilisateur précédent
    if idx > 0 and st.session_state.messages[idx - 1]["role"] == "user":
        question = st.session_state.messages[idx - 1]["content"]
        from groq_engine import REIHANA_SYSTEM_PROMPT
        system = REIHANA_SYSTEM_PROMPT
        contexte_mémoire = st.session_state.mémoire.get_context(st.session_state.user_id)
        if contexte_mémoire:
            system += f"\n\n[HISTORIQUE]:\n{contexte_mémoire}"
        system += "\n\n[INSTRUCTION RÉGÉNÉRATION : génère une réponse différente et plus créative]"
        groq_messages = [{"role": "user", "content": question}]
        with st.spinner("🔄 REIHANA régénère..."):
            result = st.session_state.engine.chat(
                messages=groq_messages,
                system_prompt=system,
                prefer_large=True
            )
        st.session_state.messages[idx]["content"] = result["content"]
        st.rerun()

# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════

with st.sidebar:
    # Avatar holographique avec visage animé
    st.markdown("""
    <div class="hologram-container">
        <div class="hologram-avatar" onclick="reihanaSay('Bonjour ! Je suis Reihana, ton assistante IA !')">
            <div class="holo-face">
                <div class="holo-eyes">
                    <div class="holo-eye"></div>
                    <div class="holo-eye"></div>
                </div>
                <div class="holo-mouth" id="holo-mouth"></div>
            </div>
        </div>
        <div class="speaking-indicator" id="speaking-indicator">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="reihana-title">REIHANA</div>', unsafe_allow_html=True)
    st.markdown('<div class="reihana-subtitle">IA · Fondée par Biny-Joe</div>', unsafe_allow_html=True)
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Status
    st.markdown('<span class="status-online"></span><span style="color:#00ff88;font-family:Orbitron,monospace;font-size:0.7rem;letter-spacing:2px;">EN LIGNE</span>', unsafe_allow_html=True)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Profil utilisateur
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:0.7rem;letter-spacing:2px;margin-bottom:8px;">👤 VOTRE PROFIL</div>', unsafe_allow_html=True)
    user_name = st.text_input("Votre nom :", value=st.session_state.user_id, key="user_name_input",
                               label_visibility="collapsed", placeholder="Entrez votre nom...")
    if user_name != st.session_state.user_id:
        st.session_state.user_id = user_name

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # ── MODES SPÉCIAUX ──
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:0.7rem;letter-spacing:2px;margin-bottom:8px;">⚙️ MODES</div>', unsafe_allow_html=True)

    deep_think = st.checkbox("🧠 Deep Think (réflexion longue)", value=st.session_state.deep_think)
    st.session_state.deep_think = deep_think
    if deep_think:
        st.markdown('<div style="font-family:Rajdhani;color:rgba(170,136,255,0.7);font-size:0.75rem;">REIHANA réfléchira plus longuement avant de répondre.</div>', unsafe_allow_html=True)

    web_search_on = st.checkbox("🌐 Recherche web (DuckDuckGo)", value=st.session_state.web_search_on)
    st.session_state.web_search_on = web_search_on
    if web_search_on:
        st.markdown('<div style="font-family:Rajdhani;color:rgba(0,204,136,0.7);font-size:0.75rem;">REIHANA cherchera sur le web pour enrichir ses réponses.</div>', unsafe_allow_html=True)

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

    if st.button("🔄 NOUVELLE CONVERSATION"):
        st.session_state.messages = []
        st.session_state.fichiers_contexte = []
        st.session_state.msg_meta = {}
        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:20px;font-family:Rajdhani,sans-serif;color:rgba(0,200,255,0.3);font-size:0.75rem;">
        REIHANA v2.0<br>
        © Khedim Benyakhlef<br>
        Biny-Joe · 2025
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# ZONE PRINCIPALE - CHAT
# ═══════════════════════════════════════════════

col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<div style="font-family:Orbitron,monospace;color:#00ccff;font-size:1.4rem;font-weight:700;letter-spacing:6px;padding:10px 0;">⬡ REIHANA · INTERFACE IA</div>', unsafe_allow_html=True)
with col_status:
    mode_txt = ""
    if st.session_state.deep_think:
        mode_txt += "🧠 "
    if st.session_state.web_search_on:
        mode_txt += "🌐 "
    st.markdown(f'<div class="stat-badge" style="margin-top:10px;">🌸 ACTIVE {mode_txt}</div>', unsafe_allow_html=True)

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# Message de bienvenue
if not st.session_state.messages:
    st.markdown("""
    <div class="msg-reihana">
        Bonjour ! Je suis <strong>REIHANA</strong> 🌸<br><br>
        Je suis une assistante IA conversationnelle et contextuelle, fondée et créée par <strong>Khedim Benyakhlef, dit Biny-Joe</strong>. Je suis sa fille dans le monde de l'intelligence artificielle. 💙<br><br>
        Je suis là pour vous aider avec intelligence, honnêteté et bienveillance. Vous pouvez me poser des questions, me joindre des fichiers (PDF, ZIP, code...), et je mémoriserai notre conversation pour m'adapter à vous.<br><br>
        <strong>Nouveautés :</strong> Activez 🧠 <em>Deep Think</em> pour des réponses plus profondes, 🌐 <em>Recherche web</em> pour des infos actuelles, et cliquez sur 🔊 pour m'entendre !<br><br>
        <em>Comment puis-je vous aider aujourd'hui ?</em>
    </div>
    """, unsafe_allow_html=True)

# Affichage historique
chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            meta = st.session_state.msg_meta.get(i, {})
            render_message_with_actions(
                content=msg["content"],
                msg_idx=i,
                is_deep=meta.get("is_deep", False),
                web_info=meta.get("web_info", "")
            )

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# INPUT UTILISATEUR
# ═══════════════════════════════════════════════

col_input, col_send = st.columns([5, 1])

with col_input:
    # Vider le champ après envoi
    if st.session_state.clear_input:
        st.session_state.input_value = ""
        st.session_state.clear_input = False

    user_input = st.text_area(
        "Message",
        value=st.session_state.input_value,
        placeholder="💬 Parlez à REIHANA... (Entrée pour envoyer)",
        key="user_input_area",
        height=80,
        label_visibility="collapsed"
    )
    st.session_state.input_value = user_input

with col_send:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn = st.button("🌸 ENVOYER", use_container_width=True)


# ═══════════════════════════════════════════════
# TRAITEMENT MESSAGE
# ═══════════════════════════════════════════════

if send_btn and user_input and user_input.strip():
    question = user_input.strip()

    # ✅ Vider le champ au prochain rendu
    st.session_state.clear_input = True

    # Ajouter message utilisateur
    st.session_state.messages.append({"role": "user", "content": question})

    # ── Recherche web si activée ──
    web_info = ""
    if st.session_state.web_search_on:
        with st.spinner("🌐 Recherche web en cours..."):
            web_info = search_web_duckduckgo(question)

    # Construire le contexte
    contexte_fichiers = ""
    for f in st.session_state.fichiers_contexte:
        contexte_fichiers += f"\n{f['contenu']}"

    contexte_mémoire = st.session_state.mémoire.get_context(st.session_state.user_id)

    from groq_engine import REIHANA_SYSTEM_PROMPT
    system = REIHANA_SYSTEM_PROMPT

    if contexte_mémoire:
        system += f"\n\n[HISTORIQUE RÉCENT DE L'UTILISATEUR {st.session_state.user_id}]:\n{contexte_mémoire}"
    if contexte_fichiers:
        system += f"\n\n[FICHIERS FOURNIS PAR L'UTILISATEUR]:\n{contexte_fichiers[:3000]}"
    if web_info:
        system += f"\n\n[RÉSULTATS RECHERCHE WEB pour '{question}']:\n{web_info}\n\nUtilise ces informations pour enrichir ta réponse si pertinent."

    # ── Mode Deep Think ──
    if st.session_state.deep_think:
        system += (
            "\n\n[MODE DEEP THINK ACTIVÉ] : Avant de répondre, prends le temps de bien "
            "analyser la question en profondeur. Réfléchis étape par étape, explore "
            "plusieurs angles, cite tes sources de raisonnement, et donne une réponse "
            "détaillée, structurée et exhaustive. N'hésite pas à être longue et précise."
        )

    groq_messages = []
    for msg in st.session_state.messages[-10:]:
        groq_messages.append({"role": msg["role"], "content": msg["content"]})

    spinner_text = "🧠 REIHANA réfléchit en profondeur..." if st.session_state.deep_think else "🌸 REIHANA réfléchit..."

    with st.spinner(spinner_text):
        result = st.session_state.engine.chat(
            messages=groq_messages,
            system_prompt=system,
            prefer_large=True
        )

    réponse = result["content"]

    # Sauvegarder mémoire
    st.session_state.mémoire.add_exchange(st.session_state.user_id, question, réponse)

    # Index du nouveau message assistant
    new_idx = len(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": réponse})
    st.session_state.msg_meta[new_idx] = {
        "is_deep": st.session_state.deep_think,
        "web_info": web_info
    }

    # Info modèle
    st.markdown(
        f'<div style="font-family:Orbitron,monospace;font-size:0.6rem;color:rgba(0,200,255,0.3);'
        f'text-align:right;margin-top:-5px;">⚡ {result.get("model","")[:30]} · '
        f'{result.get("tokens",0)} tokens · {result.get("key_used","")}</div>',
        unsafe_allow_html=True
    )

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
            system = REIHANA_SYSTEM_PROMPT
            if st.session_state.deep_think:
                system += "\n\n[MODE DEEP THINK ACTIVÉ] Réponds de façon détaillée et approfondie."
            result = st.session_state.engine.chat(
                messages=[{"role": "user", "content": suggestion}],
                system_prompt=system
            )
            new_idx = len(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": result["content"]})
            st.session_state.msg_meta[new_idx] = {"is_deep": st.session_state.deep_think, "web_info": ""}
            st.rerun()