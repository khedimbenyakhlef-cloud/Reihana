# ═══════════════════════════════════════════════════════════════
# PATCH MICRO v8 — FILTRE BRUIT + MODE TEXTE UNIQUEMENT
# Problèmes résolus :
#   1. Bruit perturbateur → noiseSuppression + echoCancellation
#   2. Auto-envoi sur silence supprimé → le texte va dans la zone
#      de saisie, l'utilisateur clique ENVOYER quand il veut
#   3. Accumulation des résultats finals (plus de perte de texte)
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# ════════════════════════════════════════════
# PARTIE 1 : Remplacer le bloc JS dans _cmp.html
# On cherche depuis la ligne startVis jusqu'à la fin du script
# ════════════════════════════════════════════

OLD_JS_SECTION = r'''# ── JS dans components.html (seul endroit où <script> fonctionne) ──
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
""", height=0)'''

NEW_JS_SECTION = r'''# ── JS v8 dans components.html — filtre bruit + mode texte seul ──
import streamlit.components.v1 as _cmp
_cmp.html(f"""
<script>
(function(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  // rec = instance SpeechRecognition
  // on  = micro actif
  // allFin = accumulation de TOUS les résultats finals
  // rafId, an = visualiseur audio
  var rec=null, on=false, allFin="", rafId=null, an=null;
  var lang="{_stt_lang}";

  function el(id){{ return window.parent.document.getElementById(id); }}
  function setSt(cls,txt){{ var e=el("reiVoiceSt"); if(e){{e.className=cls;e.innerText=txt;}} }}
  function setLv(cls,txt){{ var e=el("reiVoiceLv"); if(e){{e.className=cls;e.innerText=txt;}} }}

  // ── Visualiseur avec FILTRE BRUIT activé ──
  function startVis(){{
    if(an) return;
    navigator.mediaDevices.getUserMedia({{
      audio:{{
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl:  true,
        sampleRate:       16000
      }},
      video: false
    }})
    .then(function(stream){{
      var ctx = new(window.AudioContext||window.webkitAudioContext)();
      an = ctx.createAnalyser(); an.fftSize = 64;
      ctx.createMediaStreamSource(stream).connect(an);
      var d   = new Uint8Array(an.frequencyBinCount);
      var wv  = el("reiWv"); if(wv) wv.classList.add("von");
      var def = [2,5,9,13,15,13,9,5,2];
      (function draw(){{
        if(!on){{
          var wv2=el("reiWv");
          if(wv2){{
            wv2.classList.remove("von");
            wv2.querySelectorAll(".rwb2").forEach(function(b,i){{b.style.height=def[i]+"px";}});
          }}
          an=null; return;
        }}
        rafId = requestAnimationFrame(draw);
        an.getByteFrequencyData(d);
        var bs = window.parent.document.querySelectorAll(".rwb2");
        bs.forEach(function(b,i){{
          b.style.height = Math.max(2,Math.min(15,d[Math.floor(i*(d.length/9))]/6))+"px";
        }});
      }})();
    }}).catch(function(){{}});
  }}

  function mkRec(){{
    var r = new SR();
    r.lang = lang;
    r.continuous      = true;
    r.interimResults  = true;
    r.maxAlternatives = 1;

    r.onstart = function(){{
      on=true; allFin="";
      setSt("von","🔴 ÉCOUTE... parlez, puis cliquez ⏹ ou STOP");
      setLv("","Je t'écoute 🎙️");
      startVis();
    }};

    r.onresult = function(ev){{
      // Accumuler les résultats finals (ne pas réinitialiser allFin)
      var itr="";
      for(var i=ev.resultIndex; i<ev.results.length; i++){{
        if(ev.results[i].isFinal) allFin += ev.results[i][0].transcript + " ";
        else itr += ev.results[i][0].transcript;
      }}
      var show = (allFin + itr).trim();
      setLv(allFin.trim()?"vfin":"", show.substring(0,80)+(show.length>80?"...":"")||"...");
      // PAS d'auto-envoi — l'utilisateur clique ENVOYER
    }};

    r.onerror = function(ev){{
      var msgs = {{
        "not-allowed" : "🚫 REFUSÉ — cliquer 🔒 dans Chrome → Autoriser",
        "no-speech"   : "💬 Rien entendu",
        "network"     : "🌐 Erreur réseau",
        "aborted"     : "⏹ Arrêté"
      }};
      setSt("verr", msgs[ev.error]||("⚠️ "+ev.error));
      stopRec();
    }};

    // Redémarre automatiquement si le navigateur coupe (Chrome coupe après ~60s)
    r.onend = function(){{ if(on){{ try{{r.start();}}catch(x){{on=false;setSt("","🎙️ MICRO PRÊT");}} }} }};
    return r;
  }}

  function startRec(){{
    if(!SR){{ setSt("verr","⚠️ Chrome/Edge requis"); return; }}
    if(on) return;
    allFin=""; rec=mkRec();
    try{{ rec.start(); }}
    catch(e){{ setSt("verr","⚠️ Vérifier autorisation micro dans Chrome"); }}
  }}

  function stopRec(){{
    on=false; cancelAnimationFrame(rafId);
    if(rec){{ try{{rec.stop();rec.abort();}}catch(e){{}} rec=null; }}
    var t = allFin.trim();
    if(t){{
      setSt("vok","✅ TEXTE PRÊT — cliquez ENVOYER 📨");
      setLv("vfin", t.substring(0,70)+(t.length>70?"...":""));
      // vs=0 → met le texte dans la zone, PAS d'envoi automatique
      var url = window.parent.location.pathname
              + "?vt=" + encodeURIComponent(t)
              + "&vs=0";
      window.parent.location.href = url;
    }}else{{
      setSt("","🎙️ MICRO PRÊT");
      setLv("","Parle à REIHANA... 👂");
    }}
  }}

  window.parent.reiMicStart  = startRec;
  window.parent.reiMicStop   = stopRec;
  window.parent.reiMicToggle = function(){{ if(on) stopRec(); else startRec(); }};

}})();
</script>
""", height=0)'''

if OLD_JS_SECTION in c:
    c = c.replace(OLD_JS_SECTION, NEW_JS_SECTION)
    ok.append("✅ PARTIE 1: JS v8 — filtre bruit + accumulation finals + mode texte-seul")
else:
    errors.append("❌ PARTIE 1: Bloc JS v7 non trouvé (chercher la ligne startVis dans reihana.py)")

# ════════════════════════════════════════════
# PARTIE 2 : Supprimer l'auto-envoi côté Python
# vs=="1" ne devrait plus jamais arriver, mais on garde
# vs=="0" pour sécurité — on met juste le texte dans input_value
# ════════════════════════════════════════════

OLD_QP = '''# ── Lire texte vocal depuis query params (mis par JS) ──
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
        st.rerun()'''

NEW_QP = '''# ── Lire texte vocal depuis query params (mis par JS v8) ──
# vs est toujours "0" en v8 : le texte va dans la zone, l'user clique ENVOYER
_qp = st.query_params
_vt = _qp.get("vt","").strip()
if _vt and _vt != st.session_state.get("last_voice_text",""):
    st.session_state.input_value = _vt
    st.session_state.last_voice_text = _vt
    st.query_params.clear()
    st.rerun()'''

if OLD_QP in c:
    c = c.replace(OLD_QP, NEW_QP)
    ok.append("✅ PARTIE 2: Python — texte vocal → zone de saisie uniquement (plus d'auto-envoi)")
else:
    errors.append("❌ PARTIE 2: Bloc query_params v7 non trouvé")

# ════════════════════════════════════════════
if c != original:
    open('reihana.py','w',encoding='utf-8').write(c)
    print("\n"+"═"*60)
    print("  PATCH MICRO v8 — RÉSULTATS")
    print("═"*60)
    for m in ok: print(m)
    if errors:
        print("\n⚠️ ERREURS :")
        for e in errors: print(e)
    print(f"\n✅ SAUVEGARDÉ ({len(ok)}/2 OK)")
    print("═"*60)
    print("\nCe qui change en v8 :")
    print("  • noiseSuppression + echoCancellation + autoGainControl activés")
    print("  • Texte vocal → zone de saisie uniquement")
    print("  • Vous cliquez ENVOYER quand vous voulez")
    print("  • Accumulation correcte de tous les morceaux de parole")
else:
    print("❌ AUCUNE MODIFICATION — Vérifier les marqueurs dans reihana.py")
    for e in errors: print(e)
