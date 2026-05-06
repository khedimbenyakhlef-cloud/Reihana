"""
REIHANA v3.0 MEGA EDITION
Fondée par Khedim Benyakhlef (Biny-Joe)
"""
import streamlit as st
import sys, os, json, time, tempfile, urllib.request, urllib.parse
import base64
import hashlib
try:
    from gtts import gTTS
    GTTS_OK = True
except:
    GTTS_OK = False
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# ═══════════════════════════════════════════
# REIHANA TTS - VRAIE VOIX FEMININE gTTS
# ═══════════════════════════════════════════
def detect_text_lang(text):
    """Détecte la langue du texte automatiquement"""
    ar_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if ar_chars > len(text) * 0.15:
        return "ar"
    en_words = ['the','is','are','what','how','who','can','you','please','help','tell','me','my','your','i','we','they','this','that']
    words = text.lower().split()
    en_count = sum(1 for w in words[:20] if w in en_words)
    if en_count >= 2:
        return "en"
    return "fr"

def smart_chunk_text(text, max_chars=450):
    """Découpe le texte en morceaux intelligents pour gTTS"""
    # Nettoyage Markdown
    import re
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    clean = re.sub(r'\*(.*?)\*', r'\1', clean)
    clean = re.sub(r'#+ ', '', clean)
    clean = re.sub(r'`[^`]*`', '', clean)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\[.*?\]\(.*?\)', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    if len(clean) <= max_chars:
        return [clean]
    
    # Découper sur les ponctuations
    chunks = []
    current = ""
    # Séparateurs: . ! ? ; pour FR/EN, et ۔ . ؟ ! pour AR
    separators = re.split(r'(?<=[.!?;،۔؟])\s+', clean)
    
    for part in separators:
        part = part.strip()
        if not part:
            continue
        candidate = (current + " " + part).strip() if current else part
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # Si le morceau lui-même est trop long, couper sur les virgules
            if len(part) > max_chars:
                sub_parts = re.split(r'(?<=[,،])\s+', part)
                sub_current = ""
                for sp in sub_parts:
                    sp = sp.strip()
                    if not sp:
                        continue
                    sub_candidate = (sub_current + " " + sp).strip() if sub_current else sp
                    if len(sub_candidate) <= max_chars:
                        sub_current = sub_candidate
                    else:
                        if sub_current:
                            chunks.append(sub_current)
                        sub_current = sp[:max_chars]
                if sub_current:
                    chunks.append(sub_current)
                current = ""
            else:
                current = part
    if current:
        chunks.append(current)
    
    return [c for c in chunks if c.strip()]

def reihana_tts(text, lang=None):
    """Génère un audio MP3 base64 avec gTTS - voix féminine multilingue"""
    if not GTTS_OK:
        return None
    try:
        # Auto-détection de la langue si non précisée
        if lang is None:
            lang = detect_text_lang(text)
        
        # Mapping langue UI → code gTTS
        lang_map = {
            "fr": "fr", "🇫🇷 Français": "fr",
            "ar": "ar", "🇩🇿 العربية": "ar",
            "en": "en", "🇬🇧 English": "en"
        }
        gtts_lang = lang_map.get(lang, detect_text_lang(text))
        
        # Découpage intelligent
        chunks = smart_chunk_text(text, max_chars=450)
        if not chunks:
            return None
        
        # Générer chaque chunk et concaténer les MP3
        all_audio = b""
        for chunk in chunks[:6]:  # max 6 chunks pour éviter timeout
            if not chunk.strip():
                continue
            try:
                tts = gTTS(text=chunk, lang=gtts_lang, slow=False)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts.save(f.name)
                    fname = f.name
                with open(fname, "rb") as af:
                    all_audio += af.read()
                os.unlink(fname)
            except Exception:
                continue
        
        if not all_audio:
            return None
        
        b64 = base64.b64encode(all_audio).decode()
        return b64
    except Exception:
        return None

def play_reihana_voice(text, lang=None, mood="calm"):
    """Joue la voix gTTS de REIHANA avec harmonie musicale et animation avatar"""
    b64 = reihana_tts(text, lang)
    if b64:
        import streamlit.components.v1 as _comp
        audio_html = f"""
<audio id="reiVoiceGTTS" style="display:none">
  <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
</audio>
<script>
(function(){{
  var v = document.getElementById("reiVoiceGTTS");
  if(!v) return;

  // ── Signal harmonie : baisser la musique via toutes les iframes ──
  function broadcastToIframes(fnName){{
    try{{
      // Chercher toutes les iframes Streamlit dans la page parent
      var iframes = window.parent.document.querySelectorAll("iframe");
      iframes.forEach(function(fr){{
        try{{
          if(fr.contentWindow && fr.contentWindow[fnName]){{
            fr.contentWindow[fnName]();
          }}
        }}catch(e){{}}
      }});
      // Aussi essayer window.parent directement
      if(window.parent[fnName]) window.parent[fnName]();
    }}catch(e){{}}
  }}

  function startTalking(){{
    // Baisser musique d'ambiance
    broadcastToIframes("reiVoiceStart");
    // Animation avatar grand fond
    var av = window.parent.document.getElementById("reiBgAvatar");
    if(av) av.classList.add("talking");
    // Animation avatar sidebar
    var hm = window.parent.document.querySelector(".holo-mouth");
    if(hm) hm.classList.add("speaking");
    var vb = window.parent.document.querySelector(".voice-bars");
    if(vb) vb.classList.add("active");
    var ha = window.parent.document.querySelector(".hologram-avatar");
    if(ha) ha.classList.add("speaking");
    // Changer mood musique
    broadcastToIframes("reiChangeMood_{mood}");
    try{{
      var iframes = window.parent.document.querySelectorAll("iframe");
      iframes.forEach(function(fr){{
        try{{
          if(fr.contentWindow && fr.contentWindow.reiChangeMood){{
            fr.contentWindow.reiChangeMood("{mood}");
          }}
        }}catch(e){{}}
      }});
    }}catch(e){{}}
  }}

  function stopTalking(){{
    // Remonter musique d'ambiance
    broadcastToIframes("reiVoiceEnd");
    var av = window.parent.document.getElementById("reiBgAvatar");
    if(av) av.classList.remove("talking");
    var hm = window.parent.document.querySelector(".holo-mouth");
    if(hm) hm.classList.remove("speaking");
    var vb = window.parent.document.querySelector(".voice-bars");
    if(vb) vb.classList.remove("active");
    var ha = window.parent.document.querySelector(".hologram-avatar");
    if(ha) ha.classList.remove("speaking");
  }}

  v.onplay = startTalking;
  v.onended = stopTalking;
  v.onerror = stopTalking;

  setTimeout(function(){{
    v.play().then(function(){{
      startTalking();
    }}).catch(function(e){{
      console.log("gTTS autoplay bloqué:", e);
      document.addEventListener("click", function _once(){{
        v.play();
        document.removeEventListener("click", _once);
      }}, {{once: true}});
    }});
  }}, 400);
}})();
</script>"""
        _comp.html(audio_html, height=0)
        return True
    return False

# ═══════════════════════════════════════════
# REIHANA CHANT — CHANSON gTTS SYNCHRONISÉE
# ═══════════════════════════════════════════
def detect_song(text):
    """Détecte si le texte est une chanson écrite par REIHANA.
    Retourne (is_song, mood, lang, verses) ou (False, ...)"""
    import re
    lower = text.lower()
    
    # Indicateurs qu'il s'agit d'une chanson
    song_keywords_fr = ["couplet","refrain","pont","verse","chorus","bridge","♪","♫","🎵","🎶","🎤","strophe","mélodie","chanson","ritournelle"]
    song_keywords_ar = ["أغنية","كوبليه","لازمة","مقطع","جسر","موسيقى","لحن","غناء"]
    song_keywords_en = ["chorus","verse","bridge","song","lyric","melody","hook","refrain"]
    
    has_song_kw = any(kw in lower for kw in song_keywords_fr+song_keywords_en) or                   any(kw in text for kw in song_keywords_ar)
    
    # Détecter structure en vers (lignes courtes répétitives)
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 3]
    short_lines = [l for l in lines if len(l) < 80]
    has_verse_structure = len(short_lines) >= 4 and len(short_lines) >= len(lines) * 0.5
    
    if not (has_song_kw or has_verse_structure):
        return False, "calm", "fr", []
    
    # Détecter la langue
    lang = detect_text_lang(text)
    
    # Détecter le mood de la chanson
    mood = "calm"
    if any(w in lower for w in ["amour","love","coeur","tender","romantique","حب","عشق","رومانسي"]):
        mood = "romantic"
    elif any(w in lower for w in ["triste","sad","pleur","larme","حزن","بكاء","دموع"]):
        mood = "sad"
    elif any(w in lower for w in ["joie","joyeux","fête","happy","dance","رقص","فرح","سعيد"]):
        mood = "happy"
    elif any(w in lower for w in ["fort","puissant","epic","guerre","héros","قوة","بطل","ملحمة"]):
        mood = "epic"
    elif any(w in lower for w in ["mystère","secret","nuit","ombre","lune","ليل","قمر","سر"]):
        mood = "mystery"
    elif any(w in lower for w in ["الله","قرآن","نبي","إسلام","ديني","روح"]):
        mood = "arabic"
    
    # Extraire les vers (nettoyer les titres de sections)
    section_labels = ["couplet","refrain","pont","bridge","chorus","verse","intro","outro",
                      "كوبليه","لازمة","مقطع","جسر","intro","outro","🎵","🎶","♪","♫","**"]
    verses = []
    for line in lines:
        l = line.strip()
        # Ignorer les labels de section (lignes qui ne sont QUE des labels)
        import re as _re
        clean_l = _re.sub(r'[*#_~`]', '', l).strip().lower()
        is_label = any(clean_l.startswith(lbl.lower()) or clean_l == lbl.lower() 
                      for lbl in section_labels)
        is_label = is_label or _re.match(r'^(couplet|refrain|pont|chorus|verse|bridge|intro|outro|كوبليه|لازمة|مقطع)\s*(\d+)?\s*[:\-—]?\s*$', clean_l, _re.IGNORECASE)
        if not is_label and len(l) > 3:
            # Nettoyer les symboles musicaux
            verse = _re.sub(r'[♪♫🎵🎶🎤*#_~`]', '', l).strip()
            verse = _re.sub(r'^\s*[-•–—]\s*', '', verse).strip()
            if verse and len(verse) > 3:
                verses.append(verse)
    
    return True, mood, lang, verses[:30]  # max 30 vers


def reihana_tts_slow(text, lang="fr"):
    """gTTS avec slow=True pour effet chant — voix plus lente et mélodieuse"""
    if not GTTS_OK:
        return None
    try:
        lang_map = {"fr": "fr", "ar": "ar", "en": "en",
                    "🇫🇷 Français": "fr", "🇩🇿 العربية": "ar", "🇬🇧 English": "en"}
        gtts_lang = lang_map.get(lang, detect_text_lang(text))
        
        import re as _re
        clean = _re.sub(r'[*#_~`♪♫🎵🎶🎤]', '', text).strip()
        clean = _re.sub(r'\s+', ' ', clean)
        if not clean:
            return None
        
        tts = gTTS(text=clean[:400], lang=gtts_lang, slow=True)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            fname = f.name
        with open(fname, "rb") as af:
            b64 = base64.b64encode(af.read()).decode()
        os.unlink(fname)
        return b64
    except Exception:
        return None


def play_song(verses, lang="fr", mood="calm"):
    """Joue la chanson vers par vers avec gTTS slow + harmonie musicale"""
    if not verses or not GTTS_OK:
        return False
    
    import streamlit.components.v1 as _comp
    
    # Générer audio pour chaque vers (max 20 vers)
    audio_chunks = []
    for verse in verses[:20]:
        b64 = reihana_tts_slow(verse, lang=lang)
        if b64:
            audio_chunks.append({"text": verse[:60], "b64": b64})
    
    if not audio_chunks:
        return False
    
    # Construire la playlist JSON pour JS
    import json as _json
    playlist_json = _json.dumps([{"t": v["text"], "b": v["b64"]} for v in audio_chunks])
    
    song_html = f"""
<div id="reiSongPlayer" style="display:none"></div>
<script>
(function(){{
  var playlist = {playlist_json};
  var idx = 0;
  var mood = "{mood}";
  var lang = "{lang}";
  
  // Broadcast mood + voice start à toutes les iframes
  function broadcast(fnName, arg){{
    try{{
      var iframes = window.parent.document.querySelectorAll("iframe");
      iframes.forEach(function(fr){{
        try{{
          if(fr.contentWindow){{
            if(arg !== undefined && fr.contentWindow[fnName]){{
              fr.contentWindow[fnName](arg);
            }} else if(fr.contentWindow[fnName]){{
              fr.contentWindow[fnName]();
            }}
          }}
        }}catch(e){{}}
      }});
    }}catch(e){{}}
  }}
  
  function startAnim(){{
    var av = window.parent.document.getElementById("reiBgAvatar");
    if(av) av.classList.add("talking");
    var hm = window.parent.document.querySelector(".holo-mouth");
    if(hm) hm.classList.add("speaking");
    var vb = window.parent.document.querySelector(".voice-bars");
    if(vb) vb.classList.add("active");
    var ha = window.parent.document.querySelector(".hologram-avatar");
    if(ha) ha.classList.add("speaking");
  }}
  
  function stopAnim(){{
    var av = window.parent.document.getElementById("reiBgAvatar");
    if(av) av.classList.remove("talking");
    var hm = window.parent.document.querySelector(".holo-mouth");
    if(hm) hm.classList.remove("speaking");
    var vb = window.parent.document.querySelector(".voice-bars");
    if(vb) vb.classList.remove("active");
    var ha = window.parent.document.querySelector(".hologram-avatar");
    if(ha) ha.classList.remove("speaking");
    // Remonter musique
    broadcast("reiVoiceEnd");
  }}
  
  function playVerse(i){{
    if(i >= playlist.length){{
      stopAnim();
      return;
    }}
    var item = playlist[i];
    
    // Changer mood musical selon index (intro puis mood principal)
    if(i === 0){{
      broadcast("reiChangeMood", mood);
      broadcast("reiVoiceStart");
      startAnim();
    }}
    
    var audio = new Audio("data:audio/mp3;base64," + item.b);
    audio.volume = 1.0;
    
    audio.onended = function(){{
      // Pause musicale entre les vers (rythme)
      var pause = lang === "ar" ? 700 : 500;
      setTimeout(function(){{ playVerse(i + 1); }}, pause);
    }};
    
    audio.onerror = function(){{
      setTimeout(function(){{ playVerse(i + 1); }}, 300);
    }};
    
    audio.play().catch(function(){{
      setTimeout(function(){{ playVerse(i + 1); }}, 300);
    }});
  }}
  
  // Démarrer après courte pause (attendre que musique change)
  setTimeout(function(){{ playVerse(0); }}, 600);
}})();
</script>"""
    
    _comp.html(song_html, height=0)
    return True


# ═══════════════════════════════════════════
# AVATAR BACKGROUND SEMI-RÉALISTE
# ═══════════════════════════════════════════
st.markdown("""
<div id="reiBackground" style="
  position:fixed;
  top:50%;
  left:62%;
  transform:translate(-50%,-50%);
  width:750px;
  height:750px;
  z-index:1;
  pointer-events:none;
  opacity:0.72;
  filter:drop-shadow(0 0 40px rgba(0,255,255,0.35));
">
<svg id="reiBgAvatar" viewBox="0 0 400 520" xmlns="http://www.w3.org/2000/svg" width="520" height="520">
  <defs>
    <radialGradient id="skinBG" cx="45%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ffe8d5"/>
      <stop offset="50%" stop-color="#f5c8a0"/>
      <stop offset="100%" stop-color="#e0a070"/>
    </radialGradient>
    <radialGradient id="hairBG" cx="50%" cy="20%" r="70%">
      <stop offset="0%" stop-color="#6600cc"/>
      <stop offset="50%" stop-color="#3300aa"/>
      <stop offset="100%" stop-color="#110033"/>
    </radialGradient>
    <radialGradient id="eyeBG" cx="40%" cy="35%" r="60%">
      <stop offset="0%" stop-color="#aaffff"/>
      <stop offset="40%" stop-color="#00ccff"/>
      <stop offset="100%" stop-color="#0044bb"/>
    </radialGradient>
    <radialGradient id="lipBG" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ff88aa"/>
      <stop offset="100%" stop-color="#cc4466"/>
    </radialGradient>
    <radialGradient id="clothBG" cx="50%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#220066"/>
      <stop offset="60%" stop-color="#110033"/>
      <stop offset="100%" stop-color="#050015"/>
    </radialGradient>
    <radialGradient id="chkBG" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="rgba(255,150,120,0.6)"/>
      <stop offset="100%" stop-color="rgba(255,150,120,0)"/>
    </radialGradient>
    <radialGradient id="sakBG" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffbbdd"/>
      <stop offset="100%" stop-color="#ff5599"/>
    </radialGradient>
    <filter id="softBG"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="glowBG"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="bodyBG" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#220066"/>
      <stop offset="50%" stop-color="#110044"/>
      <stop offset="100%" stop-color="#050020"/>
    </linearGradient>
  </defs>
  <style>
    #reiBgAvatar {
      animation: bgFloat 6s ease-in-out infinite;
      transform-origin: 200px 260px;
    }
    @keyframes bgFloat {
      0%,100% { transform: translateY(0px) rotate(0deg); }
      25% { transform: translateY(-14px) rotate(1deg); }
      50% { transform: translateY(-5px) rotate(0deg); }
      75% { transform: translateY(10px) rotate(-1deg); }
    }
    #bgEyelidL, #bgEyelidR {
      animation: bgBlink 4s ease-in-out infinite;
    }
    #bgEyelidR { animation-delay: 0.05s; }
    @keyframes bgBlink {
      0%,90%,100% { opacity: 0; }
      92%,98% { opacity: 1; }
    }
    #bgPupilL {
      animation: bgLookL 7s ease-in-out infinite;
      transform-origin: 163px 205px;
    }
    #bgPupilR {
      animation: bgLookR 7s ease-in-out infinite;
      transform-origin: 237px 205px;
    }
    @keyframes bgLookL {
      0%,100% { transform: translate(0,0); }
      20% { transform: translate(5px,-2px); }
      40% { transform: translate(-4px,3px); }
      60% { transform: translate(3px,4px); }
      80% { transform: translate(-5px,-1px); }
    }
    @keyframes bgLookR {
      0%,100% { transform: translate(0,0); }
      20% { transform: translate(5px,-2px); }
      40% { transform: translate(-4px,3px); }
      60% { transform: translate(3px,4px); }
      80% { transform: translate(-5px,-1px); }
    }
    #bgLipT {
      animation: bgTalk 0.3s ease-in-out infinite paused;
    }
    #reiBgAvatar.talking #bgLipT {
      animation-play-state: running;
    }
    @keyframes bgTalk {
      0%,100% { d: path("M170,295 C180,288 192,285 200,285 C208,285 220,288 230,295"); }
      50% { d: path("M170,291 C180,282 192,278 200,278 C208,278 220,282 230,291"); }
    }
  </style>

  <!-- CORPS / ÉPAULES -->
  <ellipse cx="200" cy="480" rx="130" ry="90" fill="url(#bodyBG)"/>
  <path d="M80,420 C70,440 60,480 55,520 L345,520 C340,480 330,440 320,420 C290,400 250,390 200,390 C150,390 110,400 80,420 Z" fill="url(#clothBG)"/>
  <!-- Décolleté/Col -->
  <path d="M160,390 C170,410 185,420 200,422 C215,420 230,410 240,390 Z" fill="url(#skinBG)"/>
  <!-- Cou -->
  <rect x="178" y="355" width="44" height="45" rx="18" fill="url(#skinBG)"/>
  <!-- VISAGE -->
  <ellipse cx="200" cy="220" rx="105" ry="120" fill="url(#skinBG)"/>
  <!-- Oreilles -->
  <ellipse cx="97" cy="230" rx="14" ry="20" fill="url(#skinBG)"/>
  <ellipse cx="303" cy="230" rx="14" ry="20" fill="url(#skinBG)"/>
  <!-- Ombre visage -->
  <ellipse cx="200" cy="310" rx="80" ry="25" fill="rgba(180,120,80,0.25)"/>

  <!-- CHEVEUX ARRIÈRE -->
  <path d="M95,140 C75,180 55,280 60,390 L80,400 C70,300 80,200 95,160 Z" fill="url(#hairBG)"/>
  <path d="M305,140 C325,180 345,280 340,390 L320,400 C330,300 320,200 305,160 Z" fill="url(#hairBG)"/>
  <!-- Cheveux longs -->
  <path d="M80,200 C60,260 50,340 55,430 L90,440 C80,360 85,280 95,220 Z" fill="url(#hairBG)" opacity="0.8"/>
  <path d="M320,200 C340,260 350,340 345,430 L310,440 C320,360 315,280 305,220 Z" fill="url(#hairBG)" opacity="0.8"/>

  <!-- CHEVEUX AVANT / FRANGE -->
  <path d="M95,145 C100,100 130,70 165,60 C185,55 200,53 200,53 C200,53 215,55 235,60 C270,70 300,100 305,145 C280,110 245,90 200,88 C155,90 120,110 95,145 Z" fill="url(#hairBG)"/>
  <path d="M105,155 C115,120 140,95 170,85 C185,80 200,78 200,78 C200,78 215,80 230,85 C260,95 285,120 295,155 C270,130 240,115 200,114 C160,115 130,130 105,155 Z" fill="url(#hairBG)"/>
  <!-- Mèches frange -->
  <path d="M105,155 C100,170 98,185 105,195 C115,170 125,158 140,152 Z" fill="url(#hairBG)"/>
  <path d="M295,155 C300,170 302,185 295,195 C285,170 275,158 260,152 Z" fill="url(#hairBG)"/>
  <!-- Mèche centrale -->
  <path d="M185,75 C182,100 180,130 190,150 C195,140 200,120 200,100 C205,120 205,140 210,150 C220,130 218,100 215,75 C210,70 205,68 200,68 C195,68 190,70 185,75 Z" fill="url(#hairBG)"/>

  <!-- PAUPIÈRES ANIMÉES -->
  <path id="bgEyelidL" d="M136,194 C144,186 155,183 175,188 C183,192 188,198 188,205" stroke="#110030" stroke-width="18" fill="none" stroke-linecap="round" opacity="0"/>
  <path id="bgEyelidR" d="M264,194 C256,186 245,183 225,188 C217,192 212,198 212,205" stroke="#110030" stroke-width="18" fill="none" stroke-linecap="round" opacity="0"/>
  <!-- SOURCILS -->
  <path d="M140,170 C150,164 165,162 178,165" stroke="#220040" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M222,165 C235,162 250,164 260,170" stroke="#220040" stroke-width="4" fill="none" stroke-linecap="round"/>

  <!-- OEIL GAUCHE -->
  <ellipse cx="163" cy="205" rx="28" ry="22" fill="white"/>
  <ellipse cx="163" cy="205" rx="20" ry="21" fill="url(#eyeBG)"/>
  <ellipse cx="163" cy="205" rx="12" ry="13" fill="#001830"/>
  <ellipse cx="163" cy="205" rx="5" ry="5.5" fill="#000010"/>
  <ellipse cx="156" cy="197" rx="5" ry="4" fill="white" opacity="0.85"/>
  <ellipse cx="168" cy="212" rx="2.5" ry="2" fill="white" opacity="0.5"/>
  <!-- Cils gauche -->
  <path d="M138,195 C140,188 148,184 155,185" stroke="#110030" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M148,188 C148,180 152,175 157,177" stroke="#110030" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M135,198 C137,192 144,188 150,190" stroke="#110030" stroke-width="2" fill="none" stroke-linecap="round"/>
  <!-- Paupière gauche -->
  <path d="M136,194 C144,186 155,183 175,188 C183,192 188,198 188,205" stroke="#110030" stroke-width="3" fill="none" stroke-linecap="round"/>

  <!-- OEIL DROIT -->
  <ellipse cx="237" cy="205" rx="28" ry="22" fill="white"/>
  <ellipse cx="237" cy="205" rx="20" ry="21" fill="url(#eyeBG)"/>
  <ellipse cx="237" cy="205" rx="12" ry="13" fill="#001830"/>
  <ellipse cx="237" cy="205" rx="5" ry="5.5" fill="#000010"/>
  <ellipse cx="230" cy="197" rx="5" ry="4" fill="white" opacity="0.85"/>
  <ellipse cx="242" cy="212" rx="2.5" ry="2" fill="white" opacity="0.5"/>
  <!-- Cils droit -->
  <path d="M262,195 C260,188 252,184 245,185" stroke="#110030" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M252,188 C252,180 248,175 243,177" stroke="#110030" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M265,198 C263,192 256,188 250,190" stroke="#110030" stroke-width="2" fill="none" stroke-linecap="round"/>
  <!-- Paupière droite -->
  <path d="M264,194 C256,186 245,183 225,188 C217,192 212,198 212,205" stroke="#110030" stroke-width="3" fill="none" stroke-linecap="round"/>

  <!-- NEZ -->
  <path d="M195,225 C192,250 188,270 185,280 C190,283 200,285 215,280 C212,270 208,250 205,225 Z" fill="rgba(180,120,80,0.2)"/>
  <ellipse cx="188" cy="278" rx="8" ry="5" fill="rgba(160,100,60,0.3)"/>
  <ellipse cx="212" cy="278" rx="8" ry="5" fill="rgba(160,100,60,0.3)"/>

  <!-- JOUES -->
  <ellipse cx="138" cy="255" rx="32" ry="20" fill="url(#chkBG)"/>
  <ellipse cx="262" cy="255" rx="32" ry="20" fill="url(#chkBG)"/>

  <!-- BOUCHE -->
  <!-- lip orig replaced by animated above -->
  <path d="M170,295 C180,308 192,314 200,314 C208,314 220,308 230,295" fill="url(#lipBG)" opacity="0.9"/>
  <path d="M170,295 C180,308 192,314 200,314 C208,314 220,308 230,295" stroke="#cc4466" stroke-width="1.5" fill="none"/>
  <!-- Lèvre sup -->
  <path d="M170,295 C178,292 188,290 200,290 C212,290 222,292 230,295" fill="url(#lipBG)" opacity="0.7"/>
  <!-- Reflet lèvre -->
  <ellipse cx="195" cy="303" rx="12" ry="4" fill="rgba(255,200,210,0.4)"/>

  <!-- ACCESSOIRE CHEVEUX - épingle sakura -->
  <g transform="translate(268,105)" filter="url(#softBG)">
    <circle cx="0" cy="-8" r="7" fill="url(#sakBG)"/>
    <circle cx="7.5" cy="-2.5" r="7" fill="url(#sakBG)"/>
    <circle cx="4.6" cy="6.5" r="7" fill="url(#sakBG)"/>
    <circle cx="-4.6" cy="6.5" r="7" fill="url(#sakBG)"/>
    <circle cx="-7.5" cy="-2.5" r="7" fill="url(#sakBG)"/>
    <circle cx="0" cy="0" r="4" fill="#ffeeaa"/>
    <animateTransform attributeName="transform" type="rotate" values="0;8;0;-8;0" dur="5s" repeatCount="indefinite"/>
  </g>

  <!-- BOUCLES D OREILLES -->
  <circle cx="91" cy="248" r="8" fill="url(#sakBG)" opacity="0.9"/>
  <circle cx="91" cy="265" r="5" fill="url(#sakBG)" opacity="0.7"/>
  <circle cx="309" cy="248" r="8" fill="url(#sakBG)" opacity="0.9"/>
  <circle cx="309" cy="265" r="5" fill="url(#sakBG)" opacity="0.7"/>

  <!-- BOUCHE ANIMÉE IDs -->
  <path id="bgLipT" d="M170,295 C180,288 192,285 200,285 C208,285 220,288 230,295" stroke="#cc6680" stroke-width="3" fill="none" stroke-linecap="round"/>
  <ellipse id="bgMouthOpen" cx="200" cy="305" rx="0" ry="0" fill="#330010" opacity="0.9"/>
  <!-- REFLET LUMINEUX VISAGE -->
  <ellipse cx="170" cy="160" rx="35" ry="20" fill="rgba(255,255,255,0.06)" transform="rotate(-20,170,160)"/>

  <!-- PARTICULES AUTOUR -->
  <circle cx="50" cy="100" r="3" fill="rgba(0,255,255,0.4)"><animate attributeName="opacity" values="0.2;0.8;0.2" dur="3s" repeatCount="indefinite"/></circle>
  <circle cx="350" cy="150" r="2" fill="rgba(180,0,255,0.5)"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite"/></circle>
  <circle cx="40" cy="300" r="2.5" fill="rgba(0,200,255,0.4)"><animate attributeName="opacity" values="0.1;0.7;0.1" dur="4s" repeatCount="indefinite"/></circle>
  <circle cx="360" cy="320" r="3" fill="rgba(255,100,180,0.4)"><animate attributeName="opacity" values="0.2;0.9;0.2" dur="3.5s" repeatCount="indefinite"/></circle>
  <circle cx="100" cy="450" r="2" fill="rgba(0,255,200,0.3)"><animate attributeName="opacity" values="0.1;0.6;0.1" dur="5s" repeatCount="indefinite"/></circle>
</svg>
</div>
""", unsafe_allow_html=True)



st.set_page_config(page_title="REIHANA • IA", page_icon="🌸", layout="wide", initial_sidebar_state="expanded")

THEMES = {
    "🔵 Cyan Holographique": {"p":"#00ffff","s":"#0088ff","a":"#aa00ff","b1":"#0a0a2e","b2":"#000010","g":"0,255,255","br":"0,200,255"},
    "💜 Violet Cosmique":    {"p":"#cc88ff","s":"#8800ff","a":"#ff00cc","b1":"#1a0a2e","b2":"#0d0018","g":"150,0,255","br":"180,0,255"},
    "🌸 Rose Sakura":        {"p":"#ff88cc","s":"#ff0088","a":"#ffcc00","b1":"#2e0a1a","b2":"#1a000d","g":"255,100,180","br":"255,80,160"},
    "⚡ Or Futuriste":       {"p":"#ffcc00","s":"#ff8800","a":"#00ccff","b1":"#1a1400","b2":"#0d0a00","g":"255,200,0","br":"220,160,0"},
    "🟢 Matrix Vert":        {"p":"#00ff88","s":"#00cc44","a":"#00ffcc","b1":"#001a0d","b2":"#000d07","g":"0,255,100","br":"0,200,80"},
}

PERSONNALITES = {
    "🌸 Douce & Timide":      {"rate":1.05,"pitch":1.7,"emoji":"🌸","style":"Tu es REIHANA, douce et timide comme une petite fille de 12 ans. Tu utilises des expressions mignonnes, des '💕', tu dis 'oh !' quand tu es surprise. Tu parles avec beaucoup de douceur et bienveillance."},
    "⚡ Énergique & Curieuse": {"rate":1.25,"pitch":1.6,"emoji":"⚡","style":"Tu es REIHANA, super énergique et curieuse ! Tu mets des '!' partout, des '🔥', tu t'enthousiasmes pour tout, tu dis 'Oh incroyable !' et 'Waouh !' Tu as 12 ans et tu adores tout découvrir !"},
    "🌟 Intelligente & Mature":{"rate":1.1,"pitch":1.45,"emoji":"🌟","style":"Tu es REIHANA, intelligente et mature pour tes 12 ans. Tu t'exprimes avec précision et clarté. Tu structures tes réponses. Tu es bienveillante mais sérieuse quand il le faut."},
    "🎭 Mystérieuse & Poétique":{"rate":0.95,"pitch":1.5,"emoji":"🎭","style":"Tu es REIHANA, mystérieuse et poétique. Tu parles avec des métaphores et des images. Tu es contemplative et fascinante. Tu commences parfois par des pensées profondes."},
}

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

defs = {
    "messages":[],"user_id":"user_default","fichiers_contexte":[],
    "input_value":"","clear_input":False,"deep_think":False,"web_search_on":False,
    "liked_messages":set(),"regen_index":None,"regen_question":"",
    "theme":"🔵 Cyan Holographique","langue":"🇫🇷 Français","personnalite":"🌸 Douce & Timide",
    "music_on":False,"show_dashboard":False,"conversation_history":[],
    "total_tokens":0,"session_start":datetime.now().strftime("%H:%M"),
    "last_song":{"verses":[],"mood":"calm","lang":"fr","msg_index":-1},
    "voice_input": "",
    # ── NOUVEAU : fonctionnalités du livre ──
    "face_profiles": {},          # {user_id: encodage_visage_base64}
    "face_access_log": [],        # log des accès caméra
    "face_known_names": [],       # liste des noms enregistrés (côté Python)
    "last_face_name": "",         # dernier visage identifié
    "geo_alerts": [],             # historique alertes géolocalisation
    "conv_encrypted": True,       # chiffrement AES activé
    "aes_key": None,              # clé Fernet
    "library_poems": [],          # bibliothèque poèmes/textes
    "library_songs": [],          # bibliothèque chansons personnalisées
    "admin_dashboard_open": False,
    "suspicious_log": [],         # log questions suspectes
    "face_cam_active": False,     # caméra reconnaisance faciale active
    "gesture_cam_active": False,  # caméra gestes active
    "user_profiles": {},          # profils utilisateurs multi-personnes
    "current_profile": "default", # profil actif
    "wake_word": "reihana",       # mot d'activation
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

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&family=Share+Tech+Mono&display=swap');
.stApp{{background:radial-gradient(ellipse at 15% 40%,{b1} 0%,{b2} 50%,#000005 100%);background-attachment:fixed;}}
.stApp::before{{content:'';position:fixed;top:0;left:0;right:0;bottom:0;background:radial-gradient(circle at 10% 20%,rgba({g},0.04) 0%,transparent 50%),radial-gradient(circle at 90% 80%,rgba({g},0.06) 0%,transparent 50%);pointer-events:none;z-index:0;}}
.hologram-container{{position:relative;width:100%;text-align:center;padding:15px 0;}}
.hologram-avatar{{width:160px;height:160px;border-radius:50%;margin:0 auto;background:radial-gradient(circle,rgba({g},0.15) 0%,rgba({g},0.05) 50%,transparent 70%);border:2px solid rgba({g},0.6);box-shadow:0 0 30px rgba({g},0.5),0 0 70px rgba({g},0.2),inset 0 0 30px rgba({g},0.1);display:flex;align-items:center;justify-content:center;animation:holoPulse 3s ease-in-out infinite,holoRotate 8s linear infinite;position:relative;cursor:pointer;transition:all 0.3s ease;overflow:hidden;}}
.hologram-avatar.speaking{{animation:holoPulse 0.3s ease-in-out infinite,holoRotate 1.5s linear infinite!important;box-shadow:0 0 60px rgba({g},0.9),0 0 130px rgba({g},0.5),inset 0 0 60px rgba({g},0.3)!important;border-color:rgba({g},1)!important;}}
@keyframes holoPulse{{0%,100%{{box-shadow:0 0 30px rgba({g},0.5),0 0 70px rgba({g},0.2),inset 0 0 30px rgba({g},0.1);}}50%{{box-shadow:0 0 55px rgba({g},0.8),0 0 110px rgba({g},0.4),inset 0 0 55px rgba({g},0.25);}}}}
@keyframes holoRotate{{0%{{border-color:rgba({g},0.6);}}33%{{border-color:rgba({g},0.3);}}66%{{border-color:rgba({g},0.8);}}100%{{border-color:rgba({g},0.6);}}}}
.hologram-avatar::after{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;border-radius:50%;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba({g},0.04) 3px,rgba({g},0.04) 5px);animation:scanLines 1.5s linear infinite;pointer-events:none;z-index:10;}}
@keyframes scanLines{{0%{{background-position:0 0;}}100%{{background-position:0 80px;}}}}
.holo-mouth{{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);width:28px;height:5px;background:rgba({g},0.7);border-radius:3px;transition:all 0.08s ease;box-shadow:0 0 8px rgba({g},0.5);z-index:11;}}
.holo-mouth.speaking{{animation:mouthAnim 0.12s ease-in-out infinite alternate;}}
@keyframes mouthAnim{{0%{{height:4px;width:24px;border-radius:3px;}}100%{{height:16px;width:36px;border-radius:50% 50% 8px 8px;}}}}
.voice-bars{{display:none;justify-content:center;gap:3px;margin:8px auto;height:24px;align-items:flex-end;}}
.voice-bars.active{{display:flex;}}
.voice-bar{{width:4px;background:{p};border-radius:2px;box-shadow:0 0 6px rgba({g},0.7);}}
.voice-bar:nth-child(1){{animation:barAnim 0.5s ease-in-out infinite;height:8px;}}
.voice-bar:nth-child(2){{animation:barAnim 0.5s ease-in-out infinite 0.1s;height:16px;}}
.voice-bar:nth-child(3){{animation:barAnim 0.5s ease-in-out infinite 0.2s;height:24px;}}
.voice-bar:nth-child(4){{animation:barAnim 0.5s ease-in-out infinite 0.1s;height:16px;}}
.voice-bar:nth-child(5){{animation:barAnim 0.5s ease-in-out infinite;height:8px;}}
@keyframes barAnim{{0%,100%{{transform:scaleY(0.4);opacity:0.6;}}50%{{transform:scaleY(1);opacity:1;}}}}
.reihana-title{{font-family:'Orbitron',monospace!important;font-size:2.2rem!important;font-weight:900!important;background:linear-gradient(135deg,{p},{s},{a},{p});background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;text-align:center;letter-spacing:7px;margin:8px 0;}}
@keyframes gradientShift{{0%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}100%{{background-position:0% 50%;}}}}
.reihana-subtitle{{font-family:'Rajdhani',sans-serif;color:rgba({g},0.6);text-align:center;font-size:0.8rem;letter-spacing:4px;text-transform:uppercase;}}
.msg-reihana{{background:linear-gradient(135deg,rgba(0,20,50,0.92),rgba(0,10,35,0.85));border:1px solid rgba({br},0.3);border-left:3px solid {p};border-radius:0 15px 15px 15px;padding:14px 17px;margin:8px 0 4px 0;font-family:'Rajdhani',sans-serif;font-size:1rem;color:#c8f0ff;box-shadow:0 4px 20px rgba({g},0.12);line-height:1.6;}}
.msg-reihana::before{{content:'{PERS["emoji"]} REIHANA';font-family:'Orbitron',monospace;font-size:0.62rem;color:{p};display:block;margin-bottom:7px;letter-spacing:2px;}}
.msg-user{{background:linear-gradient(135deg,rgba(20,0,50,0.85),rgba(30,0,65,0.75));border:1px solid rgba({g},0.2);border-right:3px solid {a};border-radius:15px 0 15px 15px;padding:12px 15px;margin:8px 0;font-family:'Rajdhani',sans-serif;color:#e0d0ff;text-align:right;}}
.msg-user::before{{content:'VOUS 👤';font-family:'Orbitron',monospace;font-size:0.62rem;color:{a};display:block;margin-bottom:6px;letter-spacing:2px;}}
.think-box{{background:linear-gradient(135deg,rgba(60,0,120,0.25),rgba(40,0,90,0.15));border:1px solid rgba({g},0.15);border-left:3px solid {a};border-radius:0 10px 10px 10px;padding:10px 14px;margin:4px 0 8px 0;font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:rgba({g},0.8);}}
.stat-badge{{background:rgba({g},0.07);border:1px solid rgba({br},0.2);border-radius:8px;padding:7px 11px;font-family:'Orbitron',monospace;font-size:0.68rem;color:{p};text-align:center;margin:3px 0;}}
.stat-green{{background:rgba(0,200,100,0.08);border:1px solid rgba(0,200,100,0.25);border-radius:8px;padding:6px 11px;font-family:'Orbitron',monospace;font-size:0.65rem;color:#00cc88;text-align:center;margin:3px 0;}}
.stat-purple{{background:rgba(150,0,255,0.1);border:1px solid rgba(150,0,255,0.3);border-radius:8px;padding:6px 11px;font-family:'Orbitron',monospace;font-size:0.65rem;color:#bb66ff;text-align:center;margin:3px 0;animation:thinkPulse 2s ease-in-out infinite;}}
@keyframes thinkPulse{{0%,100%{{opacity:0.7;}}50%{{opacity:1;box-shadow:0 0 12px rgba(150,0,255,0.3);}}}}
.dash-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin:7px 0;}}
.dash-card{{background:rgba({g},0.06);border:1px solid rgba({br},0.2);border-radius:10px;padding:9px;text-align:center;}}
.dash-num{{font-family:'Orbitron',monospace;font-size:1.3rem;color:{p};font-weight:900;text-shadow:0 0 15px rgba({g},0.6);}}
.dash-lbl{{font-family:'Rajdhani',sans-serif;color:rgba({g},0.6);font-size:0.68rem;letter-spacing:2px;}}
.holo-line{{height:1px;background:linear-gradient(90deg,transparent,{p},{a},transparent);margin:12px 0;animation:hololine 3s ease-in-out infinite;}}
@keyframes hololine{{0%,100%{{opacity:0.35;}}50%{{opacity:1;}}}}
.status-online{{display:inline-block;width:7px;height:7px;background:#00ff88;border-radius:50%;animation:blink 2s ease-in-out infinite;margin-right:6px;box-shadow:0 0 6px #00ff88;}}
@keyframes blink{{0%,100%{{opacity:1;}}50%{{opacity:0.3;}}}}
.stButton>button{{background:linear-gradient(135deg,rgba({g},0.05),rgba({g},0.12))!important;border:1px solid rgba({br},0.4)!important;color:{p}!important;font-family:'Orbitron',monospace!important;font-size:0.72rem!important;letter-spacing:1.5px!important;border-radius:8px!important;transition:all 0.3s ease!important;}}
.stButton>button:hover{{background:linear-gradient(135deg,rgba({g},0.15),rgba({g},0.25))!important;box-shadow:0 0 18px rgba({g},0.4)!important;transform:translateY(-2px)!important;}}
.stTextArea textarea,.stTextInput input{{background:rgba(0,15,40,0.85)!important;border:1px solid rgba({br},0.35)!important;color:#c8f0ff!important;font-family:'Rajdhani',sans-serif!important;font-size:1rem!important;border-radius:10px!important;}}
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,#020218,#030325,{b2})!important;border-right:1px solid rgba({br},0.15)!important;}}
.stSelectbox>div>div{{background:rgba(0,15,40,0.85)!important;border:1px solid rgba({br},0.35)!important;color:#c8f0ff!important;}}
::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-track{{background:rgba(0,0,20,0.5);}}
::-webkit-scrollbar-thumb{{background:rgba({g},0.4);border-radius:2px;}}
.music-wave{{display:flex;justify-content:center;gap:2px;height:16px;align-items:flex-end;margin:4px 0;}}
.music-bar{{width:3px;background:{p};border-radius:1px;box-shadow:0 0 4px rgba({g},0.6);}}
.music-bar:nth-child(1){{animation:musicAnim 0.8s ease-in-out infinite;height:6px;}}
.music-bar:nth-child(2){{animation:musicAnim 0.8s ease-in-out infinite 0.15s;height:12px;}}
.music-bar:nth-child(3){{animation:musicAnim 0.8s ease-in-out infinite 0.3s;height:16px;}}
.music-bar:nth-child(4){{animation:musicAnim 0.8s ease-in-out infinite 0.15s;height:12px;}}
.music-bar:nth-child(5){{animation:musicAnim 0.8s ease-in-out infinite;height:6px;}}
@keyframes musicAnim{{0%,100%{{transform:scaleY(0.3);}}50%{{transform:scaleY(1);}}}}
.web-card{{background:rgba(0,30,15,0.6);border:1px solid rgba(0,200,100,0.2);border-left:2px solid #00cc88;border-radius:6px;padding:7px 10px;margin:3px 0;font-family:'Rajdhani',sans-serif;font-size:0.83rem;color:rgba(200,240,200,0.85);}}
@media(max-width:768px){{.hologram-avatar{{width:120px;height:120px;}}.reihana-title{{font-size:1.5rem!important;letter-spacing:4px;}}.msg-reihana,.msg-user{{padding:10px 12px;font-size:0.93rem;}}}}
</style>""", unsafe_allow_html=True)

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

    /* Nettoyage */
    var clean=text
        .replace(/\*\*(.*?)\*\*/g,'$1')
        .replace(/\*(.*?)\*/g,'$1')
        .replace(/<[^>]*>/g,'')
        .replace(/[#`\[\]]/g,'')
        .replace(/\n+/g,' ')
        .trim();
    if(!clean)return;

    /* Découpage en morceaux <=180 chars - contourne bug Chrome 250 chars */
    function splitChunks(str){{
        var out=[], cur='';
        var parts=str.split(/(?<=[.!?;])\s+/);
        if(!parts||!parts.length)parts=[str];
        for(var i=0;i<parts.length;i++){{
            var s=parts[i].trim();
            if(!s)continue;
            var candidate=cur?cur+' '+s:s;
            if(candidate.length<=180){{cur=candidate;}}
            else{{
                if(cur)out.push(cur);
                if(s.length>180){{
                    var sub='',subs=s.split(/,\s*/);
                    for(var j=0;j<subs.length;j++){{
                        var p=subs[j].trim();
                        if(!p)continue;
                        var c2=sub?sub+', '+p:p;
                        if(c2.length<=180){{sub=c2;}}
                        else{{if(sub)out.push(sub);sub=p;}}
                    }}
                    cur=sub;
                }}else{{cur=s;}}
            }}
        }}
        if(cur)out.push(cur);
        return out.filter(function(c){{return c.trim().length>0;}});
    }}

    var chunks=splitChunks(clean);
    if(!chunks.length)return;

    function startV(){{
        document.querySelector('.hologram-avatar')&&document.querySelector('.hologram-avatar').classList.add('speaking');
        document.querySelector('.holo-mouth')&&document.querySelector('.holo-mouth').classList.add('speaking');
        document.querySelector('.voice-bars')&&document.querySelector('.voice-bars').classList.add('active');
        var av=document.getElementById('reiBgAvatar');if(av)av.classList.add('talking');
    }}
    function stopV(){{
        document.querySelector('.hologram-avatar')&&document.querySelector('.hologram-avatar').classList.remove('speaking');
        document.querySelector('.holo-mouth')&&document.querySelector('.holo-mouth').classList.remove('speaking');
        document.querySelector('.voice-bars')&&document.querySelector('.voice-bars').classList.remove('active');
        var av=document.getElementById('reiBgAvatar');if(av)av.classList.remove('talking');
    }}

    function speakOne(voices,idx){{
        if(idx>=chunks.length){{stopV();return;}}
        var u=new SpeechSynthesisUtterance(chunks[idx]);
        u.lang=window.reiConfig.lang;
        u.rate=window.reiConfig.rate;
        u.pitch=window.reiConfig.pitch;
        u.volume=1;
        var fv=voices.filter(function(v){{return v.lang.startsWith(window.reiConfig.lang.split('-')[0]);}});
        var fem=fv.find(function(v){{return /female|femme|amelie|marie|zira|paulina/i.test(v.name);}})||fv[0];
        if(fem)u.voice=fem;
        if(idx===0)u.onstart=startV;
        u.onend=function(){{setTimeout(function(){{speakOne(voices,idx+1);}},60);}};
        u.onerror=function(){{setTimeout(function(){{speakOne(voices,idx+1);}},80);}};
        window.speechSynthesis.speak(u);
    }}

    var vv=window.speechSynthesis.getVoices();
    if(vv.length>0){{speakOne(vv,0);}}
    else{{window.speechSynthesis.onvoiceschanged=function(){{speakOne(window.speechSynthesis.getVoices(),0);}};}}
}}
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
var reiAudio=document.getElementById('reiMusicPlayer');
  reiAudio=document.createElement('audio');
  reiAudio.id='reiMusicPlayer';
  reiAudio.loop=true;
  reiAudio.volume=0.4;
  reiAudio.src='https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3';
  document.body.appendChild(reiAudio);
}}
if({str(st.session_state.music_on).lower()}){{reiAudio.play().catch(e=>console.log(e));}}
else{{reiAudio.pause();}}
</script>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 📚 MODULE 1 : CHIFFREMENT AES DES CONVERSATIONS (livre p.45)
# ═══════════════════════════════════════════════════════════════
def get_fernet():
    """Retourne la clé Fernet (AES), la crée si inexistante"""
    try:
        from cryptography.fernet import Fernet
        if not st.session_state.aes_key:
            st.session_state.aes_key = Fernet.generate_key()
        return Fernet(st.session_state.aes_key)
    except:
        return None

def encrypt_conversation(question, reponse):
    """Chiffre une conversation et la stocke en session_state (pas de fichier)"""
    try:
        if not st.session_state.conv_encrypted:
            return
        f = get_fernet()
        if not f:
            return
        data = json.dumps({
            "q": question, "r": reponse,
            "ts": datetime.now().isoformat(),
            "user": st.session_state.user_id
        })
        encrypted = f.encrypt(data.encode()).decode()
        if "conv_enc_log" not in st.session_state:
            st.session_state.conv_enc_log = []
        st.session_state.conv_enc_log.append(encrypted)
        # Garder max 100 en mémoire
        if len(st.session_state.conv_enc_log) > 100:
            st.session_state.conv_enc_log = st.session_state.conv_enc_log[-100:]
    except:
        pass

def decrypt_conversations():
    """Déchiffre et retourne les conversations depuis session_state"""
    try:
        f = get_fernet()
        if not f:
            return []
        results = []
        for line in st.session_state.get("conv_enc_log", []):
            try:
                decrypted = json.loads(f.decrypt(line.encode()).decode())
                results.append(decrypted)
            except:
                pass
        return results
    except:
        return []


# ═══════════════════════════════════════════════════════════════
# 🔍 MODULE 2 : DÉTECTION QUESTIONS SUSPECTES + GÉOLOCALISATION
# ═══════════════════════════════════════════════════════════════
RED_FLAGS = [
    "adresse", "où habites", "carte bancaire", "mot de passe", "password",
    "numéro de téléphone", "identité", "CNI", "passeport", "où es-tu",
    "your address", "credit card", "bank account", "where do you live",
    "أين تسكن", "كلمة السر", "رقم البطاقة"
]

def check_suspicious(text):
    """Détecte si une question est suspecte"""
    text_low = text.lower()
    for flag in RED_FLAGS:
        if flag.lower() in text_low:
            return True, flag
    return False, None

def get_geolocation():
    """Récupère la géolocalisation via IP"""
    try:
        import urllib.request, json
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=5) as r:
            data = json.loads(r.read().decode())
        return f"{data.get('city','?')}, {data.get('country_name','?')} ({data.get('ip','?')})"
    except:
        try:
            with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=4) as r:
                ip = json.loads(r.read().decode()).get("ip","?")
            return f"IP: {ip}"
        except:
            return "Position inconnue"

def handle_suspicious_question(question, flag):
    """Gère une question suspecte : log en session_state uniquement (pas de fichier)"""
    location = get_geolocation()
    alert = {
        "ts": datetime.now().isoformat(),
        "question": question,
        "flag": flag,
        "location": location,
        "user": st.session_state.user_id
    }
    st.session_state.suspicious_log.append(alert)
    # Garder max 50 alertes en mémoire
    if len(st.session_state.suspicious_log) > 50:
        st.session_state.suspicious_log = st.session_state.suspicious_log[-50:]
    return location


# ═══════════════════════════════════════════════════════════════
# 👥 MODULE 3 : PROFILS UTILISATEURS AVANCÉS (livre p.89)
# ═══════════════════════════════════════════════════════════════
def load_user_profiles():
    """Charge les profils depuis session_state (pas de fichier)"""
    return st.session_state.get("user_profiles", {})

def save_user_profiles(profiles):
    """Sauvegarde les profils en session_state (pas de fichier)"""
    st.session_state.user_profiles = profiles

def get_user_profile(user_id):
    """Retourne le profil d'un utilisateur ou un profil par défaut"""
    profiles = st.session_state.user_profiles
    if user_id not in profiles:
        profiles[user_id] = {
            "nom": user_id,
            "ton": "chaleureux",
            "langue": "fr",
            "niveau_detail": "normal",
            "historique_count": 0,
            "premiere_visite": datetime.now().isoformat(),
            "derniere_visite": datetime.now().isoformat(),
            "mots_interdits": [],
            "sujets_favoris": [],
            "humeur_habituelle": "neutre",
            "id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:12]
        }
        save_user_profiles(profiles)
    else:
        profiles[user_id]["derniere_visite"] = datetime.now().isoformat()
        profiles[user_id]["historique_count"] = profiles[user_id].get("historique_count",0) + 1
    return profiles[user_id]

def build_personalized_prompt(base_prompt, user_id):
    """Enrichit le prompt avec le profil utilisateur"""
    profile = get_user_profile(user_id)
    ton = profile.get("ton", "neutre")
    sujets = ", ".join(profile.get("sujets_favoris", [])[:3]) or "aucun spécifique"
    n = profile.get("historique_count", 0)
    
    prefix = f"[PROFIL {user_id[:8]}] Ton:{ton}, Visites:{n}, Sujets:{sujets}. "
    if n == 0:
        prefix += "C'est sa première visite — accueille-le chaleureusement. "
    elif n > 10:
        prefix += "C'est un utilisateur fidèle — sois familière et mémorable. "
    return prefix + base_prompt


# ═══════════════════════════════════════════════════════════════
# 📖 MODULE 4 : BIBLIOTHÈQUE POÈMES & TEXTES (livre p.95)
# ═══════════════════════════════════════════════════════════════
LIBRARY_DEFAULT = {
    "poemes": [
        {"titre": "Liberté", "auteur": "Paul Éluard", "texte": "Sur mes cahiers d'écolier, sur mon pupitre et les arbres, sur le sable sur la neige, j'écris ton nom. Liberté.", "langue": "fr"},
        {"titre": "نشيد المطر", "auteur": "بدر شاكر السياب", "texte": "عيناكِ غابتا نخيلٍ ساعةَ السَّحَر، أو شُرفتانِ راح ينأى عنهما القمر.", "langue": "ar"},
        {"titre": "Hope", "auteur": "Emily Dickinson", "texte": "Hope is the thing with feathers that perches in the soul, and sings the tune without the words, and never stops at all.", "langue": "en"},
    ],
    "proverbes": [
        {"titre": "Sagesse", "texte": "La connaissance est une lumière qui éclaire le chemin de ceux qui cherchent la vérité.", "langue": "fr"},
        {"titre": "حكمة", "texte": "العلم نور والجهل ظلام، فاطلب العلم ولو في الصين.", "langue": "ar"},
    ],
    "citations": [
        {"titre": "Ibn Khaldoun", "texte": "Celui qui ne connaît pas son histoire est condamné à la revivre.", "langue": "fr"},
        {"titre": "الإمام علي", "texte": "قيمة كل امرئ ما يحسنه.", "langue": "ar"},
    ]
}

def get_library():
    """Charge la bibliothèque depuis session_state (pas de fichier)"""
    if "library_data" not in st.session_state or not st.session_state.library_data:
        st.session_state.library_data = json.loads(json.dumps(LIBRARY_DEFAULT))
    return st.session_state.library_data

def save_library(lib):
    """Sauvegarde la bibliothèque en session_state (pas de fichier)"""
    st.session_state.library_data = lib


# ═══════════════════════════════════════════════════════════════
# 📊 MODULE 5 : DASHBOARD ADMIN (livre p.50)
# ═══════════════════════════════════════════════════════════════
def show_admin_dashboard():
    """Affiche le tableau de bord administrateur"""
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(0,20,40,0.95),rgba(0,10,25,0.9));
    border:1px solid rgba(0,255,200,0.3);border-radius:12px;padding:20px;margin:10px 0;">
    <div style="font-family:Orbitron,monospace;font-size:1rem;color:#00ffcc;letter-spacing:3px;margin-bottom:15px;">
    📊 DASHBOARD ADMIN — REIHANA SECURITY CENTER
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    
    # Stats
    n_msgs = len(st.session_state.messages)
    n_alerts = len(st.session_state.suspicious_log)
    n_tokens = st.session_state.total_tokens
    profiles = load_user_profiles()
    n_users = len(profiles)
    
    with c1:
        st.metric("💬 Messages", n_msgs)
    with c2:
        st.metric("⚠️ Alertes", n_alerts, delta=f"+{n_alerts}" if n_alerts else None)
    with c3:
        st.metric("⚡ Tokens", f"{n_tokens:,}")
    with c4:
        st.metric("👥 Profils", n_users)
    
    # Alertes suspectes
    if st.session_state.suspicious_log:
        st.markdown("### ⚠️ Questions Suspectes Détectées")
        for alert in reversed(st.session_state.suspicious_log[-5:]):
            st.markdown(f"""
            <div style="background:rgba(255,50,50,0.1);border:1px solid rgba(255,100,100,0.3);
            border-radius:8px;padding:10px;margin:4px 0;font-family:Rajdhani,sans-serif;">
            🚨 <b>{alert.get('ts','?')[:16]}</b> — 
            Flag: <code>{alert.get('flag','?')}</code> — 
            Position: {alert.get('location','?')} — 
            User: {alert.get('user','?')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Aucune alerte suspecte détectée")
    
    # Profils utilisateurs
    if profiles:
        st.markdown("### 👥 Profils Utilisateurs")
        for uid, prof in list(profiles.items())[:5]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{uid}** — Visites: {prof.get('historique_count',0)} — Ton: {prof.get('ton','?')} — Dernière: {prof.get('derniere_visite','?')[:10]}")
    
    # Conversations chiffrées
    st.markdown("### 🔐 Conversations Chiffrées (AES)")
    convs = decrypt_conversations()
    if convs:
        st.success(f"✅ {len(convs)} conversations sécurisées en mémoire")
        if st.checkbox("Afficher les 3 dernières"):
            for c in convs[-3:]:
                st.markdown(f"**{c.get('ts','?')[:16]}** — Q: {c.get('q','?')[:60]}...")
    else:
        st.info("Aucune conversation chiffrée stockée")
    
    # Bouton purge
    if st.button("🗑️ Purger les alertes", type="secondary"):
        st.session_state.suspicious_log = []
        try:
            pass  # pas de fichier à supprimer — stockage session_state
        except:
            pass
        st.success("Alertes purgées !")
        st.rerun()
    
    # ── Visages identifiés (nouveau) ──
    st.markdown("### 👁️ Accès Caméra — Visages Identifiés")
    face_log = st.session_state.face_access_log[-10:] if st.session_state.face_access_log else []
    if face_log:
        for entry in reversed(face_log):
            _fn = entry.get("name","?")
            _color = "#00ffcc" if _fn not in ("inconnu","?") else "#cc88ff"
            st.markdown(f"""
            <div style="background:rgba(0,20,40,0.8);border:1px solid rgba(0,200,150,0.2);
            border-radius:8px;padding:8px;margin:3px 0;font-family:Rajdhani,sans-serif;font-size:0.78rem;">
            👤 <b style="color:{_color};">{_fn}</b> · 
            {entry.get('age','?')}ans · {entry.get('gender','?')} · 
            😐 {entry.get('expression','?')} · 
            📷 cam:{entry.get('cam','?')} · 
            <span style="color:rgba(150,150,200,0.5);">{entry.get('ts','?')[:16]}</span>
            </div>
            """, unsafe_allow_html=True)
        known_names = st.session_state.get("face_known_names", [])
        if known_names:
            st.markdown(f"**Base visages enregistrés :** {', '.join(known_names)}")
    else:
        st.info("Aucun accès caméra enregistré")


# ═══════════════════════════════════════════════════════════════
# 🎵 MODULE 6 : BIBLIOTHÈQUE MUSICALE PERSONNALISÉE (livre p.96)
# ═══════════════════════════════════════════════════════════════
def recite_text(text, titre="", langue="fr"):
    """REIHANA récite un texte avec gTTS"""
    if not text:
        return
    full = f"{titre}. {text}" if titre else text
    play_reihana_voice(full, lang=langue)

def get_song_library():
    """Retourne la bibliothèque de chansons depuis session_state"""
    return st.session_state.get("library_songs", [])

def save_song_library(songs):
    """Sauvegarde en session_state"""
    st.session_state.library_songs = songs


# ═══════════════════════════════════════════════════════════════
# ✋ MODULE 7 : DÉTECTION GESTUELLE (MediaPipe - livre p.80)
# ═══════════════════════════════════════════════════════════════
GESTURE_HTML = """
<html><head>
<style>
  body{margin:0;background:transparent;font-family:Orbitron,monospace;}
  #gzone{display:flex;align-items:center;gap:10px;padding:4px;}
  #gBtn{width:44px;height:44px;border-radius:50%;border:2px solid rgba(0,255,100,0.5);
    background:rgba(0,20,10,0.9);color:#00ff88;font-size:18px;cursor:pointer;
    display:flex;align-items:center;justify-content:center;transition:all .2s;}
  #gBtn.active{border-color:#00ff44;background:rgba(0,80,20,0.5);animation:gPulse .8s infinite;}
  @keyframes gPulse{0%,100%{box-shadow:0 0 8px rgba(0,255,100,.4);}50%{box-shadow:0 0 20px rgba(0,255,100,.8);}}
  #gStatus{font-size:9px;letter-spacing:2px;color:rgba(0,255,100,0.5);}
  #gResult{font-size:11px;color:rgba(200,255,220,0.7);font-family:Rajdhani,sans-serif;}
</style></head><body>
<div id="gzone">
  <button id="gBtn" onclick="toggleGesture()" title="Détection gestuelle">✋</button>
  <div>
    <div id="gStatus">GESTE PRÊT</div>
    <div id="gResult">Cliquez ✋ pour activer</div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4/hands.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3/camera_utils.js" crossorigin="anonymous"></script>
<script>
var _active=false, _cam=null, _hands=null, _lastGesture='', _cooldown=false;
var gBtn=document.getElementById('gBtn');
var gStatus=document.getElementById('gStatus');
var gResult=document.getElementById('gResult');

function classifyGesture(landmarks){
  var wrist=landmarks[0];
  var indexTip=landmarks[8], indexMCP=landmarks[5];
  var middleTip=landmarks[12], middleMCP=landmarks[9];
  var ringTip=landmarks[16], ringMCP=landmarks[13];
  var pinkyTip=landmarks[20], pinkyMCP=landmarks[17];
  var thumbTip=landmarks[4], thumbIP=landmarks[3];
  
  var indexUp=indexTip.y<indexMCP.y;
  var middleUp=middleTip.y<middleMCP.y;
  var ringUp=ringTip.y<ringMCP.y;
  var pinkyUp=pinkyTip.y<pinkyMCP.y;
  var thumbUp=thumbTip.y<thumbIP.y;
  
  if(indexUp&&middleUp&&!ringUp&&!pinkyUp) return "✌️ DEUX DOIGTS — Activer IA";
  if(indexUp&&!middleUp&&!ringUp&&!pinkyUp) return "☝️ UN DOIGT — Valider";
  if(thumbUp&&!indexUp&&!middleUp&&!ringUp&&!pinkyUp) return "👍 POUCE — J'aime";
  if(!thumbUp&&!indexUp&&!middleUp&&!ringUp&&!pinkyUp) return "✊ POING — Pause";
  if(indexUp&&middleUp&&ringUp&&pinkyUp) return "🖐️ MAIN OUVERTE — Stop";
  return "🤚 Main détectée";
}

function sendGestureToStreamlit(gesture){
  if(_cooldown) return;
  _cooldown=true;
  setTimeout(function(){_cooldown=false;},2000);
  try{
    var url=window.location.href.split("?")[0]+"?gesture="+encodeURIComponent(gesture);
    window.parent.location.href=url;
  }catch(e){
    window.location.href=window.location.href.split("?")[0]+"?gesture="+encodeURIComponent(gesture);
  }
}

function toggleGesture(){
  if(_active){
    _active=false;
    gBtn.className='';gBtn.innerText='✋';
    gStatus.innerText='GESTE PRÊT';gResult.innerText='Cliquez ✋ pour activer';
    if(_cam)_cam.stop();
  }else{
    startGesture();
  }
}

function startGesture(){
  try{
    var video=document.createElement('video');
    video.style.display='none';
    document.body.appendChild(video);
    
    _hands=new Hands({locateFile:function(file){
      return 'https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4/'+file;
    }});
    _hands.setOptions({maxNumHands:1,modelComplexity:0,minDetectionConfidence:0.7,minTrackingConfidence:0.5});
    _hands.onResults(function(results){
      if(results.multiHandLandmarks&&results.multiHandLandmarks.length>0){
        var g=classifyGesture(results.multiHandLandmarks[0]);
        if(g!==_lastGesture){
          _lastGesture=g;
          gResult.innerText=g;
          if(g!='🤚 Main détectée') sendGestureToStreamlit(g);
        }
      }else{
        gResult.innerText='Montrez votre main...';
        _lastGesture='';
      }
    });
    
    navigator.mediaDevices.getUserMedia({video:true})
      .then(function(stream){
        video.srcObject=stream;
        video.play();
        _active=true;
        gBtn.className='active';gBtn.innerText='⏹';
        gStatus.innerText='✋ DÉTECTION ACTIVE';
        _cam=new Camera(video,{
          onFrame:async function(){await _hands.send({image:video});},
          width:320,height:240
        });
        _cam.start();
      })
      .catch(function(e){gStatus.innerText='🚫 Caméra refusée';});
  }catch(e){gStatus.innerText='⚠️ MediaPipe non dispo';gResult.innerText='Utilisez Chrome';}
}
</script>
</body></html>
"""

# ═══════════════════════════════════════════════════════════════
# 👁️ MODULE 8 : RECONNAISSANCE FACIALE v2 — IDENTIFICATION + CAMÉRA AV/AR
# ═══════════════════════════════════════════════════════════════
FACE_HTML = """
<html><head>
<style>
  body{margin:0;background:transparent;font-family:Orbitron,monospace;overflow:hidden;}
  #fzone{display:flex;align-items:center;gap:6px;padding:4px;flex-wrap:wrap;}
  #fBtn{width:40px;height:40px;border-radius:50%;border:2px solid rgba(150,50,255,0.5);
    background:rgba(20,0,40,0.9);color:#aa55ff;font-size:16px;cursor:pointer;
    display:flex;align-items:center;justify-content:center;transition:all .2s;}
  #fBtn.scanning{border-color:#ff5588;color:#ff5588;animation:fPulse .6s infinite;}
  #fCamSwitch{width:34px;height:34px;border-radius:50%;border:1px solid rgba(0,200,255,0.4);
    background:rgba(0,20,40,0.8);color:#00ccff;font-size:14px;cursor:pointer;
    display:flex;align-items:center;justify-content:center;}
  #fEnroll{font-size:9px;border:1px solid rgba(150,50,255,0.4);background:rgba(30,0,60,0.8);
    color:#cc88ff;padding:3px 7px;border-radius:6px;cursor:pointer;letter-spacing:1px;}
  @keyframes fPulse{0%,100%{box-shadow:0 0 8px rgba(255,50,100,.4);}50%{box-shadow:0 0 22px rgba(255,50,100,.9);}}
  #fStatus{font-size:9px;letter-spacing:2px;color:rgba(150,50,255,0.5);}
  #fResult{font-size:11px;color:rgba(220,180,255,0.9);font-family:Rajdhani,sans-serif;font-weight:600;}
  #fCanvas{display:none;width:220px;height:160px;border-radius:8px;border:1px solid rgba(150,50,255,0.4);margin-top:4px;}
  #fEnrollZone{display:none;background:rgba(20,0,40,0.95);border:1px solid rgba(150,50,255,0.4);
    border-radius:8px;padding:8px;margin-top:6px;width:220px;}
  #fEnrollZone input{width:90%;background:rgba(0,0,20,0.8);border:1px solid rgba(150,50,255,0.3);
    color:#cc88ff;font-size:10px;padding:4px 6px;border-radius:4px;outline:none;font-family:Rajdhani,sans-serif;}
  #fSaveBtn{margin-top:5px;font-size:9px;border:1px solid rgba(0,255,150,0.5);background:rgba(0,40,20,0.8);
    color:#00ff88;padding:3px 10px;border-radius:5px;cursor:pointer;width:100%;letter-spacing:1px;}
  #fKnownList{font-size:9px;color:rgba(180,150,255,0.6);margin-top:4px;letter-spacing:1px;}
  .fid-known{color:#00ffcc;font-size:12px;font-weight:700;}
  .fid-unknown{color:rgba(220,180,255,0.7);}
</style></head><body>
<div id="fzone">
  <button id="fBtn" onclick="toggleFace()" title="Reconnaissance faciale">👁️</button>
  <button id="fCamSwitch" onclick="switchCam()" title="Caméra av/ar">🔄</button>
  <button id="fEnroll" onclick="toggleEnroll()">➕ ENROL</button>
</div>
<div><div id="fStatus">CAMÉRA PRÊTE</div><div id="fResult">Cliquez 👁️ pour scanner</div></div>
<canvas id="fCanvas"></canvas>
<div id="fEnrollZone">
  <div style="font-size:9px;color:rgba(150,50,255,0.7);letter-spacing:2px;margin-bottom:4px;">ENREGISTRER VISAGE</div>
  <input id="fNameInput" placeholder="Nom de la personne..." maxlength="30"/>
  <button id="fSaveBtn" onclick="enrollFace()">📸 CAPTURER &amp; ENREGISTRER</button>
  <div id="fKnownList">Personnes connues: <span id="fKnownCount">0</span></div>
</div>
<script src="https://unpkg.com/face-api.js@0.22.2/dist/face-api.min.js"></script>
<script>
var _factive=false,_fstream=null,_fvideo=null,_fint=null;
var _facingMode='user'; // 'user'=avant, 'environment'=arrière
var _modelsLoaded=false;
var _knownFaces=[]; // [{name, descriptor}]
var fBtn=document.getElementById('fBtn');
var fStatus=document.getElementById('fStatus');
var fResult=document.getElementById('fResult');
var fCanvas=document.getElementById('fCanvas');
var fEnrollZone=document.getElementById('fEnrollZone');

// ── Charger les visages sauvegardés depuis localStorage ──
function loadKnownFaces(){
  try{
    var saved=localStorage.getItem('rei_known_faces');
    if(saved){
      var arr=JSON.parse(saved);
      _knownFaces=arr.map(function(f){
        return {name:f.name, descriptor:new Float32Array(f.descriptor)};
      });
    }
  }catch(e){}
  document.getElementById('fKnownCount').innerText=_knownFaces.length;
}

function saveKnownFaces(){
  try{
    var toSave=_knownFaces.map(function(f){
      return {name:f.name, descriptor:Array.from(f.descriptor)};
    });
    localStorage.setItem('rei_known_faces',JSON.stringify(toSave));
  }catch(e){}
  document.getElementById('fKnownCount').innerText=_knownFaces.length;
}

// ── Identifier un visage parmi les connus ──
function identifyFace(descriptor){
  if(_knownFaces.length===0) return null;
  var best=null, bestDist=0.52; // seuil de distance euclidienne
  _knownFaces.forEach(function(kf){
    var dist=faceapi.euclideanDistance(descriptor,kf.descriptor);
    if(dist<bestDist){bestDist=dist;best=kf.name;}
  });
  return best;
}

function toggleFace(){if(_factive)stopFace();else startFace();}

function toggleEnroll(){
  fEnrollZone.style.display=fEnrollZone.style.display==='block'?'none':'block';
}

async function switchCam(){
  _facingMode=(_facingMode==='user')?'environment':'user';
  if(_factive){stopFace();await startFace();}
  document.getElementById('fCamSwitch').innerText=_facingMode==='user'?'🔄':'🔃';
}

async function loadModels(){
  if(_modelsLoaded) return;
  fStatus.innerText='⏳ MODÈLES...';
  var W='https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights';
  await Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri(W),
    faceapi.nets.faceExpressionNet.loadFromUri(W),
    faceapi.nets.ageGenderNet.loadFromUri(W)
  ]);
  _modelsLoaded=true;
}

async function startFace(){
  try{
    loadKnownFaces();
    await loadModels();
    var constraints={video:{facingMode:_facingMode,width:320,height:240},audio:false};
    var stream=await navigator.mediaDevices.getUserMedia(constraints);
    _fstream=stream;
    _fvideo=document.createElement('video');
    _fvideo.srcObject=stream;
    _fvideo.play();
    _factive=true;
    fBtn.className='scanning';fBtn.innerText='⏹';
    fStatus.innerText='👁️ SCAN EN COURS...';
    fCanvas.style.display='block';

    _fint=setInterval(async function(){
      if(!_fvideo||!_factive) return;
      var det=await faceapi.detectSingleFace(_fvideo,new faceapi.TinyFaceDetectorOptions())
        .withFaceExpressions().withAgeAndGender();
      if(det){
        var age=Math.round(det.age);
        var gender=det.gender==='male'?'Homme':'Femme';
        var exprs=det.expressions;
        var topExpr=Object.entries(exprs).sort(function(a,b){return b[1]-a[1];})[0][0];
        var exprFr={happy:'😊 Heureux',sad:'😢 Triste',angry:'😠 Colère',fearful:'😨 Craintif',disgusted:'🤢 Dégoûté',surprised:'😲 Surpris',neutral:'😐 Neutre'};
        
        // ── IDENTIFICATION (basée sur localStorage noms) ──
        var name=null; // identification par nom désactivée sans faceRecognitionNet
        var nameHtml=name
          ?'<span class="fid-known">✅ '+name+'</span>'
          :'<span class="fid-unknown">❓ Inconnu</span>';
        
        fResult.innerHTML=nameHtml+' · '+gender+' ~'+age+'<br>'+(exprFr[topExpr]||topExpr);
        fStatus.innerText=name?'🌸 BIENVENUE '+name.toUpperCase():'✅ VISAGE DÉTECTÉ';
        
        // Dessiner sur canvas
        var ctx=fCanvas.getContext('2d');
        fCanvas.width=det.detection.imageSize.width;
        fCanvas.height=det.detection.imageSize.height;
        ctx.drawImage(_fvideo,0,0,fCanvas.width,fCanvas.height);
        var box=det.detection.box;
        ctx.strokeStyle=name?'#00ffcc':'#aa55ff';
        ctx.lineWidth=2;
        ctx.strokeRect(box.x,box.y,box.width,box.height);
        ctx.fillStyle=name?'#00ffcc':'#aa55ff';
        ctx.font='11px Orbitron,monospace';
        ctx.fillText(name||'Inconnu',box.x,box.y-4);
        
        // ── Envoyer à Streamlit ──
        try{
          var url=window.location.href.split("?")[0]
            +"?face_detected=1&face_age="+age+"&face_gender="+gender
            +"&face_expr="+(topExpr)+"&face_name="+(name||"inconnu")
            +"&face_cam="+_facingMode;
          window.parent.history.replaceState(null,'',url);
        }catch(e){}
      }else{
        fResult.innerHTML='<span class="fid-unknown">Aucun visage visible...</span>';
        fStatus.innerText='👁️ SCAN EN COURS...';
        // Canvas vide
        var ctx=fCanvas.getContext('2d');
        ctx.clearRect(0,0,fCanvas.width,fCanvas.height);
        if(_fvideo) ctx.drawImage(_fvideo,0,0,fCanvas.width||320,fCanvas.height||240);
      }
    },1200);
  }catch(e){
    fStatus.innerText='⚠️ '+e.message;
    fResult.innerHTML='Chrome requis';
  }
}

// ── ENRÔLEMENT : capturer et sauvegarder un nouveau visage ──
async function enrollFace(){
  var name=document.getElementById('fNameInput').value.trim();
  if(!name){fResult.innerHTML='⚠️ Entrez un nom d\'abord';return;}
  if(!_fvideo||!_factive){fResult.innerHTML='⚠️ Activez la caméra d\'abord';return;}
  try{
    fStatus.innerText='📸 CAPTURE EN COURS...';
    var det=await faceapi.detectSingleFace(_fvideo,new faceapi.TinyFaceDetectorOptions())
      .withFaceExpressions().withAgeAndGender();
    if(!det){fResult.innerHTML='⚠️ Aucun visage détecté';return;}
    // Sauvegarder le nom sans descripteur (enrôlement simplifié)
    _knownFaces=_knownFaces.filter(function(f){return f.name.toLowerCase()!==name.toLowerCase();});
    _knownFaces.push({name:name,descriptor:null});
    saveKnownFaces();
    fResult.innerHTML='<span class="fid-known">✅ '+name+' enregistré !</span>';
    fStatus.innerText='✅ PROFIL SAUVÉ';
    document.getElementById('fNameInput').value='';
    fEnrollZone.style.display='none';
    // Notifier Streamlit
    try{
      var url=window.location.href.split("?")[0]+"?face_enrolled="+encodeURIComponent(name);
      window.parent.history.replaceState(null,'',url);
    }catch(e){}
  }catch(e){fResult.innerHTML='⚠️ Erreur: '+e.message;}
}

function stopFace(){
  _factive=false;
  clearInterval(_fint);
  if(_fstream)_fstream.getTracks().forEach(function(t){t.stop();});
  _fvideo=null;_fstream=null;
  fBtn.className='';fBtn.innerText='👁️';
  fStatus.innerText='CAMÉRA PRÊTE';
  fResult.innerHTML='Cliquez 👁️ pour scanner';
  fCanvas.style.display='none';
}

// Init
loadKnownFaces();
</script>
</body></html>
"""


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
    # Injection règles chanson si demande détectée
    last_user = ""
    if st.session_state.messages:
        for m in reversed(st.session_state.messages[-4:]):
            if m["role"] == "user":
                last_user = m["content"].lower()
                break
    song_triggers = ["chanson","chante","paroles","lyrics","écris une","compose","écris-moi","song","أغنية","اكتب لي","غنية","غنّ","غني"]
    if any(t in last_user for t in song_triggers):
        system += """

[MODE CHANSON — RÈGLES OBLIGATOIRES]
Quand tu écris une chanson, tu DOIS utiliser ce format EXACT :
🎵 [Titre de la chanson]

**Couplet 1 :**
[ligne 1]
[ligne 2]
[ligne 3]
[ligne 4]

**Refrain :**
[ligne 1]
[ligne 2]
[ligne 3]

**Couplet 2 :**
[ligne 1]
[ligne 2]
[ligne 3]
[ligne 4]

**Refrain :**
[répétition refrain]

**Pont :**
[ligne 1]
[ligne 2]

**Refrain final :**
[refrain final]
🎵

Règles des vers :
- Chaque ligne = 5 à 12 mots maximum (courte pour être chantable)
- Rimes à la fin de chaque ligne si possible
- Émotions fortes, images poétiques
- Si langue arabe → utiliser l'arabe dialectal ou classique selon le style
- NE PAS expliquer la chanson, juste l'écrire"""
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
    detected=detect_lang(question)
    if detected!="🇫🇷 Français" and detected!=st.session_state.langue:
        st.session_state.langue=detected
    
    # ── Vérification question suspecte (livre p.45) ──
    is_suspicious, flag = check_suspicious(question)
    if is_suspicious and not regen:
        location = handle_suspicious_question(question, flag)
        st.warning(f"⚠️ Question sensible détectée (mot-clé: `{flag}`) — Position enregistrée: {location}")
    
    # ── Enrichir prompt avec profil utilisateur ──
    results=[]
    web_ctx=""
    if st.session_state.web_search_on:
        with st.spinner(f"🌐 {T['searching']}"):
            results=web_search(question)
            if results:
                web_ctx="\n\n[WEB — utilise pour enrichir ta réponse]:\n"+"".join(f"• {r['title']}: {r['snippet']}\n" for r in results)
    ctx_files="".join(f['contenu'] for f in st.session_state.fichiers_contexte)
    ctx_mem=st.session_state.mémoire.get_context(st.session_state.user_id)
    system=build_system()
    if ctx_mem: system+=f"\n\n[MÉMOIRE {st.session_state.user_id}]:\n{ctx_mem}"
    if ctx_files: system+=f"\n\n[FICHIERS]:\n{ctx_files[:3000]}"
    if web_ctx: system+=web_ctx
    # ── CONTEXTE VISUEL : ce que REIHANA voit via la caméra ──
    _face_log = st.session_state.face_access_log
    if _face_log:
        _last = _face_log[-1]
        _ts_diff = (datetime.now() - datetime.fromisoformat(_last['ts'])).total_seconds() if _last.get('ts') else 999
        if _ts_diff < 30:  # données fraîches (< 30 secondes)
            _vname = _last.get('name','inconnu')
            _vage  = _last.get('age','?')
            _vgender = _last.get('gender','?')
            _vexpr = _last.get('expression','?')
            _vcam  = 'avant' if _last.get('cam','user')=='user' else 'arrière'
            _vision_ctx = f"\n\n[VISION CAMÉRA — ce que tu vois en ce moment]:\n"
            if _vname and _vname != 'inconnu':
                _vision_ctx += f"Devant toi : {_vname}, {_vgender}, ~{_vage} ans, expression : {_vexpr}. "
                _vision_ctx += f"Utilise son prénom dans ta réponse de façon naturelle."
            else:
                _vision_ctx += f"Devant toi : une personne ({_vgender}, ~{_vage} ans), expression : {_vexpr}. "
                _vision_ctx += f"Adapte ton ton à cette expression."
            _vision_ctx += f" (caméra {_vcam})"
            system += _vision_ctx
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
        <svg viewBox="0 0 154 154" xmlns="http://www.w3.org/2000/svg" width="152" height="152" style="display:block;border-radius:50%;">
          <defs>
            <radialGradient id="bgG" cx="50%" cy="40%" r="60%"><stop offset="0%" stop-color="#0a0a3a"/><stop offset="100%" stop-color="#000010"/></radialGradient>
            <radialGradient id="skinG" cx="45%" cy="35%" r="65%"><stop offset="0%" stop-color="#ffe0c8"/><stop offset="60%" stop-color="#f5c8a8"/><stop offset="100%" stop-color="#e8b090"/></radialGradient>
            <radialGradient id="eyeG" cx="40%" cy="35%" r="60%"><stop offset="0%" stop-color="#88ffff"/><stop offset="40%" stop-color="#00aaff"/><stop offset="100%" stop-color="#0033aa"/></radialGradient>
            <linearGradient id="hairG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1a0050"/><stop offset="50%" stop-color="#2d0080"/><stop offset="100%" stop-color="#4400bb"/></linearGradient>
            <linearGradient id="clothG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1a004a"/><stop offset="100%" stop-color="#000830"/></linearGradient>
            <radialGradient id="chkG" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="rgba(255,120,100,0.45)"/><stop offset="100%" stop-color="rgba(255,120,100,0)"/></radialGradient>
            <radialGradient id="sakG" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffaacc"/><stop offset="100%" stop-color="#ff4488"/></radialGradient>
            <filter id="sfG"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            <clipPath id="cc"><circle cx="77" cy="77" r="77"/></clipPath>
          </defs>
          <circle cx="77" cy="77" r="77" fill="url(#bgG)"/>
          <g clip-path="url(#cc)">
            <path d="M28,58 C24,75 20,110 25,145 L35,148 C32,118 34,88 38,70 Z" fill="url(#hairG)"/>
            <path d="M126,58 C130,75 134,110 129,145 L119,148 C122,118 120,88 116,70 Z" fill="url(#hairG)"/>
            <rect x="64" y="108" width="26" height="22" rx="8" fill="url(#skinG)"/>
            <path d="M35,154 L45,126 C54,120 63,118 77,118 C91,118 100,120 109,126 L119,154 Z" fill="url(#clothG)"/>
            <ellipse cx="77" cy="78" rx="38" ry="42" fill="url(#skinG)"/>
            <path d="M39,75 C35,55 42,32 58,24 C66,20 72,18 77,18 C82,18 88,20 96,24 C112,32 119,55 115,75 C108,58 95,48 77,47 C59,48 46,58 39,75 Z" fill="url(#hairG)"/>
            <path d="M42,68 C44,58 50,50 58,46 C65,43 71,42 77,42 C83,42 89,43 96,46 C104,50 110,58 112,68 C105,60 95,55 77,54 C59,55 49,60 42,68 Z" fill="url(#hairG)"/>
            <ellipse cx="39" cy="84" rx="5.5" ry="7" fill="url(#skinG)"/>
            <ellipse cx="115" cy="84" rx="5.5" ry="7" fill="url(#skinG)"/>
            <path d="M52,66 C55,63 60,62 65,63" stroke="#1a0040" stroke-width="2.2" fill="none" stroke-linecap="round"/>
            <path d="M89,63 C94,62 99,63 102,66" stroke="#1a0040" stroke-width="2.2" fill="none" stroke-linecap="round"/>
            <ellipse cx="62" cy="80" rx="12" ry="10" fill="white"/>
            <ellipse cx="62" cy="80" rx="8" ry="8.5" fill="url(#eyeG)"/>
            <ellipse id="pupilL" cx="62" cy="80" rx="4" ry="4.5" fill="#000820"/>
            <ellipse cx="59" cy="76" rx="2.5" ry="2" fill="white" opacity="0.9"/>
            <path d="M50,74 C53,70 58,68 62,68 C66,68 71,70 74,74" stroke="#0a0030" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            <path id="eyelidL" d="M50,74 C53,74 58,74 62,74 C66,74 71,74 74,74" fill="#0a0030" opacity="0"/>
            <ellipse cx="92" cy="80" rx="12" ry="10" fill="white"/>
            <ellipse cx="92" cy="80" rx="8" ry="8.5" fill="url(#eyeG)"/>
            <ellipse id="pupilR" cx="92" cy="80" rx="4" ry="4.5" fill="#000820"/>
            <ellipse cx="89" cy="76" rx="2.5" ry="2" fill="white" opacity="0.9"/>
            <path d="M80,74 C83,70 88,68 92,68 C96,68 101,70 104,74" stroke="#0a0030" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            <path id="eyelidR" d="M80,74 C83,74 88,74 92,74 C96,74 101,74 104,74" fill="#0a0030" opacity="0"/>
            <ellipse cx="50" cy="93" rx="11" ry="7" fill="url(#chkG)" opacity="0.7"/>
            <ellipse cx="104" cy="93" rx="11" ry="7" fill="url(#chkG)" opacity="0.7"/>
            <path id="lipT" d="M67,106 C70,103 74,102 77,102 C80,102 84,103 87,106" stroke="#c06070" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            <path id="lipB" d="M67,106 C70,109 74,110 77,110 C80,110 84,109 87,106" fill="#e08090" stroke="#c06070" stroke-width="0.8" opacity="0.9"/>
            <ellipse id="mouthIn" cx="77" cy="107" rx="0" ry="0" fill="#1a0010" opacity="0.85"/>
            <rect id="mouthTth" x="72" y="106" width="10" height="3" rx="1.5" fill="white" opacity="0"/>
            <ellipse id="eyeGlL" cx="62" cy="80" rx="0" ry="0" fill="rgba(0,255,255,0.4)" opacity="0"/>
            <ellipse id="eyeGlR" cx="92" cy="80" rx="0" ry="0" fill="rgba(0,255,255,0.4)" opacity="0"/>
            <g transform="translate(100,38)" filter="url(#sfG)">
              <circle cx="0" cy="-5" r="4" fill="url(#sakG)"/>
              <circle cx="4.7" cy="-1.5" r="4" fill="url(#sakG)"/>
              <circle cx="2.9" cy="4" r="4" fill="url(#sakG)"/>
              <circle cx="-2.9" cy="4" r="4" fill="url(#sakG)"/>
              <circle cx="-4.7" cy="-1.5" r="4" fill="url(#sakG)"/>
              <circle cx="0" cy="0" r="2.5" fill="#ffddaa"/>
              <animateTransform attributeName="transform" type="rotate" values="0;5;0;-5;0" dur="4s" repeatCount="indefinite"/>
            </g>
          </g>
        </svg>
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

    import streamlit.components.v1 as comp_av
    comp_av.html("""<script>
(function(){
  // Attendre que les SVGs soient dans le DOM parent via postMessage ou polling
  function ge(id){
    // Chercher dans le document parent (Streamlit iframe)
    try{
      var el = window.parent.document.getElementById(id);
      if(el) return el;
    }catch(e){}
    return document.getElementById(id);
  }
  var _spk=false;

  function blink(){
    var eL=ge("eyelidL"),eR=ge("eyelidR"),pL=ge("pupilL"),pR=ge("pupilR");
    var bgEL=ge("bgEyelidL"),bgER=ge("bgEyelidR"),bgPL=ge("bgPupilL"),bgPR=ge("bgPupilR");
    if(eL&&eR){
      eL.setAttribute("opacity","1");eR.setAttribute("opacity","1");
      eL.setAttribute("d","M50,80 C53,80 58,80 62,80 C66,80 71,80 74,80");
      eR.setAttribute("d","M80,80 C83,80 88,80 92,80 C96,80 101,80 104,80");
      if(pL)pL.setAttribute("ry","1");if(pR)pR.setAttribute("ry","1");
      setTimeout(function(){
        eL.setAttribute("opacity","0");eR.setAttribute("opacity","0");
        eL.setAttribute("d","M50,74 C53,74 58,74 62,74 C66,74 71,74 74,74");
        eR.setAttribute("d","M80,74 C83,74 88,74 92,74 C96,74 101,74 104,74");
        if(pL)pL.setAttribute("ry","4.5");if(pR)pR.setAttribute("ry","4.5");
      },130);
    }
    if(bgEL&&bgER){
      bgEL.setAttribute("opacity","1");bgER.setAttribute("opacity","1");
      if(bgPL)bgPL.setAttribute("ry","1");if(bgPR)bgPR.setAttribute("ry","1");
      setTimeout(function(){
        bgEL.setAttribute("opacity","0");bgER.setAttribute("opacity","0");
        if(bgPL)bgPL.setAttribute("ry","5.5");if(bgPR)bgPR.setAttribute("ry","5.5");
      },130);
    }
  }
  function sb(){setTimeout(function(){blink();sb();},2500+Math.random()*3000);}

  var _mt=null;
  function mouth(lv){
    var lT=ge("lipT"),lB=ge("lipB"),mi=ge("mouthIn"),mt=ge("mouthTth");
    var bgLT=ge("bgLipT"),bgMO=ge("bgMouthOpen");
    if(!lT||!lB)return;
    var oh=lv*7;
    if(lv<0.05){
      lT.setAttribute("d","M67,106 C70,103 74,102 77,102 C80,102 84,103 87,106");
      lB.setAttribute("d","M67,106 C70,109 74,110 77,110 C80,110 84,109 87,106");
      if(mi){mi.setAttribute("rx","0");mi.setAttribute("ry","0");}
      if(mt)mt.setAttribute("opacity","0");
      if(bgLT)bgLT.setAttribute("d","M170,295 C180,288 192,285 200,285 C208,285 220,288 230,295");
      if(bgMO){bgMO.setAttribute("rx","0");bgMO.setAttribute("ry","0");}
    }else{
      var ty=106-oh*0.3,by=106+oh;
      lT.setAttribute("d","M67,"+ty+" C70,"+(ty-3)+" 74,"+(ty-4)+" 77,"+(ty-4)+" C80,"+(ty-4)+" 84,"+(ty-3)+" 87,"+ty);
      lB.setAttribute("d","M67,"+ty+" C70,"+by+" 74,"+(by+1)+" 77,"+(by+1)+" C80,"+(by+1)+" 84,"+by+" 87,"+ty);
      if(mi){mi.setAttribute("cx","77");mi.setAttribute("cy",String((ty+by)/2));mi.setAttribute("rx",String(8*lv));mi.setAttribute("ry",String(oh*0.55));mi.setAttribute("opacity","0.85");}
      if(mt){mt.setAttribute("opacity",String(lv*0.8));mt.setAttribute("y",String(ty));}
      var bgOh=lv*18;var bgTy=295-bgOh*0.3,bgBy=295+bgOh;
      if(bgLT)bgLT.setAttribute("d","M170,"+bgTy+" C180,"+(bgTy-5)+" 192,"+(bgTy-8)+" 200,"+(bgTy-8)+" C208,"+(bgTy-8)+" 220,"+(bgTy-5)+" 230,"+bgTy);
      if(bgMO){bgMO.setAttribute("cx","200");bgMO.setAttribute("cy",String((bgTy+bgBy)/2));bgMO.setAttribute("rx",String(22*lv));bgMO.setAttribute("ry",String(bgOh*0.55));bgMO.setAttribute("opacity","0.9");}
    }
  }
  function sm(){
    if(_mt)clearInterval(_mt);var ph=0;
    _mt=setInterval(function(){
      if(!_spk){mouth(0);return;}
      ph+=0.4;mouth(Math.min(Math.abs(Math.sin(ph))*0.7+Math.random()*0.3,1));
    },90);
  }
  function glow(on){
    var gL=ge("eyeGlL"),gR=ge("eyeGlR");
    if(!gL||!gR)return;
    var v=on?"10":"0",o=on?"0.35":"0";
    gL.setAttribute("rx",v);gL.setAttribute("ry",v);gL.setAttribute("opacity",o);
    gR.setAttribute("rx",v);gR.setAttribute("ry",v);gR.setAttribute("opacity",o);
  }
  function startS(){_spk=true;var b=ge("hologramAvatar")||window.parent.document.querySelector('.hologram-avatar');var bars=window.parent.document.querySelector('.voice-bars');if(b)b.classList.add("speaking");if(bars)bars.classList.add("active");glow(true);}
  function stopS(){_spk=false;var b=window.parent.document.querySelector('.hologram-avatar');var bars=window.parent.document.querySelector('.voice-bars');if(b)b.classList.remove("speaking");if(bars)bars.classList.remove("active");glow(false);mouth(0);}

  // Intercepter reihanaSpeak du parent
  try{
    var _oS=window.parent.reihanaSpeak,_oSt=window.parent.reihanaStop;
    window.parent.reihanaSpeak=function(t){startS();if(_oS)_oS(t);setTimeout(function(){if(_spk)stopS();},Math.max(1500,t.length*55)+500);};
    window.parent.reihanaStop=function(){stopS();if(_oSt)_oSt();};
    if(window.parent.speechSynthesis){
      var ns=window.parent.speechSynthesis.speak.bind(window.parent.speechSynthesis);
      window.parent.speechSynthesis.speak=function(u){u.addEventListener("start",startS);u.addEventListener("end",stopS);u.addEventListener("error",stopS);ns(u);};
    }
  }catch(e){}

  function moveBgEyes(){
    var bgPL=ge("bgPupilL"),bgPR=ge("bgPupilR");
    if(!bgPL||!bgPR)return;
    var dx=(Math.random()-0.5)*12,dy=(Math.random()-0.5)*6;
    bgPL.setAttribute("cx",String(163+dx));bgPL.setAttribute("cy",String(205+dy));
    bgPR.setAttribute("cx",String(237+dx));bgPR.setAttribute("cy",String(205+dy));
  }
  function bgExpression(){
    var svg=ge("reiBgAvatar");
    if(!svg)return;
    var tilt=(Math.random()-0.5)*4,ty=(Math.random()-0.5)*8;
    svg.style.transform="translateY("+ty+"px) rotate("+tilt+"deg)";
    svg.style.transition="transform 1.5s ease-in-out";
  }
  setInterval(moveBgEyes,2800);
  setInterval(bgExpression,3500);

  function init(){sb();sm();setTimeout(blink,800);setTimeout(moveBgEyes,500);}
  if(document.readyState==="complete"){init();}else{window.addEventListener("load",init);setTimeout(init,1200);}
})();
</script>""", height=0)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

    cs, cm = st.columns([2,1])
    with cs: st.markdown(f'<span class="status-online"></span><span style="color:#00ff88;font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:2px;">{T["online"]}</span>', unsafe_allow_html=True)
    with cm:
        st.components.v1.html("""<style>
body{margin:0;padding:2px;background:transparent}
#b{background:#1a0044;color:#00ffcc;border:2px solid #00ffcc;border-radius:8px;padding:6px 10px;cursor:pointer;font-size:13px;font-weight:bold;width:100%;display:block;transition:all 0.2s;}
#b:hover{background:#2a0066;box-shadow:0 0 10px rgba(0,255,200,0.4);}
#bsing{background:#1a0033;color:#ff88cc;border:2px solid #ff44aa;border-radius:8px;padding:5px 8px;cursor:pointer;font-size:12px;width:100%;display:block;margin-top:4px;transition:all 0.2s;}
#bsing:hover{background:#2a0044;box-shadow:0 0 10px rgba(255,80,180,0.4);}
#bsing.singing{background:#3a0055;color:#ffccee;animation:singPulse 0.6s ease-in-out infinite;}
@keyframes singPulse{0%,100%{box-shadow:0 0 5px rgba(255,80,180,0.3);}50%{box-shadow:0 0 18px rgba(255,80,180,0.8);}}
#m{color:#7700ff;font-size:9px;font-family:monospace;text-align:center;margin-top:3px;letter-spacing:1px;}
#volrow{display:flex;align-items:center;gap:5px;margin-top:5px;}
#vollbl{color:#00ffcc;font-size:9px;font-family:monospace;white-space:nowrap;}
#vol{-webkit-appearance:none;appearance:none;width:100%;height:4px;border-radius:2px;background:linear-gradient(90deg,#00ffcc 0%,#7700ff 100%);outline:none;cursor:pointer;}
#vol::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:#00ffcc;box-shadow:0 0 6px rgba(0,255,200,0.8);cursor:pointer;}
</style>
<audio id="a" loop></audio>
<button id="b" onclick="t(this)">&#127925; &#9654;</button>
<button id="bsing" onclick="toggleSing(this)">&#127908; CHANTER</button>
<div id="m">AMBIENT · CALM</div>
<div id="volrow">
  <span id="vollbl">&#128266;</span>
  <input type="range" id="vol" min="0" max="100" value="40" oninput="setVol(this.value)">
  <span id="vollbl" style="min-width:28px;text-align:right;color:#00ffcc;font-size:9px;font-family:monospace;" id="volpct">40%</span>
</div>
<script>
var S={
  calm:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3"],
  happy:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3"],
  epic:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3"],
  sad:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3"],
  mystery:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3"],
  romantic:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3"],
  tech:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-17.mp3"],
  arabic:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"]
};
var MN={calm:"CALM",happy:"JOYEUX ✨",epic:"ÉPIQUE ⚡",sad:"MÉLANCOLIQUE 💧",mystery:"MYSTÈRE 🌙",romantic:"ROMANTIQUE 💕",tech:"TECH 🤖",arabic:"ORIENTAL 🌙"};
var au=document.getElementById("a");
var _baseVol=0.40;
var _singMode=false;
var _singInterval=null;
var _currentMood="calm";
au.volume=_baseVol;
au.src=S.calm[0];

// ── Volume slider ──
function setVol(v){
  _baseVol=v/100;
  au.volume=_baseVol;
  document.getElementById("vol").value=v;
  var pct=document.getElementById("volpct");
  if(pct) pct.innerText=v+"%";
}

// ── Play/Pause ──
function t(b){
  if(au.paused){
    au.play().then(function(){b.innerHTML="&#127925; &#9646;&#9646;";}).catch(function(){});
  }else{
    au.pause(); b.innerHTML="&#127925; &#9654;";
  }
}

// ── Choisir piste selon mood ──
function pk(m){
  var l=S[m]||S.calm;
  return l[Math.floor(Math.random()*l.length)];
}

// ── Changer mood musical ──
function chMood(m){
  _currentMood=m;
  var url=pk(m);
  document.getElementById("m").innerText=(MN[m]||"AMBIENT");
  if(au.src.indexOf(url)<0){
    var p=!au.paused;
    au.src=url;
    if(p) au.play().catch(function(){});
  }
}

// ── Harmonie voix/musique : baisser musique pendant gTTS ──
// Appelé par play_reihana_voice via postMessage
window.reiVoiceStart=function(){
  // Fade out musique vers 5%
  var _f=setInterval(function(){
    if(au.volume>0.05){au.volume=Math.max(au.volume-0.04,0.05);}
    else{clearInterval(_f);}
  },60);
};
window.reiVoiceEnd=function(){
  // Fade in musique vers volume normal
  var _f=setInterval(function(){
    if(au.volume<_baseVol){au.volume=Math.min(au.volume+0.03,_baseVol);}
    else{clearInterval(_f);}
  },80);
};

// ── MODE CHANT : REIHANA chante sur la musique ──
function toggleSing(btn){
  if(_singMode){
    // Arrêter le chant
    _singMode=false;
    clearInterval(_singInterval);
    if(window.speechSynthesis) window.speechSynthesis.cancel();
    btn.classList.remove("singing");
    btn.innerHTML="&#127908; CHANTER";
    au.volume=_baseVol;
  }else{
    // Démarrer le chant
    if(au.paused){
      au.play().catch(function(){});
      document.getElementById("b").innerHTML="&#127925; &#9646;&#9646;";
    }
    _singMode=true;
    btn.classList.add("singing");
    btn.innerHTML="&#9646;&#9646; STOP CHANT";
    startSinging();
  }
}

// Syllabes de chant selon la langue/mood
var SING_SYLLABLES={
  fr:["La","la","la","Na","na","Da","da","Oh","Ah","Hmm","Ooh","Rei","Ha","na","Ya"],
  ar:["يا","لا","نا","هـا","آه","يـا","لا","لا","يا"],
  en:["La","la","na","da","oh","ah","ooh","yeah","mmm","hey"],
  calm:["La la la","Hmm hmm","Na na na","Oh oh"],
  happy:["La la la la","Yeah yeah","Na na na","Woo hoo"],
  romantic:["Ooh la la","Mmm hmm","Ah ah ah","Da da da"],
  epic:["Oh oh oh","Na na na","La la la","Hey hey"],
  sad:["Hmm hmm","Ooh ooh","Na na","La la la"],
  mystery:["Ooh ooh","Hmm hmm","Ah ah","Mmm"]
};

function pickSyllables(){
  var pool=[];
  var moodSyls=SING_SYLLABLES[_currentMood];
  if(moodSyls) pool=pool.concat(moodSyls);
  pool=pool.concat(SING_SYLLABLES.fr);
  return pool[Math.floor(Math.random()*pool.length)];
}

function startSinging(){
  if(!window.speechSynthesis||!_singMode) return;
  
  function singNext(){
    if(!_singMode) return;
    var syl=pickSyllables();
    var u=new SpeechSynthesisUtterance(syl);
    u.lang="fr-FR";
    u.rate=0.65+Math.random()*0.25;  // rythme varié
    u.pitch=1.3+Math.random()*0.5;   // voix féminine haute
    u.volume=0.9;
    
    // Musique plus douce pendant le chant
    au.volume=Math.max(_baseVol*0.35, 0.05);
    
    var vx=window.speechSynthesis.getVoices();
    var fv=vx.filter(function(v){return v.lang.startsWith("fr");});
    var fem=fv.find(function(v){return /female|femme|amelie|marie/i.test(v.name);})||fv[0];
    if(fem) u.voice=fem;
    
    u.onend=function(){
      if(_singMode){
        // Pause musicale entre les syllabes
        au.volume=_baseVol;
        var delay=400+Math.random()*800;
        setTimeout(singNext, delay);
      }else{
        au.volume=_baseVol;
      }
    };
    u.onerror=function(){
      if(_singMode) setTimeout(singNext,600);
    };
    window.speechSynthesis.speak(u);
  }
  
  singNext();
}

window.reiSpeak=function(){};  // legacy - plus utilisé
window.reiChangeMood=chMood;
window.reiSetVol=setVol;
</script>""", height=130)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-badge">👤 PROFIL</div>', unsafe_allow_html=True)
    uname=st.text_input("",value=st.session_state.user_id,key="uname",label_visibility="collapsed",placeholder="Votre nom...")
    if uname!=st.session_state.user_id: st.session_state.user_id=uname
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-badge">🎭 PERSONNALITÉ</div>', unsafe_allow_html=True)
    np=st.selectbox("",list(PERSONNALITES.keys()),index=list(PERSONNALITES.keys()).index(st.session_state.personnalite),label_visibility="collapsed",key="psel")
    if np!=st.session_state.personnalite: st.session_state.personnalite=np; st.rerun()
    st.markdown('<div class="stat-badge">🌍 LANGUE</div>', unsafe_allow_html=True)
    nl=st.selectbox("",list(LANGS.keys()),index=list(LANGS.keys()).index(st.session_state.langue),label_visibility="collapsed",key="lsel")
    if nl!=st.session_state.langue: st.session_state.langue=nl; st.rerun()
    st.markdown('<div class="stat-badge">🎨 THÈME</div>', unsafe_allow_html=True)
    nt=st.selectbox("",list(THEMES.keys()),index=list(THEMES.keys()).index(st.session_state.theme),label_visibility="collapsed",key="tsel")
    if nt!=st.session_state.theme: st.session_state.theme=nt; st.rerun()
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
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
    
    # ══ MODULE BIBLIOTHÈQUE (livre p.95) ══
    st.markdown('<div class="stat-badge">📚 BIBLIOTHÈQUE</div>', unsafe_allow_html=True)
    lib = get_library()
    all_lib_texts = lib.get('poemes',[]) + lib.get('proverbes',[]) + lib.get('citations',[])
    lib_choices = ["-- Choisir un texte --"] + [f"{t.get('titre','?')} ({t.get('auteur',t.get('langue',''))})" for t in all_lib_texts]
    lib_sel = st.selectbox("", lib_choices, label_visibility="collapsed", key="lib_sel")
    clib1, clib2 = st.columns(2)
    with clib1:
        if st.button("▶️ Réciter", use_container_width=True, key="recite_btn") and lib_sel != lib_choices[0]:
            for txt in all_lib_texts:
                if txt.get('titre','') in lib_sel:
                    st.info(f"📖 {txt.get('texte','')[:120]}...")
                    recite_text(txt.get('texte',''), titre=txt.get('titre',''), langue=txt.get('langue','fr'))
                    break
    with clib2:
        if st.button("➕ Ajouter", use_container_width=True, key="lib_add_btn"):
            st.session_state.show_lib_form = not st.session_state.get("show_lib_form", False)
    if st.session_state.get("show_lib_form", False):
        nt = st.text_input("Titre", key="lib_new_t")
        ntx = st.text_area("Texte", key="lib_new_tx", height=60)
        nl = st.selectbox("Langue", ["fr","ar","en"], key="lib_new_l")
        if st.button("💾 Sauvegarder", key="lib_save_btn") and nt and ntx:
            lib.setdefault('poemes',[]).append({"titre":nt,"texte":ntx,"langue":nl,"auteur":st.session_state.user_id})
            save_library(lib)
            st.session_state.show_lib_form = False
            st.success("✅ Ajouté !")
            st.rerun()

    # ══ MODULE RECONNAISSANCE FACIALE + GESTES (livre p.78-80) ══
    st.markdown('<div class="stat-badge">🔬 CAPTEURS IA</div>', unsafe_allow_html=True)
    import streamlit.components.v1 as _sens_comp
    csens1, csens2 = st.columns(2)
    with csens1:
        st.markdown('<div style="font-family:Orbitron,monospace;font-size:0.6rem;color:rgba(150,50,255,0.6);text-align:center;">👁️ VISAGE</div>', unsafe_allow_html=True)
        _sens_comp.html(FACE_HTML, height=90)
    with csens2:
        st.markdown('<div style="font-family:Orbitron,monospace;font-size:0.6rem;color:rgba(0,255,100,0.6);text-align:center;">✋ GESTES</div>', unsafe_allow_html=True)
        _sens_comp.html(GESTURE_HTML, height=60)

    # ── Afficher le dernier visage reconnu ──
    _last_face_log = st.session_state.face_access_log[-1] if st.session_state.face_access_log else None
    if _last_face_log:
        _fn = _last_face_log.get("name","?")
        _fe = _last_face_log.get("expression","?")
        _fa = _last_face_log.get("age","?")
        _fc = "📷" if _last_face_log.get("cam","user")=="user" else "🔃"
        _color = "#00ffcc" if _fn not in ("inconnu","?") else "rgba(200,150,255,0.6)"
        st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:0.7rem;color:{_color};padding:3px 6px;background:rgba(0,10,20,0.5);border-radius:6px;margin:3px 0;">{_fc} <b>{_fn}</b> · {_fa}ans · {_fe}</div>', unsafe_allow_html=True)
    # ── Personnes connues dans la base ──
    _known = st.session_state.get("face_known_names",[])
    if _known:
        st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.58rem;color:rgba(0,255,180,0.5);letter-spacing:1px;">BASE: {", ".join(_known[:4])}</div>', unsafe_allow_html=True)

    # ══ SÉCURITÉ : chiffrement toggle ══
    enc_label = "🔐 AES ON" if st.session_state.conv_encrypted else "🔓 AES OFF"
    if st.button(enc_label, use_container_width=True, key="aes_toggle"):
        st.session_state.conv_encrypted = not st.session_state.conv_encrypted
        st.rerun()

    # ══ ALERTES : compteur ══
    n_alerts = len(st.session_state.suspicious_log)
    if n_alerts > 0:
        st.markdown(f'<div class="stat-badge" style="border-color:rgba(255,80,80,0.5);color:#ff8888;">⚠️ {n_alerts} ALERTE(S) SUSPECTE(S)</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    if st.button(f"📊 DASHBOARD {'▲' if st.session_state.show_dashboard else '▼'}", use_container_width=True):
        st.session_state.show_dashboard=not st.session_state.show_dashboard; st.rerun()
    if st.session_state.show_dashboard:
        ai_c=len([m for m in st.session_state.messages if m["role"]=="assistant"])
        n_al = len(st.session_state.suspicious_log)
        convs_enc = decrypt_conversations()
        st.markdown(f"""<div class="dash-grid">
            <div class="dash-card"><div class="dash-num">{len(st.session_state.messages)}</div><div class="dash-lbl">MSGS</div></div>
            <div class="dash-card"><div class="dash-num">{st.session_state.total_tokens:,}</div><div class="dash-lbl">TOKENS</div></div>
            <div class="dash-card"><div class="dash-num" style="color:#ff8888;">{n_al}</div><div class="dash-lbl">⚠️ ALERTES</div></div>
            <div class="dash-card"><div class="dash-num" style="color:#88ff88;">{len(convs_enc)}</div><div class="dash-lbl">🔐 CHIFFRÉS</div></div>
        </div>
        <div class="stat-badge">⏱️ SESSION : {st.session_state.session_start}</div>
        <div class="stat-badge">🤖 {ai_c} RÉPONSES</div>
        <div class="stat-badge">{'🔐 CHIFFREMENT AES ACTIF' if st.session_state.conv_encrypted else '🔓 CHIFFREMENT DÉSACTIVÉ'}</div>""", unsafe_allow_html=True)
        if n_al > 0:
            if st.button("🔍 Voir alertes", use_container_width=True, key="view_alerts"):
                st.session_state.admin_dashboard_open = True
                st.rerun()
        if hasattr(st.session_state,'engine'):
            stats=st.session_state.engine.get_stats()
            st.markdown(f'<div class="stat-badge">⚡ CLÉ #{stats.get("cle_active",1)} | {stats.get("modele_actif","")[:18]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
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
# MAIN
# ═══════════════════════════════════════════
ch, cm2 = st.columns([3,2])
with ch: st.markdown(f'<div style="font-family:Orbitron,monospace;color:{p};font-size:1.25rem;font-weight:700;letter-spacing:5px;padding:8px 0;">⬡ REIHANA · INTERFACE IA v3.0</div>', unsafe_allow_html=True)
with cm2:
    b=("🌐 " if st.session_state.web_search_on else "")+("🧠 " if st.session_state.deep_think else "")+f"🌸 {T['active']}"
    st.markdown(f'<div class="stat-badge" style="margin-top:8px;">{b}</div>', unsafe_allow_html=True)
st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f'<div class="msg-reihana">{T["welcome"]}</div>', unsafe_allow_html=True)

for i,msg in enumerate(st.session_state.messages):
    if msg["role"]=="user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        content=msg["content"]
        st.markdown(f'<div class="msg-reihana">{content}</div>', unsafe_allow_html=True)
        # Détecter si CE message est une chanson
        _msg_is_song, _msg_mood, _msg_lang, _msg_verses = detect_song(content)
        
        if _msg_is_song and _msg_verses:
            # Layout avec bouton CHANTER en évidence
            ca,cb,cc,cd,ce=st.columns([1.1,1.1,1.1,1.8,1.5])
        else:
            ca,cb,cc,cd,ce=st.columns([1.1,1.1,1.1,1.5,1.8])
        
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
                _detected_lang = detect_text_lang(msg["content"])
                play_reihana_voice(msg["content"], lang=_detected_lang)
        with cd:
            if st.button("🔄 Regen", key=f"rg{i}", use_container_width=True):
                if i>0 and st.session_state.messages[i-1]["role"]=="user":
                    st.session_state.regen_index=i; st.session_state.regen_question=st.session_state.messages[i-1]["content"]; st.rerun()
        with ce:
            if _msg_is_song and _msg_verses:
                # Bouton CHANTER rose/violet animé
                st.markdown(f"""<style>
                .sing-btn-{i} > button {{
                    background: linear-gradient(135deg, rgba(180,0,120,0.25), rgba(100,0,180,0.2)) !important;
                    border: 1.5px solid rgba(255,80,200,0.7) !important;
                    color: #ffaaee !important;
                    animation: singGlow 2s ease-in-out infinite !important;
                }}
                @keyframes singGlow {{
                    0%,100% {{ box-shadow: 0 0 6px rgba(255,80,200,0.3); }}
                    50% {{ box-shadow: 0 0 18px rgba(255,80,200,0.8); }}
                }}
                </style>""", unsafe_allow_html=True)
                with st.container():
                    st.markdown(f'<div class="sing-btn-{i}">', unsafe_allow_html=True)
                    if st.button(f"🎵 CHANTER", key=f"sing{i}", use_container_width=True):
                        # Changer mood musique + lancer le chant
                        play_song(_msg_verses, lang=_msg_lang, mood=_msg_mood)
                        st.toast(f"🎤 REIHANA chante... mood: {_msg_mood}")
                    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 🎥 MODULE CHAT AUDIO/VISUEL — REIHANA VOIT + ENTEND EN MÊME TEMPS
# ══════════════════════════════════════════════════════════════════
import streamlit.components.v1 as _av_comp

_av_lang_map = {"🇫🇷 Français": "fr-FR", "🇩🇿 العربية": "ar-SA", "🇬🇧 English": "en-US"}
_av_lang = _av_lang_map.get(st.session_state.langue, "fr-FR")
_av_known_str = ",".join(st.session_state.get("face_known_names", []))

_av_html = f"""<html><head>
<style>
  body{{margin:0;padding:4px;background:transparent;font-family:Orbitron,monospace;overflow:hidden;}}
  
  /* ══ BARRE DE CONTRÔLES ══ */
  #avZone{{display:flex;align-items:center;gap:8px;padding:4px 0 6px 0;flex-wrap:wrap;}}
  #avBtn{{width:48px;height:48px;border-radius:50%;border:2px solid rgba(255,80,200,0.5);
    background:rgba(30,0,30,0.9);color:#ff55cc;font-size:20px;cursor:pointer;
    display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0;}}
  #avBtn.active{{border-color:#ff3399;animation:avPulse .8s infinite;}}
  #avCamBtn{{width:34px;height:34px;border-radius:50%;border:1px solid rgba(0,200,255,0.4);
    background:rgba(0,20,40,0.8);color:#00ccff;font-size:13px;cursor:pointer;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;}}
  #avEnrollBtn{{font-size:9px;border:1px solid rgba(0,255,150,0.5);background:rgba(0,40,20,0.8);
    color:#00ff88;padding:4px 8px;border-radius:6px;cursor:pointer;letter-spacing:1px;}}
  @keyframes avPulse{{0%,100%{{box-shadow:0 0 10px rgba(255,50,150,.4);}}50%{{box-shadow:0 0 26px rgba(255,50,150,.9);}}}}
  #avStatus{{font-size:9px;letter-spacing:2px;color:rgba(255,80,200,0.5);}}
  #avStatus.on{{color:#ff3399;animation:stPulse 1s ease-in-out infinite;}}
  #avStatus.ok{{color:#00ffcc;}}
  @keyframes stPulse{{0%,100%{{opacity:0.7;}}50%{{opacity:1;}}}}
  #avInfo{{font-size:10px;color:rgba(220,150,255,0.8);font-family:Rajdhani,sans-serif;font-weight:600;max-width:280px;line-height:1.4;}}
  #avMoodBar{{font-size:8px;color:rgba(255,150,255,0.5);margin-top:2px;letter-spacing:1px;}}
  
  /* ══ ÉCRAN DE VISUALISATION PRINCIPAL ══ */
  #avScreen{{
    display:none;
    position:relative;
    width:100%;
    background:rgba(0,0,20,0.95);
    border:1px solid rgba(255,80,200,0.5);
    border-radius:12px;
    overflow:hidden;
    margin-top:6px;
    box-shadow:0 0 20px rgba(255,50,150,0.3),inset 0 0 30px rgba(0,0,40,0.5);
  }}
  #avScreen.visible{{display:block;}}
  #avVideo{{
    width:100%;height:220px;
    object-fit:cover;
    display:block;
    transform:scaleX(-1);
    border-radius:0;
  }}
  #avVideo.rear{{transform:scaleX(1);}}
  
  /* ══ OVERLAY HOLOGRAPHIQUE SUR LA VIDÉO ══ */
  #avOverlay{{
    position:absolute;top:0;left:0;right:0;bottom:0;
    pointer-events:none;z-index:5;
  }}
  /* Lignes de scan */
  #avOverlay::before{{
    content:'';position:absolute;top:0;left:0;right:0;bottom:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 4px,rgba(0,255,200,0.03) 4px,rgba(0,255,200,0.03) 5px);
    animation:scanAV 2s linear infinite;
    pointer-events:none;
  }}
  @keyframes scanAV{{0%{{background-position:0 0;}}100%{{background-position:0 100px;}}}}
  /* Coin décoratifs */
  #avOverlay::after{{
    content:'';position:absolute;top:6px;left:6px;width:28px;height:28px;
    border-top:2px solid rgba(0,255,200,0.8);border-left:2px solid rgba(0,255,200,0.8);
    border-radius:2px 0 0 0;pointer-events:none;
  }}
  .av-corner-br{{position:absolute;bottom:38px;right:6px;width:28px;height:28px;
    border-bottom:2px solid rgba(255,80,200,0.8);border-right:2px solid rgba(255,80,200,0.8);
    border-radius:0 0 2px 0;pointer-events:none;z-index:6;}}
  
  /* ══ CANVAS AVEC BOÎTES DE DÉTECTION ══ */
  #avCanvas{{
    position:absolute;top:0;left:0;width:100%;height:220px;
    pointer-events:none;z-index:10;
  }}
  
  /* ══ BADGE NOM DÉTECTÉ ══ */
  #avNameBadge{{
    position:absolute;bottom:40px;left:50%;transform:translateX(-50%);
    background:rgba(0,0,30,0.9);border:1px solid rgba(0,255,200,0.6);
    border-radius:8px;padding:4px 12px;font-size:11px;
    color:#00ffcc;letter-spacing:2px;font-family:Orbitron,monospace;
    text-align:center;white-space:nowrap;z-index:15;
    display:none;box-shadow:0 0 12px rgba(0,255,200,0.4);
  }}
  #avNameBadge.unknown{{border-color:rgba(180,80,255,0.6);color:#cc88ff;box-shadow:0 0 12px rgba(150,0,255,0.3);}}
  #avNameBadge.known{{border-color:rgba(0,255,150,0.8);color:#00ffcc;box-shadow:0 0 18px rgba(0,255,150,0.5);}}
  
  /* ══ BARRE D'INFO BAS DE VIDÉO ══ */
  #avInfoBar{{
    background:rgba(0,0,20,0.9);
    padding:5px 10px;
    display:flex;justify-content:space-between;align-items:center;
    border-top:1px solid rgba(255,80,200,0.2);
    font-size:9px;letter-spacing:1px;
    font-family:Orbitron,monospace;
  }}
  #avInfoLeft{{color:rgba(0,255,200,0.7);}}
  #avInfoRight{{color:rgba(255,80,200,0.7);}}
  
  /* ══ ZONE D'ENRÔLEMENT ══ */
  #avEnrollZone{{
    display:none;background:rgba(0,10,30,0.97);border:1px solid rgba(0,255,150,0.3);
    border-radius:8px;padding:10px;margin-top:6px;
  }}
  #avEnrollZone input{{width:calc(100% - 14px);background:rgba(0,0,20,0.8);
    border:1px solid rgba(0,255,150,0.3);color:#00ff88;font-size:10px;
    padding:5px 7px;border-radius:4px;outline:none;font-family:Rajdhani,sans-serif;
    margin-bottom:5px;display:block;}}
  #avSaveBtn{{width:100%;font-size:9px;border:1px solid rgba(0,255,150,0.5);
    background:rgba(0,40,20,0.8);color:#00ff88;padding:5px;border-radius:5px;
    cursor:pointer;letter-spacing:1px;}}
  #avKnownList{{font-size:9px;color:rgba(0,255,150,0.5);margin-top:5px;letter-spacing:1px;}}
  
  .fid-known{{color:#00ffcc;font-size:12px;font-weight:700;text-shadow:0 0 8px rgba(0,255,200,0.6);}}
  .fid-unknown{{color:rgba(200,150,255,0.8);}}
</style></head><body>
<div id="avZone">
  <button id="avBtn" onclick="toggleAV()" title="Activer la caméra — REIHANA vous voit et vous reconnaît">👁️‍🗨️</button>
  <button id="avCamBtn" onclick="switchAVCam()" title="Caméra avant/arrière">🔄</button>
  <button id="avEnrollBtn" onclick="toggleEnroll()">➕ ENRÔLER</button>
  <div style="flex:1;">
    <div id="avStatus">CAMÉRA PRÊTE</div>
    <div id="avInfo">Cliquez 👁️‍🗨️ — REIHANA voit et reconnaît</div>
    <div id="avMoodBar"></div>
  </div>
</div>

<!-- ══ ÉCRAN DE VISUALISATION ══ -->
<div id="avScreen">
  <div id="avOverlay"></div>
  <div class="av-corner-br"></div>
  <video id="avVideo" autoplay muted playsinline></video>
  <canvas id="avCanvas"></canvas>
  <div id="avNameBadge">❓ INCONNU</div>
  <div id="avInfoBar">
    <span id="avInfoLeft">👁️ SCAN ACTIF</span>
    <span id="avInfoRight">cam: avant</span>
  </div>
</div>

<!-- ══ ZONE D'ENRÔLEMENT ══ -->
<div id="avEnrollZone">
  <div style="font-size:9px;color:rgba(0,255,150,0.7);letter-spacing:2px;margin-bottom:5px;">📸 ENREGISTRER CE VISAGE</div>
  <input id="avNameInput" placeholder="Nom complet de la personne..." maxlength="40"/>
  <button id="avSaveBtn" onclick="enrollAVFace()">📸 CAPTURER & ENREGISTRER</button>
  <div id="avKnownList">Personnes enregistrées : <span id="avKnownCount">0</span></div>
</div>

<script src="https://unpkg.com/face-api.js@0.22.2/dist/face-api.min.js"></script>
<script>
var _avActive=false,_avStream=null,_avFaceInt=null,_avRecog=null;
var _avFacing='user';
var _avModelsLoaded=false;
var _avRecogModelLoaded=false;
var _avLang='{_av_lang}';
var _avKnown=[]; // {{name, descriptor:Float32Array, info:{{}}}}
var _avLastName='';
var _avDetectInterval=null;
var _avCanvas2d=null;

var avBtn=document.getElementById('avBtn');
var avStatus=document.getElementById('avStatus');
var avInfo=document.getElementById('avInfo');
var avVideo=document.getElementById('avVideo');
var avCanvas=document.getElementById('avCanvas');
var avMoodBar=document.getElementById('avMoodBar');
var avScreen=document.getElementById('avScreen');
var avNameBadge=document.getElementById('avNameBadge');
var avInfoLeft=document.getElementById('avInfoLeft');
var avInfoRight=document.getElementById('avInfoRight');

// ══ BASE DE DONNÉES ADMINISTRATIVE INTÉGRÉE ══
// Structure enrichie: nom, poste, département, niveau d'accès, RDV
var _adminDB = {{
  // Exemple de structure — sera enrichi via enrôlement
  // "Jean Dupont": {{ post:"Directeur", dept:"Administration", access:3, rdv:[] }}
}};

function loadAdminDB(){{
  try{{
    var s=localStorage.getItem('rei_admin_db');
    if(s) _adminDB=JSON.parse(s);
  }}catch(e){{}}
}}

function saveAdminDB(){{
  try{{localStorage.setItem('rei_admin_db',JSON.stringify(_adminDB));}}catch(e){{}}
}}

function getPersonInfo(name){{
  return _adminDB[name] || null;
}}

// ══ CHARGER LES VISAGES CONNUS (avec descripteurs) ══
function loadAVFaces(){{
  try{{
    var s=localStorage.getItem('rei_known_faces');
    if(s){{
      var arr=JSON.parse(s);
      _avKnown=arr.map(function(f){{
        return {{name:f.name,descriptor:new Float32Array(f.descriptor),info:f.info||{{}}}};
      }});
    }}
  }}catch(e){{}}
  // Fusionner noms venant de Python
  var fromPy='{_av_known_str}'.split(',').filter(function(n){{return n.trim();}});
  fromPy.forEach(function(n){{
    if(!_avKnown.find(function(f){{return f.name===n;}}))
      _avKnown.push({{name:n,descriptor:null,info:{{}}}});
  }});
  document.getElementById('avKnownCount').innerText=_avKnown.filter(function(f){{return f.descriptor;}}).length;
}}

function saveAVFaces(){{
  try{{
    var toSave=_avKnown.filter(function(f){{return f.descriptor;}}).map(function(f){{
      return {{name:f.name,descriptor:Array.from(f.descriptor),info:f.info||{{}}}};
    }});
    localStorage.setItem('rei_known_faces',JSON.stringify(toSave));
  }}catch(e){{}}
  document.getElementById('avKnownCount').innerText=_avKnown.filter(function(f){{return f.descriptor;}}).length;
}}

// ══ IDENTIFICATION FACIALE ══
function identifyAV(descriptor){{
  if(!descriptor||_avKnown.length===0) return null;
  var best=null,bestDist=0.50; // seuil strict pour précision maximale
  _avKnown.forEach(function(kf){{
    if(!kf.descriptor) return;
    var d=faceapi.euclideanDistance(descriptor,kf.descriptor);
    if(d<bestDist){{bestDist=d;best=kf.name;}}
  }});
  return best;
}}

// ══ CHARGER LES MODÈLES (avec faceRecognitionNet pour vraie identification) ══
async function loadAVModels(){{
  if(_avModelsLoaded) return;
  avStatus.innerText='⏳ MODÈLES IA...';
  avInfo.innerText='Chargement reconnaissance faciale...';
  var W='https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights';
  try{{
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(W),
      faceapi.nets.faceExpressionNet.loadFromUri(W),
      faceapi.nets.ageGenderNet.loadFromUri(W),
      faceapi.nets.faceLandmark68TinyNet.loadFromUri(W),
      faceapi.nets.faceRecognitionNet.loadFromUri(W)  // ✅ Vraie reconnaissance
    ]);
    _avModelsLoaded=true;
    _avRecogModelLoaded=true;
    avStatus.innerText='✅ MODÈLES CHARGÉS';
    avInfo.innerText='Reconnaissance faciale prête !';
  }}catch(err){{
    // Fallback sans reconnaissance
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(W),
      faceapi.nets.faceExpressionNet.loadFromUri(W),
      faceapi.nets.ageGenderNet.loadFromUri(W)
    ]);
    _avModelsLoaded=true;
    _avRecogModelLoaded=false;
  }}
}}

// ══ DESSINER LES BOÎTES DE DÉTECTION SUR LE CANVAS ══
function drawDetections(det, name, isKnown){{
  if(!_avCanvas2d||!det) return;
  var vw=avVideo.videoWidth||avCanvas.width;
  var vh=avVideo.videoHeight||avCanvas.height;
  avCanvas.width=avCanvas.offsetWidth||avCanvas.width;
  avCanvas.height=220;
  var scaleX=avCanvas.width/vw;
  var scaleY=avCanvas.height/vh;
  
  _avCanvas2d.clearRect(0,0,avCanvas.width,avCanvas.height);
  
  var box=det.detection.box;
  var x=box.x*scaleX, y=box.y*scaleY;
  var w=box.width*scaleX, h=box.height*scaleY;
  
  // Couleur selon identification
  var color=isKnown?'rgba(0,255,200,0.9)':'rgba(180,80,255,0.9)';
  var colorFill=isKnown?'rgba(0,255,200,0.1)':'rgba(180,80,255,0.08)';
  
  // Rectangle principal
  _avCanvas2d.strokeStyle=color;
  _avCanvas2d.lineWidth=2;
  _avCanvas2d.strokeRect(x,y,w,h);
  _avCanvas2d.fillStyle=colorFill;
  _avCanvas2d.fillRect(x,y,w,h);
  
  // Coins stylisés
  var cs=14;
  _avCanvas2d.strokeStyle=isKnown?'rgba(0,255,150,1)':'rgba(255,100,255,1)';
  _avCanvas2d.lineWidth=3;
  // Coin haut-gauche
  _avCanvas2d.beginPath();_avCanvas2d.moveTo(x,y+cs);_avCanvas2d.lineTo(x,y);_avCanvas2d.lineTo(x+cs,y);_avCanvas2d.stroke();
  // Coin haut-droit
  _avCanvas2d.beginPath();_avCanvas2d.moveTo(x+w-cs,y);_avCanvas2d.lineTo(x+w,y);_avCanvas2d.lineTo(x+w,y+cs);_avCanvas2d.stroke();
  // Coin bas-gauche
  _avCanvas2d.beginPath();_avCanvas2d.moveTo(x,y+h-cs);_avCanvas2d.lineTo(x,y+h);_avCanvas2d.lineTo(x+cs,y+h);_avCanvas2d.stroke();
  // Coin bas-droit
  _avCanvas2d.beginPath();_avCanvas2d.moveTo(x+w-cs,y+h);_avCanvas2d.lineTo(x+w,y+h);_avCanvas2d.lineTo(x+w,y+h-cs);_avCanvas2d.stroke();
  
  // Label nom
  var label=name||(isKnown?'✅ RECONNU':'❓ INCONNU');
  _avCanvas2d.font='bold 11px Orbitron,monospace';
  var tw=_avCanvas2d.measureText(label).width;
  var lx=x+(w-tw)/2, ly=y-8;
  if(ly<14) ly=y+h+18;
  _avCanvas2d.fillStyle=isKnown?'rgba(0,40,30,0.9)':'rgba(20,0,40,0.9)';
  _avCanvas2d.fillRect(lx-5,ly-13,tw+10,18);
  _avCanvas2d.strokeStyle=color;_avCanvas2d.lineWidth=1;
  _avCanvas2d.strokeRect(lx-5,ly-13,tw+10,18);
  _avCanvas2d.fillStyle=color;
  _avCanvas2d.fillText(label,lx,ly);
}}

function switchAVCam(){{
  _avFacing=(_avFacing==='user')?'environment':'user';
  avVideo.className=_avFacing==='environment'?'rear':'';
  document.getElementById('avInfoRight').innerText='cam: '+(_avFacing==='user'?'avant':'arrière');
  if(_avActive){{stopAV();startAV();}}
}}

function toggleAV(){{if(_avActive)stopAV();else startAV();}}
function toggleEnroll(){{
  var ez=document.getElementById('avEnrollZone');
  ez.style.display=ez.style.display==='block'?'none':'block';
}}

async function enrollAVFace(){{
  var nameInput=document.getElementById('avNameInput');
  var name=nameInput.value.trim();
  if(!name){{alert('Entrez un nom !');return;}}
  if(!_avActive||!avVideo.srcObject){{alert('Activez la caméra d\'abord !');return;}}
  
  try{{
    var det=await faceapi.detectSingleFace(avVideo,new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks(true).withFaceDescriptor();
    if(!det){{avInfo.innerHTML='<span style="color:#ff8800;">⚠️ Aucun visage visible</span>';return;}}
    
    // Sauvegarder le descripteur
    var existing=_avKnown.findIndex(function(f){{return f.name===name;}});
    var info=getPersonInfo(name)||{{}};
    if(existing>=0){{
      _avKnown[existing].descriptor=det.descriptor;
      _avKnown[existing].info=info;
    }}else{{
      _avKnown.push({{name:name,descriptor:det.descriptor,info:info}});
    }}
    saveAVFaces();
    
    // Ajouter dans DB admin si absent
    if(!_adminDB[name]){{
      _adminDB[name]={{post:'',dept:'',access:1,rdv:[],enroled:new Date().toISOString()}};
      saveAdminDB();
    }}
    
    // Notifier Python
    try{{
      var url=window.location.href.split("?")[0]+"?face_enrolled="+encodeURIComponent(name);
      window.parent.location.href=url;
    }}catch(e){{
      window.location.href=window.location.href.split("?")[0]+"?face_enrolled="+encodeURIComponent(name);
    }}
    
    nameInput.value='';
    avInfo.innerHTML='<span style="color:#00ffcc;">✅ '+name+' enregistré !</span>';
    document.getElementById('avEnrollZone').style.display='none';
  }}catch(e){{
    avInfo.innerHTML='<span style="color:#ff5555;">❌ Erreur: '+e.message+'</span>';
  }}
}}

async function startAV(){{
  try{{
    loadAVFaces();
    loadAdminDB();
    avStatus.innerText='⏳ DÉMARRAGE...';
    await loadAVModels();
    
    var constraints={{video:{{facingMode:_avFacing,width:{{ideal:640}},height:{{ideal:480}}}},audio:false}};
    _avStream=await navigator.mediaDevices.getUserMedia(constraints);
    avVideo.srcObject=_avStream;
    avVideo.style.display='block';
    avScreen.classList.add('visible');
    
    // Initialiser canvas 2D
    _avCanvas2d=avCanvas.getContext('2d');
    
    _avActive=true;
    avBtn.classList.add('active');
    avBtn.innerText='⏹';
    avStatus.innerText='🎥 SCAN ACTIF';
    avStatus.className='on';
    avInfo.innerHTML='<span style="color:rgba(200,255,220,0.7);">Positionnez votre visage devant la caméra</span>';
    avInfoRight.innerText='cam: '+(_avFacing==='user'?'avant':'arrière');
    
    // ══ BOUCLE DE DÉTECTION FACIALE CONTINUE ══
    _avDetectInterval=setInterval(async function(){{
      if(!avVideo||!_avActive||avVideo.readyState<2) return;
      try{{
        var detResult;
        if(_avRecogModelLoaded){{
          // Détection complète avec reconnaissance
          detResult=await faceapi.detectSingleFace(avVideo,new faceapi.TinyFaceDetectorOptions({{scoreThreshold:0.4}}))
            .withFaceLandmarks(true)
            .withFaceDescriptor()
            .withFaceExpressions()
            .withAgeAndGender();
        }}else{{
          detResult=await faceapi.detectSingleFace(avVideo,new faceapi.TinyFaceDetectorOptions())
            .withFaceExpressions()
            .withAgeAndGender();
        }}
        
        if(detResult){{
          var age=Math.round(detResult.age);
          var gender=detResult.gender==='male'?'H':'F';
          var exprs=detResult.expressions;
          var topExpr=Object.entries(exprs).sort(function(a,b){{return b[1]-a[1];}})[0][0];
          var exprEm={{happy:'😊',sad:'😢',angry:'😠',fearful:'😨',disgusted:'🤢',surprised:'😲',neutral:'😐'}};
          
          // Identification
          var name=null;
          if(_avRecogModelLoaded&&detResult.descriptor){{
            name=identifyAV(detResult.descriptor);
          }}
          
          var isKnown=!!name;
          
          // Mettre à jour badge
          avNameBadge.style.display='block';
          if(isKnown){{
            var info=getPersonInfo(name)||{{}};
            var infoStr=info.post?(' · '+info.post):'';
            avNameBadge.className='known';
            avNameBadge.innerHTML='✅ '+name+(infoStr?'<br><span style="font-size:8px;color:rgba(0,255,150,0.6);">'+infoStr+'</span>':'');
            avInfo.innerHTML='<span class="fid-known">✅ '+name+'</span> · '+gender+age+' · '+(exprEm[topExpr]||topExpr);
          }}else{{
            avNameBadge.className='unknown';
            avNameBadge.innerHTML='❓ INCONNU · '+gender+' ~'+age+'ans';
            avInfo.innerHTML='<span class="fid-unknown">❓ Inconnu</span> · '+gender+age+' · '+(exprEm[topExpr]||topExpr);
          }}
          
          // Dessiner boîte de détection
          drawDetections(detResult, name, isKnown);
          
          avInfoLeft.innerHTML='👁️ DÉTECTÉ · '+(exprEm[topExpr]||topExpr);
          avMoodBar.innerText=_avRecogModelLoaded?'🧠 RECONNAISSANCE ACTIVE':'⚡ DÉTECTION BASIQUE';
          
          // Notifier Python si nouveau visage connu identifié
          if(name&&name!==_avLastName){{
            _avLastName=name;
            try{{
              var url=window.location.href.split("?")[0]
                +"?face_detected=1&face_age="+age
                +"&face_gender="+(detResult.gender==='male'?'Homme':'Femme')
                +"&face_expr="+topExpr
                +"&face_name="+encodeURIComponent(name)
                +"&face_cam="+_avFacing;
              window.parent.history.replaceState(null,'',url);
            }}catch(e){{}}
          }}
        }}else{{
          // Aucun visage
          if(_avCanvas2d) _avCanvas2d.clearRect(0,0,avCanvas.width,avCanvas.height);
          avNameBadge.style.display='none';
          avInfo.innerHTML='<span style="color:rgba(180,150,255,0.5);">Aucun visage détecté...</span>';
          avInfoLeft.innerText='👁️ EN ATTENTE';
          avMoodBar.innerText='';
          _avLastName='';
        }}
      }}catch(e){{
        // Erreur silencieuse
      }}
    }},800); // Détection toutes les 800ms
    
    // ── Démarrer reconnaissance vocale ──
    startAVSpeech();
    
  }}catch(e){{
    avStatus.innerText='⚠️ '+e.message;
    avInfo.innerText='Vérifiez les permissions caméra/micro';
  }}
}}

function startAVSpeech(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){{avInfo.innerText='Speech: Chrome/Edge requis';return;}}
  _avRecog=new SR();
  _avRecog.lang=_avLang;
  _avRecog.continuous=true;
  _avRecog.interimResults=true;
  _avRecog.maxAlternatives=1;
  
  _avRecog.onresult=function(e){{
    var final_t='',interim_t='';
    for(var i=e.resultIndex;i<e.results.length;i++){{
      var t=e.results[i][0].transcript;
      if(e.results[i].isFinal) final_t+=t;
      else interim_t+=t;
    }}
    if(interim_t) avInfo.innerHTML='🎙️ <em style="color:rgba(255,150,255,0.7);">'+interim_t+'...</em>';
    if(final_t.trim()){{
      avInfo.innerHTML='✅ <span style="color:#00ffcc;">'+final_t.trim()+'</span>';
      avStatus.className='ok';
      avStatus.innerText='✅ ENVOYÉ';
      // Envoyer à Streamlit via query_params
      var base=window.location.href.split("?")[0];
      try{{
        window.parent.location.href=base+"?stt_text="+encodeURIComponent(final_t.trim());
      }}catch(ex){{
        window.location.href=base+"?stt_text="+encodeURIComponent(final_t.trim());
      }}
    }}
  }};
  _avRecog.onerror=function(e){{
    if(e.error==='no-speech') return;
    avStatus.innerText='⚠️ Micro: '+e.error;
  }};
  _avRecog.onend=function(){{
    if(_avActive) setTimeout(function(){{try{{_avRecog.start();}}catch(ex){{}}}},800);
  }};
  try{{_avRecog.start();}}catch(e){{}}
}}

function stopAV(){{
  _avActive=false;
  clearInterval(_avDetectInterval);
  _avDetectInterval=null;
  if(_avCanvas2d) _avCanvas2d.clearRect(0,0,avCanvas.width,avCanvas.height);
  if(_avStream)_avStream.getTracks().forEach(function(t){{t.stop();}});
  _avStream=null;
  if(_avRecog){{try{{_avRecog.stop();}}catch(e){{}}}}
  avVideo.style.display='none';
  avScreen.classList.remove('visible');
  avNameBadge.style.display='none';
  avBtn.classList.remove('active');
  avBtn.innerText='👁️‍🗨️';
  avStatus.className='';
  avStatus.innerText='CAMÉRA PRÊTE';
  avInfo.innerHTML='Cliquez 👁️‍🗨️ — REIHANA voit et reconnaît';
  avMoodBar.innerText='';
  avInfoLeft.innerText='👁️ SCAN ACTIF';
  _avLastName='';
}}
loadAVFaces();
</script></body></html>"""

_av_comp.html(_av_html, height=320)

# ── Reconnaissance vocale — Web Speech API avec allow="microphone" ──
import streamlit.components.v1 as _comp_v1

_stt_lang_map = {"🇫🇷 Français": "fr-FR", "🇩🇿 العربية": "ar-SA", "🇬🇧 English": "en-US"}
_stt_lang_bcp = _stt_lang_map.get(st.session_state.langue, "fr-FR")

# Récupérer transcription depuis query_params
_stt_txt_in = st.query_params.get("stt_text", "")
if _stt_txt_in and _stt_txt_in.strip():
    st.session_state.input_value = _stt_txt_in.strip()
    st.session_state.clear_input = False
    st.query_params.clear()
    st.rerun()

_whisper_result = None

# ── Widget micro avec allow="microphone" injecté via JS ──
# L'erreur "network" sur Edge = iframe sans permission micro
# Solution : injecter allow="microphone" sur l'iframe Streamlit parent via JS
_stt_html = f"""<html><head>
<style>
  body{{margin:0;padding:0;background:transparent;font-family:Orbitron,monospace;overflow:hidden;}}
  #zone{{display:flex;align-items:center;gap:10px;padding:4px 0;}}
  #micBtn{{
    width:52px;height:52px;border-radius:50%;border:2px solid rgba(0,255,200,0.5);
    background:rgba(0,20,40,0.9);color:#00ffcc;font-size:22px;cursor:pointer;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 15px rgba(0,255,200,0.2);transition:all .2s;flex-shrink:0;
  }}
  #micBtn.listening{{border-color:#ff3333;color:#ff5555;background:rgba(255,30,30,0.15);
    animation:micPulse 0.8s ease-in-out infinite;}}
  @keyframes micPulse{{0%,100%{{box-shadow:0 0 10px rgba(255,50,50,.4);}}50%{{box-shadow:0 0 28px rgba(255,50,50,.8);}}}}
  #info{{flex:1;}}
  #status{{font-size:9px;letter-spacing:2px;color:rgba(0,255,200,0.5);margin-bottom:3px;}}
  #status.active{{color:#ff4444;}}
  #status.success{{color:#00ff88;}}
  #status.err{{color:#ff8800;}}
  #trans{{font-size:11px;color:rgba(200,240,255,0.7);font-family:Rajdhani,sans-serif;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:240px;}}
  #bars{{display:flex;align-items:flex-end;gap:2px;height:20px;opacity:0;transition:opacity .3s;margin-top:2px;}}
  #bars.active{{opacity:1;}}
  .vb{{width:3px;background:linear-gradient(0deg,#00ffcc,#7700ff);border-radius:1.5px;min-height:3px;transition:height .08s;}}
</style></head><body>
<div id="zone">
  <button id="micBtn" onclick="toggleMic()" title="Parler à REIHANA">🎙️</button>
  <div id="info">
    <div id="status">MICRO PRÊT</div>
    <div id="trans">Cliquez 🎙️ pour parler...</div>
    <div id="bars">
      <div class="vb" style="height:4px"></div><div class="vb" style="height:9px"></div>
      <div class="vb" style="height:15px"></div><div class="vb" style="height:20px"></div>
      <div class="vb" style="height:15px"></div><div class="vb" style="height:9px"></div>
      <div class="vb" style="height:4px"></div>
    </div>
  </div>
</div>
<script>
var _lang = "{_stt_lang_bcp}";
var btn = document.getElementById("micBtn");
var stat = document.getElementById("status");
var trans = document.getElementById("trans");
var bars = document.getElementById("bars");
var vbs = document.querySelectorAll(".vb");
var _recog = null;
var _listening = false;
var _animInt = null;
var _retries = 0;

// ── Injecter allow="microphone" sur TOUTES les iframes Streamlit du parent ──
(function patchIframes() {{
  try {{
    var iframes = window.parent.document.querySelectorAll("iframe");
    iframes.forEach(function(fr) {{
      var allow = fr.getAttribute("allow") || "";
      if(!allow.includes("microphone")) {{
        fr.setAttribute("allow", allow ? allow + "; microphone" : "microphone");
      }}
    }});
  }} catch(e) {{}}
  // Re-patcher après 2s (nouvelles iframes ajoutées par Streamlit)
  setTimeout(patchIframes, 2000);
}})();

function setSt(cls, txt) {{ stat.className = cls; stat.innerText = txt; }}

function animBars(on) {{
  bars.classList.toggle("active", on);
  if(_animInt) clearInterval(_animInt);
  if(on) {{
    _animInt = setInterval(function() {{
      vbs.forEach(function(v) {{
        v.style.height = Math.max(3, Math.floor(Math.random()*18)+2) + "px";
      }});
    }}, 100);
  }} else {{
    vbs.forEach(function(v) {{ v.style.height = "3px"; }});
  }}
}}

function sendText(txt) {{
  var base = window.location.href.split("?")[0];
  try {{
    window.parent.location.href = base + "?stt_text=" + encodeURIComponent(txt);
  }} catch(e) {{
    window.location.href = base + "?stt_text=" + encodeURIComponent(txt);
  }}
}}

function toggleMic() {{
  if(_listening) stopRecog();
  else startRecog();
}}

function startRecog() {{
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR) {{
    setSt("err", "⚠️ Chrome/Edge requis");
    trans.innerText = "Firefox ne supporte pas";
    return;
  }}
  
  // Demander permission micro explicitement d'abord
  if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
    navigator.mediaDevices.getUserMedia({{audio: true}})
      .then(function(stream) {{
        stream.getTracks().forEach(function(t) {{ t.stop(); }}); // libérer le stream
        launchRecognition(SR);
      }})
      .catch(function(err) {{
        setSt("err", "🚫 Micro refusé");
        trans.innerText = "Autoriser le micro dans Edge";
      }});
  }} else {{
    launchRecognition(SR);
  }}
}}

function launchRecognition(SR) {{
  _recog = new SR();
  _recog.lang = _lang;
  _recog.continuous = false;
  _recog.interimResults = true;
  _recog.maxAlternatives = 1;
  
  _recog.onstart = function() {{
    _listening = true;
    _retries = 0;
    btn.className = "listening";
    btn.innerText = "⏹";
    setSt("active", "🔴 ÉCOUTE...");
    trans.innerText = "Parlez maintenant...";
    animBars(true);
  }};
  
  _recog.onresult = function(e) {{
    var interim = "";
    var final_txt = "";
    for(var i = e.resultIndex; i < e.results.length; i++) {{
      if(e.results[i].isFinal) final_txt += e.results[i][0].transcript;
      else interim += e.results[i][0].transcript;
    }}
    trans.innerText = final_txt || interim || "...";
    if(final_txt) {{
      setSt("success", "✅ " + final_txt.trim().substring(0,30));
      animBars(false);
      btn.className = "";
      btn.innerText = "🎙️";
      _listening = false;
      setTimeout(function() {{ sendText(final_txt.trim()); }}, 500);
    }}
  }};
  
  _recog.onerror = function(e) {{
    animBars(false);
    btn.className = "";
    btn.innerText = "🎙️";
    _listening = false;
    if(e.error === "network" && _retries < 2) {{
      // Retry automatique après erreur network
      _retries++;
      setSt("err", "↺ Retry " + _retries + "/2...");
      trans.innerText = "Reconnexion...";
      setTimeout(function() {{ startRecog(); }}, 1500);
    }} else if(e.error === "not-allowed") {{
      setSt("err", "🚫 Micro bloqué");
      trans.innerText = "Cliquez sur 🔒 dans la barre Edge";
    }} else {{
      setSt("err", "❌ " + e.error);
      trans.innerText = "Réessayez ou utilisez le clavier";
    }}
  }};
  
  _recog.onend = function() {{
    if(_listening) {{
      _listening = false;
      btn.className = "";
      btn.innerText = "🎙️";
      animBars(false);
    }}
  }};
  
  try {{ _recog.start(); }} catch(ex) {{ setSt("err", "❌ " + ex.message); }}
}}

function stopRecog() {{
  _listening = false;
  if(_recog) {{ try {{ _recog.stop(); }} catch(e) {{}} }}
  btn.className = "";
  btn.innerText = "🎙️";
  animBars(false);
  setSt("", "MICRO PRÊT");
}}
</script></body></html>"""

# ── Ancien widget micro (remplacé par le micro intégré dans la barre de saisie) ──
# _comp_v1.html(_stt_html, height=70)  # DÉSACTIVÉ — micro déplacé dans la barre de saisie

# ── Bloc mort (gardé pour éviter erreurs de syntaxe) ──
if False:
    pass
    """DEBUT_BLOC_SUPPRIME
<script src="https://unpkg.com/streamlit-component-lib@2.0.0/dist/index.js"></script>
<style>
  body{{margin:0;padding:0;background:transparent;overflow:hidden;font-family:'Orbitron',monospace;}}
  #reiMicZone{{display:flex;align-items:center;gap:12px;padding:6px 0;}}
  #reiMicBtn{{
    width:54px;height:54px;border-radius:50%;border:2px solid rgba(0,255,200,0.5);
    background:rgba(0,20,40,0.9);color:#00ffcc;font-size:22px;cursor:pointer;
    transition:all .2s;display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 15px rgba(0,255,200,0.2);flex-shrink:0;
  }}
  #reiMicBtn:hover{{background:rgba(0,255,200,0.1);box-shadow:0 0 25px rgba(0,255,200,0.4);}}
  #reiMicBtn.listening{{border-color:#ff3333;color:#ff5555;background:rgba(255,30,30,0.15);
    animation:micPulse 1s ease-in-out infinite;}}
  #reiMicBtn.processing{{border-color:#ffaa00;color:#ffaa00;}}
  @keyframes micPulse{{0%,100%{{box-shadow:0 0 10px rgba(255,50,50,.4);}}50%{{box-shadow:0 0 28px rgba(255,50,50,.8);}}}}
  #reiMicInfo{{flex:1;}}
  #reiMicStatus{{font-size:9px;letter-spacing:2px;color:rgba(0,255,200,0.5);margin-bottom:3px;}}
  #reiMicStatus.active{{color:#ff4444;}}
  #reiMicStatus.processing{{color:#ffaa00;}}
  #reiMicStatus.success{{color:#00ff88;}}
  #reiMicStatus.err{{color:#ff8800;}}
  #reiTranscript{{font-size:11px;color:rgba(200,240,255,0.6);font-family:'Rajdhani',sans-serif;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:220px;}}
  #reiVolBars{{display:flex;align-items:flex-end;gap:2px;height:22px;opacity:0;transition:opacity .3s;margin-top:3px;}}
  #reiVolBars.active{{opacity:1;}}
  .reiVb{{width:3px;background:linear-gradient(0deg,#00ffcc,#7700ff);border-radius:1.5px;min-height:3px;transition:height .05s;}}
  #reiTimer{{font-size:8px;color:#ff5555;letter-spacing:1px;margin-top:2px;display:none;}}
  #reiTimer.on{{display:block;}}
  #reiInfo{{font-size:8px;color:rgba(0,255,200,0.35);margin-top:2px;letter-spacing:1px;}}
</style>

<div id="reiMicZone">
  <button id="reiMicBtn" onclick="toggleMic()" title="Cliquer pour parler">🎙️</button>
  <div id="reiMicInfo">
    <div id="reiMicStatus">MICRO PRÊT</div>
    <div id="reiTranscript">Cliquez sur 🎙️ pour parler...</div>
    <div id="reiVolBars">
      <div class="reiVb" style="height:4px"></div><div class="reiVb" style="height:8px"></div>
      <div class="reiVb" style="height:14px"></div><div class="reiVb" style="height:18px"></div>
      <div class="reiVb" style="height:22px"></div><div class="reiVb" style="height:18px"></div>
      <div class="reiVb" style="height:14px"></div><div class="reiVb" style="height:8px"></div>
      <div class="reiVb" style="height:4px"></div>
    </div>
    <div id="reiTimer">⏺ 0s / max 30s</div>
    <div id="reiInfo">🦊 Firefox · Whisper AI · Max 30s</div>
  </div>
</div>

<script>
var _mediaRecorder = null;
var _audioChunks = [];
var _listening = false;
var _analyser = null;
var _animFrame = null;
var _stream = null;
var _timerInterval = null;
var _seconds = 0;
var _sttLang = "{_stt_lang}";

var _btn = document.getElementById("reiMicBtn");
var _status = document.getElementById("reiMicStatus");
var _transcript = document.getElementById("reiTranscript");
var _volBars = document.getElementById("reiVolBars");
var _vbs = document.querySelectorAll(".reiVb");
var _timer = document.getElementById("reiTimer");

function setSt(cls, txt) {{
  _status.className = cls;
  _status.innerText = txt;
}}

function startVisualizer(stream) {{
  try {{
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
    var src = ctx.createMediaStreamSource(stream);
    _analyser = ctx.createAnalyser();
    _analyser.fftSize = 256;
    src.connect(_analyser);
    var data = new Uint8Array(_analyser.frequencyBinCount);
    _volBars.classList.add("active");
    (function draw() {{
      if (!_listening) {{
        _volBars.classList.remove("active");
        _vbs.forEach(function(b) {{ b.style.height = "3px"; }});
        return;
      }}
      _animFrame = requestAnimationFrame(draw);
      _analyser.getByteFrequencyData(data);
      var bands = [2,4,6,10,14,18,14,10,6];
      bands.forEach(function(band, i) {{
        var sum = 0;
        for (var j = 0; j < band; j++) sum += data[Math.floor(j*data.length/band/9 + i*data.length/9)];
        _vbs[i].style.height = Math.max(3, Math.min(22, (sum/band)/5)) + "px";
      }});
    }})();
  }} catch(e) {{}}
}}

function startTimer() {{
  _seconds = 0;
  _timer.classList.add("on");
  _timerInterval = setInterval(function() {{
    _seconds++;
    _timer.innerText = "⏺ " + _seconds + "s / max 30s";
    if (_seconds >= 30) stopMic(); // auto-stop à 30s
  }}, 1000);
}}

function stopTimer() {{
  clearInterval(_timerInterval);
  _timer.classList.remove("on");
}}

function toggleMic() {{
  if (_listening) stopMic();
  else startMic();
}}

function startMic() {{
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
    setSt("err", "⚠️ Micro non supporté");
    return;
  }}
  navigator.mediaDevices.getUserMedia({{ audio: true, video: false }})
    .then(function(stream) {{
      _stream = stream;
      _audioChunks = [];
      _listening = true;

      // Choisir le meilleur format selon le navigateur
      var mimeType = "audio/webm";
      if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {{
        mimeType = "audio/webm;codecs=opus";
      }} else if (MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")) {{
        mimeType = "audio/ogg;codecs=opus"; // Firefox
      }} else if (MediaRecorder.isTypeSupported("audio/mp4")) {{
        mimeType = "audio/mp4";
      }}

      _mediaRecorder = new MediaRecorder(stream, {{ mimeType: mimeType }});
      _mediaRecorder.ondataavailable = function(e) {{
        if (e.data && e.data.size > 0) _audioChunks.push(e.data);
      }};
      _mediaRecorder.onstop = function() {{
        transcribeAudio(_audioChunks, mimeType);
      }};
      _mediaRecorder.start(200); // chunk toutes les 200ms

      _btn.classList.add("listening");
      _btn.innerText = "⏹";
      setSt("active", "🔴 ENREGISTREMENT...");
      _transcript.innerText = "Parlez maintenant...";
      startVisualizer(stream);
      startTimer();
    }})
    .catch(function(err) {{
      setSt("err", "🚫 Micro refusé: " + err.message);
      _transcript.innerText = "Autoriser le micro dans Firefox";
    }});
}}

function stopMic() {{
  _listening = false;
  stopTimer();
  cancelAnimationFrame(_animFrame);
  if (_mediaRecorder && _mediaRecorder.state !== "inactive") {{
    _mediaRecorder.stop();
  }}
  if (_stream) {{
    _stream.getTracks().forEach(function(t) {{ t.stop(); }});
    _stream = null;
  }}
  _btn.classList.remove("listening");
  _btn.innerText = "🎙️";
  setSt("processing", "⚙️ TRANSCRIPTION...");
  _transcript.innerText = "Whisper AI analyse votre voix...";
}}

function transcribeAudio(chunks, mimeType) {{
  if (!chunks || chunks.length === 0) {{
    setSt("err", "⚠️ Audio vide");
    _transcript.innerText = "Aucun son capturé";
    return;
  }}

  var blob = new Blob(chunks, {{ type: mimeType }});
  
  // Choisir l'extension selon le type
  var ext = "webm";
  if (mimeType.includes("ogg")) ext = "ogg";
  else if (mimeType.includes("mp4")) ext = "mp4";

  var formData = new FormData();
  formData.append("audio", blob, "voice." + ext);
  formData.append("lang", _sttLang.split("-")[0]); // "fr", "ar", "en"

  // Envoyer audio via Streamlit.setComponentValue (officiel)
  var reader = new FileReader();
  reader.onload = function(ev) {{
    var b64 = ev.target.result.split(",")[1];
    Streamlit.setComponentValue({{b64:b64, mime:mimeType, lang:_sttLang.split("-")[0], ts:Date.now()}});
  }};
  reader.readAsDataURL(blob);
}}

window.addEventListener("message", function(e) {{
  if (e.data && e.data.type === "reiSetSttLang") {{
    _sttLang = e.data.lang;
  }}
    FIN_BLOC_SUPPRIME"""


# ── Zone texte + boutons (micro intégré dans la ligne, ne cache plus l'écran) ──
# Layout : [Micro compact | Zone texte | Envoyer | Stop]
ci_mic, ci, cs2, cs3 = st.columns([1, 5, 1, 1])

with ci_mic:
    # Micro compact — placé à GAUCHE de la zone texte
    _mic_inline_html = f"""<html><head>
<style>
  body{{margin:0;padding:2px;background:transparent;overflow:hidden;}}
  #mBtnWrap{{display:flex;flex-direction:column;align-items:center;justify-content:center;height:88px;gap:4px;}}
  #mBtn{{width:46px;height:46px;border-radius:50%;border:2px solid rgba(0,255,200,0.5);
    background:rgba(0,20,40,0.95);color:#00ffcc;font-size:20px;cursor:pointer;
    display:flex;align-items:center;justify-content:center;transition:all .2s;
    box-shadow:0 0 12px rgba(0,255,200,0.2);}}
  #mBtn.listening{{border-color:#ff3333;color:#ff5555;background:rgba(40,0,0,0.9);
    animation:mPulse 0.7s ease-in-out infinite;}}
  #mBtn.ok{{border-color:#00ff88;color:#00ff88;}}
  @keyframes mPulse{{0%,100%{{box-shadow:0 0 8px rgba(255,50,50,.3);}}50%{{box-shadow:0 0 22px rgba(255,50,50,.8);}}}}
  #mSt{{font-size:8px;color:rgba(0,255,200,0.5);letter-spacing:1px;font-family:Orbitron,monospace;
    text-align:center;max-width:50px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
  #mSt.active{{color:#ff4444;}}
  #mSt.ok{{color:#00ff88;}}
  #mBars{{display:flex;align-items:flex-end;gap:1px;height:14px;opacity:0;transition:opacity .2s;}}
  #mBars.on{{opacity:1;}}
  .mb{{width:3px;background:linear-gradient(0deg,#00ffcc,#7700ff);border-radius:1px;min-height:2px;}}
</style></head><body>
<div id="mBtnWrap">
  <button id="mBtn" onclick="tMic()" title="Cliquez pour parler à REIHANA">🎙️</button>
  <div id="mBars">
    <div class="mb" style="height:3px"></div><div class="mb" style="height:7px"></div>
    <div class="mb" style="height:12px"></div><div class="mb" style="height:7px"></div>
    <div class="mb" style="height:3px"></div>
  </div>
  <div id="mSt">MICRO</div>
</div>
<script>
var _lang="{_stt_lang_bcp}";
var _btn=document.getElementById("mBtn");
var _st=document.getElementById("mSt");
var _bars=document.getElementById("mBars");
var _mbs=document.querySelectorAll(".mb");
var _recog=null;
var _on=false;
var _anim=null;
var _retries=0;

(function pI(){{
  try{{
    var ifs=window.parent.document.querySelectorAll("iframe");
    ifs.forEach(function(f){{
      var a=f.getAttribute("allow")||"";
      if(!a.includes("microphone")) f.setAttribute("allow",a?a+"; microphone":"microphone");
    }});
  }}catch(e){{}}
  setTimeout(pI,3000);
}})();

function setSt(cls,txt){{_st.className=cls;_st.innerText=txt;}}

function anim(on){{
  _bars.classList.toggle("on",on);
  if(_anim) clearInterval(_anim);
  if(on){{
    _anim=setInterval(function(){{
      _mbs.forEach(function(b){{b.style.height=Math.max(2,Math.floor(Math.random()*12)+2)+"px";}});
    }},100);
  }}else{{_mbs.forEach(function(b){{b.style.height="2px";}});}}
}}

function send(txt){{
  var base=window.location.href.split("?")[0];
  try{{window.parent.location.href=base+"?stt_text="+encodeURIComponent(txt);}}
  catch(e){{window.location.href=base+"?stt_text="+encodeURIComponent(txt);}}
}}

function tMic(){{if(_on) stop(); else start();}}

function start(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){{setSt("err","Chrome");return;}}
  if(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia){{
    navigator.mediaDevices.getUserMedia({{audio:true}})
      .then(function(s){{s.getTracks().forEach(function(t){{t.stop();}});launch(SR);}})
      .catch(function(){{setSt("","🚫");}});
  }}else launch(SR);
}}

function launch(SR){{
  _recog=new SR();
  _recog.lang=_lang;
  _recog.continuous=false;
  _recog.interimResults=true;
  _recog.maxAlternatives=1;
  _recog.onstart=function(){{_on=true;_retries=0;_btn.className="listening";_btn.innerText="⏹";setSt("active","🔴");anim(true);}};
  _recog.onresult=function(e){{
    var fin="";
    for(var i=e.resultIndex;i<e.results.length;i++){{if(e.results[i].isFinal)fin+=e.results[i][0].transcript;}}
    if(fin){{setSt("ok","✅");_btn.className="ok";_btn.innerText="🎙️";_on=false;anim(false);setTimeout(function(){{send(fin.trim());}},400);}}
  }};
  _recog.onerror=function(e){{
    anim(false);_btn.className="";_btn.innerText="🎙️";_on=false;
    if(e.error==="network"&&_retries<2){{_retries++;setSt("","↺");setTimeout(start,1500);}}
    else setSt("","❌");
  }};
  _recog.onend=function(){{if(_on){{_on=false;_btn.className="";_btn.innerText="🎙️";anim(false);setSt("","MICRO");}}}};
  try{{_recog.start();}}catch(ex){{setSt("","❌");}}
}}

function stop(){{
  _on=false;
  if(_recog){{try{{_recog.stop();}}catch(e){{}}}}
  _btn.className="";_btn.innerText="🎙️";anim(false);setSt("","MICRO");
}}
</script></body></html>"""
    import streamlit.components.v1 as _mic_inline_comp
    _mic_inline_comp.html(_mic_inline_html, height=92)

with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    if st.session_state.get("whisper_ready"):
        st.session_state.whisper_ready = False
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")
with cs3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔇", use_container_width=True, key="micstop", help="Arrêter le micro"):
        pass

# ── Réception audio via postMessage + Whisper Groq côté Python ──
# Le JS envoie l'audio base64 via postMessage → intercepté par ce script JS
# qui le stocke dans sessionStorage, puis un polling Python le lit via query_params

import streamlit.components.v1 as _comp_recv

# Script JS qui écoute postMessage du widget micro et relaie à Python via URL
_recv_html = """
<script>
(function(){
  // Écouter les messages du widget micro (iframe enfant)
  window.addEventListener("message", function(e) {
    var d = e.data;
    if(!d || d.type !== "rei_audio") return;
    // Stocker dans sessionStorage
    try {
      sessionStorage.setItem("rei_audio_b64", d.b64);
      sessionStorage.setItem("rei_audio_mime", d.mime || "audio/webm");
      sessionStorage.setItem("rei_audio_lang", d.lang || "fr");
      sessionStorage.setItem("rei_audio_ts", String(d.ts || Date.now()));
    } catch(ex) {}
    // Déclencher le bouton caché Streamlit via un lien URL
    // On utilise query_params avec seulement le timestamp (pas l'audio - trop grand)
    // L'audio est stocké dans sessionStorage et récupéré via un petit fetch
    window.location.href = window.location.href.split("?")[0] + "?rei_ts=" + (d.ts || Date.now());
  }, false);
  
  // Aussi écouter depuis les iframes filles
  try {
    var iframes = document.querySelectorAll("iframe");
    iframes.forEach(function(fr) {
      try {
        fr.contentWindow.addEventListener("message", function(e) {
          var d = e.data;
          if(d && d.type === "rei_audio") window.dispatchEvent(new MessageEvent("message", {data: d}));
        }, false);
      } catch(ex) {}
    });
  } catch(ex) {}
})();
</script>
"""

# ── VRAIE SOLUTION FINALE : utiliser un endpoint Streamlit natif ──
# postMessage cross-origin est bloqué. La seule solution fiable sans declare_component :
# Groq Whisper depuis le navigateur directement avec la clé dans st.secrets
# MAIS exposer la clé côté client est risqué.
# Solution : SpeechRecognition Web API (gratuite, native, pas de clé)

# ── Vérifier si une transcription STT est arrivée via query_params ──
_rei_ts = st.query_params.get("rei_ts", "")
if _rei_ts and _rei_ts != str(st.session_state.get("last_rei_ts", "")):
    st.session_state.last_rei_ts = _rei_ts
    # L'audio est dans sessionStorage côté JS — on ne peut pas y accéder depuis Python
    # Donc on utilise la Web Speech API à la place (voir widget ci-dessus)
    pass

# ── Vérifier si une transcription texte est arrivée via query_params ──
_stt_txt = st.query_params.get("stt_text", "")
if _stt_txt and _stt_txt.strip():
    st.session_state.input_value = _stt_txt.strip()
    st.session_state.clear_input = False
    st.query_params.clear()
    st.rerun()

# ── Traiter l'audio si _whisper_result reçu (legacy declare_component) ──
if (_whisper_result and isinstance(_whisper_result, dict)
        and _whisper_result.get("b64")
        and _whisper_result.get("ts",0) != st.session_state.get("last_audio_ts",0)):
    st.session_state.last_audio_ts = _whisper_result["ts"]
    _w_b64  = _whisper_result["b64"]
    _w_mime = _whisper_result.get("mime","audio/ogg")
    _w_lang = _whisper_result.get("lang","fr")
    try:
        import base64
        from groq import Groq as _GroqClient
        try:
            _groq_key = st.secrets["GROQ_API_KEY"]
        except:
            _groq_key = os.environ.get("GROQ_API_KEY","")
        if not _groq_key:
            _eng = st.session_state.get("engine")
            _groq_key = getattr(_eng,"api_key","") or getattr(_eng,"groq_api_key","")
        _gc = _GroqClient(api_key=_groq_key)
        _audio_bytes = base64.b64decode(_w_b64)
        _ext = "ogg" if "ogg" in _w_mime else ("mp4" if "mp4" in _w_mime else "webm")
        with tempfile.NamedTemporaryFile(suffix="."+_ext, delete=False) as _tf:
            _tf.write(_audio_bytes)
            _tf_path = _tf.name
        with open(_tf_path,"rb") as _af:
            _whisper_resp = _gc.audio.transcriptions.create(
                file=(_af.name, _af, _w_mime),
                model="whisper-large-v3",
                language=_w_lang,
                response_format="text"
            )
        os.unlink(_tf_path)
        _transcribed = str(_whisper_resp).strip() if _whisper_resp else ""
        if _transcribed:
            st.session_state.input_value = _transcribed
            st.session_state.whisper_ready = True
    except Exception as _we:
        st.session_state.whisper_ready = False
        st.error(f"Whisper erreur: {_we}")
    st.rerun()

# ── Script de liaison STT → champ Streamlit : SUPPRIMÉ ──
# Inutile : declare_component remonte la valeur directement via _whisper_result

if st.session_state.regen_index is not None:
    idx=st.session_state.regen_index; q=st.session_state.regen_question
    if q:
        rep,res,_=process_msg(q,regen=True,regen_idx=idx)
        st.session_state.messages[idx]["content"]=rep
        st.session_state.mémoire.add_exchange(st.session_state.user_id,q,rep)
        _regen_lang = detect_text_lang(rep)
        play_reihana_voice(rep, lang=_regen_lang)
    st.session_state.regen_index=None; st.session_state.regen_question=""; st.rerun()

if send_btn and user_input and user_input.strip():
    question=user_input.strip()
    # ── Vider le champ de saisie AVANT l'envoi ──
    st.session_state.input_value = ""
    st.session_state.clear_input = True
    st.session_state.messages.append({"role":"user","content":question})
    rep,res,web_res=process_msg(question)
    if web_res:
        wh='<div style="font-family:Orbitron,monospace;font-size:0.58rem;color:#00cc88;margin:4px 0;letter-spacing:1px;">🌐 SOURCES</div>'
        for r in web_res[:3]:
            if r.get('url'): wh+=f'<div class="web-card">🔗 <a href="{r["url"]}" target="_blank" style="color:#00cc88;">{r["title"][:55]}</a></div>'
        st.markdown(wh, unsafe_allow_html=True)
    st.session_state.mémoire.add_exchange(st.session_state.user_id,question,rep)
    st.session_state.messages.append({"role":"assistant","content":rep})
    # ── Chiffrer et sauvegarder (livre p.45) ──
    encrypt_conversation(question, rep)
    # ── Mettre à jour profil utilisateur ──
    get_user_profile(st.session_state.user_id)
    st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.57rem;color:rgba(150,150,200,0.38);text-align:right;margin:-3px 0 5px 0;">⚡ {res.get("model","")[:26]} · {res.get("tokens",0)} tokens</div>', unsafe_allow_html=True)
    # Détecter chanson et stocker
    _is_song, _smood, _slang, _sverses = detect_song(rep)
    if _is_song and _sverses:
        st.session_state.last_song = {"verses": _sverses, "mood": _smood, "lang": _slang, "msg_index": len(st.session_state.messages)-1}
    else:
        # Auto-lecture gTTS normale
        _auto_lang = detect_text_lang(rep)
        play_reihana_voice(rep, lang=_auto_lang)
    st.rerun()

# ══ DASHBOARD ADMIN ÉTENDU (livre p.50) ══
if st.session_state.admin_dashboard_open:
    st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
    show_admin_dashboard()

# ══ TRAITER GESTE DÉTECTÉ ══
_gesture_in = st.query_params.get("gesture", "")
if _gesture_in and _gesture_in != st.session_state.get("last_gesture",""):
    st.session_state.last_gesture = _gesture_in
    st.query_params.clear()
    gesture_actions = {
        "☝️ UN DOIGT — Valider": lambda: None,  # valider
        "✊ POING — Pause": lambda: None,  # pause
        "🖐️ MAIN OUVERTE — Stop": lambda: None,  # stop
        "✌️ DEUX DOIGTS — Activer IA": lambda: None,  # activer
        "👍 POUCE — J'aime": lambda: None,  # j'aime
    }
    st.toast(f"✋ Geste détecté : {_gesture_in}", icon="✋")
    if "STOP" in _gesture_in.upper() or "MAIN OUVERTE" in _gesture_in:
        st.session_state.voice_input = ""

# ══ TRAITER VISAGE DÉTECTÉ ══
_face_det = st.query_params.get("face_detected","")
if _face_det:
    _face_age = st.query_params.get("face_age","?")
    _face_gender = st.query_params.get("face_gender","?")
    _face_expr = st.query_params.get("face_expr","?")
    _face_name = st.query_params.get("face_name","inconnu")
    _face_cam  = st.query_params.get("face_cam","user")
    st.session_state.face_access_log.append({
        "ts": datetime.now().isoformat(),
        "age": _face_age, "gender": _face_gender, "expression": _face_expr,
        "name": _face_name, "cam": _face_cam
    })
    # ── Si visage connu et nouveau : salutation personnalisée ──
    _last_name = st.session_state.get("last_face_name","")
    if _face_name and _face_name != "inconnu" and _face_name != _last_name:
        st.session_state.last_face_name = _face_name
        # Personnaliser le profil utilisateur avec ce nom
        st.session_state.user_id = _face_name
        # Message de bienvenue automatique dans le chat
        _greet_text = f"Bonjour {_face_name} ! 🌸 Je t'ai reconnu(e) ! Comment puis-je t'aider aujourd'hui ?"
        if st.session_state.langue == "🇬🇧 English":
            _greet_text = f"Hello {_face_name}! 🌸 I recognized you! How can I help you today?"
        elif st.session_state.langue == "🇩🇿 العربية":
            _greet_text = f"مرحباً {_face_name}! 🌸 لقد تعرفت عليك! كيف يمكنني مساعدتك اليوم؟"
        st.session_state.messages.append({"role":"assistant","content":_greet_text})
        play_reihana_voice(_greet_text, lang=detect_text_lang(_greet_text))
        st.rerun()

# ── TRAITER ENRÔLEMENT DE VISAGE ──
_face_enrolled = st.query_params.get("face_enrolled","")
if _face_enrolled and _face_enrolled.strip():
    _enrolled_name = _face_enrolled.strip()
    # Sauvegarder le profil de ce nouveau visage connu
    get_user_profile(_enrolled_name)
    if "face_known_names" not in st.session_state:
        st.session_state.face_known_names = []
    if _enrolled_name not in st.session_state.face_known_names:
        st.session_state.face_known_names.append(_enrolled_name)
    st.toast(f"✅ Visage de {_enrolled_name} enregistré dans la base !", icon="👁️")
    st.query_params.clear()

st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)
st.markdown(f'<div style="font-family:Orbitron,monospace;color:rgba({g},0.45);font-size:0.6rem;letter-spacing:3px;margin-bottom:8px;">SUGGESTIONS RAPIDES</div>', unsafe_allow_html=True)
scols=st.columns(len(T["suggestions"]))
for i,(col,sug) in enumerate(zip(scols,T["suggestions"])):
    with col:
        if st.button(sug,key=f"sug{i}",use_container_width=True):
            st.session_state.messages.append({"role":"user","content":sug})
            rep,res,_=process_msg(sug)
            st.session_state.messages.append({"role":"assistant","content":rep})
            _sug_lang = detect_text_lang(rep)
            play_reihana_voice(rep, lang=_sug_lang)
            st.rerun()
