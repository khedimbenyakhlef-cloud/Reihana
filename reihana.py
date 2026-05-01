"""
REIHANA v3.0 MEGA EDITION
Fondée par Khedim Benyakhlef (Biny-Joe)
"""
import streamlit as st
import sys, os, json, time, tempfile, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "backend"))

st.set_page_config(page_title="REIHANA • IA", page_icon="🌸", layout="wide", initial_sidebar_state="expanded")

# ═══════════════════════════════════════════
# THÈMES
# ═══════════════════════════════════════════
THEMES = {
    "🔵 Cyan Holographique": {"p":"#00ffff","s":"#0088ff","a":"#aa00ff","b1":"#0a0a2e","b2":"#000010","g":"0,255,255","br":"0,200,255"},
    "💜 Violet Cosmique":    {"p":"#cc88ff","s":"#8800ff","a":"#ff00cc","b1":"#1a0a2e","b2":"#0d0018","g":"150,0,255","br":"180,0,255"},
    "🌸 Rose Sakura":        {"p":"#ff88cc","s":"#ff0088","a":"#ffcc00","b1":"#2e0a1a","b2":"#1a000d","g":"255,100,180","br":"255,80,160"},
    "⚡ Or Futuriste":       {"p":"#ffcc00","s":"#ff8800","a":"#00ccff","b1":"#1a1400","b2":"#0d0a00","g":"255,200,0","br":"220,160,0"},
    "🟢 Matrix Vert":        {"p":"#00ff88","s":"#00cc44","a":"#00ffcc","b1":"#001a0d","b2":"#000d07","g":"0,255,100","br":"0,200,80"},
}

# ═══════════════════════════════════════════
# PERSONNALITÉS
# ═══════════════════════════════════════════
PERSONNALITES = {
    "🌸 Douce & Timide":      {"rate":1.05,"pitch":1.7,"emoji":"🌸","style":"Tu es REIHANA, douce et timide comme une petite fille de 12 ans. Tu utilises des expressions mignonnes, des '💕', tu dis 'oh !' quand tu es surprise. Tu parles avec beaucoup de douceur et bienveillance."},
    "⚡ Énergique & Curieuse": {"rate":1.25,"pitch":1.6,"emoji":"⚡","style":"Tu es REIHANA, super énergique et curieuse ! Tu mets des '!' partout, des '🔥', tu t'enthousiasmes pour tout, tu dis 'Oh incroyable !' et 'Waouh !' Tu as 12 ans et tu adores tout découvrir !"},
    "🌟 Intelligente & Mature":{"rate":1.1,"pitch":1.45,"emoji":"🌟","style":"Tu es REIHANA, intelligente et mature pour tes 12 ans. Tu t'exprimes avec précision et clarté. Tu structures tes réponses. Tu es bienveillante mais sérieuse quand il le faut."},
    "🎭 Mystérieuse & Poétique":{"rate":0.95,"pitch":1.5,"emoji":"🎭","style":"Tu es REIHANA, mystérieuse et poétique. Tu parles avec des métaphores et des images. Tu es contemplative et fascinante. Tu commences parfois par des pensées profondes."},
}

# ═══════════════════════════════════════════
# LANGUES
# ═══════════════════════════════════════════
LANGS = {
    "🇫🇷 Français": {
        "send":"🌸 ENVOYER","new_conv":"🔄 NOUVELLE CONVERSATION",
        "thinking":"réfléchit...","deep_thinking":"réfléchit profondément...",
        "searching":"Recherche sur le web...","placeholder":"💬 Parlez à REIHANA...",
        "suggestions":["Qui es-tu REIHANA ?","Analyse mon fichier","Explique l'IA moderne","Aide-moi à coder"],
        "online":"EN LIGNE","active":"ACTIVE","copied":"✅ Copié !","saved":"💾 Sauvegardé",
        "welcome":"Bonjour ! Je suis <strong>REIHANA</strong> 🌸<br><br>Assistante IA fondée par <strong>Khedim Benyakhlef (Biny-Joe)</strong> — sa fille dans le monde de l'IA 💙<br><br><em>Comment puis-je vous aider ?</em>",
        "slang":"fr-FR",
    },
    "🇬🇧 English": {
        "send":"🌸 SEND","new_conv":"🔄 NEW CONVERSATION",
        "thinking":"is thinking...","deep_thinking":"thinking deeply...",
        "searching":"Searching the web...","placeholder":"💬 Talk to REIHANA...",
        "suggestions":["Who are you REIHANA?","Analyze my file","Explain modern AI","Help me code"],
        "online":"ONLINE","active":"ACTIVE","copied":"✅ Copied!","saved":"💾 Saved",
        "welcome":"Hello! I'm <strong>REIHANA</strong> 🌸<br><br>AI assistant founded by <strong>Khedim Benyakhlef (Biny-Joe)</strong> — his daughter in the AI world 💙<br><br><em>How can I help you?</em>",
        "slang":"en-US",
    },
    "🇩🇿 العربية": {
        "send":"🌸 إرسال","new_conv":"🔄 محادثة جديدة",
        "thinking":"تفكر...","deep_thinking":"تفكر بعمق...",
        "searching":"البحث على الويب...","placeholder":"💬 تحدث مع ريحانة...",
        "suggestions":["من أنت ريحانة؟","حلل ملفي","اشرح الذكاء الاصطناعي","ساعدني في البرمجة"],
        "online":"متصلة","active":"نشطة","copied":"✅ تم النسخ!","saved":"💾 تم الحفظ",
        "welcome":"مرحباً! أنا <strong>ريحانة</strong> 🌸<br><br>مساعدة ذكاء اصطناعي أسسها <strong>خضيم بن يخلف (بيني جو)</strong> 💙<br><br><em>كيف يمكنني مساعدتك؟</em>",
        "slang":"ar-SA",
    },
}

# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
defs = {
    "messages":[],"user_id":"user_default","fichiers_contexte":[],
    "input_value":"","clear_input":False,"deep_think":False,"web_search_on":False,
    "liked_messages":set(),"regen_index":None,"regen_question":"",
    "theme":"🔵 Cyan Holographique","langue":"🇫🇷 Français","personnalite":"🌸 Douce & Timide",
    "music_on":False,"show_dashboard":False,"conversation_history":[],
    "total_tokens":0,"session_start":datetime.now().strftime("%H:%M"),
}
for k,v in defs.items():
    if k not in st.session_state: st.session_state[k]=v

if "engine" not in st.session_state:
    from groq_engine import groq_engine, FileProcessor, REIHANA_SYSTEM_PROMPT, mémoire
    st.session_state.mémoire=mémoire; st.session_state.engine=groq_engine
    st.session_state.file_processor=FileProcessor(); st.session_state.BASE_PROMPT=REIHANA_SYSTEM_PROMPT

T=LANGS[st.session_state.langue]
TH=THEMES[st.session_state.theme]
PERS=PERSONNALITES[st.session_state.personnalite]
p,s,a,b1,b2,g,br=TH["p"],TH["s"],TH["a"],TH["b1"],TH["b2"],TH["g"],TH["br"]

# ═══════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&family=Share+Tech+Mono&display=swap');
.stApp{{background:radial-gradient(ellipse at 15% 40%,{b1} 0%,{b2} 50%,#000005 100%);background-attachment:fixed;}}
.stApp::before{{content:'';position:fixed;top:0;left:0;right:0;bottom:0;background:radial-gradient(circle at 10% 20%,rgba({g},0.04) 0%,transparent 50%),radial-gradient(circle at 90% 80%,rgba({g},0.06) 0%,transparent 50%);pointer-events:none;z-index:0;}}

/* HOLOGRAMME */
.hologram-container{{position:relative;width:100%;text-align:center;padding:15px 0;}}
.hologram-avatar{{width:160px;height:160px;border-radius:50%;margin:0 auto;background:radial-gradient(circle,rgba({g},0.15) 0%,rgba({g},0.05) 50%,transparent 70%);border:2px solid rgba({g},0.6);box-shadow:0 0 30px rgba({g},0.5),0 0 70px rgba({g},0.2),inset 0 0 30px rgba({g},0.1);display:flex;align-items:center;justify-content:center;font-size:72px;animation:holoPulse 3s ease-in-out infinite,holoRotate 8s linear infinite;position:relative;cursor:pointer;transition:all 0.3s ease;}}
.hologram-avatar.speaking{{animation:holoPulse 0.3s ease-in-out infinite,holoRotate 1.5s linear infinite!important;box-shadow:0 0 60px rgba({g},0.9),0 0 130px rgba({g},0.5),inset 0 0 60px rgba({g},0.3)!important;border-color:rgba({g},1)!important;}}
@keyframes holoPulse{{0%,100%{{box-shadow:0 0 30px rgba({g},0.5),0 0 70px rgba({g},0.2),inset 0 0 30px rgba({g},0.1);}}50%{{box-shadow:0 0 55px rgba({g},0.8),0 0 110px rgba({g},0.4),inset 0 0 55px rgba({g},0.25);}}}}
@keyframes holoRotate{{0%{{border-color:rgba({g},0.6);}}33%{{border-color:rgba({g},0.3);}}66%{{border-color:rgba({g},0.8);}}100%{{border-color:rgba({g},0.6);}}}}
.hologram-avatar::after{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;border-radius:50%;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba({g},0.04) 3px,rgba({g},0.04) 5px);animation:scanLines 1.5s linear infinite;}}
@keyframes scanLines{{0%{{background-position:0 0;}}100%{{background-position:0 80px;}}}}

/* BOUCHE */
.holo-mouth{{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);width:32px;height:6px;background:rgba({g},0.7);border-radius:3px;transition:all 0.08s ease;box-shadow:0 0 8px rgba({g},0.5);}}
.holo-mouth.speaking{{animation:mouthAnim 0.12s ease-in-out infinite alternate;}}
@keyframes mouthAnim{{0%{{height:4px;width:24px;border-radius:3px;}}100%{{height:18px;width:40px;border-radius:50% 50% 8px 8px;}}}}

/* BARRES VOCALES */
.voice-bars{{display:none;justify-content:center;gap:3px;margin:8px auto;height:24px;align-items:flex-end;}}
.voice-bars.active{{display:flex;}}
.voice-bar{{width:4px;background:{p};border-radius:2px;box-shadow:0 0 6px rgba({g},0.7);}}
.voice-bar:nth-child(1){{animation:barAnim 0.5s ease-in-out infinite;height:8px;}}
.voice-bar:nth-child(2){{animation:barAnim 0.5s ease-in-out infinite 0.1s;height:16px;}}
.voice-bar:nth-child(3){{animation:barAnim 0.5s ease-in-out infinite 0.2s;height:24px;}}
.voice-bar:nth-child(4){{animation:barAnim 0.5s ease-in-out infinite 0.1s;height:16px;}}
.voice-bar:nth-child(5){{animation:barAnim 0.5s ease-in-out infinite;height:8px;}}
@keyframes barAnim{{0%,100%{{transform:scaleY(0.4);opacity:0.6;}}50%{{transform:scaleY(1);opacity:1;}}}}

/* TITRE */
.reihana-title{{font-family:'Orbitron',monospace!important;font-size:2.2rem!important;font-weight:900!important;background:linear-gradient(135deg,{p},{s},{a},{p});background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;text-align:center;letter-spacing:7px;margin:8px 0;}}
@keyframes gradientShift{{0%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}100%{{background-position:0% 50%;}}}}
.reihana-subtitle{{font-family:'Rajdhani',sans-serif;color:rgba({g},0.6);text-align:center;font-size:0.8rem;letter-spacing:4px;text-transform:uppercase;}}

/* MESSAGES */
.msg-reihana{{background:linear-gradient(135deg,rgba(0,20,50,0.92),rgba(0,10,35,0.85));border:1px solid rgba({br},0.3);border-left:3px solid {p};border-radius:0 15px 15px 15px;padding:14px 17px;margin:8px 0 4px 0;font-family:'Rajdhani',sans-serif;font-size:1rem;color:#c8f0ff;box-shadow:0 4px 20px rgba({g},0.12);line-height:1.6;}}
.msg-reihana::before{{content:'{PERS["emoji"]} REIHANA';font-family:'Orbitron',monospace;font-size:0.62rem;color:{p};display:block;margin-bottom:7px;letter-spacing:2px;}}
.msg-user{{background:linear-gradient(135deg,rgba(20,0,50,0.85),rgba(30,0,65,0.75));border:1px solid rgba({g},0.2);border-right:3px solid {a};border-radius:15px 0 15px 15px;padding:12px 15px;margin:8px 0;font-family:'Rajdhani',sans-serif;color:#e0d0ff;text-align:right;}}
.msg-user::before{{content:'VOUS 👤';font-family:'Orbitron',monospace;font-size:0.62rem;color:{a};display:block;margin-bottom:6px;letter-spacing:2px;}}

/* DEEP THINK */
.think-box{{background:linear-gradient(135deg,rgba(60,0,120,0.25),rgba(40,0,90,0.15));border:1px solid rgba({g},0.15);border-left:3px solid {a};border-radius:0 10px 10px 10px;padding:10px 14px;margin:4px 0 8px 0;font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:rgba({g},0.8);}}
.think-header{{font-family:'Orbitron',monospace;font-size:0.58rem;color:{a};letter-spacing:2px;margin-bottom:5px;}}

/* STATS */
.stat-badge{{background:rgba({g},0.07);border:1px solid rgba({br},0.2);border-radius:8px;padding:7px 11px;font-family:'Orbitron',monospace;font-size:0.68rem;color:{p};text-align:center;margin:3px 0;}}
.stat-green{{background:rgba(0,200,100,0.08);border:1px solid rgba(0,200,100,0.25);border-radius:8px;padding:6px 11px;font-family:'Orbitron',monospace;font-size:0.65rem;color:#00cc88;text-align:center;margin:3px 0;}}
.stat-purple{{background:rgba(150,0,255,0.1);border:1px solid rgba(150,0,255,0.3);border-radius:8px;padding:6px 11px;font-family:'Orbitron',monospace;font-size:0.65rem;color:#bb66ff;text-align:center;margin:3px 0;animation:thinkPulse 2s ease-in-out infinite;}}
@keyframes thinkPulse{{0%,100%{{opacity:0.7;}}50%{{opacity:1;box-shadow:0 0 12px rgba(150,0,255,0.3);}}}}

/* DASHBOARD */
.dash-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin:7px 0;}}
.dash-card{{background:rgba({g},0.06);border:1px solid rgba({br},0.2);border-radius:10px;padding:9px;text-align:center;}}
.dash-num{{font-family:'Orbitron',monospace;font-size:1.3rem;color:{p};font-weight:900;text-shadow:0 0 15px rgba({g},0.6);}}
.dash-lbl{{font-family:'Rajdhani',sans-serif;color:rgba({g},0.6);font-size:0.68rem;letter-spacing:2px;}}

/* LINES & STATUS */
.holo-line{{height:1px;background:linear-gradient(90deg,transparent,{p},{a},transparent);margin:12px 0;animation:hololine 3s ease-in-out infinite;}}
@keyframes hololine{{0%,100%{{opacity:0.35;}}50%{{opacity:1;}}}}
.status-online{{display:inline-block;width:7px;height:7px;background:#00ff88;border-radius:50%;animation:blink 2s ease-in-out infinite;margin-right:6px;box-shadow:0 0 6px #00ff88;}}
@keyframes blink{{0%,100%{{opacity:1;}}50%{{opacity:0.3;}}}}

/* BUTTONS */
.stButton>button{{background:linear-gradient(135deg,rgba({g},0.05),rgba({g},0.12))!important;border:1px solid rgba({br},0.4)!important;color:{p}!important;font-family:'Orbitron',monospace!important;font-size:0.72rem!important;letter-spacing:1.5px!important;border-radius:8px!important;transition:all 0.3s ease!important;}}
.stButton>button:hover{{background:linear-gradient(135deg,rgba({g},0.15),rgba({g},0.25))!important;box-shadow:0 0 18px rgba({g},0.4)!important;transform:translateY(-2px)!important;}}

/* INPUT */
.stTextArea textarea,.stTextInput input{{background:rgba(0,15,40,0.85)!important;border:1px solid rgba({br},0.35)!important;color:#c8f0ff!important;font-family:'Rajdhani',sans-serif!important;font-size:1rem!important;border-radius:10px!important;}}

/* SIDEBAR */
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,#020218,#030325,{b2})!important;border-right:1px solid rgba({br},0.15)!important;}}

/* SELECT */
.stSelectbox>div>div{{background:rgba(0,15,40,0.85)!important;border:1px solid rgba({br},0.35)!important;color:#c8f0ff!important;}}

/* SCROLLBAR */
::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-track{{background:rgba(0,0,20,0.5);}}
::-webkit-scrollbar-thumb{{background:rgba({g},0.4);border-radius:2px;}}

/* MUSIC WAVE */
.music-wave{{display:flex;justify-content:center;gap:2px;height:16px;align-items:flex-end;margin:4px 0;}}
.music-bar{{width:3px;background:{p};border-radius:1px;box-shadow:0 0 4px rgba({g},0.6);}}
.music-bar:nth-child(1){{animation:musicAnim 0.8s ease-in-out infinite;height:6px;}}
.music-bar:nth-child(2){{animation:musicAnim 0.8s ease-in-out infinite 0.15s;height:12px;}}
.music-bar:nth-child(3){{animation:musicAnim 0.8s ease-in-out infinite 0.3s;height:16px;}}
.music-bar:nth-child(4){{animation:musicAnim 0.8s ease-in-out infinite 0.15s;height:12px;}}
.music-bar:nth-child(5){{animation:musicAnim 0.8s ease-in-out infinite;height:6px;}}
@keyframes musicAnim{{0%,100%{{transform:scaleY(0.3);}}50%{{transform:scaleY(1);}}}}

/* WEB CARD */
.web-card{{background:rgba(0,30,15,0.6);border:1px solid rgba(0,200,100,0.2);border-left:2px solid #00cc88;border-radius:6px;padding:7px 10px;margin:3px 0;font-family:'Rajdhani',sans-serif;font-size:0.83rem;color:rgba(200,240,200,0.85);}}

/* MOBILE */
@media(max-width:768px){{.hologram-avatar{{width:120px;height:120px;font-size:52px;}}.reihana-title{{font-size:1.5rem!important;letter-spacing:4px;}}.msg-reihana,.msg-user{{padding:10px 12px;font-size:0.93rem;}}.dash-grid{{grid-template-columns:repeat(2,1fr);}}}}
</style>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# JAVASCRIPT
# ═══════════════════════════════════════════
st.markdown(f"""<script>
window.reiConfig={{rate:{PERS['rate']},pitch:{PERS['pitch']},lang:'{T["slang"]}'}};

window.reiEnterSend=function(){{
    document.addEventListener('keydown',function(e){{
        if(e.key==='Enter'&&!e.shiftKey){{
            var ta=document.querySelector('textarea');
            if(ta&&document.activeElement===ta){{
                e.preventDefault();
                var btns=Array.from(document.querySelectorAll('button'));
                var send=btns.find(function(b){{return b.innerText.includes('ENVOYER')||b.innerText.includes('SEND');}});
                if(send)send.click();
            }}
        }}
    }});
}};
setTimeout(window.reiEnterSend,1000);
window.reihanaSpeak=function(text){{
    if(!window.speechSynthesis)return;
    window.speechSynthesis.cancel();
    let clean=text.replace(/\\*\\*(.*?)\\*\\*/g,'$1').replace(/\\*(.*?)\\*/g,'$1').replace(/<[^>]*>/g,'').replace(/[\\[\\]{{}}]/g,'').substring(0,900);
    function doSpeak(voices){{
        let u=new SpeechSynthesisUtterance(clean);
        u.lang=window.reiConfig.lang; u.rate=window.reiConfig.rate; u.pitch=window.reiConfig.pitch; u.volume=1;
        let fv=voices.filter(v=>v.lang.startsWith(window.reiConfig.lang.split('-')[0]));
        let fem=fv.find(v=>v.name.toLowerCase().match(/female|femme|amelie|marie|zira|paulina/))||fv[0];
        if(fem)u.voice=fem;
        u.onstart=()=>{{document.querySelector('.hologram-avatar')?.classList.add('speaking');document.querySelector('.holo-mouth')?.classList.add('speaking');document.querySelector('.voice-bars')?.classList.add('active');}};
        u.onend=()=>{{document.querySelector('.hologram-avatar')?.classList.remove('speaking');document.querySelector('.holo-mouth')?.classList.remove('speaking');document.querySelector('.voice-bars')?.classList.remove('active');}};
        window.speechSynthesis.speak(u);
    }}
    let vv=window.speechSynthesis.getVoices();
    if(vv.length>0)doSpeak(vv);
    else window.speechSynthesis.onvoiceschanged=()=>doSpeak(window.speechSynthesis.getVoices());
}};

window.reihanaStop=function(){{
    window.speechSynthesis?.cancel();
    document.querySelector('.hologram-avatar')?.classList.remove('speaking');
    document.querySelector('.holo-mouth')?.classList.remove('speaking');
    document.querySelector('.voice-bars')?.classList.remove('active');
}};

window._musicOn=false; window._musicNodes=[]; window._audioCtx=null;
window.startMusic=function(){{
    if(window._musicOn)return; window._musicOn=true;
    try{{
        let ctx=new(window.AudioContext||window.webkitAudioContext)();
        window._audioCtx=ctx;
        [[55,0.04,0],[110,0.03,5],[220,0.025,-3],[329.6,0.018,0],[440,0.012,8],[660,0.008,-5]].forEach(([freq,vol,det])=>{{
            let o=ctx.createOscillator(),g=ctx.createGain(),f=ctx.createBiquadFilter();
            o.type='sine'; o.frequency.value=freq; if(det)o.detune.value=det;
            g.gain.value=vol; f.type='lowpass'; f.frequency.value=800;
            let lfo=ctx.createOscillator(),lg=ctx.createGain();
            lfo.frequency.value=0.07+Math.random()*0.05; lg.gain.value=vol*0.3;
            o.connect(f); f.connect(g); g.connect(ctx.destination);
            lfo.connect(lg); lg.connect(g.gain);
            o.start(); lfo.start();
            window._musicNodes.push(o,g,lfo,lg);
        }});
    }}catch(e){{console.log('audio',e);}}
}};
window.stopMusic=function(){{
    window._musicOn=false;
    window._musicNodes.forEach(n=>{{try{{n.stop();n.disconnect();}}catch(e){{}}}});
    window._musicNodes=[];
    window._audioCtx?.close(); window._audioCtx=null;
}};

window.playNotif=function(){{
    try{{
        let ctx=new(window.AudioContext||window.webkitAudioContext)();
        [523,659,784].forEach((f,i)=>{{
            let o=ctx.createOscillator(),g=ctx.createGain();
            o.frequency.value=f; o.type='sine';
            g.gain.setValueAtTime(0.12,ctx.currentTime+i*0.12);
            g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+i*0.12+0.22);
            o.connect(g); g.connect(ctx.destination);
            o.start(ctx.currentTime+i*0.12); o.stop(ctx.currentTime+i*0.12+0.25);
        }});
    }}catch(e){{}}
}};

if({str(st.session_state.music_on).lower()}){{setTimeout(window.startMusic,600);}}
</script>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════

def web_search(query, n=5):
    try:
        url=f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 REIHANA/3.0'})
        with urllib.request.urlopen(req,timeout=6) as r: data=json.loads(r.read().decode())
        results=[]
        if data.get('AbstractText'): results.append({'title':data.get('Heading',query),'snippet':data['AbstractText'][:350],'url':data.get('AbstractURL','')})
        for item in data.get('RelatedTopics',[])[:n]:
            if isinstance(item,dict) and item.get('Text'): results.append({'title':item.get('Text','')[:65],'snippet':item.get('Text','')[:220],'url':item.get('FirstURL','')})
        return results[:n]
    except: return []

def detect_lang(text):
    ar=sum(1 for c in text if '\u0600'<=c<='\u06FF')
    if ar>len(text)*0.3: return "🇩🇿 العربية"
    en=['the','is','are','what','how','who','can','you','please','help','tell','me','my','your']
    if any(w in text.lower().split() for w in en): return "🇬🇧 English"
    return "🇫🇷 Français"

def save_conv():
    if not st.session_state.messages: return
    st.session_state.conversation_history.append({
        "date":datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user":st.session_state.user_id,
        "messages":st.session_state.messages[-20:],
        "lang":st.session_state.langue,
        "pers":st.session_state.personnalite,
    })
    if len(st.session_state.conversation_history)>50:
        st.session_state.conversation_history=st.session_state.conversation_history[-50:]

def build_system():
    lang_inst={"🇫🇷 Français":"Réponds TOUJOURS en français.","🇬🇧 English":"Always respond in English.","🇩🇿 العربية":"أجب دائماً باللغة العربية."}[st.session_state.langue]
    system=st.session_state.BASE_PROMPT+f"\n\n[PERSONNALITÉ]:\n{PERS['style']}\n\n[LANGUE]: {lang_inst}"
    if st.session_state.deep_think:
        system+="""

[MODE DEEP THINK EXPERT]
Structure OBLIGATOIRE de ta réponse :
🔍 ÉTAPE 1 — ANALYSE : Décompose la question
🧩 ÉTAPE 2 — CONTEXTE : Facteurs importants
💡 ÉTAPE 3 — HYPOTHÈSES : Ce que tu assumes
🔗 ÉTAPE 4 — RAISONNEMENT : Développe étape par étape
✅ ÉTAPE 5 — VÉRIFICATION : Cherche les failles
🎯 ÉTAPE 6 — CONCLUSION : Réponse finale claire

Sois exhaustif. N'omets aucune étape."""
    return system

def process_msg(question, regen=False, regen_idx=None):
    # Auto-détection langue
    detected=detect_lang(question)
    if detected!="🇫🇷 Français" and detected!=st.session_state.langue:
        st.session_state.langue=detected

    # Web search
    results=[]
    web_ctx=""
    if st.session_state.web_search_on:
        with st.spinner(f"🌐 {T['searching']}"):
            results=web_search(question)
            if results:
                web_ctx="\n\n[WEB — utilise pour enrichir ta réponse]:\n"+"".join(f"• {r['title']}: {r['snippet']}\n" for r in results)

    # Contexte
    ctx_files="".join(f['contenu'] for f in st.session_state.fichiers_contexte)
    ctx_mem=st.session_state.mémoire.get_context(st.session_state.user_id)
    system=build_system()
    if ctx_mem: system+=f"\n\n[MÉMOIRE {st.session_state.user_id}]:\n{ctx_mem}"
    if ctx_files: system+=f"\n\n[FICHIERS]:\n{ctx_files[:3000]}"
    if web_ctx: system+=web_ctx

    # Messages
    msgs=st.session_state.messages if not regen else st.session_state.messages[:regen_idx-1]
    groq_msgs=[{"role":m["role"],"content":m["content"]} for m in msgs[-12:] if m["role"] in ["user","assistant"]]
    groq_msgs.append({"role":"user","content":question})

    spinner="🧠 REIHANA "+T["deep_thinking"] if st.session_state.deep_think else "🌸 REIHANA "+T["thinking"]
    with st.spinner(spinner):
        res=st.session_state.engine.chat(messages=groq_msgs,system_prompt=system,prefer_large=st.session_state.deep_think)

    rep=res["content"]
    st.session_state.total_tokens+=res.get("tokens",0)
    return rep, res, results

def safe_js(text):
    return text.replace("'","").replace('"','').replace('\n',' ').replace('\\',' ').replace('`','')[:680]

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="hologram-container">
        <div class="hologram-avatar" onclick="window.reihanaStop()">
            {PERS["emoji"]}
            <div class="holo-mouth"></div>
        </div>
        <div class="voice-bars">
            <div class="voice-bar"></div><div class="voice-bar"></div><div class="voice-bar"></div>
            <div class="voice-bar"></div><div class="voice-bar"></div>
        </div>
    </div>
    <div class="reihana-title">REIHANA</div>
    <div class="reihana-subtitle">IA · Biny-Joe · {PERS["emoji"]} {st.session_state.personnalite[:14]}</div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Status + Musique
    cs, cm = st.columns([2,1])
    with cs: st.markdown(f'<span class="status-online"></span><span style="color:#00ff88;font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:2px;">{T["online"]}</span>', unsafe_allow_html=True)
    with cm:
        if st.button("🎵"+"▶" if not st.session_state.music_on else "🎵"+"⏸", key="mbtn"):
            st.session_state.music_on = not st.session_state.music_on
            action = "window.startMusic()" if st.session_state.music_on else "window.stopMusic()"
            st.markdown(f"<script>{action};</script>", unsafe_allow_html=True)
            st.rerun()
    if st.session_state.music_on:
        st.markdown('<div class="music-wave"><div class="music-bar"></div><div class="music-bar"></div><div class="music-bar"></div><div class="music-bar"></div><div class="music-bar"></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Profil
    st.markdown('<div class="stat-badge">👤 PROFIL</div>', unsafe_allow_html=True)
    uname=st.text_input("",value=st.session_state.user_id,key="uname",label_visibility="collapsed",placeholder="Votre nom...")
    if uname!=st.session_state.user_id: st.session_state.user_id=uname

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Personnalité
    st.markdown('<div class="stat-badge">🎭 PERSONNALITÉ</div>', unsafe_allow_html=True)
    np=st.selectbox("",list(PERSONNALITES.keys()),index=list(PERSONNALITES.keys()).index(st.session_state.personnalite),label_visibility="collapsed",key="psel")
    if np!=st.session_state.personnalite: st.session_state.personnalite=np; st.rerun()

    # Langue
    st.markdown('<div class="stat-badge">🌍 LANGUE</div>', unsafe_allow_html=True)
    nl=st.selectbox("",list(LANGS.keys()),index=list(LANGS.keys()).index(st.session_state.langue),label_visibility="collapsed",key="lsel")
    if nl!=st.session_state.langue: st.session_state.langue=nl; st.rerun()

    # Thème
    st.markdown('<div class="stat-badge">🎨 THÈME</div>', unsafe_allow_html=True)
    nt=st.selectbox("",list(THEMES.keys()),index=list(THEMES.keys()).index(st.session_state.theme),label_visibility="collapsed",key="tsel")
    if nt!=st.session_state.theme: st.session_state.theme=nt; st.rerun()

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Modes
    st.markdown('<div class="stat-badge">⚙️ MODES</div>', unsafe_allow_html=True)
    mw, mt = st.columns(2)
    with mw:
        if st.button(f"🌐{'✓' if st.session_state.web_search_on else ''}", use_container_width=True, key="wbtn"):
            st.session_state.web_search_on=not st.session_state.web_search_on; st.rerun()
    with mt:
        if st.button(f"🧠{'✓' if st.session_state.deep_think else ''}", use_container_width=True, key="tbtn"):
            st.session_state.deep_think=not st.session_state.deep_think; st.rerun()
    if st.session_state.web_search_on: st.markdown('<div class="stat-green">🌐 WEB SEARCH ON</div>', unsafe_allow_html=True)
    if st.session_state.deep_think: st.markdown('<div class="stat-purple">🧠 DEEP THINK EXPERT</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Fichiers
    st.markdown('<div class="stat-badge">📎 FICHIERS</div>', unsafe_allow_html=True)
    uf=st.file_uploader("",type=['txt','pdf','md','py','js','json','csv','zip'],label_visibility="collapsed")
    if uf:
        with tempfile.NamedTemporaryFile(delete=False,suffix=Path(uf.name).suffix) as tmp:
            tmp.write(uf.read()); tp=tmp.name
        with st.spinner("🔍 Analyse..."):
            res=st.session_state.file_processor.process_file(tp)
            st.session_state.fichiers_contexte.append({"nom":uf.name,"contenu":f"\n\n[FICHIER: {uf.name}]\n{res.get('content','')}"})
            st.session_state.mémoire.add_file(st.session_state.user_id,uf.name,res.get('content','')[:200])
        st.markdown(f'<div class="stat-green">✅ {uf.name}</div>', unsafe_allow_html=True)
        os.unlink(tp)
    if st.session_state.fichiers_contexte:
        st.markdown(f'<div class="stat-badge">📚 {len(st.session_state.fichiers_contexte)} fichier(s)</div>', unsafe_allow_html=True)
        if st.button("🗑️ VIDER"): st.session_state.fichiers_contexte=[]; st.rerun()

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Dashboard
    if st.button(f"📊 DASHBOARD {'▲' if st.session_state.show_dashboard else '▼'}", use_container_width=True):
        st.session_state.show_dashboard=not st.session_state.show_dashboard; st.rerun()
    if st.session_state.show_dashboard:
        ai_c=len([m for m in st.session_state.messages if m["role"]=="assistant"])
        st.markdown(f"""<div class="dash-grid">
            <div class="dash-card"><div class="dash-num">{len(st.session_state.messages)}</div><div class="dash-lbl">MSGS</div></div>
            <div class="dash-card"><div class="dash-num">{st.session_state.total_tokens:,}</div><div class="dash-lbl">TOKENS</div></div>
            <div class="dash-card"><div class="dash-num">{len(st.session_state.liked_messages)}</div><div class="dash-lbl">❤️ LIKES</div></div>
            <div class="dash-card"><div class="dash-num">{len(st.session_state.conversation_history)}</div><div class="dash-lbl">HISTORIQUE</div></div>
        </div>
        <div class="stat-badge">⏱️ SESSION : {st.session_state.session_start}</div>
        <div class="stat-badge">🤖 {ai_c} RÉPONSES</div>""", unsafe_allow_html=True)
        if hasattr(st.session_state,'engine'):
            stats=st.session_state.engine.get_stats()
            st.markdown(f'<div class="stat-badge">⚡ CLÉ #{stats.get("cle_active",1)} | {stats.get("modele_actif","")[:18]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    # Historique
    hc1,hc2=st.columns(2)
    with hc1:
        if st.button("💾 SAUVER", use_container_width=True):
            save_conv(); st.toast(T["saved"])
    with hc2:
        if st.button(T["new_conv"][:12]+"...", use_container_width=True):
            save_conv()
            for k in ["messages","fichiers_contexte","liked_messages","total_tokens"]:
                st.session_state[k]=[]; st.session_state.liked_messages=set(); st.session_state.total_tokens=0
            st.rerun()

    if st.session_state.conversation_history:
        with st.expander(f"📜 ({len(st.session_state.conversation_history)})"):
            for i,c in enumerate(reversed(st.session_state.conversation_history[-5:])):
                st.markdown(f'<div class="stat-badge">📅 {c["date"]}</div>', unsafe_allow_html=True)
                if st.button(f"↩️ #{len(st.session_state.conversation_history)-i}",key=f"rst_{i}"):
                    st.session_state.messages=c["messages"]; st.rerun()

    st.markdown('<div style="text-align:center;margin-top:12px;font-family:Rajdhani,sans-serif;color:rgba(150,150,200,0.28);font-size:0.7rem;line-height:1.9;">REIHANA v3.0 MEGA<br>© Khedim Benyakhlef<br>Biny-Joe · 2025</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# MAIN — HEADER
# ═══════════════════════════════════════════
ch, cm2 = st.columns([3,2])
with ch: st.markdown(f'<div style="font-family:Orbitron,monospace;color:{p};font-size:1.25rem;font-weight:700;letter-spacing:5px;padding:8px 0;">⬡ REIHANA · INTERFACE IA v3.0</div>', unsafe_allow_html=True)
with cm2:
    b=("🌐 " if st.session_state.web_search_on else "")+("🧠 " if st.session_state.deep_think else "")+f"🌸 {T['active']}"
    st.markdown(f'<div class="stat-badge" style="margin-top:8px;">{b}</div>', unsafe_allow_html=True)
st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# MESSAGES
# ═══════════════════════════════════════════
if not st.session_state.messages:
    st.markdown(f'<div class="msg-reihana">{T["welcome"]}</div>', unsafe_allow_html=True)

for i,msg in enumerate(st.session_state.messages):
    if msg["role"]=="user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        content=msg["content"]
        st.markdown(f'<div class="msg-reihana">{content}</div>', unsafe_allow_html=True)

        # Action buttons
        ca,cb,cc,cd,_=st.columns([1.1,1.1,1.1,1.5,3])
        liked=i in st.session_state.liked_messages
        with ca:
            if st.button("💖" if liked else "❤️", key=f"lk{i}", use_container_width=True):
                (st.session_state.liked_messages.discard if liked else st.session_state.liked_messages.add)(i); st.rerun()
        with cb:
            if st.button("📋", key=f"cp{i}", use_container_width=True):
                sf=safe_js(content)
                st.markdown(f"<script>navigator.clipboard.writeText('{sf}');</script>", unsafe_allow_html=True)
                st.toast(T["copied"])
        with cc:
            if st.button("🔊 Lire", key=f"sp{i}", use_container_width=True):
                    import streamlit.components.v1 as components
                    clean = msg["content"].replace("'"," ").replace('"',' ').replace('`',' ').replace(chr(10),' ')[:300]
                    components.html(f"""<script>
                    var u = new SpeechSynthesisUtterance('{clean}');
                    u.lang = window.reiConfig ? window.reiConfig.lang : 'fr-FR'; u.rate = window.reiConfig ? window.reiConfig.rate : 1.1; u.pitch = window.reiConfig ? window.reiConfig.pitch : 1.5; var vx=window.speechSynthesis.getVoices(); var fv=vx.filter(v=>v.lang.startsWith(u.lang.split('-')[0])); if(fv[0])u.voice=fv[0];
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(u);
                    </script>""", height=0)
        with cd:
            if st.button("🔄 Regen", key=f"rg{i}", use_container_width=True):
                if i>0 and st.session_state.messages[i-1]["role"]=="user":
                    st.session_state.regen_index=i; st.session_state.regen_question=st.session_state.messages[i-1]["content"]; st.rerun()

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════
# INPUT
# ═══════════════════════════════════════════
ci, cs2 = st.columns([5,1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")

# ═══════════════════════════════════════════
# TRAITEMENT — REGEN
# ═══════════════════════════════════════════
if st.session_state.regen_index is not None:
    idx=st.session_state.regen_index; q=st.session_state.regen_question
    if q:
        rep,res,_=process_msg(q,regen=True,regen_idx=idx)
        st.session_state.messages[idx]["content"]=rep
        st.session_state.mémoire.add_exchange(st.session_state.user_id,q,rep)
        st.markdown(f"<script>setTimeout(()=>{{window.playNotif();setTimeout(()=>window.reihanaSpeak('{safe_js(rep)}'),400);}},200);</script>", unsafe_allow_html=True)
    st.session_state.regen_index=None; st.session_state.regen_question=""; st.rerun()

# ═══════════════════════════════════════════
# TRAITEMENT — ENVOI
# ═══════════════════════════════════════════
if send_btn and user_input and user_input.strip():
    question=user_input.strip()
    st.session_state.messages.append({"role":"user","content":question})
    rep,res,web_res=process_msg(question)

    if web_res:
        wh='<div style="font-family:Orbitron,monospace;font-size:0.58rem;color:#00cc88;margin:4px 0;letter-spacing:1px;">🌐 SOURCES</div>'
        for r in web_res[:3]:
            if r.get('url'): wh+=f'<div class="web-card">🔗 <a href="{r["url"]}" target="_blank" style="color:#00cc88;">{r["title"][:55]}</a></div>'
        st.markdown(wh, unsafe_allow_html=True)

    st.session_state.mémoire.add_exchange(st.session_state.user_id,question,rep)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.57rem;color:rgba(150,150,200,0.38);text-align:right;margin:-3px 0 5px 0;">⚡ {res.get("model","")[:26]} · {res.get("tokens",0)} tokens</div>', unsafe_allow_html=True)
    st.markdown(f"<script>setTimeout(()=>{{window.playNotif();setTimeout(()=>window.reihanaSpeak('{safe_js(rep)}'),400);}},200);</script>", unsafe_allow_html=True)
    st.rerun()

# ═══════════════════════════════════════════
# SUGGESTIONS
# ═══════════════════════════════════════════
st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
st.markdown(f'<div style="font-family:Orbitron,monospace;color:rgba({g},0.45);font-size:0.6rem;letter-spacing:3px;margin-bottom:8px;">SUGGESTIONS RAPIDES</div>', unsafe_allow_html=True)
scols=st.columns(len(T["suggestions"]))
for i,(col,sug) in enumerate(zip(scols,T["suggestions"])):
    with col:
        if st.button(sug,key=f"sug{i}",use_container_width=True):
            st.session_state.messages.append({"role":"user","content":sug})
            rep,res,_=process_msg(sug)
            st.session_state.messages.append({"role":"assistant","content":rep})
            st.markdown(f"<script>setTimeout(()=>{{window.playNotif();setTimeout(()=>window.reihanaSpeak('{safe_js(rep)}'),400);}},200);</script>", unsafe_allow_html=True)
            st.rerun()