"""
╔══════════════════════════════════════════════════════════════╗
║       REIHANA - MODULE AVATAR ANIMÉ v1.0                    ║
║       Petite fille anime semi-réaliste 12 ans               ║
║       Fondée par Khedim Benyakhlef (Biny-Joe)               ║
║       AJOUT : ne supprime rien dans reihana.py              ║
╚══════════════════════════════════════════════════════════════╝

UTILISATION dans reihana.py :
─────────────────────────────
1. En haut du fichier, après les imports existants :
   from avatar_reihana import render_avatar_sidebar, get_avatar_js

2. Dans la SIDEBAR, REMPLACE ces lignes :
   
   ANCIEN CODE (à remplacer) :
   ┌─────────────────────────────────────────────────────────┐
   │ st.markdown(f\"\"\"                                       │
   │ <div class="hologram-container">                        │
   │     <div class="hologram-avatar" ...>                   │
   │         {PERS["emoji"]}                                 │
   │         <div class="holo-mouth"></div>                  │
   │     </div>                                              │
   │     <div class="voice-bars">...</div>                   │
   │ </div>                                                  │
   │ \"\"\", unsafe_allow_html=True)                           │
   └─────────────────────────────────────────────────────────┘

   NOUVEAU CODE (à mettre à la place) :
   ┌─────────────────────────────────────────────────────────┐
   │ render_avatar_sidebar(p, g, br)                         │
   └─────────────────────────────────────────────────────────┘

3. Dans le bloc JAVASCRIPT existant, à la fin du st.markdown(...),
   juste AVANT la balise </script> finale, ajouter :
   
   {get_avatar_js()}

   OU simplement appeler une seule fois dans le main :
   st.markdown(get_avatar_js(), unsafe_allow_html=True)
"""

import streamlit as st
import streamlit.components.v1 as components


def render_avatar_sidebar(p="#00ffff", g="0,255,255", br="0,200,255"):
    """
    Affiche l'avatar animé de REIHANA dans la sidebar.
    Remplace le bloc hologram-container existant.
    
    Args:
        p  : couleur primaire du thème (ex: "#00ffff")
        g  : couleur RGB du glow (ex: "0,255,255")
        br : couleur RGB de la bordure (ex: "0,200,255")
    """

    avatar_html = f"""
    <style>
    /* ═══════════════════════════════════════
       AVATAR REIHANA — CONTAINER PRINCIPAL
    ═══════════════════════════════════════ */
    .rei-avatar-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px 0 6px 0;
        position: relative;
    }}

    /* Anneau holographique autour de l'avatar */
    .rei-holo-ring {{
        position: relative;
        width: 170px;
        height: 170px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }}
    .rei-holo-ring::before {{
        content: '';
        position: absolute;
        inset: -4px;
        border-radius: 50%;
        background: conic-gradient(
            rgba({g},0.9) 0deg,
            rgba({g},0.1) 90deg,
            rgba({g},0.8) 180deg,
            rgba({g},0.2) 270deg,
            rgba({g},0.9) 360deg
        );
        animation: ringRotate 3s linear infinite;
        z-index: 0;
    }}
    .rei-holo-ring::after {{
        content: '';
        position: absolute;
        inset: 2px;
        border-radius: 50%;
        background: #000010;
        z-index: 1;
    }}
    @keyframes ringRotate {{
        from {{ transform: rotate(0deg); }}
        to   {{ transform: rotate(360deg); }}
    }}

    /* SVG de l'avatar */
    .rei-svg-container {{
        position: relative;
        z-index: 2;
        width: 154px;
        height: 154px;
        border-radius: 50%;
        overflow: hidden;
        box-shadow:
            0 0 20px rgba({g},0.6),
            0 0 50px rgba({g},0.25),
            inset 0 0 20px rgba({g},0.1);
        transition: box-shadow 0.2s ease;
    }}
    .rei-svg-container.speaking {{
        box-shadow:
            0 0 40px rgba({g},1),
            0 0 90px rgba({g},0.6),
            inset 0 0 40px rgba({g},0.3) !important;
        animation: speakPulse 0.3s ease-in-out infinite alternate;
    }}
    @keyframes speakPulse {{
        from {{ box-shadow: 0 0 35px rgba({g},0.9), 0 0 80px rgba({g},0.5); }}
        to   {{ box-shadow: 0 0 55px rgba({g},1),   0 0 110px rgba({g},0.7); }}
    }}

    /* Lignes scan holographiques sur l'avatar */
    .rei-scanlines {{
        position: absolute;
        inset: 0;
        border-radius: 50%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 4px,
            rgba({g},0.03) 4px,
            rgba({g},0.03) 6px
        );
        pointer-events: none;
        z-index: 3;
        animation: scanMove 2s linear infinite;
    }}
    @keyframes scanMove {{
        from {{ background-position: 0 0; }}
        to   {{ background-position: 0 60px; }}
    }}

    /* Barres vocales sous l'avatar */
    .rei-voice-bars {{
        display: none;
        justify-content: center;
        gap: 3px;
        margin: 8px 0 2px 0;
        height: 22px;
        align-items: flex-end;
    }}
    .rei-voice-bars.active {{ display: flex; }}
    .rei-vbar {{
        width: 4px;
        background: {p};
        border-radius: 2px;
        box-shadow: 0 0 6px rgba({g},0.8);
    }}
    .rei-vbar:nth-child(1) {{ animation: vbarAnim 0.5s ease-in-out infinite 0.0s; height:7px; }}
    .rei-vbar:nth-child(2) {{ animation: vbarAnim 0.5s ease-in-out infinite 0.1s; height:14px; }}
    .rei-vbar:nth-child(3) {{ animation: vbarAnim 0.5s ease-in-out infinite 0.2s; height:22px; }}
    .rei-vbar:nth-child(4) {{ animation: vbarAnim 0.5s ease-in-out infinite 0.1s; height:14px; }}
    .rei-vbar:nth-child(5) {{ animation: vbarAnim 0.5s ease-in-out infinite 0.0s; height:7px; }}
    @keyframes vbarAnim {{
        0%,100% {{ transform: scaleY(0.35); opacity:0.6; }}
        50%      {{ transform: scaleY(1);    opacity:1; }}
    }}

    /* Bouton stop au clic sur l'avatar */
    .rei-svg-container:hover .rei-scanlines {{
        background: repeating-linear-gradient(
            0deg, transparent, transparent 4px,
            rgba({g},0.07) 4px, rgba({g},0.07) 6px
        );
    }}
    </style>

    <div class="rei-avatar-wrap">
        <div class="rei-holo-ring" onclick="window.reihanaStop()" title="Cliquer pour arrêter">
            <div class="rei-svg-container" id="reiAvatarBox">
                <!-- ══════════════════════════════════
                     SVG AVATAR — Petite fille anime
                     Style semi-réaliste, 12 ans
                ══════════════════════════════════ -->
                <svg id="reiAvatarSVG"
                     viewBox="0 0 154 154"
                     xmlns="http://www.w3.org/2000/svg"
                     width="154" height="154">
                    <defs>
                        <!-- Fond dégradé ciel/intérieur -->
                        <radialGradient id="bgGrad" cx="50%" cy="40%" r="60%">
                            <stop offset="0%"   stop-color="#0a0a3a"/>
                            <stop offset="100%" stop-color="#000010"/>
                        </radialGradient>
                        <!-- Peau -->
                        <radialGradient id="skinGrad" cx="45%" cy="35%" r="65%">
                            <stop offset="0%"   stop-color="#ffe0c8"/>
                            <stop offset="60%"  stop-color="#f5c8a8"/>
                            <stop offset="100%" stop-color="#e8b090"/>
                        </radialGradient>
                        <!-- Joues rosées -->
                        <radialGradient id="cheekGrad" cx="50%" cy="50%" r="50%">
                            <stop offset="0%"   stop-color="rgba(255,120,100,0.45)"/>
                            <stop offset="100%" stop-color="rgba(255,120,100,0)"/>
                        </radialGradient>
                        <!-- Cheveux -->
                        <linearGradient id="hairGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%"   stop-color="#1a0050"/>
                            <stop offset="50%"  stop-color="#2d0080"/>
                            <stop offset="100%" stop-color="#4400bb"/>
                        </linearGradient>
                        <!-- Reflet cheveux -->
                        <linearGradient id="hairShine" x1="20%" y1="0%" x2="80%" y2="100%">
                            <stop offset="0%"   stop-color="rgba({g},0.35)"/>
                            <stop offset="100%" stop-color="rgba({g},0)"/>
                        </linearGradient>
                        <!-- Yeux iris -->
                        <radialGradient id="eyeGrad" cx="40%" cy="35%" r="60%">
                            <stop offset="0%"   stop-color="#88ffff"/>
                            <stop offset="40%"  stop-color="#00aaff"/>
                            <stop offset="100%" stop-color="#0033aa"/>
                        </radialGradient>
                        <!-- Lueur yeux -->
                        <radialGradient id="eyeGlow" cx="50%" cy="50%" r="50%">
                            <stop offset="0%"   stop-color="rgba({g},0.5)"/>
                            <stop offset="100%" stop-color="rgba({g},0)"/>
                        </radialGradient>
                        <!-- Vêtement -->
                        <linearGradient id="clothGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%"   stop-color="#1a004a"/>
                            <stop offset="100%" stop-color="#000830"/>
                        </linearGradient>
                        <!-- Fleur sakura décoration -->
                        <radialGradient id="sakuraGrad" cx="50%" cy="50%" r="50%">
                            <stop offset="0%"   stop-color="#ffaacc"/>
                            <stop offset="100%" stop-color="#ff4488"/>
                        </radialGradient>
                        <!-- Filtre glow -->
                        <filter id="glowFx" x="-30%" y="-30%" width="160%" height="160%">
                            <feGaussianBlur stdDeviation="2.5" result="blur"/>
                            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                        </filter>
                        <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="1.5" result="blur"/>
                            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                        </filter>
                        <clipPath id="circleClip">
                            <circle cx="77" cy="77" r="77"/>
                        </clipPath>
                    </defs>

                    <!-- ─── FOND ─── -->
                    <circle cx="77" cy="77" r="77" fill="url(#bgGrad)"/>

                    <!-- Particules lumineuses fond -->
                    <g clip-path="url(#circleClip)" opacity="0.5">
                        <circle cx="20" cy="30" r="1.2" fill="{p}" opacity="0.6">
                            <animate attributeName="opacity" values="0.3;0.9;0.3" dur="2.3s" repeatCount="indefinite"/>
                        </circle>
                        <circle cx="130" cy="25" r="0.9" fill="{p}" opacity="0.5">
                            <animate attributeName="opacity" values="0.2;0.8;0.2" dur="1.7s" repeatCount="indefinite"/>
                        </circle>
                        <circle cx="140" cy="70" r="1.4" fill="{p}" opacity="0.4">
                            <animate attributeName="opacity" values="0.4;1;0.4" dur="2.8s" repeatCount="indefinite"/>
                        </circle>
                        <circle cx="15" cy="90" r="1" fill="{p}" opacity="0.5">
                            <animate attributeName="opacity" values="0.1;0.7;0.1" dur="3.1s" repeatCount="indefinite"/>
                        </circle>
                    </g>

                    <g clip-path="url(#circleClip)">

                    <!-- ─── CHEVEUX (couche arrière) ─── -->
                    <!-- Cheveux longs derrière -->
                    <path d="M28,58 C24,75 20,110 25,145 L35,148 C32,118 34,88 38,70 Z"
                          fill="url(#hairGrad)" opacity="0.95"/>
                    <path d="M126,58 C130,75 134,110 129,145 L119,148 C122,118 120,88 116,70 Z"
                          fill="url(#hairGrad)" opacity="0.95"/>
                    <!-- Mèches côtés bas -->
                    <path d="M30,80 C22,100 20,130 28,154 L38,154 C32,132 34,105 40,88 Z"
                          fill="url(#hairGrad)" opacity="0.8"/>
                    <path d="M124,80 C132,100 134,130 126,154 L116,154 C122,132 120,105 114,88 Z"
                          fill="url(#hairGrad)" opacity="0.8"/>

                    <!-- ─── COU ─── -->
                    <rect x="64" y="108" width="26" height="22" rx="8"
                          fill="url(#skinGrad)"/>
                    <!-- Ombre cou -->
                    <ellipse cx="77" cy="108" rx="12" ry="3"
                             fill="rgba(0,0,0,0.18)"/>

                    <!-- ─── VÊTEMENT (uniforme futuriste) ─── -->
                    <!-- Corps -->
                    <path d="M35,154 L45,126 C54,120 63,118 77,118 C91,118 100,120 109,126 L119,154 Z"
                          fill="url(#clothGrad)"/>
                    <!-- Col -->
                    <path d="M62,118 L77,128 L92,118 L88,115 L77,124 L66,115 Z"
                          fill="rgba({g},0.3)" filter="url(#softGlow)"/>
                    <!-- Détail lumineux uniforme -->
                    <line x1="77" y1="128" x2="77" y2="154"
                          stroke="rgba({g},0.5)" stroke-width="1.5" opacity="0.7"/>
                    <path d="M55,132 C62,130 70,129 77,129 C84,129 92,130 99,132"
                          stroke="rgba({g},0.4)" stroke-width="1" fill="none"/>

                    <!-- ─── VISAGE ─── -->
                    <!-- Forme tête -->
                    <ellipse cx="77" cy="78" rx="38" ry="42"
                             fill="url(#skinGrad)"/>
                    <!-- Ombre menton -->
                    <ellipse cx="77" cy="115" rx="18" ry="4"
                             fill="rgba(0,0,0,0.12)"/>
                    <!-- Ombre côtés visage -->
                    <ellipse cx="42" cy="82" rx="8" ry="20"
                             fill="rgba(160,90,60,0.08)"/>
                    <ellipse cx="112" cy="82" rx="8" ry="20"
                             fill="rgba(160,90,60,0.08)"/>

                    <!-- ─── CHEVEUX (dessus tête) ─── -->
                    <!-- Calotte principale -->
                    <path d="M39,75 C35,55 42,32 58,24 C66,20 72,18 77,18 C82,18 88,20 96,24 C112,32 119,55 115,75 C108,58 95,48 77,47 C59,48 46,58 39,75 Z"
                          fill="url(#hairGrad)"/>
                    <!-- Reflet brillant sur cheveux -->
                    <path d="M55,28 C62,22 72,19 82,20 C90,21 98,25 103,30 C94,26 85,24 77,24 C69,24 62,26 55,28 Z"
                          fill="url(#hairShine)" opacity="0.7"/>
                    <!-- Frange -->
                    <path d="M42,68 C44,58 50,50 58,46 C65,43 71,42 77,42 C83,42 89,43 96,46 C104,50 110,58 112,68 C105,60 95,55 77,54 C59,55 49,60 42,68 Z"
                          fill="url(#hairGrad)"/>
                    <!-- Mèche frange gauche -->
                    <path d="M42,68 C40,72 40,78 44,82 C43,76 43,70 47,66 C45,66 43,67 42,68 Z"
                          fill="url(#hairGrad)"/>
                    <!-- Mèche frange droite -->
                    <path d="M112,68 C114,72 114,78 110,82 C111,76 111,70 107,66 C109,66 111,67 112,68 Z"
                          fill="url(#hairGrad)"/>
                    <!-- Reflet frange -->
                    <path d="M58,46 C65,43 71,42 77,42 C83,42 89,43 96,46 C89,44 83,43 77,43 C71,43 65,44 58,46 Z"
                          fill="url(#hairShine)" opacity="0.5"/>

                    <!-- ─── OREILLES ─── -->
                    <ellipse cx="39" cy="84" rx="5.5" ry="7"
                             fill="url(#skinGrad)"/>
                    <ellipse cx="115" cy="84" rx="5.5" ry="7"
                             fill="url(#skinGrad)"/>
                    <!-- Détail intérieur oreille -->
                    <ellipse cx="39" cy="84" rx="2.5" ry="4"
                             fill="rgba(200,120,90,0.3)"/>
                    <ellipse cx="115" cy="84" rx="2.5" ry="4"
                             fill="rgba(200,120,90,0.3)"/>

                    <!-- ─── SOURCILS ─── -->
                    <path d="M52,66 C55,63 60,62 65,63" stroke="#1a0040" stroke-width="2.2"
                          fill="none" stroke-linecap="round"/>
                    <path d="M89,63 C94,62 99,63 102,66" stroke="#1a0040" stroke-width="2.2"
                          fill="none" stroke-linecap="round"/>

                    <!-- ─── YEUX ─── -->
                    <!-- Ombre sous yeux -->
                    <ellipse cx="62" cy="81" rx="13" ry="11"
                             fill="rgba(0,0,0,0.08)"/>
                    <ellipse cx="92" cy="81" rx="13" ry="11"
                             fill="rgba(0,0,0,0.08)"/>

                    <!-- Blanc de l'œil gauche -->
                    <ellipse cx="62" cy="80" rx="12" ry="10"
                             fill="white"/>
                    <!-- Iris gauche -->
                    <ellipse cx="62" cy="80" rx="8" ry="8.5"
                             fill="url(#eyeGrad)"/>
                    <!-- Lueur iris gauche -->
                    <ellipse cx="62" cy="80" rx="8" ry="8.5"
                             fill="url(#eyeGlow)" opacity="0.6"/>
                    <!-- Pupille gauche -->
                    <ellipse id="pupilL" cx="62" cy="80" rx="4" ry="4.5"
                             fill="#000820"/>
                    <!-- Reflets yeux gauche -->
                    <ellipse cx="59" cy="76" rx="2.5" ry="2"
                             fill="white" opacity="0.9"/>
                    <ellipse cx="65" cy="83" rx="1.2" ry="1"
                             fill="white" opacity="0.5"/>
                    <!-- Cils gauche (haut) -->
                    <path d="M50,74 C53,70 58,68 62,68 C66,68 71,70 74,74"
                          stroke="#0a0030" stroke-width="2.5" fill="none" stroke-linecap="round"/>
                    <!-- Paupière gauche -->
                    <path id="eyelidL" d="M50,74 C53,74 58,74 62,74 C66,74 71,74 74,74"
                          stroke="#0a0030" stroke-width="0" fill="#0a0030" opacity="0"/>

                    <!-- Blanc de l'œil droit -->
                    <ellipse cx="92" cy="80" rx="12" ry="10"
                             fill="white"/>
                    <!-- Iris droit -->
                    <ellipse cx="92" cy="80" rx="8" ry="8.5"
                             fill="url(#eyeGrad)"/>
                    <!-- Lueur iris droit -->
                    <ellipse cx="92" cy="80" rx="8" ry="8.5"
                             fill="url(#eyeGlow)" opacity="0.6"/>
                    <!-- Pupille droite -->
                    <ellipse id="pupilR" cx="92" cy="80" rx="4" ry="4.5"
                             fill="#000820"/>
                    <!-- Reflets yeux droit -->
                    <ellipse cx="89" cy="76" rx="2.5" ry="2"
                             fill="white" opacity="0.9"/>
                    <ellipse cx="95" cy="83" rx="1.2" ry="1"
                             fill="white" opacity="0.5"/>
                    <!-- Cils droit (haut) -->
                    <path d="M80,74 C83,70 88,68 92,68 C96,68 101,70 104,74"
                          stroke="#0a0030" stroke-width="2.5" fill="none" stroke-linecap="round"/>
                    <!-- Paupière droite (clignement) -->
                    <path id="eyelidR" d="M80,74 C83,74 88,74 92,74 C96,74 101,74 104,74"
                          stroke="#0a0030" stroke-width="0" fill="#0a0030" opacity="0"/>

                    <!-- Cils bas (discrets) -->
                    <path d="M51,88 C54,91 58,92 62,92" stroke="#0a0030" stroke-width="1.2"
                          fill="none" stroke-linecap="round" opacity="0.5"/>
                    <path d="M81,88 C84,91 88,92 92,92" stroke="#0a0030" stroke-width="1.2"
                          fill="none" stroke-linecap="round" opacity="0.5"/>

                    <!-- ─── NEZ ─── -->
                    <path d="M75,93 C74,97 75,100 77,101 C79,100 80,97 79,93"
                          fill="rgba(180,100,70,0.18)" rx="3"/>
                    <!-- Petites narines -->
                    <ellipse cx="74" cy="100" rx="2" ry="1.3"
                             fill="rgba(160,80,60,0.25)"/>
                    <ellipse cx="80" cy="100" rx="2" ry="1.3"
                             fill="rgba(160,80,60,0.25)"/>

                    <!-- ─── JOUES ROSÉES ─── -->
                    <ellipse cx="50" cy="93" rx="11" ry="7"
                             fill="url(#cheekGrad)" opacity="0.7"/>
                    <ellipse cx="104" cy="93" rx="11" ry="7"
                             fill="url(#cheekGrad)" opacity="0.7"/>

                    <!-- ─── BOUCHE (animée) ─── -->
                    <!-- Lèvre supérieure -->
                    <path id="lipTop"
                          d="M67,106 C70,103 74,102 77,102 C80,102 84,103 87,106"
                          stroke="#c06070" stroke-width="1.8" fill="none" stroke-linecap="round"/>
                    <!-- Lèvre inférieure / sourire -->
                    <path id="lipBottom"
                          d="M67,106 C70,109 74,110 77,110 C80,110 84,109 87,106"
                          fill="#e08090" stroke="#c06070" stroke-width="0.8" opacity="0.9"/>
                    <!-- Intérieur bouche (visible quand parle) -->
                    <ellipse id="mouthInner" cx="77" cy="107" rx="0" ry="0"
                             fill="#1a0010" opacity="0.8"/>
                    <!-- Dents (visibles quand parle) -->
                    <rect id="mouthTeeth" x="72" y="106" width="10" height="3"
                          rx="1.5" fill="white" opacity="0"/>

                    <!-- ─── ACCESSOIRE : Épingle sakura dans cheveux ─── -->
                    <!-- Tige -->
                    <line x1="95" y1="42" x2="100" y2="52"
                          stroke="rgba({g},0.7)" stroke-width="1.2"/>
                    <!-- Fleur sakura -->
                    <g transform="translate(100,38)" filter="url(#softGlow)">
                        <circle cx="0" cy="-5" r="4" fill="url(#sakuraGrad)" opacity="0.9"/>
                        <circle cx="4.7" cy="-1.5" r="4" fill="url(#sakuraGrad)" opacity="0.9"/>
                        <circle cx="2.9" cy="4" r="4" fill="url(#sakuraGrad)" opacity="0.9"/>
                        <circle cx="-2.9" cy="4" r="4" fill="url(#sakuraGrad)" opacity="0.9"/>
                        <circle cx="-4.7" cy="-1.5" r="4" fill="url(#sakuraGrad)" opacity="0.9"/>
                        <circle cx="0" cy="0" r="2.5" fill="#ffddaa"/>
                        <!-- Animation rotation douce -->
                        <animateTransform attributeName="transform" type="rotate"
                                          values="0;5;0;-5;0" dur="4s" repeatCount="indefinite"/>
                    </g>

                    <!-- ─── LUEUR HOLOGRAPHIQUE YEUX (quand parle) ─── -->
                    <ellipse id="eyeGlowL" cx="62" cy="80" rx="0" ry="0"
                             fill="rgba({g},0.4)" opacity="0"/>
                    <ellipse id="eyeGlowR" cx="92" cy="80" rx="0" ry="0"
                             fill="rgba({g},0.4)" opacity="0"/>

                    </g><!-- fin clip -->

                    <!-- ─── SCAN LINE OVERLAY ─── -->
                    <rect width="154" height="154" fill="none"
                          stroke="rgba({g},0.08)" stroke-width="0"/>
                </svg>
                <div class="rei-scanlines"></div>
            </div>
        </div>

        <!-- Barres vocales -->
        <div class="rei-voice-bars" id="reiVoiceBars">
            <div class="rei-vbar"></div>
            <div class="rei-vbar"></div>
            <div class="rei-vbar"></div>
            <div class="rei-vbar"></div>
            <div class="rei-vbar"></div>
        </div>
    </div>
    """

    st.markdown(avatar_html, unsafe_allow_html=True)


def get_avatar_js():
    """
    Retourne le bloc <script> pour les animations de l'avatar.
    À injecter UNE SEULE FOIS dans la page, après render_avatar_sidebar().

    Usage :
        st.markdown(get_avatar_js(), unsafe_allow_html=True)
    """
    return """
    <script>
    // ═══════════════════════════════════════════════════
    //   REIHANA AVATAR — CONTRÔLEUR D'ANIMATIONS
    // ═══════════════════════════════════════════════════

    (function() {
        // ── Éléments SVG ──
        function getEl(id) { return document.getElementById(id); }

        // ── État ──
        let _isSpeaking = false;
        let _blinkInterval = null;
        let _mouthInterval = null;
        let _breatheInterval = null;

        // ══════════════════════════════
        //   CLIGNEMENT DES YEUX
        // ══════════════════════════════
        function blink() {
            const eL = getEl('eyelidL');
            const eR = getEl('eyelidR');
            const pL = getEl('pupilL');
            const pR = getEl('pupilR');
            if (!eL || !eR) return;

            // Fermeture rapide
            eL.setAttribute('opacity', '1');
            eR.setAttribute('opacity', '1');
            eL.setAttribute('d', 'M50,80 C53,80 58,80 62,80 C66,80 71,80 74,80');
            eR.setAttribute('d', 'M80,80 C83,80 88,80 92,80 C96,80 101,80 104,80');
            if (pL) pL.setAttribute('ry', '1');
            if (pR) pR.setAttribute('ry', '1');

            setTimeout(() => {
                // Réouverture
                eL.setAttribute('opacity', '0');
                eR.setAttribute('opacity', '0');
                eL.setAttribute('d', 'M50,74 C53,74 58,74 62,74 C66,74 71,74 74,74');
                eR.setAttribute('d', 'M80,74 C83,74 88,74 92,74 C96,74 101,74 104,74');
                if (pL) pL.setAttribute('ry', '4.5');
                if (pR) pR.setAttribute('ry', '4.5');
            }, 130);
        }

        function startBlink() {
            if (_blinkInterval) clearInterval(_blinkInterval);
            // Clignement aléatoire toutes les 2.5-5.5 secondes
            function scheduleBlink() {
                const delay = 2500 + Math.random() * 3000;
                _blinkInterval = setTimeout(() => {
                    blink();
                    scheduleBlink();
                }, delay);
            }
            scheduleBlink();
        }

        // ══════════════════════════════
        //   ANIMATION BOUCHE (PAROLE)
        // ══════════════════════════════
        function animMouthOpen(level) {
            // level : 0 (fermé) à 1 (grand ouvert)
            const lipT  = getEl('lipTop');
            const lipB  = getEl('lipBottom');
            const inner = getEl('mouthInner');
            const teeth = getEl('mouthTeeth');
            if (!lipT || !lipB) return;

            const openH = level * 7; // max 7px d'ouverture

            if (level < 0.05) {
                // Bouche fermée — sourire doux
                lipT.setAttribute('d', 'M67,106 C70,103 74,102 77,102 C80,102 84,103 87,106');
                lipB.setAttribute('d', 'M67,106 C70,109 74,110 77,110 C80,110 84,109 87,106');
                if (inner) { inner.setAttribute('rx','0'); inner.setAttribute('ry','0'); }
                if (teeth) teeth.setAttribute('opacity','0');
            } else {
                // Bouche ouverte (parole)
                const topY  = 106 - openH * 0.3;
                const botY  = 106 + openH;
                lipT.setAttribute('d', `M67,${topY} C70,${topY-3} 74,${topY-4} 77,${topY-4} C80,${topY-4} 84,${topY-3} 87,${topY}`);
                lipB.setAttribute('d', `M67,${topY} C70,${botY} 74,${botY+1} 77,${botY+1} C80,${botY+1} 84,${botY} 87,${topY}`);
                if (inner) {
                    inner.setAttribute('cx','77');
                    inner.setAttribute('cy', String((topY + botY) / 2));
                    inner.setAttribute('rx', String(8 * level));
                    inner.setAttribute('ry', String(openH * 0.55));
                    inner.setAttribute('opacity','0.85');
                }
                if (teeth) {
                    teeth.setAttribute('opacity', String(level * 0.8));
                    teeth.setAttribute('y', String(topY));
                }
            }
        }

        function startMouthAnim() {
            if (_mouthInterval) clearInterval(_mouthInterval);
            let phase = 0;
            _mouthInterval = setInterval(() => {
                if (!_isSpeaking) { animMouthOpen(0); return; }
                // Oscillation naturelle de la bouche
                phase += 0.4;
                const level = Math.abs(Math.sin(phase)) * 0.7 + Math.random() * 0.3;
                animMouthOpen(Math.min(level, 1));
            }, 90);
        }

        // ══════════════════════════════
        //   LUEUR YEUX (PAROLE)
        // ══════════════════════════════
        function setEyeGlow(active) {
            const gL = getEl('eyeGlowL');
            const gR = getEl('eyeGlowR');
            if (!gL || !gR) return;
            if (active) {
                gL.setAttribute('rx','10'); gL.setAttribute('ry','10'); gL.setAttribute('opacity','0.35');
                gR.setAttribute('rx','10'); gR.setAttribute('ry','10'); gR.setAttribute('opacity','0.35');
            } else {
                gL.setAttribute('rx','0'); gL.setAttribute('ry','0'); gL.setAttribute('opacity','0');
                gR.setAttribute('rx','0'); gR.setAttribute('ry','0'); gR.setAttribute('opacity','0');
            }
        }

        // ══════════════════════════════
        //   PAROLE — DEBUT / FIN
        // ══════════════════════════════
        function startSpeaking() {
            _isSpeaking = true;
            const box = document.getElementById('reiAvatarBox');
            const bars = document.getElementById('reiVoiceBars');
            if (box)  box.classList.add('speaking');
            if (bars) bars.classList.add('active');
            setEyeGlow(true);
        }

        function stopSpeaking() {
            _isSpeaking = false;
            const box = document.getElementById('reiAvatarBox');
            const bars = document.getElementById('reiVoiceBars');
            if (box)  box.classList.remove('speaking');
            if (bars) bars.classList.remove('active');
            setEyeGlow(false);
            animMouthOpen(0);
        }

        // ══════════════════════════════
        //   PATCH reihanaSpeak / Stop
        // ══════════════════════════════
        // On surcharge les fonctions existantes pour y brancher l'avatar
        const _origSpeak = window.reihanaSpeak;
        const _origStop  = window.reihanaStop;

        window.reihanaSpeak = function(text) {
            startSpeaking();
            if (_origSpeak) _origSpeak(text);

            // Fallback sécurité : si speech synthesis non disponible ou très court
            const estDuration = Math.max(1500, text.length * 55);
            setTimeout(() => {
                if (_isSpeaking) stopSpeaking();
            }, estDuration + 500);
        };

        window.reihanaStop = function() {
            stopSpeaking();
            if (_origStop) _origStop();
        };

        // Aussi brancher sur les événements SpeechSynthesis quand ils arrivent
        const _origDoSpeak = window.speechSynthesis;
        if (_origDoSpeak) {
            // Intercept via onvoiceschanged hook — on patch aussi speechSynthesis.speak
            const _nativeSpeech = window.speechSynthesis.speak.bind(window.speechSynthesis);
            window.speechSynthesis.speak = function(utterance) {
                utterance.addEventListener('start', startSpeaking);
                utterance.addEventListener('end',   stopSpeaking);
                utterance.addEventListener('error', stopSpeaking);
                _nativeSpeech(utterance);
            };
        }

        // ══════════════════════════════
        //   INIT
        // ══════════════════════════════
        function init() {
            startBlink();
            startMouthAnim();
            // Petite animation d'entrée
            setTimeout(() => blink(), 800);
        }

        // Lancer après que le DOM soit prêt
        if (document.readyState === 'complete') {
            init();
        } else {
            window.addEventListener('load', init);
            setTimeout(init, 1200); // Fallback Streamlit
        }

    })();
    </script>
    """
