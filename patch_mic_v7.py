# ═══════════════════════════════════════════════════════════════
# PATCH MICRO v7 — ARCHITECTURE CORRECTE FINALE
# Problème v6 : st.markdown échappe les <script> → code affiché
# Solution :
#   - st.button natif pour déclencher (100% cliquable)
#   - st.components.v1.html UNIQUEMENT pour le JS (height=0)
#   - st.markdown UNIQUEMENT pour le CSS et HTML statique
#   - Communication via st.query_params (URL redirect)
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

MIC_START = '# ── Reconnaissance vocale v6 — st.button natif + JS ──'
MIC_END   = '\n# ── Zone saisie : texte + bouton micro natif + envoyer ──'

if MIC_START in c and MIC_END in c:
    s = c.index(MIC_START)
    e = c.index(MIC_END)

    NEW_MIC = r'''# ── Reconnaissance vocale v7 — Architecture correcte ──
_stt_lang_map = {"🇫🇷 Français":"fr-FR","🇩🇿 العربية":"ar-SA","🇬🇧 English":"en-US"}
_stt_lang = _stt_lang_map.get(st.session_state.langue,"fr-FR")

# ── Lire texte vocal depuis query params (mis par JS) ──
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
        _is_song,_smood,_slang,_sverses = detect_song(_rep)
        if _is_song and _sverses:
            st.session_state.last_song={"verses":_sverses,"mood":_smood,"lang":_slang,"msg_index":len(st.session_state.messages)-1}
        else:
            play_reihana_voice(_rep, lang=detect_text_lang(_rep))
        st.rerun()

# ── CSS uniquement (pas de script ici) ──
st.markdown("""
<style>
#reiVoiceBox{font-family:'Orbitron',monospace;padding:5px 2px 3px 2px;}
#reiVoiceSt{font-size:8.5px;letter-spacing:2px;color:rgba(0,255,200,0.45);height:13px;margin-bottom:3px;}
#reiVoiceSt.von{color:#ff3333;}
#reiVoiceSt.vok{color:#00ff88;}
#reiVoiceSt.verr{color:#ffaa00;font-size:8px;}
#reiVoiceLv{font-family:'Rajdhani',monospace;font-size:13px;color:#88ccff;
            font-style:italic;white-space:nowrap;overflow:hidden;
            text-overflow:ellipsis;min-height:17px;}
#reiVoiceLv.vfin{color:#ccffee;font-style:normal;font-weight:700;}
#reiWv{display:flex;align-items:flex-end;gap:2px;height:16px;margin-top:3px;opacity:0;transition:opacity .3s;}
#reiWv.von{opacity:1;}
.rwb2{width:3px;border-radius:2px;min-height:2px;
      background:linear-gradient(0deg,#00ffcc,#8800ff);transition:height .06s;}
</style>
<div id="reiVoiceBox">
  <div id="reiVoiceSt">🎙️ MICRO PRÊT</div>
  <div id="reiVoiceLv">Parle à REIHANA... 👂</div>
  <div id="reiWv">
    <div class="rwb2" style="height:2px"></div><div class="rwb2" style="height:5px"></div>
    <div class="rwb2" style="height:9px"></div><div class="rwb2" style="height:13px"></div>
    <div class="rwb2" style="height:15px"></div><div class="rwb2" style="height:13px"></div>
    <div class="rwb2" style="height:9px"></div><div class="rwb2" style="height:5px"></div>
    <div class="rwb2" style="height:2px"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── JS dans components.html (seul endroit où <script> fonctionne) ──
import streamlit.components.v1 as _cmp
_cmp.html(f"""
<script>
(function(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var rec=null,on=false,fin="",silT=null,rafId=null,an=null;
  var lang="{_stt_lang}";

  // Accéder aux éléments dans le document parent
  function el(id){{
    return window.parent.document.getElementById(id);
  }}

  function setSt(cls,txt){{
    var e=el("reiVoiceSt"); if(e){{e.className=cls;e.innerText=txt;}}
  }}
  function setLv(cls,txt){{
    var e=el("reiVoiceLv"); if(e){{e.className=cls;e.innerText=txt;}}
  }}

  function startVis(){{
    if(an)return;
    navigator.mediaDevices.getUserMedia({{audio:true,video:false}})
    .then(function(stream){{
      var ctx=new(window.AudioContext||window.webkitAudioContext)();
      an=ctx.createAnalyser();an.fftSize=64;
      ctx.createMediaStreamSource(stream).connect(an);
      var d=new Uint8Array(an.frequencyBinCount);
      var wv=el("reiWv"); if(wv)wv.classList.add("von");
      var def=[2,5,9,13,15,13,9,5,2];
      (function draw(){{
        if(!on){{
          var wv2=el("reiWv");
          if(wv2){{wv2.classList.remove("von");
            wv2.querySelectorAll(".rwb2").forEach(function(b,i){{b.style.height=def[i]+"px";}});}}
          an=null;return;
        }}
        rafId=requestAnimationFrame(draw);
        an.getByteFrequencyData(d);
        var bs=window.parent.document.querySelectorAll(".rwb2");
        bs.forEach(function(b,i){{b.style.height=Math.max(2,Math.min(15,d[Math.floor(i*(d.length/9))]/6))+"px";}});
      }})();
    }}).catch(function(){{}});
  }}

  function mkRec(){{
    var r=new SR();
    r.lang=lang;r.continuous=true;r.interimResults=true;r.maxAlternatives=2;
    r.onstart=function(){{
      on=true;fin="";
      setSt("von","🔴 ÉCOUTE... (silence 3s = envoi auto)");
      setLv("","Je t'écoute 🎙️");
      startVis();
    }};
    r.onresult=function(e){{
      var itr="";fin="";
      for(var i=e.resultIndex;i<e.results.length;i++){{
        if(e.results[i].isFinal)fin+=e.results[i][0].transcript+" ";
        else itr+=e.results[i][0].transcript;
      }}
      var show=(fin+itr).trim();
      setLv(fin.trim()?"vfin":"",show.substring(0,80)+(show.length>80?"...":"")||"...");
      clearTimeout(silT);
      if(fin.trim())silT=setTimeout(function(){{if(on&&fin.trim())stopRec(true);}},3000);
    }};
    r.onerror=function(ev){{
      var msgs={{"not-allowed":"🚫 REFUSÉ — cliquer 🔒 dans Chrome → Autoriser",
                 "no-speech":"💬 Rien entendu","network":"🌐 Erreur réseau","aborted":"⏹"}};
      setSt("verr",msgs[ev.error]||("⚠️ "+ev.error));
      stopRec(false);
    }};
    r.onend=function(){{if(on){{try{{r.start();}}catch(x){{on=false;setSt("","🎙️ MICRO PRÊT");}}}}  }};
    return r;
  }}

  function startRec(){{
    if(!SR){{setSt("verr","⚠️ Chrome/Edge requis");return;}}
    if(on)return;
    fin="";rec=mkRec();
    try{{rec.start();}}
    catch(e){{setSt("verr","⚠️ Vérifier autorisation micro dans Chrome");}}
  }}

  function stopRec(autoSend){{
    on=false;clearTimeout(silT);cancelAnimationFrame(rafId);
    if(rec){{try{{rec.stop();rec.abort();}}catch(e){{}}rec=null;}}
    var t=fin.trim();
    if(t){{
      setSt("vok",autoSend?"✅ ENVOI AUTO...":"✅ TEXTE PRÊT");
      setLv("vfin",t.substring(0,70)+(t.length>70?"...":""));
      // Rediriger avec le texte → Streamlit le lit via query_params
      var url=window.parent.location.pathname
              +"?vt="+encodeURIComponent(t)
              +"&vs="+(autoSend?"1":"0");
      window.parent.location.href=url;
    }}else{{
      setSt("","🎙️ MICRO PRÊT");
      setLv("","Parle à REIHANA... 👂");
    }}
  }}

  // Exposer dans la fenêtre PARENTE pour que st.button puisse appeler
  window.parent.reiMicStart=startRec;
  window.parent.reiMicStop=function(){{stopRec(false);}};
  window.parent.reiMicToggle=function(){{if(on)stopRec(false);else startRec();}};

}})();
</script>
""", height=0)

'''

    c = c[:s] + NEW_MIC + c[e:]
    ok.append("✅ PARTIE 1: JS dans components.html, CSS dans st.markdown")
else:
    errors.append(f"❌ PARTIE 1: MIC_START='{MIC_START[:40]}' ou MIC_END non trouvé")

# ══════════════════════════════════════════════
# REMPLACER les colonnes input (v6) par version v7
# ══════════════════════════════════════════════
OLD_COLS = '''# ── Zone saisie : texte + bouton micro natif + envoyer ──
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

NEW_COLS = '''# ── Zone saisie : textarea + boutons ──
ci, cmic, cs2 = st.columns([4, 1, 1])
with ci:
    if st.session_state.clear_input:
        st.session_state.input_value=""; st.session_state.clear_input=False; st.rerun()
    user_input=st.text_area("",value=st.session_state.input_value,placeholder=T["placeholder"],key="uinput",height=80,label_visibility="collapsed")
    st.session_state.input_value=user_input
with cmic:
    st.markdown("<br>", unsafe_allow_html=True)
    _mic_on = st.session_state.get("mic_on", False)
    _mic_label = "⏹ STOP" if _mic_on else "🎙️ MICRO"
    if st.button(_mic_label, use_container_width=True, key="micbtn"):
        st.session_state.mic_on = not _mic_on
        # JS appelé via components.html séparé (pas st.markdown)
        import streamlit.components.v1 as _mc2
        _mc2.html(f"""<script>
        (function(){{
          var fn = window.parent.{'reiMicStop' if _mic_on else 'reiMicStart'};
          if(fn) fn();
        }})();
        </script>""", height=0)
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_btn=st.button(T["send"], use_container_width=True, key="sbtn")'''

if OLD_COLS in c:
    c = c.replace(OLD_COLS, NEW_COLS)
    ok.append("✅ PARTIE 2: Colonnes avec bouton micro v7")
else:
    errors.append("❌ PARTIE 2: Colonnes v6 non trouvées")

# ════════════════════════════════════════════
if c != original:
    open('reihana.py','w',encoding='utf-8').write(c)
    print("\n"+"═"*60)
    print("  PATCH MICRO v7 — RÉSULTATS")
    print("═"*60)
    for m in ok: print(m)
    if errors:
        print("\n⚠️")
        for e in errors: print(e)
    print(f"\n✅ SAUVEGARDÉ ({len(ok)}/2 OK)")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION")
    for e in errors: print(e)
