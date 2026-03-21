HTML_SKELETON = """<!DOCTYPE html>
<html lang="ko" class="theme-light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{lesson_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&family=Noto+Serif+KR:wght@400;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/theme/white.css">
  <style>
    /* ===== THEMES ===== */
    html.theme-light {
      --bg: #FAFAF9; --surface: #FFFFFF; --surface-hover: #F5F5F4;
      --border: rgba(0,0,0,0.08);
      --text: #1a1a2e; --text-secondary: #5a6a7a;
      --accent: #1e4f8c; --accent-secondary: #b8860b;
      --positive: #2d6a4f; --negative: #c62828; --warning: #b8860b;
      --gold: #c9a227; --gold-light: #fef3c7; --gold-mid: #fde68a;
      --cream: #fefcf3; --olive: #2d5016; --sky: #dbeafe;
    }
    html.theme-dark {
      --bg: #0d1117; --surface: #161b22; --surface-hover: #1f2937;
      --border: rgba(255,255,255,0.08);
      --text: #e6edf3; --text-secondary: #8b949e;
      --accent: #58a6ff; --accent-secondary: #d4a843;
      --positive: #3fb950; --negative: #f85149; --warning: #d29922;
      --gold: #d4a843; --gold-light: #2d2006; --gold-mid: #453011;
      --cream: #1a1410; --olive: #5a8a3d; --sky: #1a3a5c;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; overflow: hidden; font-family: 'Noto Sans KR', sans-serif; -webkit-font-smoothing: antialiased; }

    /* ===== REVEAL OVERRIDES ===== */
    .reveal { height: 100%; font-family: 'Noto Sans KR', sans-serif; }
    .reveal .slides { text-align: left; }
    .reveal section { height: 100%; display: flex !important; flex-direction: column; justify-content: center; padding: 60px 80px !important; }

    /* ===== TYPOGRAPHY ===== */
    .reveal h1 { font-family: 'Noto Serif KR', serif; font-size: 3.2rem; font-weight: 700; line-height: 1.3; color: var(--text); letter-spacing: -0.02em;}
    .reveal h2 { font-size: 2.2rem; font-weight: 700; line-height: 1.3; color: var(--text); letter-spacing: -0.02em;}
    .reveal h3 { font-size: 1.5rem; font-weight: 600; line-height: 1.4; color: var(--text); }
    .reveal p { font-size: 1.1rem; line-height: 1.7; color: var(--text); }

    /* ===== SLIDE TYPES ===== */
    .slide-title { background: linear-gradient(145deg, #1a3a6b 0%, #0d2444 40%, #1a3a2a 100%) !important; color: #f8f4e8 !important; }
    html.theme-dark .slide-title { background: linear-gradient(145deg, #0a1628 0%, #040d1a 40%, #0a1a0a 100%) !important; color: #f8f4e8 !important; }
    .slide-title h1, .slide-title h2, .slide-title p { color: inherit !important; }
    .slide-section { background: linear-gradient(135deg, #1e4f8c 0%, #0f2d59 100%) !important; color: #f8f4e8 !important; }
    html.theme-dark .slide-section { background: linear-gradient(135deg, #0d2444 0%, #060f20 100%) !important; color: #f8f4e8 !important; }
    .slide-section h1, .slide-section h2, .slide-section p { color: inherit !important; }
    .slide-content { background: var(--cream) !important; }
    html.theme-dark .slide-content { background: #0d1117 !important; }
    .slide-discuss { background: linear-gradient(135deg, #1a4a2a 0%, #0d2e1a 100%) !important; color: #f0f8f0 !important; }
    .slide-discuss h1, .slide-discuss h2, .slide-discuss p { color: inherit !important; }
    .slide-closing { background: linear-gradient(145deg, #2d1a0a 0%, #1a0d00 60%, #1a1a2e 100%) !important; color: #f8f0dc !important; }
    .slide-closing h1, .slide-closing h2, .slide-closing p { color: inherit !important; }

    /* ===== COMPONENTS ===== */
    .scripture-box { background: linear-gradient(135deg, var(--gold-light), #fff8e7); border-left: 4px solid var(--gold); border-radius: 0 12px 12px 0; padding: 20px 24px; margin: 16px 0; position: relative;}
    html.theme-dark .scripture-box { background: linear-gradient(135deg, #2a1f00, #1a1500); border-left-color: #d4a843; }
    .scripture-box .verse-text { font-family: 'Noto Serif KR', serif; font-size: 1.05rem; line-height: 1.8; color: #3a2a00; font-style: italic; }
    html.theme-dark .scripture-box .verse-text { color: #e8d5a0; }
    .scripture-box .ref { display: block; margin-top: 8px; font-size: 0.85rem; font-weight: 600; color: var(--gold); }

    .principle-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 22px; display: flex; align-items: flex-start; gap: 14px; margin-top: 12px; }
    .principle-icon { width: 40px; height: 40px; min-width: 40px; border-radius: 10px; background: linear-gradient(135deg, var(--accent), #1a6fcc); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;}
    html.theme-dark .principle-icon { background: linear-gradient(135deg, #1e4f8c, #0d2c5c); }
    .principle-card h3 { font-size: 1.05rem; margin-bottom: 4px; color: var(--text); font-weight: 700;}
    .principle-card p { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; }

    .q-item { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; display: flex; align-items: flex-start; gap: 12px; }
    .q-num { background: rgba(255,255,255,0.25); color: white; font-weight: 700; width: 28px; height: 28px; min-width: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
    .q-text { font-size: 1rem; color: rgba(255,255,255,0.92); line-height: 1.6; }

    .title-badge { display: inline-block; background: rgba(212,168,67,0.2); border: 1px solid rgba(212,168,67,0.4); color: #d4a843; font-size: 0.85rem; font-weight: 600; padding: 5px 16px; border-radius: 20px; margin-bottom: 20px; }
    .title-divider { width: 60px; height: 2px; background: linear-gradient(to right, #d4a843, transparent); margin: 20px 0; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 16px; }
    .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 16px; }
    .slide-subtitle { font-size: 1rem; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500; }
    .story-panel { background: var(--surface); border-radius: 16px; padding: 24px; border: 1px solid var(--border); }
    html.theme-dark .story-panel { background: #161b22; border-color: rgba(255,255,255,0.08); }
    .overview-card { background: var(--surface); border-radius: 14px; padding: 16px 20px; border: 1px solid var(--border); transition: box-shadow 0.2s; }
    .overview-card:hover { box-shadow: 0 4px 16px rgba(30,79,140,0.08); }
    .overview-card .chap { font-size: 0.75rem; font-weight: 700; color: var(--accent); margin-bottom: 4px; text-transform: uppercase;}
    .overview-card h3 { font-size: 1rem; margin-bottom: 4px; color: var(--text); font-weight: 700;}
    .overview-card p { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; }

    /* Video Button */
    .video-btn { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #c62828, #d32f2f); color: white !important; font-weight: 600; padding: 10px 20px; border-radius: 30px; text-decoration: none; margin-top: 16px; box-shadow: 0 4px 12px rgba(198,40,40,0.3); transition: transform 0.2s; }
    .video-btn:hover { transform: translateY(-2px); }
    .video-btn svg { width: 20px; height: 20px; fill: white; }

    /* Progress & Nav */
    .slide-progress { position: fixed; top: 0; left: 0; width: 0%; height: 3px; background: linear-gradient(to right, var(--gold), #f0c84a); z-index: 100; transition: width 0.3s ease; }
    .slide-nav { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; align-items: center; gap: 10px; z-index: 9998; background: rgba(255,255,255,0.9); backdrop-filter: blur(8px); border: 1px solid rgba(0,0,0,0.08); border-radius: 24px; padding: 6px 12px; }
    html.theme-dark .slide-nav { background: rgba(22,27,34,0.9); border-color: rgba(255,255,255,0.08); }
    .slide-nav button { width: 32px; height: 32px; background: transparent; border: none; color: var(--text); cursor: pointer; opacity: 0.4; }
    .slide-counter { font-size: 12px; color: var(--text-secondary); font-weight: 500; min-width: 44px; text-align: center; }
    .viz-menu { position: fixed; top: 16px; right: 16px; z-index: 9999; }
    .viz-menu-toggle { width: 40px; height: 40px; border-radius: 10px; background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.08); display: flex; align-items: center; justify-content: center; cursor: pointer; }
    html.theme-dark .viz-menu-toggle { background: rgba(22,27,34,0.9); color: #e6edf3; }
    .viz-menu-dropdown { position: absolute; top: 48px; right: 0; min-width: 180px; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 6px; opacity: 0; visibility: hidden; transform: translateY(-6px); transition: all 0.2s; }
    .viz-menu-dropdown.open { opacity: 1; visibility: visible; transform: translateY(0); }
    .viz-menu-dropdown button { width: 100%; padding: 9px 12px; border: none; background: transparent; color: var(--text); display: flex; align-items: center; gap: 8px; cursor: pointer; }
    
    /* Animations */
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .animate { animation: fadeInUp 0.6s ease-out both; }
    .delay-1 { animation-delay: 0.15s; } .delay-2 { animation-delay: 0.3s; } .delay-3 { animation-delay: 0.45s; } .delay-4 { animation-delay: 0.6s; }
  </style>
</head>
<body>
  <div class="slide-progress" id="progressBar"></div>
  <div class="viz-menu">
    <button class="viz-menu-toggle" onclick="toggleMenu()">
      <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="5" x2="17" y2="5"/><line x1="3" y1="10" x2="17" y2="10"/><line x1="3" y1="15" x2="17" y2="15"/></svg>
    </button>
    <div class="viz-menu-dropdown" id="vizMenuDropdown">
      <button onclick="cycleTheme()"><span id="themeIcon">☀️</span><span id="themeLabel">라이트 모드</span></button>
      <button onclick="downloadImage()"><span>📥</span><span>PNG 저장</span></button>
      <button onclick="window.print()"><span>🖨️</span><span>인쇄 / PDF</span></button>
    </div>
  </div>
  <nav class="slide-nav">
    <button onclick="Reveal.prev()"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 18l-6-6 6-6"/></svg></button>
    <span class="slide-counter" id="slideCounter">1 / 1</span>
    <button onclick="Reveal.next()"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg></button>
  </nav>

  <div class="reveal">
    <div class="slides">
      
{llm_slides_output}
      
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.js"></script>
  <script>
    var currentTheme = localStorage.getItem('viz-theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    function applyTheme(t) {
      document.documentElement.className = 'theme-' + t;
      var icon = document.getElementById('themeIcon'), label = document.getElementById('themeLabel');
      if(icon) icon.textContent = t === 'dark' ? '🌙' : '☀️';
      if(label) label.textContent = t === 'dark' ? '다크 모드' : '라이트 모드';
      localStorage.setItem('viz-theme', t); currentTheme = t;
    }
    function cycleTheme() { applyTheme(currentTheme === 'dark' ? 'light' : 'dark'); }
    applyTheme(currentTheme);

    function toggleMenu() { document.getElementById('vizMenuDropdown').classList.toggle('open'); }
    document.addEventListener('click', e => { if (!e.target.closest('.viz-menu')) document.getElementById('vizMenuDropdown').classList.remove('open'); });

    async function downloadImage() {
      var m = document.querySelector('.viz-menu'), n = document.querySelector('.slide-nav'), p = document.getElementById('progressBar');
      m.style.display='none'; n.style.display='none'; p.style.display='none';
      try {
        var url = await htmlToImage.toPng(document.body, { quality: 1, pixelRatio: 2 });
        var a = document.createElement('a'); a.href = url; a.download = 'presentation.png'; a.click();
      } catch(e) {}
      m.style.display=''; n.style.display=''; p.style.display='';
    }

    Reveal.initialize({ width: 1280, height: 720, center: false, controls: false, progress: false, slideNumber: false, hash: true, transition: 'fade' });
    
    function updateNav() {
      var t = Reveal.getTotalSlides(), i = Reveal.getState().indexh + 1;
      document.getElementById('slideCounter').textContent = i + ' / ' + t;
      document.getElementById('progressBar').style.width = ((i / t) * 100) + '%';
    }
    Reveal.on('slidechanged', updateNav); Reveal.on('ready', updateNav);
    
    Reveal.on('slidechanged', function(e) {
      e.currentSlide.querySelectorAll('.animate').forEach(el => {
        el.style.animation = 'none'; el.offsetHeight; el.style.animation = '';
      });
    });
  </script>
</body>
</html>
"""
