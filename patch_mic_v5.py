# ═══════════════════════════════════════════════════════════════
# PATCH MICRO DEFINITIF v5
# Diagnostic: _vc.html() sur Render = iframe sandbox sans allow-same-origin
#             → localStorage bloqué, clics parfois bloqués
# Solution FINALE:
#   - ZERO iframe pour le micro
#   - st.markdown injecte JS directement dans la page Streamlit
#   - Vrai bouton st.button natif déclenche/arrête l'écoute
#   - SpeechRecognition tourne dans le contexte principal
#   - Texte vocal → URL hash → lu par Python via st.query_params
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# ══════════════════════════════════════════════
# SUPPRIMER tout l'ancien bloc micro (v4)
# et le remplacer par la version st.markdown pure
# ══════════════════════════════════════════════
MIC_START = '# ── Reconnaissance vocale v4 — localStorage + composant reader ──'
MIC_END   = '\nci, cs2 = st.columns([5, 1])'

if MIC_START in c and MIC_END in c:
    s = c.index(MIC_START)
    e = c.index(MIC_END)

    NEW_MIC = r'''# ── Reconnaissance vocale v5 — st.markdown natif ──
_stt_lang_map = {"🇫🇷 Français":"fr-FR","🇩🇿 العربية":"ar-SA","🇬🇧 English":"en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue,"fr-FR")

# Lire texte vocal depuis query params (mis par JS via window.location)
_qp = st.query_params
_vt = _qp.get("vt","").strip()
_vs = _qp.get("vs","0")
if _vt and _vt != st.session_state.get("last_voice_text",""):
    st.session_state.input_value = _vt
    st.session_state.last_voice_text = _vt
    if _vs == "1":
        st.query_params.clear()
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
        st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.57rem;color:rgba(150,150,200,0.38);text-align:right;margin:-3px 0 5px 0;">⚡ {_res.get("model","")[:26]} · {_res.get("tokens",0)} tokens</div>', unsafe_allow_html=True)
        _is_song,_smood,_slang,_sverses = detect_song(_rep)
        if _is_song and _sverses:
            st.session_state.last_song={"verses":_sverses,"mood":_smood,"lang":_slang,"msg_index":len(st.session_state.messages)-1}
        else:
            play_reihana_voice(_rep, lang=detect_text_lang(_rep))
        st.rerun()

# ── Injecter le moteur vocal JS dans la page principale ──
st.markdown(f"""
<style>
#reiMicBar{{
  display:flex;align-items:center;gap:12px;
  padding:7px 4px 5px 4px;
  font-family:'Orbitron',monospace;
}}
#reiMicCircle{{
  width:56px;height:56px;border-radius:50%;
  border:2.5px solid rgba(0,255,200,0.6);
  background:radial-gradient(circle at 38% 38%,rgba(0,40,90,0.97),rgba(0,8,28,0.99));
  color:#00ffcc;font-size:26px;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 18px rgba(0,255,200,0.22),inset 0 1px 0 rgba(255,255,255,0.05);
  position:relative;outline:none;flex-shrink:0;
  transition:all 0.22s ease;
  -webkit-tap-highlight-color:transparent;
  user-select:none;
}}
#reiMicCircle:hover{{
  box-shadow:0 0 30px rgba(0,255,200,0.55);
  transform:scale(1.07);
}}
#reiMicCircle.active{{
  border-color:rgba(255,30,30,0.95);
  color:#ff2020;
  background:radial-gradient(circle at 38% 38%,rgba(80,0,0,0.97),rgba(30,0,0,0.99));
  box-shadow:0 0 36px rgba(255,30,30,0.75),inset 0 1px 0 rgba(255,80,80,0.1);
  animation:rmc_pulse 0.72s ease-in-out infinite;
}}
#reiMicCircle.done{{
  border-color:rgba(0,255,90,0.9);
  color:#00ff55;
  box-shadow:0 0 24px rgba(0,255,90,0.5);
}}
@keyframes rmc_pulse{{
  0%,100%{{transform:scale(1.0); box-shadow:0 0 20px rgba(255,30,30,0.5);}}
  50%  {{transform:scale(1.14); box-shadow:0 0 48px rgba(255,30,30,0.95);}}
}}
#reiMicRipple{{
  position:absolute;width:56px;height:56px;
  border-radius:50%;border:2px solid transparent;pointer-events:none;
}}
#reiMicCircle.active #reiMicRipple{{
  animation:rmc_ripple 0.88s ease-out infinite;
}}
@keyframes rmc_ripple{{
  0%  {{width:56px;height:56px;margin:0;border-color:rgba(255,30,30,0.82);opacity:1;}}
  100%{{width:104px;height:104px;margin:-24px;border-color:rgba(255,30,30,0);opacity:0;}}
}}
#reiMicPanel{{flex:1;min-width:0;}}
#reiMicLabel{{
  font-size:8.5px;letter-spacing:2.5px;
  color:rgba(0,255,200,0.38);
  height:13px;margin-bottom:3px;
  transition:color 0.2s;
}}
#reiMicLabel.active{{color:#ff2222;animation:rml_blink 0.9s ease-in-out infinite;}}
#reiMicLabel.done{{color:#00ff77;}}
#reiMicLabel.err{{color:#ffaa00;}}
@keyframes rml_blink{{0%,100%{{opacity:0.45;}}50%{{opacity:1;}}}}
#reiMicText{{
  font-size:13px;font-family:'Rajdhani',monospace;
  color:#88ccff;font-style:italic;letter-spacing:0.3px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  min-height:17px;transition:color 0.2s;
}}
#reiMicText.final{{color:#ccffee;font-style:normal;font-weight:700;}}
#reiWave{{
  display:flex;align-items:flex-end;gap:2.5px;
  height:22px;margin-top:4px;
  opacity:0;transition:opacity 0.28s;
}}
#reiWave.active{{opacity:1;}}
.rwb{{
  width:3.5px;border-radius:2px;min-height:3px;
  background:linear-gradient(0deg,#00ffcc,#8800ff);
  box-shadow:0 0 4px rgba(0,255,200,0.4);
  transition:height 0.055s ease;
}}
</style>

<div id="reiMicBar">
  <button id="reiMicCircle" onclick="reiMicToggle()" title="Parler à REIHANA">
    <div id="reiMicRipple"></div>
    🎙️
  </button>
  <div id="reiMicPanel">
    <div id="reiMicLabel">MICRO PRÊT · CLIQUER POUR PARLER</div>
    <div id="reiMicText">Parle, je t'écoute... 👂</div>
    <div id="reiWave">
      <div class="rwb" style="height:3px"></div>
      <div class="rwb" style="height:6px"></div>
      <div class="rwb" style="height:11px"></div>
      <div class="rwb" style="height:16px"></div>
      <div class="rwb" style="height:20px"></div>
      <div class="rwb" style="height:16px"></div>
      <div class="rwb" style="height:11px"></div>
      <div class="rwb" style="height:6px"></div>
      <div class="rwb" style="height:3px"></div>
    </div>
  </div>
</div>

<script>
(function(){{
  // ── Éléments ──
  var btn  = document.getElementById("reiMicCircle");
  var lbl  = document.getElementById("reiMicLabel");
  var txt  = document.getElementById("reiMicText");
  var wave = document.getElementById("reiWave");
  var bars = wave.querySelectorAll(".rwb");
  var defH = [3,6,11,16,20,16,11,6,3];

  // ── État ──
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var rec=null, on=false, final_="", interim_="";
  var silTimer=null, rafId=null, analyser=null;
  var lang="{_stt_lang}";

  // ── Pas de support ──
  if(!SR){{
    lbl.innerText="⚠️ Chrome ou Edge requis pour le micro";
    lbl.style.color="#ffaa00"; lbl.style.animation="none";
    btn.style.opacity="0.3"; btn.disabled=true; return;
  }}

  // ── Visualiseur audio ──
  function startVis(){{
    if(analyser) return;
    navigator.mediaDevices.getUserMedia({{audio:true,video:false}})
    .then(function(stream){{
      var ctx=new(window.AudioContext||window.webkitAudioContext)();
      var src=ctx.createMediaStreamSource(stream);
      analyser=ctx.createAnalyser(); analyser.fftSize=64;
      src.connect(analyser);
      var data=new Uint8Array(analyser.frequencyBinCount);
      wave.classList.add("active");
      (function draw(){{
        if(!on){{
          wave.classList.remove("active");
          bars.forEach(function(b,i){{b.style.height=defH[i]+"px";}});
          analyser=null; return;
        }}
        rafId=requestAnimationFrame(draw);
        analyser.getByteFrequencyData(data);
        bars.forEach(function(b,i){{
          var v=data[Math.floor(i*(data.length/9))];
          b.style.height=Math.max(3,Math.min(21,v/5))+"px";
        }});
      }})();
    }}).catch(function(){{}});
  }}

  // ── Créer SpeechRecognition ──
  function mkRec(){{
    var r=new SR();
    r.lang=lang; r.continuous=true; r.interimResults=true; r.maxAlternatives=2;

    r.onstart=function(){{
      on=true; final_=""; interim_="";
      btn.className="active";
      lbl.className="active"; lbl.innerText="🔴 ÉCOUTE EN COURS...";
      txt.className=""; txt.innerText="Je t'écoute... 🎙️";
      startVis();
    }};

    r.onresult=function(e){{
      interim_=""; final_="";
      for(var i=e.resultIndex;i<e.results.length;i++){{
        if(e.results[i].isFinal) final_+=e.results[i][0].transcript+" ";
        else interim_+=e.results[i][0].transcript;
      }}
      var show=(final_+interim_).trim();
      txt.className=final_.trim()?"final":"";
      txt.innerText=show.substring(0,80)+(show.length>80?"...":"")||"...";

      // Timer silence 3s → envoi auto
      clearTimeout(silTimer);
      if(final_.trim()){{
        silTimer=setTimeout(function(){{
          if(on && final_.trim()) stopRec(true);
        }},3000);
      }}
    }};

    r.onerror=function(ev){{
      var msgs={{
        "not-allowed":"🚫 Micro refusé — cliquer 🔒 dans Chrome puis Autoriser",
        "no-speech":"💬 Rien entendu — réessayez",
        "network":"🌐 Erreur réseau",
        "aborted":"⏹ Arrêté"
      }};
      lbl.className="err";
      lbl.innerText=msgs[ev.error]||("⚠️ Erreur: "+ev.error);
      stopRec(false);
    }};

    r.onend=function(){{
      if(on){{ try{{r.start();}}catch(x){{on=false;btn.className="";}} }}
    }};
    return r;
  }}

  // ── Toggle ──
  window.reiMicToggle=function(){{
    if(on) stopRec(false); else startRec();
  }};

  function startRec(){{
    final_=""; interim_="";
    rec=mkRec();
    try{{ rec.start(); }}
    catch(e){{
      lbl.className="err";
      lbl.innerText="⚠️ Impossible de démarrer — vérifier autorisation micro";
    }}
  }}

  function stopRec(autoSend){{
    on=false;
    clearTimeout(silTimer);
    cancelAnimationFrame(rafId);
    if(rec){{ try{{rec.stop();rec.abort();}}catch(e){{}} rec=null; }}
    btn.className="";

    var t=final_.trim();
    if(t){{
      btn.className="done";
      lbl.className="done";
      lbl.innerText=autoSend?"✅ ENVOI AUTOMATIQUE...":"✅ TEXTE PRÊT";
      txt.className="final";
      txt.innerText=t.substring(0,70)+(t.length>70?"...":"");

      // ── Naviguer vers ?vt=TEXTE&vs=1/0
      // Streamlit lit ces query params au prochain rerun
      var encoded=encodeURIComponent(t);
      var send=autoSend?"1":"0";
      var url=window.location.pathname+"?vt="+encoded+"&vs="+send;
      window.location.href=url;

    }}else{{
      lbl.className=""; lbl.innerText="MICRO PRÊT · CLIQUER POUR PARLER";
      txt.className=""; txt.innerText="Parle, je t'écoute... 👂";
    }}
  }}

}})();
</script>
""", unsafe_allow_html=True)

'''

    c = c[:s] + NEW_MIC + c[e:]
    ok.append("✅ PARTIE 1: Micro v5 st.markdown pur + query_params installé")
else:
    errors.append(f"❌ Marqueurs non trouvés dans le fichier")

# ════════════════════════════════════════════
# Écriture
# ════════════════════════════════════════════
if c != original:
    open('reihana.py','w',encoding='utf-8').write(c)
    print("\n"+"═"*60)
    print("  PATCH MICRO v5 DEFINITIF — RÉSULTATS")
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
