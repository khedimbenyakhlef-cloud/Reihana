# ═══════════════════════════════════════════════════════════════
# PATCH MICRO DEFINITIF v4 — localStorage + polling Python
# Approche:
#   1. Le micro JS écrit le texte dans localStorage["rei_voice"]
#   2. Un second composant lit localStorage toutes les 800ms
#      et retourne la valeur via Streamlit.setComponentValue
#   3. Python traite la valeur et met à jour input_value
# C'est la seule approche 100% fiable avec Streamlit
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# Localiser le bloc micro complet à remplacer
MIC_START = '# ── Reconnaissance vocale BIDIRECTIONNELLE haute performance ──'
MIC_END   = '\nci, cs2 = st.columns([5, 1])'

if MIC_START in c and MIC_END in c:
    s = c.index(MIC_START)
    e = c.index(MIC_END)
    
    NEW_MIC = '''# ── Reconnaissance vocale v4 — localStorage + composant reader ──
_stt_lang_map = {"🇫🇷 Français":"fr-FR","🇩🇿 العربية":"ar-SA","🇬🇧 English":"en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue,"fr-FR")

import streamlit.components.v1 as _vc

# ── COMPOSANT 1 : UI micro (écrit dans localStorage) ──
_vc.html(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:transparent;overflow:hidden;font-family:Orbitron,monospace;}}
#W{{display:flex;align-items:center;gap:10px;padding:5px 2px;width:100%;}}
#M{{width:54px;height:54px;border-radius:50%;border:2.5px solid #00ffcc88;
    background:radial-gradient(circle at 35% 35%,#001440,#000818);
    color:#00ffcc;font-size:24px;cursor:pointer;display:flex;
    align-items:center;justify-content:center;transition:all .25s;
    box-shadow:0 0 14px #00ffcc22;position:relative;outline:none;flex-shrink:0;}}
#M:hover{{box-shadow:0 0 24px #00ffcc66;transform:scale(1.07);}}
#M.on{{border-color:#ff2222dd;color:#ff2222;
       background:radial-gradient(circle at 35% 35%,#3a0000,#1a0000);
       box-shadow:0 0 28px #ff222288;
       animation:mp .7s ease-in-out infinite;}}
#M.ok{{border-color:#00ff66cc;color:#00ff66;box-shadow:0 0 20px #00ff6655;}}
@keyframes mp{{0%,100%{{transform:scale(1);box-shadow:0 0 14px #ff222244;}}
               50%{{transform:scale(1.13);box-shadow:0 0 40px #ff2222cc;}}}}
#RI{{position:absolute;width:54px;height:54px;border-radius:50%;
     border:2px solid transparent;pointer-events:none;}}
#M.on #RI{{animation:re .85s ease-out infinite;}}
@keyframes re{{0%{{width:54px;height:54px;margin:0;border-color:#ff222299;opacity:1;}}
               100%{{width:98px;height:98px;margin:-22px;border-color:#ff222200;opacity:0;}}}}
#I{{flex:1;min-width:0;}}
#S{{font-size:8px;letter-spacing:2px;color:#00ffcc55;height:12px;margin-bottom:2px;}}
#S.on{{color:#ff3333;animation:sb .9s ease-in-out infinite;}}
#S.ok{{color:#00ff88;}} #S.er{{color:#ffaa00;}}
@keyframes sb{{0%,100%{{opacity:.5;}}50%{{opacity:1;}}}}
#L{{font-size:12px;color:#88ccff;font-family:Rajdhani,sans-serif;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    min-height:15px;font-style:italic;transition:color .2s;}}
#L.fi{{color:#ccffee;font-style:normal;font-weight:700;}}
#B{{display:flex;align-items:flex-end;gap:2px;height:20px;margin-top:3px;opacity:0;transition:opacity .3s;}}
#B.on{{opacity:1;}}
.bv{{width:3px;border-radius:2px;min-height:3px;
     background:linear-gradient(0deg,#00ffcc,#8800ff);
     box-shadow:0 0 3px #00ffcc55;transition:height .05s;}}
</style></head><body>
<div id="W">
  <button id="M" onclick="tog()" title="Parler à REIHANA"><div id="RI"></div>🎙️</button>
  <div id="I">
    <div id="S">MICRO PRÊT · CLIQUER POUR PARLER</div>
    <div id="L">Parle à REIHANA... 👂</div>
    <div id="B">
      <div class="bv" style="height:3px"></div><div class="bv" style="height:6px"></div>
      <div class="bv" style="height:11px"></div><div class="bv" style="height:16px"></div>
      <div class="bv" style="height:19px"></div><div class="bv" style="height:16px"></div>
      <div class="bv" style="height:11px"></div><div class="bv" style="height:6px"></div>
      <div class="bv" style="height:3px"></div>
    </div>
  </div>
</div>
<script>
var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
var r=null,on=false,fin="",sT=null,an=null,af=null;
var M=document.getElementById("M"),S=document.getElementById("S");
var L=document.getElementById("L"),B=document.getElementById("B");
var bv=B.querySelectorAll(".bv");
var lang="{_stt_lang}";

// Écrire dans localStorage du parent (Streamlit)
function setLS(key,val){{
  try{{localStorage.setItem(key,val);}}catch(e){{
    try{{window.parent.localStorage.setItem(key,val);}}catch(e2){{}}
  }}
}}

if(!SR){{S.innerText="⚠️ Chrome/Edge requis";M.disabled=true;M.style.opacity=".3";}}

function startVis(){{
  navigator.mediaDevices.getUserMedia({{audio:true}}).then(function(s){{
    var ctx=new(window.AudioContext||window.webkitAudioContext)();
    an=ctx.createAnalyser();an.fftSize=64;
    ctx.createMediaStreamSource(s).connect(an);
    var d=new Uint8Array(an.frequencyBinCount);
    var def=[3,6,11,16,19,16,11,6,3];
    B.classList.add("on");
    (function draw(){{
      if(!on){{B.classList.remove("on");bv.forEach(function(b,i){{b.style.height=def[i]+"px";}});return;}}
      af=requestAnimationFrame(draw);an.getByteFrequencyData(d);
      bv.forEach(function(b,i){{b.style.height=Math.max(3,Math.min(20,d[Math.floor(i*d.length/9)]/5))+"px";}});
    }})();
  }}).catch(function(){{}});
}}

function mkR(){{
  var rr=new SR();
  rr.lang=lang;rr.continuous=true;rr.interimResults=true;rr.maxAlternatives=2;
  rr.onstart=function(){{
    on=true;fin="";M.className="on";
    S.className="on";S.innerText="🔴 ÉCOUTE EN COURS...";
    L.className="";L.innerText="Je t'écoute... 🎙️";
    setLS("rei_voice_status","listening");
    startVis();
  }};
  rr.onresult=function(e){{
    var itr="";fin="";
    for(var i=e.resultIndex;i<e.results.length;i++){{
      if(e.results[i].isFinal)fin+=e.results[i][0].transcript+" ";
      else itr+=e.results[i][0].transcript;
    }}
    var show=(fin+itr).trim();
    L.className=fin.trim()?"fi":"";
    L.innerText=show.substring(0,75)+(show.length>75?"...":"")||"...";
    // Écrire texte en temps réel dans localStorage
    if(show) setLS("rei_voice_text",show);
    setLS("rei_voice_final","0");
    clearTimeout(sT);
    if(fin.trim()){{
      sT=setTimeout(function(){{if(on&&fin.trim())stop(true);}},3000);
    }}
  }};
  rr.onerror=function(ev){{
    S.className="er";
    S.innerText=({{
      "not-allowed":"🚫 MICRO REFUSÉ — Cliquer sur 🔒 dans Chrome",
      "no-speech":"💬 Rien entendu — Réessayez",
      "network":"🌐 Erreur réseau",
      "aborted":"⏹ Arrêté"
    }})[ev.error]||("⚠️ "+ev.error);
    stop(false);
  }};
  rr.onend=function(){{if(on){{try{{rr.start();}}catch(x){{on=false;M.className="";}}}}  }};
  return rr;
}}

window.tog=function(){{if(on)stop(false);else start();}};

function start(){{
  fin="";r=mkR();
  try{{r.start();}}catch(e){{S.className="er";S.innerText="⚠️ Impossible de démarrer";}}
}}

function stop(auto){{
  on=false;clearTimeout(sT);cancelAnimationFrame(af);
  if(r){{try{{r.stop();r.abort();}}catch(e){{}}r=null;}}
  var txt=fin.trim();
  if(txt){{
    M.className="ok";S.className="ok";
    S.innerText=auto?"✅ ENVOYÉ AUTOMATIQUEMENT":"✅ TEXTE PRÊT — APPUYER ENVOYER";
    L.className="fi";L.innerText="\\""+txt.substring(0,55)+(txt.length>55?"...":"")+"\\"";
    // Signaler: texte final prêt
    setLS("rei_voice_text",txt);
    setLS("rei_voice_final",auto?"1":"0");
    setLS("rei_voice_ts",Date.now().toString());
    setTimeout(function(){{
      M.className="";S.className="";S.innerText="MICRO PRÊT · CLIQUER POUR PARLER";
      L.className="";L.innerText="Parle à REIHANA... 👂";fin="";
      setLS("rei_voice_status","ready");
    }},2800);
  }}else{{
    M.className="";S.className="";S.innerText="MICRO PRÊT · CLIQUER POUR PARLER";
    L.className="";L.innerText="Parle à REIHANA... 👂";
  }}
}}
</script></body></html>""", height=92)

# ── COMPOSANT 2 : Reader localStorage → retourne valeur Python ──
_lsread = _vc.html("""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:transparent;">
<script>
// Ce composant lit localStorage et retourne la valeur à Streamlit
var _lastTs = "0";
var _lastText = "";

function readAndSend() {{
  try {{
    var txt = localStorage.getItem("rei_voice_text") || "";
    var fin = localStorage.getItem("rei_voice_final") || "0";
    var ts  = localStorage.getItem("rei_voice_ts") || "0";
    
    if(txt && ts !== _lastTs) {{
      _lastTs = ts;
      _lastText = txt;
      // Effacer après lecture pour éviter double envoi
      if(fin === "1") {{
        localStorage.removeItem("rei_voice_text");
        localStorage.removeItem("rei_voice_final");
        localStorage.removeItem("rei_voice_ts");
      }}
      Streamlit.setComponentValue(JSON.stringify({{text:txt, final:fin==="1"}}));
    }}
  }} catch(e) {{}}
}}

Streamlit.setComponentReady();
Streamlit.setFrameHeight(0);
// Lire toutes les 600ms
setInterval(readAndSend, 600);
</script></body></html>""", height=0)

# ── Python traite le résultat ──
if _lsread:
    try:
        import json as _json
        _vdata = _json.loads(_lsread)
        _vtext = _vdata.get("text","").strip()
        _vfinal = _vdata.get("final", False)
        if _vtext and _vtext != st.session_state.get("last_voice_text",""):
            st.session_state.input_value = _vtext
            st.session_state.last_voice_text = _vtext
            if _vfinal:
                # Auto-envoi
                question = _vtext
                st.session_state.input_value = ""
                st.session_state.last_voice_text = ""
                st.session_state.messages.append({"role":"user","content":question})
                rep,res,web_res = process_msg(question)
                if web_res:
                    wh=\'<div style="font-family:Orbitron,monospace;font-size:0.58rem;color:#00cc88;margin:4px 0;">🌐 SOURCES</div>\'
                    for _wr in web_res[:3]:
                        if _wr.get("url"): wh+=f\'<div class="web-card">🔗 <a href="{_wr["url"]}" target="_blank" style="color:#00cc88;">{_wr["title"][:55]}</a></div>\'
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
    except Exception:
        pass

'''

    c = c[:s] + NEW_MIC + c[e:]
    ok.append("✅ PARTIE 1: Micro v4 localStorage + reader installé")
else:
    errors.append("❌ Marqueurs non trouvés")

if c != original:
    open('reihana.py','w',encoding='utf-8').write(c)
    print("\n"+"═"*60)
    print("  PATCH MICRO v4 — RÉSULTATS")
    print("═"*60)
    for m in ok: print(m)
    if errors:
        print("\n⚠️")
        for e in errors: print(e)
    print(f"\n✅ SAUVEGARDÉ ({len(ok)}/1 OK)")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION")
    for e in errors: print(e)
