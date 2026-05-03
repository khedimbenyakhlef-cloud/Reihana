# ═══════════════════════════════════════════════════════════════
# PATCH MICRO v6 — BOUTON NATIF st.button + JS séparé
# Le bouton HTML dans st.markdown n'est pas cliquable car
# Streamlit met pointer-events:none sur les éléments markdown.
# Solution: st.button natif Streamlit déclenche le JS via
# un script qui appelle reiMicToggle() défini par st.markdown
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

MIC_START = '# ── Reconnaissance vocale v5 — st.markdown natif ──'
MIC_END   = '\nci, cs2 = st.columns([5, 1])'

if MIC_START in c and MIC_END in c:
    s = c.index(MIC_START)
    e = c.index(MIC_END)

    NEW_MIC = r'''# ── Reconnaissance vocale v6 — st.button natif + JS ──
_stt_lang_map = {"🇫🇷 Français":"fr-FR","🇩🇿 العربية":"ar-SA","🇬🇧 English":"en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue,"fr-FR")

# ── Lire texte vocal depuis query params ──
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

# ── Injecter le moteur JS de reconnaissance vocale ──
# (définit reiMicStart/reiMicStop dans window, cliquable via st.button)
st.markdown(f"""
<style>
#reiVoiceStatus{{
  font-family:'Orbitron',monospace;
  font-size:9px;letter-spacing:2px;
  color:rgba(0,255,200,0.5);
  padding:4px 0 2px 2px;
  height:15px;
  transition:color 0.2s;
}}
#reiVoiceStatus.on{{color:#ff3333;animation:rvs_blink 0.85s ease-in-out infinite;}}
#reiVoiceStatus.ok{{color:#00ff88;}}
#reiVoiceStatus.err{{color:#ffaa00;font-size:8px;}}
@keyframes rvs_blink{{0%,100%{{opacity:0.45;}}50%{{opacity:1;}}}}
#reiVoiceLive{{
  font-family:'Rajdhani',monospace;font-size:13px;
  color:#88ccff;font-style:italic;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  padding:0 2px;min-height:18px;
  transition:color 0.2s;
}}
#reiVoiceLive.final{{color:#ccffee;font-style:normal;font-weight:700;}}
#reiWaveBars{{
  display:flex;align-items:flex-end;gap:2px;
  height:18px;padding:2px 0;
  opacity:0;transition:opacity 0.3s;
}}
#reiWaveBars.on{{opacity:1;}}
.rwbar{{
  width:3px;border-radius:2px;min-height:2px;
  background:linear-gradient(0deg,#00ffcc,#8800ff);
  transition:height 0.055s;
}}
</style>
<div id="reiVoiceStatus">🎙️ MICRO PRÊT — CLIQUER LE BOUTON CI-DESSOUS</div>
<div id="reiVoiceLive">Parle à REIHANA et elle te répondra... 👂</div>
<div id="reiWaveBars">
  <div class="rwbar" style="height:2px"></div><div class="rwbar" style="height:5px"></div>
  <div class="rwbar" style="height:9px"></div><div class="rwbar" style="height:13px"></div>
  <div class="rwbar" style="height:16px"></div><div class="rwbar" style="height:13px"></div>
  <div class="rwbar" style="height:9px"></div><div class="rwbar" style="height:5px"></div>
  <div class="rwbar" style="height:2px"></div>
</div>
<script>
(function(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var rec=null, on=false, final_="", silT=null, rafId=null, an=null;
  var lang="{_stt_lang}";
  var st_=document.getElementById("reiVoiceStatus");
  var lv=document.getElementById("reiVoiceLive");
  var wb=document.getElementById("reiWaveBars");
  var bars=wb?wb.querySelectorAll(".rwbar"):[];
  var defH=[2,5,9,13,16,13,9,5,2];

  if(!SR){{
    if(st_){{st_.innerText="⚠️ Chrome/Edge requis pour le micro";st_.style.color="#ffaa00";st_.style.animation="none";}}
    return;
  }}

  function startVis(){{
    if(an)return;
    navigator.mediaDevices.getUserMedia({{audio:true,video:false}})
    .then(function(stream){{
      var ctx=new(window.AudioContext||window.webkitAudioContext)();
      an=ctx.createAnalyser();an.fftSize=64;
      ctx.createMediaStreamSource(stream).connect(an);
      var d=new Uint8Array(an.frequencyBinCount);
      if(wb)wb.classList.add("on");
      (function draw(){{
        if(!on){{if(wb)wb.classList.remove("on");bars.forEach(function(b,i){{b.style.height=defH[i]+"px";}});an=null;return;}}
        rafId=requestAnimationFrame(draw);an.getByteFrequencyData(d);
        bars.forEach(function(b,i){{b.style.height=Math.max(2,Math.min(16,d[Math.floor(i*(d.length/9))]/6))+"px";}});
      }})();
    }}).catch(function(){{}});
  }}

  function mkRec(){{
    var r=new SR();
    r.lang=lang;r.continuous=true;r.interimResults=true;r.maxAlternatives=2;
    r.onstart=function(){{
      on=true;final_="";
      if(st_){{st_.className="on";st_.innerText="🔴 ÉCOUTE EN COURS... (silence 3s = envoi auto)";}}
      if(lv){{lv.className="";lv.innerText="Je t'écoute... 🎙️";}}
      startVis();
    }};
    r.onresult=function(e){{
      var itr="";final_="";
      for(var i=e.resultIndex;i<e.results.length;i++){{
        if(e.results[i].isFinal)final_+=e.results[i][0].transcript+" ";
        else itr+=e.results[i][0].transcript;
      }}
      var show=(final_+itr).trim();
      if(lv){{lv.className=final_.trim()?"final":"";lv.innerText=show.substring(0,80)+(show.length>80?"...":"")||"...";}}
      clearTimeout(silT);
      if(final_.trim())silT=setTimeout(function(){{if(on&&final_.trim())window.reiMicStop(true);}},3000);
    }};
    r.onerror=function(ev){{
      var msgs={{"not-allowed":"🚫 MICRO REFUSÉ — cliquer 🔒 dans Chrome → Autoriser",
                 "no-speech":"💬 Rien entendu — réessayez","network":"🌐 Erreur réseau","aborted":"⏹ Arrêté"}};
      if(st_){{st_.className="err";st_.innerText=msgs[ev.error]||("⚠️ "+ev.error);}}
      window.reiMicStop(false);
    }};
    r.onend=function(){{if(on){{try{{r.start();}}catch(x){{on=false;}}}}  }};
    return r;
  }}

  window.reiMicStart=function(){{
    if(on)return;
    final_="";rec=mkRec();
    try{{rec.start();}}
    catch(e){{if(st_){{st_.className="err";st_.innerText="⚠️ Impossible — vérifier autorisation micro";}}}}
  }};

  window.reiMicStop=function(autoSend){{
    on=false;clearTimeout(silT);cancelAnimationFrame(rafId);
    if(rec){{try{{rec.stop();rec.abort();}}catch(e){{}}rec=null;}}
    var t=final_.trim();
    if(t){{
      if(st_){{st_.className="ok";st_.innerText=autoSend?"✅ ENVOI EN COURS...":"✅ TEXTE CAPTURÉ";}}
      if(lv){{lv.className="final";lv.innerText=t.substring(0,70)+(t.length>70?"...":"");}}
      var url=window.location.pathname+"?vt="+encodeURIComponent(t)+"&vs="+(autoSend?"1":"0");
      window.location.href=url;
    }}else{{
      if(st_){{st_.className="";st_.innerText="🎙️ MICRO PRÊT — CLIQUER LE BOUTON CI-DESSOUS";}}
      if(lv){{lv.className="";lv.innerText="Parle à REIHANA et elle te répondra... 👂";}}
    }}
  }};

  window.reiMicToggle=function(){{
    if(on)window.reiMicStop(false);else window.reiMicStart();
  }};
}})();
</script>
""", unsafe_allow_html=True)

'''

    c = c[:s] + NEW_MIC + c[e:]
    ok.append("✅ JS micro injecté via st.markdown")
else:
    errors.append("❌ MIC_START ou MIC_END non trouvés")

# ══════════════════════════════════════════════
# REMPLACER les colonnes input par version avec
# vrai st.button micro natif Streamlit
# ══════════════════════════════════════════════
OLD_COLS = '''ci, cs2 = st.columns([5, 1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")'''

NEW_COLS = '''# ── Zone saisie : texte + bouton micro natif + envoyer ──
ci, cmic, cs2 = st.columns([4, 1, 1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cmic:
    st.markdown("<br>", unsafe_allow_html=True)
    # Vrai bouton Streamlit natif — cliquable à 100%
    _mic_label = "⏹ STOP" if st.session_state.get("mic_on", False) else "🎙️ MICRO"
    if st.button(_mic_label, use_container_width=True, key="micbtn"):
        st.session_state.mic_on = not st.session_state.get("mic_on", False)
        # Déclencher reiMicToggle() défini dans le JS ci-dessus
        st.markdown("""<script>
        setTimeout(function(){
            if(window.reiMicToggle) window.reiMicToggle();
        }, 150);
        </script>""", unsafe_allow_html=True)
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")'''

if OLD_COLS in c:
    c = c.replace(OLD_COLS, NEW_COLS)
    ok.append("✅ st.button micro natif ajouté (cliquable 100%)")
else:
    errors.append("❌ Colonnes input non trouvées")

# ════════════════════════════════════════════
# Écriture
# ════════════════════════════════════════════
if c != original:
    open('reihana.py','w',encoding='utf-8').write(c)
    print("\n"+"═"*60)
    print("  PATCH MICRO v6 — RÉSULTATS")
    print("═"*60)
    for m in ok: print(m)
    if errors:
        print("\n⚠️ PROBLÈMES:")
        for e in errors: print(e)
    print(f"\n✅ SAUVEGARDÉ ({len(ok)}/2 OK)")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION")
    for e in errors: print(e)
