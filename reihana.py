"""
REIHANA v3.0 MEGA EDITION
Fondée par Khedim Benyakhlef (Biny-Joe)
"""
import streamlit as st
import sys, os, json, time, tempfile, urllib.request, urllib.parse
import base64
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

_comp_v1.html(_stt_html, height=70)

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


# ── Zone texte + boutons ──
ci, cs2, cs3 = st.columns([5, 1, 1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    # Afficher notification si Whisper vient de transcrire
    if st.session_state.get("whisper_ready"):
        st.session_state.whisper_ready = False
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")
with cs3:
    st.markdown("<br>", unsafe_allow_html=True)
    # Bouton stop micro (visuel seulement - JS gère le vrai stop)
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
