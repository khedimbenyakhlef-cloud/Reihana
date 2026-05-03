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
    "last_voice_text": "",
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

# ── Reconnaissance vocale v9 — STYLE CHATGPT : frappe en temps réel ──
_stt_lang_map = {"🇫🇷 Français":"fr-FR","🇩🇿 العربية":"ar-SA","🇬🇧 English":"en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue,"fr-FR")

# ── Lire texte + commande envoi depuis query params ──
_qp = st.query_params
_vt = _qp.get("vt","").strip()
_vs = _qp.get("vs","0")
if _vt and _vt != st.session_state.get("last_voice_text",""):
    st.session_state.input_value = _vt
    st.session_state.last_voice_text = _vt
    st.query_params.clear()
    if _vs == "1":
        _question = _vt
        st.session_state.input_value = ""
        st.session_state.last_voice_text = ""
        st.session_state.messages.append({"role":"user","content":_question})
        _rep,_res,_wres = process_msg(_question)
        if _wres:
            _wh='<div style="font-family:Orbitron,monospace;font-size:0.58rem;color:#00cc88;margin:4px 0;">🌐 SOURCES</div>'
            for _wr in _wres[:3]:
                if _wr.get("url"): _wh+=f'<div class="web-card">🔗 <a href="{_wr["url"]}" target="_blank" style="color:#00cc88;">{_wr["title"][:55]}</a></div>'
            st.markdown(_wh, unsafe_allow_html=True)
        st.session_state.mémoire.add_exchange(st.session_state.user_id,_question,_rep)
        st.session_state.messages.append({"role":"assistant","content":_rep})
        _is_song,_smood,_slang,_sverses = detect_song(_rep)
        if _is_song and _sverses:
            st.session_state.last_song={"verses":_sverses,"mood":_smood,"lang":_slang,"msg_index":len(st.session_state.messages)-1}
        else:
            play_reihana_voice(_rep, lang=detect_text_lang(_rep))
        st.rerun()
    else:
        st.rerun()

# ── Widget HTML complet v9 — textarea + MICRO + STOP + ENVOYER (style ChatGPT) ──
_init_val = st.session_state.get("input_value","").replace("\\","\\\\").replace("`","\\`")
import streamlit.components.v1 as _cmp
_cmp.html(f"""
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:'Orbitron',monospace;}}
#rei-ta{{
  width:100%;min-height:82px;max-height:160px;
  background:rgba(0,15,35,0.9);
  border:1.5px solid rgba(0,255,200,0.22);
  border-radius:8px;color:#ddf8ff;
  font-family:'Rajdhani',sans-serif;font-size:14px;
  padding:10px 13px;resize:vertical;outline:none;
  transition:border-color .2s, box-shadow .2s;
  overflow-y:auto;
}}
#rei-ta:focus{{border-color:rgba(0,255,200,0.55);}}
#rei-ta.rec{{border-color:#ff3333;box-shadow:0 0 10px rgba(255,51,51,0.25);}}
#rei-ta::placeholder{{color:rgba(0,200,160,0.38);font-style:italic;}}
#rei-bar{{display:flex;align-items:center;gap:7px;margin-top:6px;}}
.rb{{font-family:'Orbitron',monospace;font-size:10px;letter-spacing:1px;
     padding:6px 13px;border-radius:6px;border:1px solid;cursor:pointer;
     transition:all .15s;white-space:nowrap;background:transparent;}}
#rb-mic{{border-color:rgba(0,255,200,0.45);color:#00ffcc;}}
#rb-mic:hover{{background:rgba(0,255,200,0.12);}}
#rb-mic.on{{border-color:#ff3333;color:#ff5555;animation:pm 1s infinite;}}
@keyframes pm{{0%,100%{{box-shadow:0 0 3px rgba(255,50,50,.3)}}50%{{box-shadow:0 0 10px rgba(255,50,50,.7)}}}}
#rb-stop{{border-color:rgba(255,160,0,.4);color:#ffaa00;}}
#rb-stop:hover{{background:rgba(255,160,0,.1);}}
#rb-send{{border-color:rgba(0,180,255,.5);color:#88ddff;margin-left:auto;padding:6px 18px;}}
#rb-send:hover{{background:rgba(0,180,255,.15);}}
#rei-st{{font-size:8px;letter-spacing:2px;color:rgba(0,255,200,.4);flex:1;
         overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
#rei-st.on{{color:#ff4444;}}
#rei-st.ok{{color:#00ff88;}}
#rei-st.err{{color:#ffaa00;}}
#rei-wv{{display:flex;align-items:flex-end;gap:2px;height:14px;opacity:0;transition:opacity .3s;}}
#rei-wv.on{{opacity:1;}}
.rw{{width:3px;border-radius:2px;min-height:2px;
     background:linear-gradient(0deg,#00ffcc,#8800ff);transition:height .06s;}}
</style>

<textarea id="rei-ta" placeholder="Écris ou parle à REIHANA... 👂">{_init_val}</textarea>

<div id="rei-bar">
  <button class="rb" id="rb-mic">🎙️ MICRO</button>
  <button class="rb" id="rb-stop">⏹ STOP</button>
  <span id="rei-st">🎙️ PRÊT</span>
  <div id="rei-wv">
    <div class="rw" style="height:2px"></div><div class="rw" style="height:5px"></div>
    <div class="rw" style="height:9px"></div><div class="rw" style="height:13px"></div>
    <div class="rw" style="height:14px"></div><div class="rw" style="height:13px"></div>
    <div class="rw" style="height:9px"></div><div class="rw" style="height:5px"></div>
    <div class="rw" style="height:2px"></div>
  </div>
  <button class="rb" id="rb-send">📨 ENVOYER</button>
</div>

<script>
(function(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var rec=null,on=false,allFin="",rafId=null,an=null;
  var lang="{_stt_lang}";
  var ta=document.getElementById("rei-ta");
  var bMic=document.getElementById("rb-mic");
  var bStp=document.getElementById("rb-stop");
  var bSnd=document.getElementById("rb-send");
  var sSt=document.getElementById("rei-st");
  var wv=document.getElementById("rei-wv");
  var def=[2,5,9,13,14,13,9,5,2];

  function setSt(c,t){{sSt.className=c;sSt.innerText=t;}}

  function startVis(){{
    if(an)return;
    navigator.mediaDevices.getUserMedia({{
      audio:{{noiseSuppression:true,echoCancellation:true,autoGainControl:true}},video:false
    }}).then(function(s){{
      var ctx=new(window.AudioContext||window.webkitAudioContext)();
      an=ctx.createAnalyser();an.fftSize=64;
      ctx.createMediaStreamSource(s).connect(an);
      var d=new Uint8Array(an.frequencyBinCount);
      wv.classList.add("on");
      (function draw(){{
        if(!on){{
          wv.classList.remove("on");
          wv.querySelectorAll(".rw").forEach(function(b,i){{b.style.height=def[i]+"px";}});
          an=null;return;
        }}
        rafId=requestAnimationFrame(draw);
        an.getByteFrequencyData(d);
        wv.querySelectorAll(".rw").forEach(function(b,i){{
          b.style.height=Math.max(2,Math.min(14,d[Math.floor(i*d.length/9)]/6))+"px";
        }});
      }})();
    }}).catch(function(){{}});
  }}

  function mkRec(){{
    var r=new SR();
    r.lang=lang;r.continuous=true;r.interimResults=true;r.maxAlternatives=1;
    r.onstart=function(){{
      on=true;allFin="";
      bMic.classList.add("on");
      ta.classList.add("rec");
      setSt("on","🔴 ÉCOUTE EN COURS...");
      startVis();
    }};
    r.onresult=function(ev){{
      var itr="";
      for(var i=ev.resultIndex;i<ev.results.length;i++){{
        if(ev.results[i].isFinal)allFin+=ev.results[i][0].transcript+" ";
        else itr+=ev.results[i][0].transcript;
      }}
      // ✨ FRAPPE EN TEMPS RÉEL dans le textarea
      ta.value=(allFin+itr).trim();
      ta.scrollTop=ta.scrollHeight;
      setSt("on","🔴 "+(allFin+itr).trim().slice(-45));
    }};
    r.onerror=function(ev){{
      var m={{"not-allowed":"🚫 Autoriser le micro dans Chrome","no-speech":"💬 Rien entendu","network":"🌐 Erreur réseau","aborted":"⏹"}};
      setSt("err",m[ev.error]||("⚠️ "+ev.error));
      stopRec();
    }};
    r.onend=function(){{if(on){{try{{r.start();}}catch(x){{on=false;setSt("","🎙️ PRÊT");}}}}  }};
    return r;
  }}

  function startRec(){{
    if(!SR){{setSt("err","⚠️ Chrome/Edge requis");return;}}
    if(on)return;
    allFin="";rec=mkRec();
    try{{rec.start();}}catch(e){{setSt("err","⚠️ Vérifier autorisation micro");}}
  }}

  function stopRec(){{
    on=false;cancelAnimationFrame(rafId);
    bMic.classList.remove("on");ta.classList.remove("rec");
    if(rec){{try{{rec.stop();rec.abort();}}catch(e){{}}rec=null;}}
    if(ta.value.trim())setSt("ok","✅ Texte prêt — cliquez 📨 ENVOYER");
    else setSt("","🎙️ PRÊT");
  }}

  function sendMsg(){{
    var t=ta.value.trim();
    if(!t)return;
    if(on)stopRec();
    setSt("ok","📨 Envoi en cours...");
    window.parent.location.href=window.parent.location.pathname
      +"?vt="+encodeURIComponent(t)+"&vs=1";
  }}

  bMic.onclick=startRec;
  bStp.onclick=stopRec;
  bSnd.onclick=sendMsg;
  ta.addEventListener("keydown",function(e){{
    if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){{e.preventDefault();sendMsg();}}
  }});
}})();
</script>
""", height=160, scrolling=False)

# Variables nécessaires pour la suite du code (regen etc.)
user_input = st.session_state.get("input_value","")
send_btn = False  # Tout passe par le bouton HTML ENVOYER via query_params

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
