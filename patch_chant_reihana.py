# ═══════════════════════════════════════════════════════════════
# PATCH CHANT REIHANA — REIHANA CHANTE SES PROPRES CHANSONS
# 1. Détection automatique si la réponse IA est une chanson
# 2. Bouton 🎵 CHANTER apparaît sur chaque message-chanson
# 3. gTTS lit vers par vers avec rythme de chant (slow=True)
# 4. Musique change de mood selon style de la chanson
# 5. Session state stocke la dernière chanson détectée
# ═══════════════════════════════════════════════════════════════

c = open('reihana.py', 'r', encoding='utf-8').read()
original = c
ok = []
errors = []

# ════════════════════════════════════════════
# PARTIE 1 — Ajouter après les imports/fonctions TTS
# une fonction detect_song + sing_song avec gTTS lent
# On l'insère juste après play_reihana_voice
# ════════════════════════════════════════════

OLD_ANCHOR = '''# ═══════════════════════════════════════════
# AVATAR BACKGROUND SEMI-RÉALISTE'''

NEW_SONG_FUNCTIONS = '''# ═══════════════════════════════════════════
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
    
    has_song_kw = any(kw in lower for kw in song_keywords_fr+song_keywords_en) or \
                  any(kw in text for kw in song_keywords_ar)
    
    # Détecter structure en vers (lignes courtes répétitives)
    lines = [l.strip() for l in text.split("\\n") if l.strip() and len(l.strip()) > 3]
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
        is_label = is_label or _re.match(r'^(couplet|refrain|pont|chorus|verse|bridge|intro|outro|كوبليه|لازمة|مقطع)\\s*(\\d+)?\\s*[:\\-—]?\\s*$', clean_l, _re.IGNORECASE)
        if not is_label and len(l) > 3:
            # Nettoyer les symboles musicaux
            verse = _re.sub(r'[♪♫🎵🎶🎤*#_~`]', '', l).strip()
            verse = _re.sub(r'^\\s*[-•–—]\\s*', '', verse).strip()
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
        clean = _re.sub(r'\\s+', ' ', clean)
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
# AVATAR BACKGROUND SEMI-RÉALISTE'''

if OLD_ANCHOR in c:
    c = c.replace(OLD_ANCHOR, NEW_SONG_FUNCTIONS)
    ok.append("✅ PARTIE 1: Fonctions detect_song + reihana_tts_slow + play_song ajoutées")
else:
    errors.append("❌ PARTIE 1: Ancre AVATAR BACKGROUND non trouvée")

# ════════════════════════════════════════════
# PARTIE 2 — Session state : ajouter last_song
# ════════════════════════════════════════════
OLD_SS = '''if "messages" not in st.session_state: st.session_state.messages=[]'''
NEW_SS  = '''if "messages" not in st.session_state: st.session_state.messages=[]
if "last_song" not in st.session_state: st.session_state.last_song={"verses":[],"mood":"calm","lang":"fr","msg_index":-1}'''

if OLD_SS in c:
    c = c.replace(OLD_SS, NEW_SS)
    ok.append("✅ PARTIE 2: Session state last_song ajouté")
else:
    # Chercher variante
    alt = 'if "messages" not in st.session_state:'
    if alt in c:
        # Trouver la ligne et ajouter après
        lines = c.split('\n')
        for idx2, line in enumerate(lines):
            if alt in line and 'st.session_state.messages=[]' in line:
                lines.insert(idx2+1, 'if "last_song" not in st.session_state: st.session_state.last_song={"verses":[],"mood":"calm","lang":"fr","msg_index":-1}')
                c = '\n'.join(lines)
                ok.append("✅ PARTIE 2: Session state last_song ajouté (variante)")
                break
        else:
            errors.append("❌ PARTIE 2: Session state messages non trouvé")
    else:
        errors.append("❌ PARTIE 2: Session state messages non trouvé")

# ════════════════════════════════════════════
# PARTIE 3 — Après process_msg dans send_btn :
# détecter si la réponse est une chanson et stocker
# ════════════════════════════════════════════
OLD_SEND = '''    st.session_state.mémoire.add_exchange(st.session_state.user_id,question,rep)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.markdown(f\'<div style="font-family:Orbitron,monospace;font-size:0.57rem;color:rgba(150,150,200,0.38);text-align:right;margin:-3px 0 5px 0;">⚡ {res.get("model","")[:26]} · {res.get("tokens",0)} tokens</div>\', unsafe_allow_html=True)
    # Auto-lecture gTTS après réponse IA
    _auto_lang = detect_text_lang(rep)
    play_reihana_voice(rep, lang=_auto_lang)
    st.rerun()'''

NEW_SEND = '''    st.session_state.mémoire.add_exchange(st.session_state.user_id,question,rep)
    st.session_state.messages.append({"role":"assistant","content":rep})
    st.markdown(f\'<div style="font-family:Orbitron,monospace;font-size:0.57rem;color:rgba(150,150,200,0.38);text-align:right;margin:-3px 0 5px 0;">⚡ {res.get("model","")[:26]} · {res.get("tokens",0)} tokens</div>\', unsafe_allow_html=True)
    # Détecter chanson et stocker
    _is_song, _smood, _slang, _sverses = detect_song(rep)
    if _is_song and _sverses:
        st.session_state.last_song = {"verses": _sverses, "mood": _smood, "lang": _slang, "msg_index": len(st.session_state.messages)-1}
    else:
        # Auto-lecture gTTS normale
        _auto_lang = detect_text_lang(rep)
        play_reihana_voice(rep, lang=_auto_lang)
    st.rerun()'''

if OLD_SEND in c:
    c = c.replace(OLD_SEND, NEW_SEND)
    ok.append("✅ PARTIE 3: Détection chanson après envoi message")
else:
    errors.append("❌ PARTIE 3: Bloc send_btn non trouvé")

# ════════════════════════════════════════════
# PARTIE 4 — Ajouter bouton 🎵 CHANTER sur les messages
# qui sont des chansons (msg_index correspond)
# ════════════════════════════════════════════
OLD_BUTTONS = '''        ca,cb,cc,cd,_=st.columns([1.1,1.1,1.1,1.5,3])
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
                    st.session_state.regen_index=i; st.session_state.regen_question=st.session_state.messages[i-1]["content"]; st.rerun()'''

NEW_BUTTONS = '''        # Détecter si CE message est une chanson
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
                    st.markdown('</div>', unsafe_allow_html=True)'''

if OLD_BUTTONS in c:
    c = c.replace(OLD_BUTTONS, NEW_BUTTONS)
    ok.append("✅ PARTIE 4: Bouton 🎵 CHANTER ajouté sur les messages-chansons")
else:
    errors.append("❌ PARTIE 4: Bloc boutons messages non trouvé")

# ════════════════════════════════════════════
# PARTIE 5 — Améliorer le prompt système pour
# que REIHANA structure bien ses chansons
# ════════════════════════════════════════════
OLD_BUILD_SYS = '''def build_system():
    lang_inst={"🇫🇷 Français":"Réponds TOUJOURS en français.","🇬🇧 English":"Always respond in English.","🇩🇿 العربية":"أجب دائماً باللغة العربية."}[st.session_state.langue]
    system=st.session_state.BASE_PROMPT+f"\\n\\n[PERSONNALITÉ]:\\n{PERS[\'style\']}\\n\\n[LANGUE]: {lang_inst}"'''

NEW_BUILD_SYS = '''def build_system():
    lang_inst={"🇫🇷 Français":"Réponds TOUJOURS en français.","🇬🇧 English":"Always respond in English.","🇩🇿 العربية":"أجب دائماً باللغة العربية."}[st.session_state.langue]
    system=st.session_state.BASE_PROMPT+f"\\n\\n[PERSONNALITÉ]:\\n{PERS[\'style\']}\\n\\n[LANGUE]: {lang_inst}"
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
- NE PAS expliquer la chanson, juste l'écrire"""'''

if OLD_BUILD_SYS in c:
    c = c.replace(OLD_BUILD_SYS, NEW_BUILD_SYS)
    ok.append("✅ PARTIE 5: build_system amélioré pour guider l'écriture de chansons")
else:
    errors.append("❌ PARTIE 5: build_system non trouvé")

# ════════════════════════════════════════════
# ÉCRITURE FINALE
# ════════════════════════════════════════════
if c != original:
    open('reihana.py', 'w', encoding='utf-8').write(c)
    print("\n" + "═"*60)
    print("  PATCH CHANT REIHANA — RÉSULTATS")
    print("═"*60)
    for msg in ok:
        print(msg)
    if errors:
        print("\n⚠️  PROBLÈMES:")
        for e in errors:
            print(e)
    print(f"\n✅ FICHIER reihana.py SAUVEGARDÉ ({len(ok)}/5 parties OK)")
    print("═"*60)
else:
    print("❌ AUCUNE MODIFICATION")
    for e in errors:
        print(e)
