# ═══════════════════════════════════════════════════════════════
# PATCH MICRO HAUTE PERFORMANCE — APPROCHE BIDIRECTIONNELLE
# Problème fondamental: React/Streamlit ignore les DOM events
# Solution: components.v1.html avec return value (bidirectionnel)
# Le texte vocal passe par la valeur de retour du composant
# et Streamlit le lit directement en Python
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# ════════════════════════════════════════════
# REMPLACER tout le bloc micro existant
# par la version bidirectionnelle
# ════════════════════════════════════════════

OLD_MIC_START = '# ── Reconnaissance vocale — INJECTION DIRECTE page principale ──'
OLD_MIC_END   = '""", unsafe_allow_html=True)\n\n\nci, cs2 = st.columns([5, 1])'

if OLD_MIC_START in c and OLD_MIC_END in c:
    s = c.index(OLD_MIC_START)
    e = c.index(OLD_MIC_END) + len('""", unsafe_allow_html=True)\n\n\n')
    old_block = c[s:e]

    NEW_MIC_BLOCK = '''# ── Reconnaissance vocale BIDIRECTIONNELLE haute performance ──
_stt_lang_map = {"🇫🇷 Français":"fr-FR","🇩🇿 العربية":"ar-SA","🇬🇧 English":"en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue,"fr-FR")

# Lire le résultat vocal retourné par le composant
import streamlit.components.v1 as _vc
_voice_result = _vc.html(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;font-family:'Orbitron',monospace;overflow:hidden;}}
#wrap{{display:flex;align-items:center;gap:10px;padding:6px 2px;}}

/* ── Bouton micro ── */
#mic{{
  width:56px;height:56px;border-radius:50%;flex-shrink:0;
  border:2.5px solid rgba(0,255,200,0.6);
  background:radial-gradient(circle at 35% 35%,rgba(0,40,80,0.95),rgba(0,8,30,0.99));
  color:#00ffcc;font-size:26px;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:all 0.25s;
  box-shadow:0 0 16px rgba(0,255,200,0.2),inset 0 1px 0 rgba(255,255,255,0.06);
  position:relative;outline:none;
}}
#mic:hover{{box-shadow:0 0 26px rgba(0,255,200,0.55);transform:scale(1.06);}}
#mic.on{{
  border-color:rgba(255,40,40,0.95);color:#ff2222;
  background:radial-gradient(circle at 35% 35%,rgba(70,0,0,0.95),rgba(30,0,0,0.99));
  box-shadow:0 0 32px rgba(255,40,40,0.7),inset 0 1px 0 rgba(255,100,100,0.1);
  animation:mpulse 0.7s ease-in-out infinite;
}}
#mic.done{{border-color:rgba(0,255,100,0.9);color:#00ff66;box-shadow:0 0 22px rgba(0,255,100,0.5);}}
@keyframes mpulse{{
  0%,100%{{transform:scale(1.0);box-shadow:0 0 18px rgba(255,40,40,0.5);}}
  50%{{transform:scale(1.12);box-shadow:0 0 42px rgba(255,40,40,0.95);}}
}}
/* Anneau expansion */
#ring{{
  position:absolute;width:56px;height:56px;border-radius:50%;
  border:2px solid transparent;pointer-events:none;
}}
#mic.on #ring{{animation:rexp 0.9s ease-out infinite;}}
@keyframes rexp{{
  0%{{width:56px;height:56px;margin:0;border-color:rgba(255,40,40,0.8);opacity:1;}}
  100%{{width:100px;height:100px;margin:-22px;border-color:rgba(255,40,40,0);opacity:0;}}
}}

/* ── Info panel ── */
#info{{flex:1;min-width:0;}}
#status{{font-size:8.5px;letter-spacing:2.5px;color:rgba(0,255,200,0.4);height:13px;transition:all 0.2s;margin-bottom:3px;}}
#status.on{{color:#ff3333;animation:sblink 0.9s ease-in-out infinite;}}
#status.ok{{color:#00ff88;}}
#status.err{{color:#ffaa00;}}
@keyframes sblink{{0%,100%{{opacity:0.5;}}50%{{opacity:1;}}}}

#live{{
  font-size:12.5px;color:#99ddff;font-family:'Rajdhani',sans-serif;
  letter-spacing:0.3px;min-height:16px;font-style:italic;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  transition:color 0.2s;
}}
#live.final{{color:#ccffee;font-style:normal;font-weight:600;}}

/* ── Visualiseur ── */
#bars{{display:flex;align-items:flex-end;gap:2.5px;height:24px;margin-top:4px;opacity:0;transition:opacity 0.3s;}}
#bars.on{{opacity:1;}}
.bar{{
  width:3.5px;border-radius:2px;min-height:3px;
  background:linear-gradient(0deg,#00ffcc,#8800ff);
  box-shadow:0 0 4px rgba(0,255,200,0.45);
  transition:height 0.05s ease;
}}

/* ── Bouton stop discret ── */
#stopbtn{{
  font-size:10px;letter-spacing:1px;color:rgba(255,100,100,0.7);
  background:none;border:1px solid rgba(255,100,100,0.3);
  border-radius:4px;padding:2px 7px;cursor:pointer;
  display:none;transition:all 0.2s;margin-top:4px;
}}
#stopbtn:hover{{color:#ff4444;border-color:rgba(255,80,80,0.7);background:rgba(255,0,0,0.08);}}
#stopbtn.show{{display:block;}}
</style></head>
<body>
<div id="wrap">
  <button id="mic" onclick="toggle()" title="Cliquer pour parler à REIHANA">
    <div id="ring"></div>🎙️
  </button>
  <div id="info">
    <div id="status">MICRO PRÊT · CLIQUER POUR PARLER</div>
    <div id="live">Parle, je t'écoute... 👂</div>
    <div id="bars">
      <div class="bar" style="height:3px"></div>
      <div class="bar" style="height:5px"></div>
      <div class="bar" style="height:10px"></div>
      <div class="bar" style="height:15px"></div>
      <div class="bar" style="height:19px"></div>
      <div class="bar" style="height:15px"></div>
      <div class="bar" style="height:10px"></div>
      <div class="bar" style="height:5px"></div>
      <div class="bar" style="height:3px"></div>
    </div>
    <button id="stopbtn" onclick="stop_(false)">⏹ ARRÊTER</button>
  </div>
</div>

<script>
var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
var _r=null,_on=false,_final="",_interim="",_an=null,_raf=null,_silT=null;
var mic=document.getElementById("mic");
var st_=document.getElementById("status");
var lv=document.getElementById("live");
var bars=document.getElementById("bars");
var bEls=bars.querySelectorAll(".bar");
var stopBtn=document.getElementById("stopbtn");
var _lang="{_stt_lang}";

if(!SR){{
  st_.innerText="⚠️ Chrome/Edge requis";
  mic.style.opacity="0.3";mic.disabled=true;
}}

/* ── Visualiseur AudioContext ── */
function startVis(){{
  if(_an) return;
  navigator.mediaDevices.getUserMedia({{audio:true,video:false}}).then(function(stream){{
    var ctx=new(window.AudioContext||window.webkitAudioContext)();
    var src=ctx.createMediaStreamSource(stream);
    _an=ctx.createAnalyser(); _an.fftSize=64;
    src.connect(_an);
    var d=new Uint8Array(_an.frequencyBinCount);
    var def=[3,5,10,15,19,15,10,5,3];
    function draw(){{
      if(!_on){{
        bars.classList.remove("on");
        bEls.forEach(function(b,i){{b.style.height=def[i]+"px";}});
        return;
      }}
      _raf=requestAnimationFrame(draw);
      _an.getByteFrequencyData(d);
      bars.classList.add("on");
      bEls.forEach(function(b,i){{
        var idx=Math.floor(i*(d.length/9));
        var h=Math.max(3,Math.min(22,d[idx]/5));
        b.style.height=h+"px";
      }});
    }}
    draw();
  }}).catch(function(){{}});
}}

/* ── Créer SpeechRecognition ── */
function mkR(){{
  var r=new SR();
  r.lang=_lang;
  r.continuous=true;
  r.interimResults=true;
  r.maxAlternatives=3;

  r.onstart=function(){{
    _on=true; _final=""; _interim="";
    mic.className="on";
    st_.className="on"; st_.innerText="🔴 ÉCOUTE EN COURS...";
    lv.className=""; lv.innerText="Je t'écoute... 🎙️";
    stopBtn.className="show";
    startVis();
  }};

  r.onresult=function(e){{
    _interim=""; 
    for(var i=e.resultIndex;i<e.results.length;i++){{
      if(e.results[i].isFinal){{
        _final+=e.results[i][0].transcript+" ";
      }} else {{
        _interim+=e.results[i][0].transcript;
      }}
    }}
    var show=(_final+_interim).trim();
    lv.className=_final.trim()?"final":"";
    lv.innerText=show.substring(0,80)+(show.length>80?"...":"")||"...";

    /* ── ENVOYER le texte intermédiaire à Streamlit via Streamlit.setComponentValue ── */
    if(show) Streamlit.setComponentValue({{text:show, final:false, send:false}});

    /* Timer silence 3s après texte final → envoi automatique */
    clearTimeout(_silT);
    if(_final.trim()){{
      _silT=setTimeout(function(){{
        if(_on && _final.trim()) stop_(true);
      }},3000);
    }}
  }};

  r.onerror=function(ev){{
    var msg={{
      "not-allowed":"🚫 MICRO REFUSÉ — Autorisez dans Chrome",
      "no-speech":"💬 Aucun son détecté — Réessayez",
      "network":"🌐 Erreur réseau",
      "aborted":"⏹ Arrêté"
    }}[ev.error]||("⚠️ "+ev.error);
    st_.className="err"; st_.innerText=msg;
    stop_(false);
  }};

  r.onend=function(){{
    if(_on){{ try{{r.start();}}catch(x){{_on=false;mic.className="";}} }}
  }};
  return r;
}}

/* ── Toggle ── */
window.toggle=function(){{ if(_on) stop_(false); else start_(); }};

function start_(){{
  if(!SR) return;
  _final=""; _interim="";
  _r=mkR();
  try{{ _r.start(); }}
  catch(e){{ st_.className="err"; st_.innerText="⚠️ Erreur démarrage"; }}
}}

function stop_(autoSend){{
  _on=false;
  clearTimeout(_silT);
  cancelAnimationFrame(_raf);
  if(_r){{ try{{_r.stop();_r.abort();}}catch(e){{}} _r=null; }}
  stopBtn.className="";

  var txt=_final.trim();
  if(txt){{
    mic.className="done";
    st_.className="ok"; st_.innerText="✅ "+(autoSend?"ENVOYÉ AUTOMATIQUEMENT":"TEXTE PRÊT");
    lv.className="final";
    lv.innerText="\\""+txt.substring(0,60)+(txt.length>60?"...":"")+"\\"";

    /* ── ENVOYER la valeur finale à Streamlit ── */
    Streamlit.setComponentValue({{text:txt, final:true, send:autoSend}});

    setTimeout(function(){{
      mic.className="";
      st_.className=""; st_.innerText="MICRO PRÊT · CLIQUER POUR PARLER";
      lv.className=""; lv.innerText="Parle, je t'écoute... 👂";
      _final=""; _interim="";
    }},2500);
  }} else {{
    mic.className="";
    st_.className=""; st_.innerText="MICRO PRÊT · CLIQUER POUR PARLER";
    lv.className=""; lv.innerText="Parle, je t'écoute... 👂";
  }}
}}

Streamlit.setComponentReady();
Streamlit.setFrameHeight(90);
</script>
</body></html>""", height=90)

# Traiter le résultat vocal retourné par le composant
if _voice_result and isinstance(_voice_result, dict):
    _vtext = _voice_result.get("text","").strip()
    _vfinal = _voice_result.get("final", False)
    _vsend = _voice_result.get("send", False)

    if _vtext:
        # Mettre à jour le champ input avec le texte vocal
        st.session_state.input_value = _vtext

        # Auto-envoi si silence détecté
        if _vfinal and _vsend:
            question = _vtext
            st.session_state.input_value = ""
            st.session_state.messages.append({"role":"user","content":question})
            rep,res,web_res = process_msg(question)
            if web_res:
                wh='<div style="font-family:Orbitron,monospace;font-size:0.58rem;color:#00cc88;margin:4px 0;letter-spacing:1px;">🌐 SOURCES</div>'
                for r in web_res[:3]:
                    if r.get("url"): wh+=f'<div class="web-card">🔗 <a href="{r["url"]}" target="_blank" style="color:#00cc88;">{r["title"][:55]}</a></div>'
                st.markdown(wh, unsafe_allow_html=True)
            st.session_state.mémoire.add_exchange(st.session_state.user_id,question,rep)
            st.session_state.messages.append({"role":"assistant","content":rep})
            st.markdown(f\'<div style="font-family:Orbitron,monospace;font-size:0.57rem;color:rgba(150,150,200,0.38);text-align:right;margin:-3px 0 5px 0;">⚡ {res.get("model","")[:26]} · {res.get("tokens",0)} tokens</div>\', unsafe_allow_html=True)
            _is_song,_smood,_slang,_sverses = detect_song(rep)
            if _is_song and _sverses:
                st.session_state.last_song={"verses":_sverses,"mood":_smood,"lang":_slang,"msg_index":len(st.session_state.messages)-1}
            else:
                play_reihana_voice(rep, lang=detect_text_lang(rep))
            st.rerun()

'''

    c = c[:s] + NEW_MIC_BLOCK + c[e:]
    ok.append("✅ PARTIE 1: Micro bidirectionnel (Streamlit.setComponentValue) installé")
else:
    errors.append("❌ PARTIE 1: Marqueurs micro non trouvés")

# ════════════════════════════════════════════
# Écriture
# ════════════════════════════════════════════
if c != original:
    open('reihana.py','w',encoding='utf-8').write(c)
    print("\n"+"═"*60)
    print("  PATCH MICRO HAUTE PERF — RÉSULTATS")
    print("═"*60)
    for m in ok: print(m)
    if errors:
        print("\n⚠️ PROBLÈMES:")
        for e in errors: print(e)
    print(f"\n✅ SAUVEGARDÉ ({len(ok)}/1 OK)")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION")
    for e in errors: print(e)
