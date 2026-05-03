# ═══════════════════════════════════════════════════════════════
# PATCH MUSIQUE HARMONIEUSE REIHANA v3.0
# 1. Musique s'adoucit quand REIHANA parle (harmonie voix/musique)
# 2. REIHANA peut "chanter" sur la musique d'ambiance
# 3. Bouton volume curseur pour la musique d'ambiance
# 4. Mood musical suit automatiquement la réponse IA
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# ════════════════════════════════════════════
# PARTIE 1 — Remplacer le bloc musique sidebar
# (ancien composant HTML avec speechSynthesis)
# par le nouveau avec: volume slider + chant + harmonie gTTS
# ════════════════════════════════════════════

OLD_MUSIC_BLOCK = '''    cs, cm = st.columns([2,1])
    with cs: st.markdown(f\'<span class="status-online"></span><span style="color:#00ff88;font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:2px;">{T["online"]}</span>\', unsafe_allow_html=True)
    with cm:
        st.components.v1.html("""<style>body{margin:0;padding:2px;background:transparent}#b{background:#1a0044;color:#00ffcc;border:2px solid #00ffcc;border-radius:8px;padding:8px 16px;cursor:pointer;font-size:14px;font-weight:bold;width:100%;display:block}#b:hover{background:#2a0066}#m{color:#7700ff;font-size:9px;font-family:monospace;text-align:center;margin-top:3px}</style><audio id="a" loop></audio><button id="b" onclick="t(this)">&#127925;&#9654;</button><div id="m">AMBIENT</div><script>var S={calm:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3"],happy:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3"],epic:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3"],sad:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3"],mystery:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3"],romantic:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3"],tech:["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3","https://www.soundhelix.com/examples/mp3/SoundHelix-Song-17.mp3"]};var MN={calm:"AMBIENT",happy:"JOYEUX",epic:"EPIQUE",sad:"MELANCOLIQUE",mystery:"MYSTERIEUX",romantic:"ROMANTIQUE",tech:"TECH"};var au=document.getElementById("a");au.volume=0.4;au.src=S.calm[0];function pk(m){var l=S[m]||S.calm;return l[Math.floor(Math.random()*l.length)];}function t(b){if(au.paused){au.play().then(function(){b.innerHTML="&#127925;&#9646;&#9646;";}).catch(function(){});}else{au.pause();b.innerHTML="&#127925;&#9654;";}}function chMood(m){var url=pk(m);document.getElementById("m").innerText=MN[m]||"AMBIENT";if(au.src.indexOf(url)<0){var p=!au.paused;au.src=url;if(p)au.play().catch(function(){});}}function speak(txt,lang){if(!window.speechSynthesis)return;window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(txt);if(lang=="ar"){u.lang="ar-SA";u.rate=0.80;u.pitch=1.25;}else if(lang=="en"){u.lang="en-US";u.rate=0.88;u.pitch=1.1;}else{u.lang="fr-FR";u.rate=0.84;u.pitch=1.18;}u.volume=1.0;au.volume=0.06;u.onend=function(){var f=setInterval(function(){if(au.volume<0.38){au.volume=Math.min(au.volume+0.04,0.4);}else{clearInterval(f);}},80);};u.onerror=function(){au.volume=0.4;};window.speechSynthesis.speak(u);}window.reiSpeak=speak;window.reiChangeMood=chMood;</script>""", height=75)'''

NEW_MUSIC_BLOCK = '''    cs, cm = st.columns([2,1])
    with cs: st.markdown(f\'<span class="status-online"></span><span style="color:#00ff88;font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:2px;">{T["online"]}</span>\', unsafe_allow_html=True)
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
</script>""", height=130)'''

if OLD_MUSIC_BLOCK in c:
    c = c.replace(OLD_MUSIC_BLOCK, NEW_MUSIC_BLOCK)
    ok.append("✅ PARTIE 1: Bloc musique remplacé (volume slider + chant + harmonie)")
else:
    errors.append("❌ PARTIE 1: Bloc musique non trouvé")

# ════════════════════════════════════════════
# PARTIE 2 — play_reihana_voice : envoyer signal harmonie
# au lecteur musical via postMessage iframe parent
# ════════════════════════════════════════════
OLD_PLAY_VOICE = '''def play_reihana_voice(text, lang=None, mood="calm"):
    """Joue la voix gTTS de REIHANA avec animation avatar"""
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
  
  function startTalking(){{
    // Animation avatar petit
    var av = window.parent.document.getElementById("reiBgAvatar");
    if(av) av.classList.add("talking");
    var hm = window.parent.document.querySelector(".holo-mouth");
    if(hm) hm.classList.add("speaking");
    var vb = window.parent.document.querySelector(".voice-bars");
    if(vb) vb.classList.add("active");
    var ha = window.parent.document.querySelector(".hologram-avatar");
    if(ha) ha.classList.add("speaking");
    // Anim bouche sidebar SVG
    var lp = window.parent.document.getElementById("lipT");
    if(lp) lp.style.animationPlayState = "running";
  }}
  
  function stopTalking(){{
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
  
  // Lancer avec délai pour contourner autoplay browser policy
  setTimeout(function(){{
    v.play().then(function(){{
      startTalking();
    }}).catch(function(e){{
      console.log("gTTS autoplay bloqué:", e);
      // Essayer après interaction utilisateur
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
    return False'''

NEW_PLAY_VOICE = '''def play_reihana_voice(text, lang=None, mood="calm"):
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
    return False'''

if OLD_PLAY_VOICE in c:
    c = c.replace(OLD_PLAY_VOICE, NEW_PLAY_VOICE)
    ok.append("✅ PARTIE 2: play_reihana_voice avec harmonie musicale (fade in/out)")
else:
    errors.append("❌ PARTIE 2: play_reihana_voice non trouvée")

# ════════════════════════════════════════════
# ÉCRITURE FINALE
# ════════════════════════════════════════════
if c != original:
    open('reihana.py', 'w', encoding='utf-8').write(c)
    print("\n" + "═"*60)
    print("  PATCH MUSIQUE HARMONIE REIHANA — RÉSULTATS")
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
    print("❌ AUCUNE MODIFICATION — patterns non trouvés")
    for e in errors:
        print(e)
