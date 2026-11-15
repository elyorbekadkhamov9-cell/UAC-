#!/usr/bin/env python3
"""Build news-uac.js from the public page of the Telegram channel (https://t.me/s/ChemistryUAC).

  python3 tools/tg_feed.py                 fetch the live page, save post images to assets/news/
  python3 tools/tg_feed.py --html FILE     parse a saved page (used by the test), no network, no images

Rules for which posts become news cards:
  - the post must have text of at least 60 characters that is not just a link
  - a post written mostly in Cyrillic within 15 minutes of the previous post is treated as the Russian
    copy of that post and skipped (the site is in Uzbek)
  - the newest 9 posts are kept
The feed file is never overwritten when no posts could be parsed."""
import sys, re, os, json, html, urllib.request
from html.parser import HTMLParser
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNEL = "ChemistryUAC"; KEEP = 9; MIN_TEXT = 60
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "wbr"}

class Page(HTMLParser):
    """Collects, per message: id, datetime, text (with line breaks), first image url, kind of media."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.posts = []; self.cur = None; self.depth = 0; self.text_depth = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = a.get("class") or ""
        if "tgme_widget_message " in cls + " " and a.get("data-post"):
            self.cur = dict(id=a["data-post"].split("/")[-1], date="", text=[], img="", media=""); self.posts.append(self.cur); self.depth = 0
        if self.cur is None: return
        if tag not in VOID: self.depth += 1
        style = html.unescape(a.get("style") or "")
        if ("tgme_widget_message_photo_wrap" in cls or "tgme_widget_message_video_thumb" in cls) and not self.cur["img"]:
            m = re.search(r"background-image:\s*url\(['\"]?([^'\")]+)", style)
            if m: self.cur["img"] = m.group(1)
        if "tgme_widget_message_photo_wrap" in cls and not self.cur["media"]: self.cur["media"] = "photo"
        if "tgme_widget_message_video_player" in cls: self.cur["media"] = "video"
        if "tgme_widget_message_document_wrap" in cls and not self.cur["media"]: self.cur["media"] = "file"
        if "tgme_widget_message_text" in cls and self.text_depth is None and not self.cur["text"]: self.text_depth = self.depth
        if tag == "br" and self.text_depth is not None: self.cur["text"].append("\n")
        if tag == "time" and a.get("datetime") and "time" in cls.split(): self.cur["date"] = a["datetime"]
    def handle_endtag(self, tag):
        if self.cur is None or tag in VOID: return
        if self.text_depth is not None and self.depth == self.text_depth: self.text_depth = None
        self.depth -= 1
        if self.depth <= 0: self.cur = None; self.text_depth = None
    def handle_data(self, data):
        if self.cur is not None and self.text_depth is not None: self.cur["text"].append(data)

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍\U000E0020-\U000E007F]")
def clean(s): return re.sub(r"[ \t ]+", " ", EMOJI.sub("", s)).strip()
def cyr_share(s):
    letters = [c for c in s if c.isalpha()]
    return sum("Ѐ" <= c <= "ӿ" for c in letters) / max(1, len(letters))
def cut(s, n):
    if len(s) <= n: return s
    s = s[:n]; i = s.rfind(" ")
    return (s[:i] if i > n * 0.6 else s).rstrip(" ,.;:—-") + "…"

def to_item(p):
    raw = "".join(p["text"]); lines = [clean(l) for l in raw.split("\n")]
    lines = [l for l in lines if l and not re.fullmatch(r"(#\S+\s*)+", l)]
    body = " ".join(lines)
    if len(body) < MIN_TEXT or re.fullmatch(r"https?://\S+", body): return None
    greet = re.compile(r"^(barchaga |hammaga )?(assalomu alaykum|salom)\b", re.I)
    k = next((i for i, l in enumerate(lines) if len(l) >= 12 and not greet.match(l)), 0)
    cand = lines[k]; tail = lines[k + 1:]
    if len(cand) > 130:
        m = re.match(r"(.{20,128}?[.!?])\s+(.*)", cand)
        if m: title, tail = m.group(1), [m.group(2)] + tail
        else: title = cut(cand, 128)
    else: title = cand
    rest = " ".join(tail)
    return dict(id=p["id"], date=p["date"][:10], title=title, text=cut(rest, 190), media=p["media"], cyr=round(cyr_share(body), 2),
                url=f"https://t.me/{CHANNEL}/{p['id']}", img_src=p["img"], ts=p["date"])

def build(page_html):
    pg = Page(); pg.feed(page_html); items = []; prev_ts = None
    for p in pg.posts:
        it = to_item(p) if p["date"] else None
        ts = datetime.fromisoformat(p["date"]) if p["date"] else None
        if it and it["cyr"] > 0.5 and prev_ts and ts and (ts - prev_ts).total_seconds() <= 900: it = None
        if ts: prev_ts = ts
        if it: items.append(it)
    return items[-KEEP:][::-1], len(pg.posts)

def main():
    local = "--html" in sys.argv
    if local: page = open(sys.argv[sys.argv.index("--html") + 1], encoding="utf-8").read()
    else:
        req = urllib.request.Request(f"https://t.me/s/{CHANNEL}", headers={"User-Agent": "Mozilla/5.0 (UAC site feed)"})
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    items, seen = build(page)
    if not items:
        print(f"no posts parsed ({seen} messages seen); feed left unchanged"); sys.exit(1)
    img_dir = os.path.join(ROOT, "assets", "news"); wanted = set()
    for it in items:
        src = it.pop("img_src"); it.pop("ts"); it.pop("cyr"); it["img"] = ""
        if local or not src: continue
        name = f"{it['id']}.jpg"; path = os.path.join(img_dir, name); wanted.add(name)
        try:
            if not os.path.exists(path):
                os.makedirs(img_dir, exist_ok=True)
                data = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
                if len(data) < 2000 or len(data) > 3_000_000: raise ValueError("unexpected image size")
                open(path, "wb").write(data)
            it["img"] = f"assets/news/{name}"
        except Exception as e: print("image skipped", it["id"], e)
    if not local and os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            if f.endswith(".jpg") and f not in wanted: os.remove(os.path.join(img_dir, f))
    out = "/* Generated by tools/tg_feed.py from t.me/s/%s. Do not edit by hand. */\nwindow.NEWS_UAC=%s;\n" % (CHANNEL, json.dumps(items, ensure_ascii=False, indent=1))
    dest = os.path.join(ROOT, "news-uac.js")
    if "--out" in sys.argv: dest = sys.argv[sys.argv.index("--out") + 1]
    open(dest, "w", encoding="utf-8").write(out)
    print(f"{len(items)} posts written from {seen} messages")

if __name__ == "__main__": main()
