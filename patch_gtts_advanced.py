# ═══════════════════════════════════════════════════════════════
# PATCH GTTS AVANCÉ REIHANA v3.0
# - Détection arabe automatique (Unicode Arabic block)
# - gTTS remplace speechSynthesis partout
# - Bouton "Lire" utilise gTTS
# - Auto-lecture après chaque réponse IA
# - Animation bouche REIHANA pendant lecture
# - Chunking intelligent pour textes longs (gTTS max 500 chars)
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c

errors = []
ok = []

# ════════════════════════════════════════════
# PARTIE 1 — Améliorer reihana_tts avec chunking + arabe
# ════════════════════════════════════════════
OLD_TTS = '''def reihana_tts(text, lang="fr"):
    """Genere un audio MP3 base64 avec gTTS - vraie voix feminine"""
    if not GTTS_OK:
        return None
    try:
        clean = text[:280].replace("*","").replace("#","").replace("`","")
        lang_map = {"fr": "fr", "ar": "ar", "en": "en"}
        gtts_lang = lang_map.get(lang, "fr")
        tts = gTTS(text=clean, lang=gtts_lang, slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            fname = f.name
        with open(fname, "rb") as af:
            b64 = base64.b64encode(af.read()).decode()
        os.unlink(fname)
        return b64
    except Exception as e:
        return None'''

NEW_TTS = '''def detect_text_lang(text):
    """Détecte la langue du texte automatiquement"""
    ar_chars = sum(1 for c in text if '\\u0600' <= c <= '\\u06FF')
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
    clean = re.sub(r'\\*\\*(.*?)\\*\\*', r'\\1', text)
    clean = re.sub(r'\\*(.*?)\\*', r'\\1', clean)
    clean = re.sub(r'#+ ', '', clean)
    clean = re.sub(r'`[^`]*`', '', clean)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\\[.*?\\]\\(.*?\\)', '', clean)
    clean = re.sub(r'\\s+', ' ', clean).strip()
    
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
        return None'''

if OLD_TTS in c:
    c = c.replace(OLD_TTS, NEW_TTS)
    ok.append("✅ PARTIE 1: reihana_tts améliorée avec chunking + auto-détection langue")
else:
    errors.append("❌ PARTIE 1: reihana_tts non trouvée")

# ════════════════════════════════════════════
# PARTIE 2 — Améliorer play_reihana_voice avec animation bouche
# ════════════════════════════════════════════
OLD_PLAY = '''def play_reihana_voice(text, lang="fr", mood="calm"):
    """Joue la voix de REIHANA avec la bonne musique selon le mood"""
    b64 = reihana_tts(text, lang)
    if b64:
        st.markdown(
            f\'\'\'<audio id="reiVoice" autoplay style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
            </audio>
            <script>
            setTimeout(function(){{
                var v=document.getElementById("reiVoice");
                if(v){{
                    if(window.reiChangeMood) window.reiChangeMood("{mood}");
                    v.play().catch(function(){{}});
                    v.onended=function(){{
                        if(window.reiChangeMood) window.reiChangeMood("{mood}");
                    }};
                }}
            }}, 300);
            </script>\'\'\',
            unsafe_allow_html=True
        )
        return True
    return False'''

NEW_PLAY = '''def play_reihana_voice(text, lang=None, mood="calm"):
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

if OLD_PLAY in c:
    c = c.replace(OLD_PLAY, NEW_PLAY)
    ok.append("✅ PARTIE 2: play_reihana_voice améliorée avec animation avatar")
else:
    errors.append("❌ PARTIE 2: play_reihana_voice non trouvée")

# ════════════════════════════════════════════
# PARTIE 3 — Bouton "Lire" → gTTS au lieu de speechSynthesis
# ════════════════════════════════════════════
OLD_LIRE = '''        with cc:
            if st.button("🔊 Lire", key=f"sp{i}", use_container_width=True):
                import streamlit.components.v1 as components
                clean = msg["content"].replace("'"," ").replace('"',' ').replace('`',' ').replace(chr(10),' ')
                components.html(f"""<script>
                var u = new SpeechSynthesisUtterance('{clean}');
                u.lang = window.reiConfig ? window.reiConfig.lang : 'fr-FR'; u.rate = window.reiConfig ? window.reiConfig.rate : 1.1; u.pitch = window.reiConfig ? window.reiConfig.pitch : 1.5;
                var vx=window.speechSynthesis.getVoices(); var fv=vx.filter(v=>v.lang.startsWith(u.lang.split('-')[0])); if(fv[0])u.voice=fv[0];
                window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
                </script>""", height=0)'''

NEW_LIRE = '''        with cc:
            if st.button("🔊 Lire", key=f"sp{i}", use_container_width=True):
                _detected_lang = detect_text_lang(msg["content"])
                play_reihana_voice(msg["content"], lang=_detected_lang)'''

if OLD_LIRE in c:
    c = c.replace(OLD_LIRE, NEW_LIRE)
    ok.append("✅ PARTIE 3: Bouton 'Lire' → gTTS (supporte l'arabe)")
else:
    errors.append("❌ PARTIE 3: Bouton Lire non trouvé (vérification manuelle requise)")

# ════════════════════════════════════════════
# PARTIE 4 — Auto-lecture après envoi message (send_btn)
# ════════════════════════════════════════════
OLD_SEND_SPEAK = '''    st.markdown(f"<script>setTimeout(()=>{{window.playNotif();setTimeout(()=>window.reihanaSpeak('{safe_js(rep)}'),400);}},200);</script>", unsafe_allow_html=True)
    st.rerun()'''

NEW_SEND_SPEAK = '''    # Auto-lecture gTTS après réponse IA
    _auto_lang = detect_text_lang(rep)
    play_reihana_voice(rep, lang=_auto_lang)
    st.rerun()'''

if OLD_SEND_SPEAK in c:
    c = c.replace(OLD_SEND_SPEAK, NEW_SEND_SPEAK)
    ok.append("✅ PARTIE 4: Auto-lecture gTTS après envoi message")
else:
    errors.append("❌ PARTIE 4: Bloc send_btn speak non trouvé")

# ════════════════════════════════════════════
# PARTIE 5 — Auto-lecture après regen
# ════════════════════════════════════════════
OLD_REGEN_SPEAK = '''        st.markdown(f"<script>setTimeout(()=>{{window.playNotif();setTimeout(()=>window.reihanaSpeak('{safe_js(rep)}'),400);}},200);</script>", unsafe_allow_html=True)
    st.session_state.regen_index=None'''

NEW_REGEN_SPEAK = '''        _regen_lang = detect_text_lang(rep)
        play_reihana_voice(rep, lang=_regen_lang)
    st.session_state.regen_index=None'''

if OLD_REGEN_SPEAK in c:
    c = c.replace(OLD_REGEN_SPEAK, NEW_REGEN_SPEAK)
    ok.append("✅ PARTIE 5: Auto-lecture gTTS après regen")
else:
    errors.append("❌ PARTIE 5: Bloc regen speak non trouvé")

# ════════════════════════════════════════════
# PARTIE 6 — Auto-lecture suggestions rapides
# ════════════════════════════════════════════
OLD_SUG_SPEAK = '''            st.markdown(f"<script>setTimeout(()=>{{window.playNotif();setTimeout(()=>window.reihanaSpeak('{safe_js(rep)}'),400);}},200);</script>", unsafe_allow_html=True)
            st.rerun()'''

NEW_SUG_SPEAK = '''            _sug_lang = detect_text_lang(rep)
            play_reihana_voice(rep, lang=_sug_lang)
            st.rerun()'''

if OLD_SUG_SPEAK in c:
    c = c.replace(OLD_SUG_SPEAK, NEW_SUG_SPEAK)
    ok.append("✅ PARTIE 6: Auto-lecture gTTS suggestions rapides")
else:
    errors.append("❌ PARTIE 6: Bloc suggestions speak non trouvé")

# ════════════════════════════════════════════
# ÉCRITURE FINALE
# ════════════════════════════════════════════
if c != original:
    open('reihana.py', 'w', encoding='utf-8').write(c)
    print("\n" + "═"*60)
    print("  PATCH GTTS AVANCÉ REIHANA — RÉSULTATS")
    print("═"*60)
    for msg in ok:
        print(msg)
    if errors:
        print("\n⚠️  AVERTISSEMENTS:")
        for e in errors:
            print(e)
    print("\n✅ FICHIER reihana.py SAUVEGARDÉ")
    print(f"   Parties OK: {len(ok)}/6")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION — Vérifiez les patterns")
    for e in errors:
        print(e)
