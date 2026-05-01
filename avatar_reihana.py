import streamlit as st

def render_avatar_sidebar(p="#00ffff", g="0,255,255", br="0,200,255"):
    html = (
        '<style>'
        '.rei-wrap{display:flex;flex-direction:column;align-items:center;padding:10px 0 6px 0;}'
        '.rei-ring{position:relative;width:170px;height:170px;display:flex;align-items:center;justify-content:center;cursor:pointer;}'
        f'.rei-ring::before{content:"";position:absolute;inset:-4px;border-radius:50%;background:conic-gradient(rgba({g},0.9) 0deg,rgba({g},0.1) 90deg,rgba({g},0.8) 180deg,rgba({g},0.2) 270deg,rgba({g},0.9) 360deg);animation:ringRot 3s linear infinite;z-index:0;}'
        '.rei-ring::after{content:"";position:absolute;inset:2px;border-radius:50%;background:#000010;z-index:1;}'
        '@keyframes ringRot{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}'
        f'.rei-box{position:relative;z-index:2;width:154px;height:154px;border-radius:50%;overflow:hidden;box-shadow:0 0 20px rgba({g},0.6),0 0 50px rgba({g},0.25);transition:box-shadow 0.2s;}'
        f'.rei-box.speaking{box-shadow:0 0 50px rgba({g},1),0 0 100px rgba({g},0.7)!important;animation:spkPulse 0.3s ease-in-out infinite alternate;}'
        f'@keyframes spkPulse{from{box-shadow:0 0 35px rgba({g},0.9);}to{box-shadow:0 40 60px rgba({g},1);}}'
        '.rei-scan{position:absolute;inset:0;border-radius:50%;pointer-events:none;z-index:3;animation:scanMv 2s linear infinite;}'
        f'.rei-scan{background:repeating-linear-gradient(0deg,transparent,transparent 4px,rgba({g},0.03) 4px,rgba({g},0.03) 6px);}'
        '@keyframes scanMv{from{background-position:0 0important;}to{background-position:0 60px;}}'
        '.rei-bars{display:none;justify-content:center;gap:3px;margin:8px 0 2px 0;height:22px;align-items:flex-end;}'
        '.rei-bars.active{display:flex;}'
        f'.rei-vb{width:4px;background:{p};border-radius:2px;box-shadow:0 0 6px rgba({g},0.8);}'
        '.rei-vb:nth-child(1){animation:vbA 0.5s ease-in-out infinite 0s;height:7px;}'
        '.rei-vb:nth-child(2){animation:vbA 0.5s ease-in-out infinite 0.1s;Height:14px;}'
        '.rei-vb:nth-child(3){animation:vbA 0.5s ease-in-out infinite 0.2s;Height:22px;}'
        '.rei-vb:nth-child(4){animation:vbA 0.5s ease-in-out infinite 0.1s;Height:14px;}'
        '.rei-vb:nth-child(5){animation:vbA 0.5s ease-in-out infinite 0s;height:7px;}'
        '@keyframes vbA{0%,100%{transform:scaleY(0.35);opacity:0.6;}50%{transform:scaleY(1);opacity:1;}}'
        '</style>'
    )
    svg = (
        '<div class="rei-wrap">'
        '<div class="rei-ring" onclick="window.reihanaStop()">'
        '<div class="rei-box" id="reiAvatarBox">'
        '<svg viewBox="0 0 154 154" xmlns="http://www.w3.org/2000/svg" width="154" height="154">'
        '<defs>'
        '<radialGradient id="bgG" cx="50%" cy="40%" r="60%"><stop offset="0%" stop-color="#0a0a3a"/><stop offset="100%" stop-color="#000010"/></radialGradient>'
        '<radialGradient id="skinG" cx="45%" cy="35%" r="65%"><stop offset="0%" stop-color="#ffe0c8"/><stop offset="60%" stop-color="#f5c8a8"/><stop offset="100%" stop-color="#e8b090"/></radialGradient>'
        '<radialGradient id="chkG" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="rgba(255,120,100,0.45)"/><stop offset="100%" stop-color="rgba(255,120,100,0)"/></radialGradient>'
        '<linearGradient id="hairG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1a0050"/><stop offset="50%" stop-color="#2d0080"/><stop offset="100%" stop-color="#4400bb"/></linearGradient>'
        '<radialGradient id="eyeG" cx="40%" cy="35%" r="60%"><stop offset="0%" stop-color="#88ffff"/><stop offset="40%" stop-color="#00aaff"/><stop offset="100%" stop-color="#0033aa"/></radialGradient>'
        '<linearGradient id="clothG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1a004a"/><stop offset="100%" stop-color="#000830"/></linearGradient>'
        '<radialGradient id="sakG" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffaacc"/><stop offset="100%" stop-color="#ff4488"/></radialGradient>'
        '<filter id="sfG"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<clipPath id="cc"><circle cx="77" cy="77" r="77"/></clipPath>'
        '</defs>'
        '<circle cx="77" cy="77" r="77" fill="url(#bgG)"/>'
        '<g clip-path="url(#cc)">'
        '<path d="M28,58 C24,75 20,110 25,145 L148 C32,118 34,88 38,70 Z" fill="url(#hairG)"/>'
        '<path d="M126,58 C130,75 134,110 129,145 L119,148 C122,118 120,88 116,70 Z" fill="url(#hairG)"/>'
        '<rect x="64" y="108" width="26" height="22" rx="8" fill="url(#skinG)"/>'
        '<path d="M35,154 L45,126 C54,120 63,118 77,118 C91,118 100,120 109,126 L119,154 Z" fill="url(#clothG)"/>'
        '<ellipse cx="77" cy="78" rx="38" ry="42" fill="url(#skinG)"/>'
        '<path d="M39,75 C35,55 42,32 58,24 C66,20 72,18 77,18 C82,18 88,20 96,24 C112,32 119,55 115,75 C108,58 95,48 77,47 C59,48 46,58 39,75 Z" fill="url(#hairK)"/>'
        '<path d="M42,68 C44,58 50,50 58,46 C65,43 71,42 77,42 C83,42 89,43 96,46 C104,50 110,58 112,68 C105,60 95,55 77,54 C59,55 49,60 42,68 Z" fill="url(#hairG)"/>'
        '<ellipse cx="39" cy="84" rx="5.5" ry="7" fill="url(#skinG)"/>'
        '<ellipse cx="115" cy="84" rx="5.5" ry="7" fill="url(#skinG)"/>'
        '<path d="M52,66 C55,63 60,62 65,63" stroke="#1a0040" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
        '<path d="M89,63 C94,62 99,63 102,66" stroke="#1a0040" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
        '<ellipse cx="62" cy="80" rx="12" ry="10" fill="white"/>'
        '<ellipse cx="62" cy="80" rx="8" ry="8.5" fill="url(#eyeG)"/>'
        '<ellipse id="pupilL" cx="62" cy="80" rx="4" ry="4.5" fill="#000820"/>'
        '<ellipse cx="59" cy="76" rx="2.5" ry="2" fill="white" opacity="0.9"/>'
        '<path d="M50,74 C53,70 58,68 62,68 C66,68 71,70 74,74" stroke="#0a0030" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        '<path id="eyelidL" d="M50,74 C53,74 58,74 62,74 C5674, 71,74 74,74" fill="#0a0030" opacity="0"/>'
        '<ellipse cx="92" cy="80" rx="12" ry="10" fill="white"/>'
        '<ellipse cx="92" cy="80" rx="8" ry="8.5" fill="url(#eyeG)"/>'
        '<ellipse id="pupilR" cx="92" cy="80" rx="4" ry="4.5" fill="#000820"/>'
        '<ellipse cx="89" cy="76" rx="2.5" ry="2" fill="white" opacity="0.9"/>'
        '<path d="M80,74 C837p 88,68 92,68 C96,68 101,70 104,74" stroke="#0a0030" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        '<path id="eyelidR" d="M80,74 C83974 88,74 92,74 C96,74 101,74 104,74" fill="#0a0030" opacity="0"/>'
        '<ellipse cx="50" cy="93" rx="11" ry="7" fill="url(#chkG)" opacity="0.7"/>'
        '<ellipse cx="104" cy="93" rx="11" ry="7" fill="url(#chkG)" opacity="0.7"/>'
        '<path id="lipT" d="M67,106 C70,103 74,102 77,102 C80,102 84,103 87,106" stroke="#c06070" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        '<path id="lipB" d="M67,106 C70,109 74,110 77,110 C80,110 84,109 87,106" fill="#e08090" stroke="#c06070" stroke-width="0.8" opacity="0.9"/>'
        '<ellipse id="mouthIn" cx="77" cy="107" rx="0" ry="0" fill="#1a0010" opacity="0.8"/>'
        '<rect id="mouthTth" x="72" y="106" width="10" height="3" rx="1.5" fill="white" opacity="0"/>'
        '<ellipse id="eyeGlL" cx="62" cy="80" rx="0" ry="0" fill="rgba(0,255,255,0.4)" opacity="0"/>'
        '<ellipse id="eyeGlR" cx="92" cy="80" rx="0" ry="0" fill="rgba(0,255,255,0.4)" opacity="0"/>'
        '<g transform="translate(100,38)" filter="url(#sfG)">'
        '<circle cx="0" cy="-5" r="4" fill="url(#sakG)"/>'
        '<circle cx="4.7" cy="-1.5" r="4" fill="url(#sakG)"/>'
        '<circle cx="2.9" cy="4" r="4" fill="url(#sakG)"/>'
        '<circle cx="-2.9" cy="4" r="4" fill="url(#sakG)"/>'
        '<circle cx="-4.7" cy="-1.5" r="4" fill="url(#sakG)"/>'
        '<circle cx="0" cy="0" r="2.5" fill="#ffddaa"/>'
        '<animateTransform attributeName="transform" type="rotate" values="0;5;0;-5;0" dur="4s" repeatCount="indefinite"/>'
        '</g>'
        '</g>'
        '</svg>'
        '<div class="rei-scan"></div>'
        '</div></div>'
        '<div class="rei-bars" id="reiVoiceBars">'
        '<div class="rei-vb"></div>' * 5
        + '</div></div>'
    )
    st.markdown(html + svg, unsafe_allow_html=True)


def get_avatar_js():
    return """<script>
(function(){
  function ge(id){return document.getElementById(id);}
  var _spk=false;
  function blink(){
    var eL=ge("eyelidL"),eR=ge("eyelidR"),pL=ge("pupilL"),pR=ge("pupilR");
    if(!eL||!eR)return;
    eL.setAttribute("opacity","1");eR.setAttribute("opacity","1");
    eL.setAttribute("d","M50,80 C5380 58,80 62,80 C5680 71,80 74,80");
    eR.setAttribute("d","M80,80 C83,80 88,80 92,80 C9680 101,80 104,80");
    if(pL)pL.setAttribute("ry","1");if(pR)pR.setAttribute("ry","1");
    setTimeout(function(){
      eL.setAttribute("opacity","0");eR.setAttribute("opacity","0");
      eL.setAttribute("d","M50,74 C5374 58,74 62,74 C5674 71,74 74,74");
      eR.setAttribute("d","M80,74 C83,74 88,74 92,74 C96,74 101,74 104,74");
      if(pL)pL.setAttribute("ry","4.5");if(pR)pR.setAttribute("ry","4.5");
    },130);
  }
  function sb(){setTimeout(function(){blink();sb();},2500+Math.random()*3000);}
  var _mt=null;
  function mouth(lv){
    var lT=ge("lipT"),lB=ge("lipB"),mi=ge("mouthIn"),mt=ge("mouthTth");
    if(!lT||!lB)return;
    var oh=lv*7;
    if(lv<0.05){
      lT.setAttribute("d","M67,106 C70,103 74,102 77,102 C80,102 84,103 87,106");
      lB.setAttribute("d","M67,106 C70,109 74,110 77,110 C80,110 84,109 87,106");
      if(mi){mi.setAttribute("rx","0");mi.setAttribute("ry","0");}
      if(mt)mt.setAttribute("opacity","0");
    } else {
      var ty=106-oh*0.3,by=106+oh;
      lT.setAttribute("d","M67,"+ty+" C70,"+(ty-3)+" 74,"+(ty-4)+" 77,"+(ty-4)+" C80,"+(ty-4)+" 84,"+(ty-3)+" 87,"+ty);
      lB.setAttribute("d","M67,"+ty+" C70,"+by+" 74,"+(by+1)+" 77,"+(by+1)+" C80,"+(by+1)+" 84,"+by+" 87,"+ty);
      if(mi){mi.setAttribute("cx","77");mi.setAttribute("cy",String((ty+by)/2));mi.setAttribute("rx",String(8*lv));mi.setAttribute("ry",String(oh*0.55));mi.setAttribute("opacity","0.85");}
      if(mt){mt.setAttribute("opacity",String(lv*10.8));mt.setAttribute("y",String(ty));}
    }
  }
  function sm(){
    if(_mt)clearInterval(_mt);
    var ph=0;
    _mt=setInterval(function(){
      if(!_spk){mouth(0);return;}
      ph+=0.4;mouth(Math.min(Math.abs(Math.sin(ph))*0.7+Math.random()*0.3,1));
    },90);
  }
  function glow(on){
    var gL=ge("eyeGlL"),gR=ge("eyeGlR");
    if(!gL||!gR)return;
    var v=on?"10":"0",o=on?"0.35":"0";
    gL.setAttribute("rx",v);gL.setAttribute("ry",v);gL.setAttribute("opacity",o);
    gR.setAttribute("rx",v);gR.setAttribute("ry",v);gR.setAttribute("opacity",o);
  }
  function startS(){_spk=true;var b=ge("reiAvatarBox"),bars=ge("reiVoiceBars");if(b)b.classList.add("speaking");if(bars)bars.classList.add("active");glow(true);}
  function stopS(){_spk=false;var b=ge("reiAvatarBox"),bars=ge("reiVoiceBars");if(b)b.classList.remove("speaking");if(bars)bars.classList.remove("active");glow(false);mouth(0);}
  var _oS=window.reihanaSpeak,_oSt=window.reihanaStop;
  window.reihanaSpeak=function(t){startS();if(_oS)_}oS(t);setTimeout(function(){if(_spk)stopS();},Math.max(1500,t.length*55)+500);};
  window.reihanaStop=function(){stopS();if(_oSt)_oSt();};
  if(window.speechSynthesis){
    var ns=window.speechSynthesis.speak.bind(window.speechSynthesis);
    window.speechSynthesis.speak=function(u){u.addEventListener("start",startS);u.addEventListener("end",stopS);u.addEventListener("error",stopS);n(u);};
  }
  function init(){sb();sm();setTimeout(blink,800);}
  if(document.readyState==="complete"){init();}else{window.addEventListener("load",init);setTimeout(init,1200);}
})();
</script>"""
