# ═══════════════════════════════════════════════════════════════
# PATCH RECONNAISSANCE VOCALE ULTRA-RÉALISTE REIHANA v3.0
# 1. Bouton micro 🎙️ à côté de la zone de texte
# 2. Web Speech API - reconnaissance FR/AR/EN automatique
# 3. Texte reconnu s'écrit dans le champ en temps réel
# 4. Animation REIHANA pendant l'écoute (onde vocale, yeux)
# 5. Visualiseur de niveau sonore en temps réel
# 6. Détection silence automatique → envoi automatique
# 7. Indicateur d'état (écoute / traitement / erreur)
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# ════════════════════════════════════════════
# PARTIE 1 — Remplacer la zone d'input + send_btn
# par la version avec micro intégré
# ════════════════════════════════════════════

OLD_INPUT_ZONE = '''st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

ci, cs2 = st.columns([5,1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")'''

NEW_INPUT_ZONE = '''st.markdown('<div class="holo-line"></div>', unsafe_allow_html=True)

# ── Reconnaissance vocale ultra-réaliste ──
_stt_lang_map = {"🇫🇷 Français": "fr-FR", "🇩🇿 العربية": "ar-SA", "🇬🇧 English": "en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue, "fr-FR")

import streamlit.components.v1 as _stt_comp
_stt_comp.html(f"""
<style>
  body{{margin:0;padding:0;background:transparent;overflow:hidden;}}
  
  #reiMicZone{{
    display:flex;
    align-items:center;
    gap:8px;
    padding:4px 0;
    font-family:'Orbitron',monospace;
  }}
  
  #reiMicBtn{{
    width:52px; height:52px;
    border-radius:50%;
    border:2px solid rgba(0,255,200,0.5);
    background:linear-gradient(135deg,rgba(0,20,60,0.9),rgba(0,10,40,0.95));
    color:#00ffcc;
    font-size:22px;
    cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    transition:all 0.3s ease;
    box-shadow:0 0 12px rgba(0,255,200,0.2);
    flex-shrink:0;
    position:relative;
  }}
  #reiMicBtn:hover{{
    background:linear-gradient(135deg,rgba(0,40,80,0.9),rgba(0,20,60,0.95));
    box-shadow:0 0 20px rgba(0,255,200,0.5);
    transform:scale(1.08);
  }}
  #reiMicBtn.listening{{
    border-color:rgba(255,60,60,0.9);
    color:#ff4444;
    background:linear-gradient(135deg,rgba(60,0,0,0.9),rgba(40,0,0,0.95));
    box-shadow:0 0 25px rgba(255,60,60,0.6);
    animation:micPulse 0.8s ease-in-out infinite;
  }}
  #reiMicBtn.processing{{
    border-color:rgba(255,200,0,0.9);
    color:#ffcc00;
    animation:micProcess 1s linear infinite;
  }}
  @keyframes micPulse{{
    0%,100%{{box-shadow:0 0 15px rgba(255,60,60,0.4);transform:scale(1);}}
    50%{{box-shadow:0 0 35px rgba(255,60,60,0.9);transform:scale(1.12);}}
  }}
  @keyframes micProcess{{
    0%{{transform:rotate(0deg);}}
    100%{{transform:rotate(360deg);}}
  }}
  
  /* Anneau d'onde sonore autour du micro */
  #reiMicRing{{
    position:absolute;
    width:52px; height:52px;
    border-radius:50%;
    border:2px solid rgba(255,60,60,0);
    pointer-events:none;
    transition:all 0.1s;
  }}
  #reiMicBtn.listening #reiMicRing{{
    animation:ringExpand 1s ease-out infinite;
  }}
  @keyframes ringExpand{{
    0%{{width:52px;height:52px;border-color:rgba(255,60,60,0.8);opacity:1;}}
    100%{{width:90px;height:90px;margin:-19px;border-color:rgba(255,60,60,0);opacity:0;}}
  }}
  
  #reiMicInfo{{
    flex:1;
    min-width:0;
  }}
  
  #reiMicStatus{{
    font-size:9px;
    letter-spacing:2px;
    color:rgba(0,255,200,0.5);
    margin-bottom:3px;
    height:14px;
    transition:all 0.3s;
  }}
  #reiMicStatus.active{{color:#ff4444; animation:statusBlink 1s ease-in-out infinite;}}
  #reiMicStatus.processing{{color:#ffcc00;}}
  #reiMicStatus.success{{color:#00ff88;}}
  @keyframes statusBlink{{0%,100%{{opacity:0.6;}}50%{{opacity:1;}}}}
  
  /* Transcription en temps réel */
  #reiTranscript{{
    font-size:11px;
    color:#aaddff;
    font-family:'Rajdhani',sans-serif;
    letter-spacing:0.5px;
    min-height:16px;
    max-height:40px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    font-style:italic;
    opacity:0.8;
    transition:all 0.2s;
  }}
  
  /* Visualiseur de niveau sonore */
  #reiVolBars{{
    display:flex;
    align-items:flex-end;
    gap:2px;
    height:28px;
    padding:4px 0;
    opacity:0;
    transition:opacity 0.3s;
  }}
  #reiVolBars.active{{opacity:1;}}
  .reiVb{{
    width:3px;
    background:linear-gradient(0deg,#00ffcc,#7700ff);
    border-radius:1.5px;
    min-height:3px;
    transition:height 0.05s ease;
    box-shadow:0 0 3px rgba(0,255,200,0.5);
  }}
</style>

<div id="reiMicZone">
  <button id="reiMicBtn" onclick="toggleMic()" title="Cliquer pour parler">
    <div id="reiMicRing"></div>
    🎙️
  </button>
  <div id="reiMicInfo">
    <div id="reiMicStatus">MICRO PRÊT</div>
    <div id="reiTranscript">Cliquez sur 🎙️ pour parler à REIHANA...</div>
    <div id="reiVolBars">
      <div class="reiVb" style="height:4px" id="vb0"></div>
      <div class="reiVb" style="height:8px" id="vb1"></div>
      <div class="reiVb" style="height:14px" id="vb2"></div>
      <div class="reiVb" style="height:18px" id="vb3"></div>
      <div class="reiVb" style="height:22px" id="vb4"></div>
      <div class="reiVb" style="height:18px" id="vb5"></div>
      <div class="reiVb" style="height:14px" id="vb6"></div>
      <div class="reiVb" style="height:8px" id="vb7"></div>
      <div class="reiVb" style="height:4px" id="vb8"></div>
    </div>
  </div>
</div>

<script>
var _recog = null;
var _listening = false;
var _analyser = null;
var _animFrame = null;
var _silenceTimer = null;
var _finalText = "";
var _sttLang = "{_stt_lang}";

var _btn = document.getElementById("reiMicBtn");
var _status = document.getElementById("reiMicStatus");
var _transcript = document.getElementById("reiTranscript");
var _volBars = document.getElementById("reiVolBars");
var _vbs = document.querySelectorAll(".reiVb");

// ── Vérifier support ──
var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if(!SpeechRecognition){{
  _status.innerText = "⚠️ NON SUPPORTÉ (Chrome requis)";
  _btn.style.opacity = "0.3";
  _btn.disabled = true;
}}

// ── Visualiseur niveau sonore via AudioContext ──
function startVisualizer(){{
  navigator.mediaDevices.getUserMedia({{audio:true,video:false}}).then(function(stream){{
    var ctx = new (window.AudioContext||window.webkitAudioContext)();
    var src = ctx.createMediaStreamSource(stream);
    _analyser = ctx.createAnalyser();
    _analyser.fftSize = 256;
    src.connect(_analyser);
    var data = new Uint8Array(_analyser.frequencyBinCount);
    
    _volBars.classList.add("active");
    
    function drawBars(){{
      if(!_listening){{
        _volBars.classList.remove("active");
        _vbs.forEach(function(b){{b.style.height="3px";}});
        return;
      }}
      _animFrame = requestAnimationFrame(drawBars);
      _analyser.getByteFrequencyData(data);
      
      var bands = [2,4,6,10,14,18,14,10,6];
      bands.forEach(function(band, i){{
        var sum = 0;
        for(var j=0;j<band;j++) sum += data[Math.floor(j*data.length/band/9+i*data.length/9)];
        var avg = sum/band;
        var h = Math.max(3, Math.min(26, avg/4));
        _vbs[i].style.height = h + "px";
      }});
    }}
    drawBars();
  }}).catch(function(){{
    // Micro refusé - barres statiques
  }});
}}

// ── Créer reconnaissance ──
function createRecognition(){{
  if(!SpeechRecognition) return null;
  var r = new SpeechRecognition();
  r.lang = _sttLang;
  r.continuous = true;
  r.interimResults = true;
  r.maxAlternatives = 1;
  
  r.onstart = function(){{
    _listening = true;
    _btn.classList.add("listening");
    _status.className = "active";
    _status.innerText = "🔴 ÉCOUTE EN COURS...";
    _transcript.innerText = "Je vous écoute...";
    startVisualizer();
    
    // Signaler à l'avatar REIHANA qu'elle écoute
    try{{
      var av = window.parent.document.getElementById("reiBgAvatar");
      if(av) av.style.filter = "drop-shadow(0 0 30px rgba(255,80,80,0.6))";
    }}catch(e){{}}
  }};
  
  r.onresult = function(e){{
    var interim = "";
    _finalText = "";
    for(var i=e.resultIndex; i<e.results.length; i++){{
      if(e.results[i].isFinal){{
        _finalText += e.results[i][0].transcript + " ";
      }} else {{
        interim += e.results[i][0].transcript;
      }}
    }}
    
    var display = (_finalText + interim).trim();
    _transcript.innerText = display || "...";
    
    // Envoyer texte intermédiaire au champ Streamlit via postMessage
    if(display){{
      window.parent.postMessage({{type:"reiSTT", text:display, final:_finalText.trim()!=""}}, "*");
    }}
    
    // Réinitialiser timer silence (3 secondes sans parler → stop)
    clearTimeout(_silenceTimer);
    if(_finalText.trim()){{
      _silenceTimer = setTimeout(function(){{
        if(_listening && _finalText.trim()){{
          stopMic(true); // true = envoyer automatiquement
        }}
      }}, 2800);
    }}
  }};
  
  r.onerror = function(e){{
    _status.className = "";
    if(e.error === "no-speech"){{
      _status.innerText = "💬 AUCUN SON DÉTECTÉ";
    }} else if(e.error === "not-allowed"){{
      _status.innerText = "🚫 MICRO REFUSÉ";
    }} else{{
      _status.innerText = "⚠️ ERREUR: " + e.error;
    }}
    stopMic(false);
  }};
  
  r.onend = function(){{
    if(_listening){{
      // Reconnexion auto si l'utilisateur parle encore
      try{{ r.start(); }}catch(ex){{
        _listening = false;
        _btn.classList.remove("listening","processing");
      }}
    }}
  }};
  
  return r;
}}

// ── Toggle micro ──
function toggleMic(){{
  if(_listening){{
    stopMic(false);
  }} else {{
    startMic();
  }}
}}

function startMic(){{
  _finalText = "";
  _recog = createRecognition();
  if(!_recog) return;
  try{{
    _recog.start();
  }}catch(e){{
    _status.innerText = "⚠️ Impossible de démarrer";
  }}
}}

function stopMic(autoSend){{
  _listening = false;
  clearTimeout(_silenceTimer);
  cancelAnimationFrame(_animFrame);
  _volBars.classList.remove("active");
  _vbs.forEach(function(b){{b.style.height="3px";}});
  
  if(_recog){{
    try{{ _recog.stop(); _recog.abort(); }}catch(e){{}}
    _recog = null;
  }}
  
  _btn.classList.remove("listening");
  
  // Restaurer avatar
  try{{
    var av = window.parent.document.getElementById("reiBgAvatar");
    if(av) av.style.filter = "";
  }}catch(e){{}}
  
  var txt = _finalText.trim();
  if(txt){{
    _btn.classList.add("processing");
    _status.className = "processing";
    _status.innerText = "⚙️ TRAITEMENT...";
    _transcript.innerText = "\"" + txt.substring(0,60) + (txt.length>60?"...":"") + "\"";
    
    // Envoyer le texte final à Streamlit
    window.parent.postMessage({{type:"reiSTT_FINAL", text:txt, autoSend:autoSend}}, "*");
    
    setTimeout(function(){{
      _btn.classList.remove("processing");
      _status.className = "success";
      _status.innerText = "✅ MESSAGE ENVOYÉ";
      setTimeout(function(){{
        _status.className = "";
        _status.innerText = "MICRO PRÊT";
        _transcript.innerText = "Cliquez sur 🎙️ pour parler à REIHANA...";
        _finalText = "";
      }}, 2000);
    }}, 1500);
  }} else {{
    _status.className = "";
    _status.innerText = "MICRO PRÊT";
    _transcript.innerText = "Cliquez sur 🎙️ pour parler à REIHANA...";
  }}
}}

// ── Écouter les messages STT depuis l'iframe parente ──
// (pour mettre à jour la langue si l'utilisateur change)
window.addEventListener("message", function(e){{
  if(e.data && e.data.type === "reiSetSttLang"){{
    _sttLang = e.data.lang;
    if(_recog) _recog.lang = _sttLang;
  }}
}});
</script>
""", height=140)

# ── Zone texte + boutons ──
ci, cs2, cs3 = st.columns([5, 1, 1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
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

# ── Script de liaison STT → champ Streamlit ──
import streamlit.components.v1 as _bridge_comp
_bridge_comp.html("""
<script>
// Écouter les messages postMessage de l'iframe STT
window.addEventListener("message", function(e) {
  if(!e.data || !e.data.type) return;
  
  if(e.data.type === "reiSTT_FINAL") {
    var txt = e.data.text;
    var autoSend = e.data.autoSend;
    
    // Trouver le textarea de Streamlit et injecter le texte
    var iframes = document.querySelectorAll("iframe");
    
    // Méthode 1: Chercher dans tous les iframes
    function injectText(targetDoc) {
      var ta = targetDoc.querySelector('textarea[data-testid="stTextArea"]') ||
               targetDoc.querySelector('textarea');
      if(ta) {
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        nativeInputValueSetter.call(ta, txt);
        ta.dispatchEvent(new Event('input', {bubbles:true}));
        ta.dispatchEvent(new Event('change', {bubbles:true}));
        ta.focus();
        return true;
      }
      return false;
    }
    
    // Essayer dans le document courant (parent)
    var done = injectText(document);
    
    // Si auto-envoi, cliquer sur ENVOYER après injection
    if(autoSend) {
      setTimeout(function() {
        var btns = Array.from(document.querySelectorAll('button'));
        var sendBtn = btns.find(function(b) {
          return b.innerText.includes('ENVOYER') || 
                 b.innerText.includes('SEND') || 
                 b.innerText.includes('إرسال');
        });
        if(sendBtn) {
          sendBtn.click();
        }
      }, 800);
    }
  }
  
  if(e.data.type === "reiSTT") {
    // Mise à jour en temps réel dans le textarea
    var txt = e.data.text;
    var ta = document.querySelector('textarea');
    if(ta && e.data.final === false) {
      // Afficher texte intermédiaire (italique via placeholder-like)
      ta.setAttribute('placeholder', '🎙️ ' + txt + '...');
    } else if(ta && txt) {
      var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      nativeInputValueSetter.call(ta, txt);
      ta.dispatchEvent(new Event('input', {bubbles:true}));
    }
  }
});
</script>
""", height=0)'''

if OLD_INPUT_ZONE in c:
    c = c.replace(OLD_INPUT_ZONE, NEW_INPUT_ZONE)
    ok.append("✅ PARTIE 1: Zone micro ultra-réaliste + visualiseur + auto-envoi")
else:
    errors.append("❌ PARTIE 1: Zone input non trouvée")

# ════════════════════════════════════════════
# PARTIE 2 — Session state : voice_input
# ════════════════════════════════════════════
OLD_DEFS_END = '''    "last_song":{"verses":[],"mood":"calm","lang":"fr","msg_index":-1},
}'''
NEW_DEFS_END = '''    "last_song":{"verses":[],"mood":"calm","lang":"fr","msg_index":-1},
    "voice_input": "",
}'''

if OLD_DEFS_END in c:
    c = c.replace(OLD_DEFS_END, NEW_DEFS_END)
    ok.append("✅ PARTIE 2: Session state voice_input ajouté")
else:
    errors.append("❌ PARTIE 2: Fin des defs session state non trouvée")

# ════════════════════════════════════════════
# ÉCRITURE
# ════════════════════════════════════════════
if c != original:
    open('reihana.py', 'w', encoding='utf-8').write(c)
    print("\n" + "═"*60)
    print("  PATCH MICRO ULTRA-RÉALISTE REIHANA — RÉSULTATS")
    print("═"*60)
    for msg in ok:
        print(msg)
    if errors:
        print("\n⚠️  PROBLÈMES:")
        for e in errors:
            print(e)
    print(f"\n✅ FICHIER reihana.py SAUVEGARDÉ ({len(ok)}/2 parties OK)")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION")
    for e in errors:
        print(e)
