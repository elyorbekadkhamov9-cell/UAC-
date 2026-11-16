#!/usr/bin/env python3
"""Site generator for the shared parts of the UAC site.

  python3 tools/build.py

- rewrites the header nav and footer nav of every page (one source of truth: NAV below)
- writes the generated pages: konsepsiyalar.html, konsepsiya-*.html, yangiliklar.html, videolar.html
- writes sitemap.xml
Hand-written pages (index, kunlik, masalalar, kutubxona, jamoa) keep their own content."""
import re, json, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = "https://elyorbekadkhamov9-cell.github.io/UAC-/"
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
OUT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg>'
CHEV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'

# ---------------------------------------------------------------- navigation
NAV = [("index.html", "Bosh sahifa"), ("kunlik.html", "Kunlik masala"), ("masalalar.html", "Masalalar"),
       ("group", "O‘rganish", [("konsepsiyalar.html", "Konsepsiyalar"), ("videolar.html", "Videolar"), ("kutubxona.html", "Kutubxona")]),
       ("yangiliklar.html", "Yangiliklar"), ("jamoa.html", "Jamoa")]
FLAT = [("index.html", "Bosh sahifa"), ("kunlik.html", "Kunlik masala"), ("masalalar.html", "Masalalar"), ("konsepsiyalar.html", "Konsepsiyalar"),
        ("videolar.html", "Videolar"), ("kutubxona.html", "Kutubxona"), ("yangiliklar.html", "Yangiliklar"), ("jamoa.html", "Jamoa")]

def link(href, label, cur):
    cls = ' class="nav-daily"' if href == "kunlik.html" else ""
    state = ' aria-current="page"' if href == cur else " data-hover"
    return f'<a{cls} href="{href}"{state}>{label}</a>'

def header_nav(cur):
    """cur is the nav entry this page belongs to (an article page passes konsepsiyalar.html)."""
    rows = []
    for it in NAV:
        if it[0] == "group":
            inside = any(h == cur for h, _ in it[2])
            rows.append(f'      <div class="nav-group"{" data-current" if inside else ""}>\n'
                        f'        <button class="nav-btn" type="button" aria-expanded="false" aria-controls="nav-learn">{it[1]}{CHEV}</button>\n'
                        f'        <div class="nav-menu" id="nav-learn">' + "".join(link(h, l, cur) for h, l in it[2]) + '</div>\n      </div>')
        else:
            rows.append("      " + link(it[0], it[1], cur))
    return '<nav class="nav-links" aria-label="Sahifalar">\n' + "\n".join(rows) + "\n    </nav>"

def footer_nav(self_href):
    links = "".join(f'<a href="{h}">{l}</a>' for h, l in FLAT if h != self_href)
    return ('<nav aria-label="Pastki havolalar">\n        ' + links +
            '\n        <a href="https://t.me/ChemistryUAC" target="_blank" rel="noopener">Telegram</a>'
            '<a href="https://www.instagram.com/uac_uz" target="_blank" rel="noopener">Instagram</a>'
            '<a href="https://youtube.com/@chemistryuac" target="_blank" rel="noopener">YouTube</a>'
            f'\n        <a href="{B}privacy.html">Maxfiylik</a>\n      </nav>')

def patch_nav(fn, cur):
    p = os.path.join(ROOT, fn); s = open(p, encoding="utf-8").read()
    s, n1 = re.subn(r'<nav class="nav-links".*?</nav>', lambda m: header_nav(cur), s, count=1, flags=re.S)
    s, n2 = re.subn(r'<nav aria-label="Pastki havolalar">.*?</nav>', lambda m: footer_nav(fn), s, count=1, flags=re.S)
    assert n1 == 1 and n2 == 1, (fn, n1, n2)
    open(p, "w", encoding="utf-8").write(s)

# ---------------------------------------------------------------- page shell
def head(fn, title, desc, extra_css=""):
    url = B + fn
    return f'''<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-8YB7JX7F8F"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-8YB7JX7F8F');
</script>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="icon" type="image/png" href="assets/logo-mark.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<meta name="theme-color" content="#F2F7FB">
<meta property="og:type" content="website">
<meta property="og:site_name" content="UAC">
<meta property="og:locale" content="uz_UZ">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{B}assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;900&family=Instrument+Serif:ital@0;1&family=Geologica:wght@300..700&family=Literata:ital,wght@0,400;1,400&display=swap">
<link rel="stylesheet" href="site.css">
<style>
{extra_css.strip()}
</style>
</head>
'''

def shell(fn, cur, title, desc, css, main, scripts=""):
    return head(fn, title, desc, css) + f'''<body>
<a class="skip" href="#main">Asosiy qismga o‘tish</a>
<canvas id="scene" aria-hidden="true"></canvas>

<header class="nav">
  <div class="wrap">
    <a class="brand" href="index.html"><img src="assets/logo-mark.png" alt="">UAC</a>
    {header_nav(cur)}
    <a class="nav-tg" href="https://t.me/ChemistryUAC" target="_blank" rel="noopener" data-sfx="click" data-hover>Telegram
      {OUT}</a>
  </div>
</header>

<main id="main" tabindex="-1">
{main.strip()}
</main>

<footer>
  <div class="wrap">
    <div class="ft-big" aria-hidden="true">UAC</div>
    <div class="ft-row">
      <span>© 2026 UAC — O’zbekiston Kimyogarlar Assotsiatsiyasi</span>
      {footer_nav(fn)}
    </div>
  </div>
</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>
<script src="site.js"></script>
{scripts.strip()}
</body>
</html>
'''

def write(fn, text):
    open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(text)

# ---------------------------------------------------------------- concepts
def F(s):  # formula pill
    return f'<span class="fx">{s}</span>'

CONCEPTS = [
 dict(slug="18-elektron", cover="18 e⁻", title="18 elektron qoidasi", topic="Koordinatsion kimyo", secs="20 soniya", date="2026-10-31",
  lead="Mn(CO)<sub>5</sub> degan modda yo‘q, Mn<sub>2</sub>(CO)<sub>10</sub> esa bor. Sababi bitta sanoqda: metall atrofidagi elektronlar 18 ta bo‘lishi kerak.",
  card="Karbonil formulasini bir daqiqada tekshirish usuli: metall atrofidagi elektronlarni sanang.",
  body=[
   ("Nega aynan 18?", [
     "Oktet qoidasida faqat s va p orbitallar sanaladi, shuning uchun 8 chiqadi. O‘tish metallarida d qavat ham bog‘lanishda qatnashadi:",
     "<p class=\"eq\">" + F("s<sup>2</sup> + p<sup>6</sup> + d<sup>10</sup> = 18") + "</p>",
     "Metall atrofida 18 elektron bo‘lsa, uning valent qavati to‘ladi va kompleks barqaror bo‘ladi. Bu davrdagi keyingi inert gazning elektron soniga teng."]),
   ("Qanday sanaladi", [
     "Metall o‘z guruh raqamicha elektron beradi, har bir CO esa 2 tadan.",
     "<ul class=\"calc\"><li>" + F("Ni(CO)<sub>4</sub>") + " 10 + 4·2 = <b>18</b></li><li>" + F("Fe(CO)<sub>5</sub>") + " 8 + 5·2 = <b>18</b></li><li>" + F("Mo(CO)<sub>6</sub>") + " 6 + 6·2 = <b>18</b></li></ul>"]),
   ("17 chiqsa-chi?", [
     "Ikki metall atomi bir-biri bilan bog‘lanadi. M–M bog‘ har bir metallga yana bittadan elektron qo‘shadi.",
     "<ul class=\"calc\"><li>Mn: 7 + 5·2 = 17, shuning uchun " + F("Mn<sub>2</sub>(CO)<sub>10</sub>") + ", har bir Mn da <b>18</b></li><li>Co: 9 + 4·2 = 17, shuning uchun " + F("Co<sub>2</sub>(CO)<sub>8</sub>") + ", har bir Co da <b>18</b></li></ul>",
     "Istisno ham bor: " + F("V(CO)<sub>6</sub>") + ". Unda 5 + 12 = 17 elektron, lekin dimer hosil bo‘lmaydi, chunki oltita CO dan keyin V–V bog‘ga joy qolmaydi. Shu sababli u elektronni oson qabul qilib, 18 elektronli " + F("[V(CO)<sub>6</sub>]<sup>−</sup>") + " anioniga aylanadi."]),
  ],
  task=dict(q="M(CO)<sub>x</sub> karbonilida metallning massa ulushi 28,5%. Formulasini toping.",
   a=["Metall ulushi 28,5% bo‘lsa, CO ulushi 71,5%: M = 0,285 · 28,01x / 0,715 ≈ 11,17x.",
      "x = 4 da M ≈ 44,7 (Sc), elektronlar 3 + 8 = 11. x = 6 da M ≈ 67,0 (Zn atrofida), elektronlar 12 + 12 = 24. Ikkalasi ham 18 emas.",
      "x = 5 da M ≈ 55,8, bu temir: 8 + 10 = 18. Javob: <b>Fe(CO)<sub>5</sub></b>."])),
 dict(slug="siklopentadien", cover="pKa 15", title="Siklopentadien nega kislota?", topic="Organik kimyo", secs="49 soniya", date="2026-11-08",
  lead="Siklopentadien oddiy uglevodorod, lekin uning pK<sub>a</sub> 15 atrofida. Bu suvnikiga (15,7) juda yaqin, alkanlarda esa pK<sub>a</sub> 50 atrofida.",
  card="Uglevodorod suv bilan bir qatorda turadi. Sababi aromatiklikda.",
  body=[
   ("Proton ketgach nima qoladi", [
     "C–H bog‘ uzilganda juft elektron uglerodda qoladi va halqadagi π-sistemaga qo‘shiladi. Endi halqada 6 ta π-elektron bor: ikki qo‘sh bog‘dan 4 ta, juftdan 2 ta.",
     "<p class=\"eq\">" + F("C<sub>5</sub>H<sub>6</sub> ⇌ C<sub>5</sub>H<sub>5</sub><sup>−</sup> + H<sup>+</sup>") + "</p>",
     "Halqa tekis, π-elektronlar soni esa Hückel qoidasiga mos keladi: 4n + 2, n = 1 da 6. Demak, siklopentadienil anioni aromatik va juda barqaror. Anion qanchalik barqaror bo‘lsa, kislota shunchalik kuchli."]),
   ("Taqqoslash: siklogeptatrien", [
     "Siklogeptatriendan proton olinsa, halqada 8 ta π-elektron qolardi. Bu 4n + 2 ga to‘g‘ri kelmaydi, anion aromatik emas. Natija pK<sub>a</sub> da ko‘rinadi:",
     "<ul class=\"calc\"><li>alkanlar: pK<sub>a</sub> ≈ <b>50</b></li><li>siklogeptatrien: pK<sub>a</sub> ≈ <b>39</b></li><li>suv: pK<sub>a</sub> = <b>15,7</b></li><li>siklopentadien: pK<sub>a</sub> ≈ <b>15</b></li></ul>"]),
   ("Shu anion ferrotsenni hosil qiladi", [
     "Siklopentadienil anioni temir(II) tuzi bilan ferrotsen beradi:",
     "<p class=\"eq\">" + F("2 NaC<sub>5</sub>H<sub>5</sub> + FeCl<sub>2</sub> → Fe(C<sub>5</sub>H<sub>5</sub>)<sub>2</sub> + 2 NaCl") + "</p>",
     "Elektronlarni sanasak: Fe<sup>2+</sup> dan 6 ta, ikki halqadan 6 tadan 12 ta, jami <b>18</b>. Ferrotsenning barqarorligi <a href=\"konsepsiya-18-elektron.html\">18 elektron qoidasi</a> bilan tushuntiriladi."]),
  ],
  task=dict(q="Siklopropenil kationi C<sub>3</sub>H<sub>3</sub><sup>+</sup> aromatikmi?",
   a=["Halqada bitta qo‘sh bog‘ va bitta bo‘sh p-orbital bor, π-elektronlar soni 2 ta.",
      "4n + 2 qoidasi n = 0 da 2 ni beradi, halqa tekis va tutash.",
      "Javob: <b>ha, aromatik</b>. Bu eng kichik aromatik sistema."])),
 dict(slug="sn2", cover="SN2", title="SN2: orqadan hujum", topic="Organik kimyo", secs="35 soniya", date="2026-11-12",
  lead="SN2 reaksiyasi bir bosqichda ketadi. Nukleofil uglerodga ketuvchi guruhning qarama-qarshi tomonidan hujum qiladi va konfiguratsiya ag‘dariladi.",
  card="Bir bosqich, orqadan hujum, inversiya. 8-bit o‘yin ko‘rinishida.",
  body=[
   ("Bir bosqich, bitta o‘tish holati", [
     "OH<sup>−</sup> (R)-2-brombutandagi uglerodga bromning orqa tomonidan yaqinlashadi. O‘tish holatida C–Br bog‘ uzilayotgan, C–O bog‘ esa endi hosil bo‘layotgan bo‘ladi, qolgan uch guruh bir tekislikda yotadi.",
     "<p class=\"eq\">" + F("HO<sup>−</sup> + (R)-C<sub>4</sub>H<sub>9</sub>Br → (S)-C<sub>4</sub>H<sub>9</sub>OH + Br<sup>−</sup>") + "</p>",
     "Brom ketgach, uch guruh shamolda ag‘darilgan soyabon kabi teskari tomonga o‘tadi. (R)-2-brombutandan (S)-butan-2-ol chiqadi. Bu Valden inversiyasi."]),
   ("Tezlik ikkala moddaga bog‘liq", [
     "O‘tish holatida ikkala zarracha ham qatnashadi, shuning uchun reaksiya ikkinchi tartibli:",
     "<p class=\"eq\">" + F("v = k[OH<sup>−</sup>][RBr]") + "</p>",
     "Ikkala konsentratsiyani ikki baravar oshirsangiz, tezlik to‘rt baravar ortadi. SN2 nomidagi “2” shundan."]),
   ("Uchlamchi uglerodda ishlamaydi", [
     "(CH<sub>3</sub>)<sub>3</sub>C–Br da uchta metil guruhi orqa tomonni to‘sib turadi, nukleofil uglerodga yetib bora olmaydi. Bunday substratlar SN1 va E2 bo‘yicha reaksiyaga kirishadi."]),
  ],
  task=dict(q="Optik faol 2-yodoktan atsetondagi radioaktiv Na<sup>131</sup>I eritmasida qoldirildi. Optik faollik yo‘qolish tezligi radioaktiv yod kirish tezligidan necha marta katta?",
   a=["Har bir almashinish SN2 bo‘yicha ketadi va bitta molekulaning konfiguratsiyasini ag‘daradi.",
      "Bitta enantiomer kamayib, bitta qarama-qarshisi paydo bo‘ladi. Ikkalasi ham optik aylanishni bir xil tomonga o‘zgartiradi.",
      "Javob: <b>2 marta</b>. Hughes 1935-yilda aynan shu nisbatni o‘lchab, SN2 inversiya bilan ketishini ko‘rsatgan."])),
]

MON = ["yanvar","fevral","mart","aprel","may","iyun","iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
def nice(d):
    y, m, dd = d.split("-"); return f"{int(dd)}-{MON[int(m)-1]}, {y}"

ART_CSS = '''
.art{padding-block:clamp(40px,7vh,84px) 110px}
.art .wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,330px);gap:0 72px;align-items:start}
.art-head,.art-body{grid-column:1}
.reel{grid-column:2;grid-row:1 / span 2}
.crumb{font-size:15px;color:var(--muted)}.crumb a{color:var(--sky-ink)}
.art h1{font-family:var(--f-display);font-weight:900;font-size:clamp(34px,5vw,64px);line-height:1;letter-spacing:-.04em;color:var(--navy);margin-top:16px;text-wrap:balance}
.art-meta{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:18px;color:var(--muted);font-size:15px}
.art-lead{font-size:clamp(20px,2vw,23px);line-height:1.5;color:var(--ink);margin-top:26px;max-width:34em;text-wrap:pretty}
.art-body{max-width:38em}
.art-body h2{font-family:var(--f-display);font-weight:700;font-size:clamp(22px,2.2vw,28px);letter-spacing:-.025em;line-height:1.15;color:var(--navy);margin-top:48px}
.art-body p{margin-top:16px;font-size:18.5px;line-height:1.65;text-wrap:pretty}
.art-body a:not(.btn){color:var(--sky-ink)}
.art sub,.art sup{font-size:.7em;line-height:0}
.fx{display:inline-block;padding:3px 12px;border:1.5px solid var(--line-strong);border-radius:999px;background:var(--surface);font-weight:550;color:var(--navy);white-space:nowrap;font-variant-numeric:tabular-nums}
.eq{margin-top:18px!important;overflow-x:auto;padding-bottom:4px}.eq .fx{font-size:19px;padding:8px 18px;white-space:normal;border-radius:18px}
.calc{list-style:none;margin:18px 0 0;padding:0;display:grid;gap:10px;font-size:18.5px}
.calc li{padding:12px 0;border-bottom:1px solid var(--line)}
.calc .fx{margin-right:10px}
.calc b{color:var(--navy);font-weight:700}
.task{margin-top:56px;border:1px solid var(--line);border-radius:22px;background:var(--surface);box-shadow:var(--shadow);padding:clamp(20px,3vw,32px)}
.task h2{margin-top:0}
.task .q{font-size:20px;line-height:1.5;margin-top:14px}
.task details{margin-top:18px}
.task summary{display:inline-flex;align-items:center;min-height:48px;padding:0 20px;border-radius:999px;border:1.5px solid var(--line-strong);cursor:pointer;font-weight:550;list-style:none;user-select:none}
.task summary::-webkit-details-marker{display:none}
.task details[open] summary{background:var(--navy);border-color:var(--navy);color:#fff}
.task ol{margin:18px 0 0;padding-left:1.4em;display:grid;gap:10px;font-size:18px;line-height:1.55}
.task li::marker{color:var(--sky-ink);font-weight:600}
.reel{position:sticky;top:96px;align-self:start}
.reel video{display:block;width:100%;aspect-ratio:9/16;border-radius:22px;background:var(--navy);box-shadow:0 1px 2px rgba(12,31,53,.1),0 24px 44px -18px rgba(12,31,53,.45)}
.reel p{margin-top:12px;font-size:15px;color:var(--muted)}
.next{margin-top:56px;display:flex;flex-wrap:wrap;gap:12px}
.btn-ghost{background:var(--surface);color:var(--ink);border-color:var(--line-strong)}
@media (max-width:900px){ .art .wrap{grid-template-columns:minmax(0,1fr)} .reel{position:static;max-width:300px;grid-column:1;grid-row:auto;margin-top:30px} }
'''

def article(c, i):
    fn = f"konsepsiya-{c['slug']}.html"
    body = ""
    for h, paras in c["body"]:
        body += f"        <h2>{h}</h2>\n" + "".join(("        " + (p if p.startswith("<") else f"<p>{p}</p>") + "\n") for p in paras)
    t = c["task"]
    nxt = CONCEPTS[(i + 1) % len(CONCEPTS)]
    main = f'''
  <article class="art">
    <div class="wrap">
      <header class="art-head">
        <p class="crumb"><a href="konsepsiyalar.html">Konsepsiyalar</a> / {c["topic"]}</p>
        <h1 id="h1">{c["title"]}</h1>
        <p class="art-meta"><span>{nice(c["date"])}</span><span>Video: {c["secs"]}</span></p>
        <p class="art-lead">{c["lead"]}</p>
      </header>
      <aside class="reel" aria-label="Video">
        <video controls playsinline preload="none" poster="assets/k/{c["slug"]}.jpg" src="assets/video/{c["slug"]}.mp4"></video>
        <p>{c["title"]}, {c["secs"]}. Ovozsiz ham tushunarli.</p>
      </aside>
      <div class="art-body">
{body.rstrip()}
          <section class="task" aria-labelledby="task-h">
            <h2 id="task-h">O‘zingizni sinang</h2>
            <p class="q">{t["q"]}</p>
            <details><summary>Yechimni ko‘rish</summary><ol>{"".join(f"<li>{a}</li>" for a in t["a"])}</ol></details>
          </section>
          <div class="next">
            <a class="btn btn-primary" href="konsepsiya-{nxt["slug"]}.html" data-hover>Keyingi mavzu: {nxt["title"]}{ARROW}</a>
            <a class="btn btn-ghost" href="kunlik.html" data-hover>Bugungi masalani yechish</a>
          </div>
      </div>
    </div>
  </article>'''
    plain = re.sub(r"<[^>]+>", "", c["lead"])
    write(fn, shell(fn, "konsepsiyalar.html", f"{re.sub('<[^>]+>', '', c['title'])} — UAC konsepsiyalar", plain, ART_CSS, main))
    return fn

LIST_CSS = '''
.klist{padding-block:8px 110px;display:grid;gap:22px;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr))}
.kcard{display:grid;grid-template-columns:132px minmax(0,1fr);gap:20px;align-items:center;padding:16px;border-radius:24px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);text-decoration:none;color:inherit;transition:transform .25s var(--ease),border-color .25s var(--ease)}
.kcard:hover{transform:translateY(-2px);border-color:var(--line-strong)}
.kcard .ph{aspect-ratio:9/16;border-radius:14px;overflow:hidden;background:var(--navy)}
.kcard img{display:block;width:100%;height:100%;object-fit:cover;transition:transform .5s var(--ease)}
.kcard:hover img{transform:scale(1.03)}
.kcard .tp{font-size:14px;font-weight:600;color:var(--sky-ink)}
.kcard h2{font-family:var(--f-display);font-weight:700;font-size:22px;line-height:1.12;letter-spacing:-.025em;color:var(--navy);margin-top:8px;text-wrap:balance}
.kcard p{margin-top:10px;color:var(--muted);font-size:16px;line-height:1.5}
.kcard .mt{margin-top:14px;font-size:14px;color:var(--muted)}
@media (prefers-reduced-motion:reduce){ .kcard,.kcard img{transition:none} }
'''

def concepts_index():
    cards = ""
    for c in reversed(CONCEPTS):
        cards += f'''    <a class="kcard" href="konsepsiya-{c["slug"]}.html" data-hover>
      <span class="ph"><img src="assets/k/{c["slug"]}.jpg" alt="" width="540" height="960" loading="lazy"></span>
      <span><span class="tp">{c["topic"]}</span><h2>{c["title"]}</h2><p>{c["card"]}</p><span class="mt">{nice(c["date"])} · video {c["secs"]}</span></span>
    </a>
'''
    main = f'''
  <section class="page-head" data-shape="benzene" data-look="3.55,1.25,0.52,0.55" data-look-n="0.9,1.8,0.42,0.25" aria-labelledby="h1">
    <div class="wrap">
      <h1 class="page-title" id="h1">Konsep<wbr>siyalar</h1>
      <p class="page-sub">Olimpiada masalalarida kerak bo‘ladigan g‘oyalar. Har birida qisqa video, tushuntirish va bitta masala bor.</p>
    </div>
  </section>
  <section class="wrap klist" aria-label="Mavzular">
{cards.rstrip()}
  </section>'''
    write("konsepsiyalar.html", shell("konsepsiyalar.html", "konsepsiyalar.html", "UAC Konsepsiyalar — olimpiada kimyosi g‘oyalari",
          "Olimpiada masalalarida kerak bo‘ladigan g‘oyalar: qisqa video, tushuntirish va masala bilan.", LIST_CSS, main))
    data = [dict(slug=c["slug"], cover=c["cover"], title=c["title"], topic=c["topic"], card=c["card"], date=c["date"]) for c in CONCEPTS]
    write("concepts-data.js", "/* Generated by tools/build.py */\nwindow.CONCEPTS=" + json.dumps(data, ensure_ascii=False) + ";\n")

# ---------------------------------------------------------------- news
NEWS_CSS = '''
.nsec{padding-block:18px 64px}
.nsec:last-of-type{padding-bottom:110px}
.nsec-head{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px 24px;margin-bottom:24px}
.nsec-head h2{font-family:var(--f-display);font-weight:700;font-size:clamp(26px,3vw,38px);letter-spacing:-.03em;color:var(--navy)}
.nsec-head p{color:var(--muted);font-size:17px;max-width:36em}
.nsec-head a{color:var(--sky-ink);font-weight:550;text-underline-offset:.2em}
.empty{color:var(--muted);padding:26px;border:1.5px dashed var(--line-strong);border-radius:20px}
.wlist{display:grid;gap:26px}
.witem{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:clamp(20px,3vw,44px);padding:clamp(18px,2.4vw,28px);background:var(--surface);border:1px solid var(--line);border-radius:26px;box-shadow:var(--shadow);scroll-margin-top:110px}
.witem .nc-cover{aspect-ratio:4/3;border-radius:18px}
.witem h3{font-family:var(--f-display);font-weight:700;font-size:clamp(21px,2.1vw,27px);line-height:1.15;letter-spacing:-.025em;color:var(--navy);margin-top:10px;text-wrap:balance}
.witem .lead{font-size:19px;line-height:1.55;margin-top:14px;color:var(--ink)}
.witem .more p{margin-top:12px;font-size:17.5px;line-height:1.62;color:var(--ink);max-width:40em}
.witem sub,.witem sup{font-size:.7em;line-height:0}
.witem details{margin-top:14px}
.witem summary{cursor:pointer;color:var(--sky-ink);font-weight:550;min-height:44px;display:inline-flex;align-items:center;list-style:none}
.witem summary::-webkit-details-marker{display:none}
.witem details[open] summary{display:none}
.src{margin-top:16px;font-size:15px;color:var(--muted)}.src a{color:var(--sky-ink)}
@media (max-width:760px){ .witem{grid-template-columns:minmax(0,1fr)} .witem .nc-cover{aspect-ratio:16/9} }
'''

def news_page():
    main = '''
  <section class="page-head" data-shape="dna" data-look="3.1,1.2,0.5,0.5" data-look-n="0.9,1.8,0.32,0.22" aria-labelledby="h1">
    <div class="wrap">
      <h1 class="page-title" id="h1">Yangi<wbr>liklar</h1>
      <p class="page-sub">UAC kanalidagi so‘nggi postlar va dunyo kimyosidagi voqealar. Har bir xabarda manba ko‘rsatilgan.</p>
    </div>
  </section>
  <section class="wrap nsec" aria-labelledby="uac-h">
    <div class="nsec-head"><h2 id="uac-h">UAC yangiliklari</h2><a href="https://t.me/ChemistryUAC" target="_blank" rel="noopener">Hammasi Telegramda</a></div>
    <div class="ngrid" id="uacFeed"></div>
  </section>
  <section class="wrap nsec" aria-labelledby="world-h">
    <div class="nsec-head"><h2 id="world-h">Dunyo kimyosi</h2><p>Yangi ishlar va voqealarning qisqa bayoni, o‘z so‘zimiz bilan.</p></div>
    <div class="wlist" id="worldFeed"></div>
  </section>'''
    scripts = '''<script src="news-uac.js"></script>
<script src="news-world.js"></script>
<script src="feed.js"></script>
<script>
UACFeed.uacCards(document.getElementById("uacFeed"), 6);
UACFeed.worldArticles(document.getElementById("worldFeed"));
</script>'''
    write("yangiliklar.html", shell("yangiliklar.html", "yangiliklar.html", "UAC Yangiliklar — kanal va dunyo kimyosi",
          "UAC kanalidagi so‘nggi postlar va dunyo kimyosidagi yangiliklar, manbalari bilan.", NEWS_CSS, main, scripts))

# ---------------------------------------------------------------- videos
VIDEOS = [  # every id was checked through YouTube oEmbed on 2026-11-15 (title, channel, embeddable); the card shows the video's own YouTube thumbnail, with our render (tools/covers.py) underneath as the fallback
 dict(id="H6_E6C_e_fg", img="assets/c/ferrotsen.jpg", t="Ferrotsen", ch="Periodic Videos", topic="Metallorganik kimyo", d="Periodic Videos jamoasining ferrotsen haqidagi videosi. Konsepsiyalardagi ferrotsen mavzusiga qo‘shimcha."),
 dict(id="WrsROtPSeuA", img="assets/c/sn2.jpg", t="SN2 stereokimyosi", ch="Khan Academy", topic="Organik kimyo", d="SN2 reaksiyasining stereokimyosi haqida dars."),
 dict(id="yrvV85H737o", img="assets/c/tbubr.jpg", t="SN1 va SN2 mexanizmlari", ch="The Organic Chemistry Tutor", topic="Organik kimyo", d="Nukleofil almashinish reaksiyalari: SN1 va SN2 mexanizmlari bitta darsda."),
 dict(id="lLdPSLNxDqA", img="assets/c/oktaedr.jpg", t="Kristall maydon nazariyasi, 1-qism", ch="MIT OpenCourseWare", topic="Koordinatsion kimyo", d="MIT 5.111 kursining 28-ma’ruzasi: o‘tish metallari va kristall maydon nazariyasi."),
 dict(id="Ja9eEQQzTic", img="assets/c/xef4.jpg", t="Molekula shakli: VSEPR", ch="MIT OpenCourseWare", topic="Umumiy kimyo", d="MIT 5.111 kursining 12-ma’ruzasi: VSEPR nazariyasi va molekulalar shakli."),
 dict(id="Hc5ODj1Ml6c", img="assets/c/karbonat.jpg", t="Formal zaryad va rezonans", ch="MIT OpenCourseWare", topic="Umumiy kimyo", d="MIT 5.111 kursining 11-ma’ruzasi: formal zaryad va rezonans."),
]
EVENT = dict(id="7QqwFxdXp3s", img="assets/news/843.jpg", t="ARBIChO 2026: taqdirlash marosimi", ch="Fan olimpiadalari markazi")

VID_CSS = '''
.vwrap{padding-block:8px 110px}
.vfeat{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:clamp(20px,3vw,48px);align-items:center;padding:clamp(16px,2vw,24px);border-radius:28px;background:var(--navy);color:#fff;text-decoration:none;box-shadow:var(--shadow)}
.vfeat h2{font-family:var(--f-display);font-weight:700;font-size:clamp(24px,2.8vw,36px);line-height:1.1;letter-spacing:-.03em;text-wrap:balance}
.vfeat p{margin-top:14px;color:#C9DDEE;font-size:17px;line-height:1.55;max-width:30em}
.vfeat .go{display:inline-flex;align-items:center;gap:10px;margin-top:22px;min-height:48px;padding:0 20px;border-radius:999px;background:var(--sun);color:var(--ink);font-weight:600}
.vfeat .go svg{width:18px;height:18px}
.vthumb{position:relative;display:block;aspect-ratio:16/9;border-radius:18px;overflow:hidden;background:linear-gradient(135deg,#24507C,#12283F)}
.vthumb .lbl{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(12,31,53,0) 45%,rgba(12,31,53,.82));display:flex;flex-direction:column;justify-content:flex-end;padding:16px;font-family:var(--f-display);font-weight:700;font-size:18px;line-height:1.15;letter-spacing:-.02em;color:#fff}
.vthumb .lbl small{font-family:var(--f-body);font-weight:500;font-size:13px;letter-spacing:0;color:#C9DDEE;margin-bottom:6px}
.vthumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .5s var(--ease)}
.witem .src+.src{margin-top:4px}
.vthumb .play{z-index:2;position:absolute;right:14px;bottom:14px;width:46px;height:46px;border-radius:50%;background:var(--sun);display:grid;place-items:center;box-shadow:0 6px 16px rgba(0,0,0,.3)}
.vthumb .play svg{width:18px;height:18px;margin-left:3px;color:var(--ink)}
.vgrid{margin-top:56px}
.vgrid h2{font-family:var(--f-display);font-weight:700;font-size:clamp(24px,2.6vw,34px);letter-spacing:-.03em;color:var(--navy)}
.vgrid>p{margin-top:10px;color:var(--muted);font-size:17px;max-width:38em}
.vlist{margin-top:26px;display:grid;gap:26px 22px;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr))}
.vcard{display:block;text-decoration:none;color:inherit}
.vcard:hover .vthumb img{transform:scale(1.03)}
.vcard .tp{display:block;margin-top:14px;font-size:14px;font-weight:600;color:var(--sky-ink)}
.vcard h3{font-family:var(--f-display);font-weight:700;font-size:20px;line-height:1.15;letter-spacing:-.02em;color:var(--navy);margin-top:6px}
.vcard p{margin-top:8px;color:var(--muted);font-size:16px;line-height:1.5}
.vcard .ch{display:block;margin-top:10px;font-size:14px;color:var(--muted)}
.vsoon{margin-top:64px;display:flex;flex-wrap:wrap;gap:16px 28px;align-items:center;justify-content:space-between;padding:26px 28px;border-radius:22px;background:var(--band)}
.vsoon h2{font-family:var(--f-display);font-weight:700;font-size:22px;letter-spacing:-.02em;color:var(--navy)}
.vsoon p{margin-top:6px;color:var(--ink);font-size:17px;max-width:34em}
@media (max-width:820px){ .vfeat{grid-template-columns:minmax(0,1fr)} }
@media (prefers-reduced-motion:reduce){ .vthumb img{transition:none} }
'''
PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 4l14 8-14 8z"/></svg>'

def thumb(v):
    return (f'<span class="vthumb"><span class="lbl"><small>{v["ch"]}</small>{v["t"]}</span>'
            f'<img src="{v["img"]}" alt="" loading="lazy" onerror="this.remove()">'
            f'<img class="yt" src="https://i.ytimg.com/vi/{v["id"]}/maxresdefault.jpg" alt="" loading="lazy" onerror="this.remove()" '
            f'''onload="if(this.naturalWidth&lt;200&amp;&amp;this.src.indexOf('maxres')&gt;0)this.src=this.src.replace('maxresdefault','hqdefault')">'''
            f'<span class="play">{PLAY}</span></span>')

def videos_page():
    cards = ""
    for v in VIDEOS:
        cards += f'''      <a class="vcard" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener" data-hover>
        {thumb(v)}
        <span class="tp">{v["topic"]}</span><h3>{v["t"]}</h3><p>{v["d"]}</p><span class="ch">{v["ch"]} · ingliz tilida</span>
      </a>
'''
    main = f'''
  <section class="page-head" data-shape="crystal" data-look="3.35,1.15,0.72,0.55" data-look-n="0.9,1.8,0.45,0.25" aria-labelledby="h1">
    <div class="wrap">
      <h1 class="page-title" id="h1">Videolar</h1>
      <p class="page-sub">Olimpiada mavzulari bo‘yicha tanlangan darslar. Video YouTube’da ochiladi.</p>
    </div>
  </section>
  <section class="wrap vwrap">
    <a class="vfeat" href="https://www.youtube.com/watch?v={EVENT["id"]}" target="_blank" rel="noopener" data-hover>
      {thumb(EVENT)}
      <span><h2>ARBIChO 2026: taqdirlash marosimi</h2><p>Nukusda o‘tgan 3-Abu Rayhon Beruniy nomidagi xalqaro kimyo olimpiadasining yopilish marosimi. Yozuv Fan olimpiadalari markazi kanalida.</p><span class="go">YouTube’da ko‘rish {OUT}</span></span>
    </a>
    <div class="vgrid">
      <h2>Tanlangan darslar</h2>
      <p>Kanaldagi mavzularga mos, ishonchli manbalardan olingan {len(VIDEOS)} ta dars.</p>
      <div class="vlist">
{cards.rstrip()}
      </div>
    </div>
    <div class="vsoon">
      <div><h2>UAC darslari YouTube’da</h2><p>O‘zbek tilidagi video darslarimizni @chemistryuac kanaliga yuklashni boshlayapmiz. Obuna bo‘lsangiz, birinchi darsdan xabar topasiz.</p></div>
      <a class="btn btn-primary" href="https://youtube.com/@chemistryuac" target="_blank" rel="noopener" data-sfx="click" data-hover>Kanalga obuna bo‘lish{ARROW}</a>
    </div>
  </section>'''
    write("videolar.html", shell("videolar.html", "videolar.html", "UAC Videolar — olimpiada kimyosi bo‘yicha darslar",
          "Olimpiada mavzulari bo‘yicha tanlangan video darslar va UAC YouTube kanali.", VID_CSS, main))

# ---------------------------------------------------------------- sitemap
def sitemap():
    urls = [("", "1.0"), ("kunlik.html", "0.9"), ("masalalar.html", "0.9"), ("konsepsiyalar.html", "0.8")] + \
           [(f"konsepsiya-{c['slug']}.html", "0.7") for c in CONCEPTS] + \
           [("yangiliklar.html", "0.8"), ("videolar.html", "0.7"), ("kutubxona.html", "0.8"), ("jamoa.html", "0.6"), ("privacy.html", "0.3")]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{B}{u}</loc><lastmod>2026-11-15</lastmod><priority>{p}</priority></url>\n" for u, p in urls) + "</urlset>\n"
    write("sitemap.xml", sm)

if __name__ == "__main__":
    for fn, cur in [("index.html", "index.html"), ("kunlik.html", "kunlik.html"), ("masalalar.html", "masalalar.html"),
                    ("kutubxona.html", "kutubxona.html"), ("jamoa.html", "jamoa.html")]:
        patch_nav(fn, cur)
    for i, c in enumerate(CONCEPTS): article(c, i)
    concepts_index(); news_page(); videos_page(); sitemap()
    print("built", len(CONCEPTS), "concepts,", len(VIDEOS) + 1, "videos")
