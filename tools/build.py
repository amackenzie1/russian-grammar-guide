# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown>=3.5"]
# ///
"""Compile parts/**/*.md into one standalone guide.html.

Usage: uv run tools/build.py [output.html]
"""
import base64
import html
import os
import re
import urllib.parse
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
TITLE = "A Guide to Russian Grammar"
REPO = "https://github.com/amackenzie1/russian-grammar-guide"

PARTS = {
    "00": ("Introduction", "What this guide is and how to use it."),
    "01": ("Sounds and Letters", "Reading Cyrillic, hard and soft consonants, stress, and the spelling rules that shape every ending."),
    "02": ("First Sentences", "Real sentences from day one: no “to be”, gender, plurals, adjectives, and verbs in the present and past."),
    "03": ("Cases", "The heart of Russian: how the ending of a word says what it is doing in the sentence."),
    "04": ("The Verb System", "Aspect, conjugation, commands, reflexive verbs, “would”, and the words for can, must and need."),
    "05": ("Motion, Space, Time and Number", "Going and carrying, where and where to, verbal prefixes, counting, clock time and dates."),
    "06": ("Bigger Sentences", "Joining clauses, reported speech, который, negation, comparison, and sentences with no subject."),
    "07": ("Real Spoken Russian", "Names and address, particles, diminutives, hedges, feelings, slang and everyday formulas."),
    "08": ("Written and Formal Russian", "Participles, verbal adverbs, officialese, declining numbers, word formation and advanced patterns."),
    "09": ("Reference", "Complete tables to look things up in."),
}

# ★ Particularly important: the sections a beginner should read first.
FIRST_PASS = set(
    """
    s-00-01
    s-01-01 s-01-02 s-01-03 s-01-05 s-01-07
    s-02-01 s-02-02 s-02-03 s-02-04 s-02-05 s-02-06 s-02-07 s-02-08 s-02-09
    s-03-01 s-03-02 s-03-03 s-03-04 s-03-05 s-03-06 s-03-10
    s-04-01 s-04-02 s-04-05 s-04-08
    s-05-01 s-05-02 s-05-07 s-05-08
    s-06-01
    s-07-01 s-07-08
    """.split()
)
# ☺ Particularly fun: the sections people read for pleasure.
FUN = set("s-01-06 s-02-09 s-03-11 s-05-05 s-05-06 s-07-01 s-07-02 s-07-04 s-07-07 s-07-09 s-08-07".split())
STAR, SMILE = "★", "☺\ufe0e"


def marks(sid, long=False):
    out = ""
    if sid in FIRST_PASS:
        out += f'<span class="mk star" title="Particularly important">{STAR}{" Particularly important" if long else ""}</span>'
    if sid in FUN:
        out += f'<span class="mk fun" title="Particularly fun">{SMILE}{" Particularly fun" if long else ""}</span>'
    return out


def level(sid):
    return 1 if sid in FIRST_PASS else 2


NS = re.compile(r"\[\[ns:\s?(.*?)\]\]", re.S)
LINE_KINDS = {"ex", "vocab", "dialogue"}
CALLOUT_LABEL = {"note": "Note", "warn": "Watch out", "aside": "Aside", "summary": "In short"}


def inline(s):
    """Escape, then apply **bold** / *italic* / [[ns]] inside line-block fields."""
    s = html.escape(s.strip(), quote=False)
    s = re.sub(r"\[([^\]]+)\]\((#[\w-]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", s)
    return s


def md(text):
    out = markdown.markdown(text, extensions=["tables", "sane_lists"])
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out


def render_line_block(kind, lines):
    rows = []
    for line in lines:
        if not line.strip():
            continue
        f = [inline(x) for x in re.sub(r"\s*\|$", "", line.strip()).split(" | ")]
        f += [""] * (3 - len(f))
        if kind == "ex":
            lit = f'<div class="lit">{f[2]}</div>' if f[2] else ""
            rows.append(f'<div class="row"><div class="ru">{f[0]}</div><div class="en">{f[1]}</div>{lit}</div>')
        elif kind == "vocab":
            note = f' <span class="vnote">{f[2]}</span>' if f[2] else ""
            rows.append(f'<div class="vrow"><span class="ru">{f[0]}</span><span class="en">{f[1]}{note}</span></div>')
        else:
            m = re.match(r"([^:]{1,24}):\s+(.*)", f[0], re.S)
            who, ru = (m.group(1), m.group(2)) if m else ("", f[0])
            lit = f'<div class="lit">{f[2]}</div>' if f[2] else ""
            rows.append(
                f'<div class="row"><div class="who">{who}</div><div class="line"><div class="ru">{ru}</div>'
                f'<div class="en">{f[1]}</div>{lit}</div></div>'
            )
    label = {"vocab": '<div class="block-label">Vocabulary</div>'}.get(kind, "")
    return f'<div class="{kind}">{label}{"".join(rows)}</div>'


def render_section(text, sid, number, relpath=""):
    text = NS.sub(lambda m: m.group(1), text)
    lines = text.split("\n")
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else sid
    body, buf, block = [], [], None

    def flush():
        if buf:
            chunk = "\n".join(buf)
            # demote headings: ## -> h3, ### -> h4
            chunk = re.sub(r"^(#{2,5}) ", lambda m: "#" * (len(m.group(1)) + 1) + " ", chunk, flags=re.M)
            body.append(md(chunk))
            buf.clear()

    for line in lines[1:]:
        s = line.strip()
        if block is None:
            if s.startswith(":::") and s != ":::":
                flush()
                kind, _, rest = s[3:].partition(" ")
                block = (kind, rest.strip(), [])
            else:
                buf.append(line)
        else:
            if s == ":::":
                kind, btitle, content = block
                if kind in LINE_KINDS:
                    body.append(render_line_block(kind, content))
                elif kind == "cursive":
                    body.append(render_cursive(btitle, content))
                elif kind == "keyboard":
                    body.append(render_keyboard(content))
                elif kind == "figure":
                    body.append(render_figure(btitle, content))
                else:
                    label = html.escape(btitle) if btitle else CALLOUT_LABEL.get(kind, kind.title())
                    inner = "\n".join(content)
                    body.append(
                        f'<aside class="callout {html.escape(kind)}"><div class="callout-title">{label}</div>'
                        f"{render_blocks_inside(inner)}</aside>"
                    )
                block = None
            else:
                block[2].append(line)
    if block is not None:
        raise SystemExit(f"{sid}: unclosed block '{block[0]}'")
    flush()
    num = f'<span class="num">{number}</span> ' if number else ""
    label = f"{number} {title}".strip()
    issue = f"{REPO}/issues/new?" + urllib.parse.urlencode({"template": "correction.yml", "title": f"[{label}] ", "section": label})
    idea = f"{REPO}/issues/new?" + urllib.parse.urlencode({"template": "suggestion.yml", "title": f"[{label}] ", "section": label})
    fix = (
        f'<p class="fixme">Spotted a mistake in this section? <a href="{html.escape(issue)}">Report it</a>. '
        f'Think it should be explained differently, reordered, expanded or cut? '
        f'<a href="{html.escape(idea)}">Suggest a change</a>, or <a href="{REPO}/edit/main/{relpath}">edit the source</a> on GitHub.</p>'
    )
    return title, f'<section class="sec" id="{sid}" data-lv="{level(sid)}" data-title="{html.escape(title)}"><h2>{num}{html.escape(title)}</h2>{"".join(body)}{fix}</section>'


def render_cursive(mode, lines):
    """Show text in print, italic and a cursive face. `grid` mode makes one small card per line."""
    rows = [[inline(x) for x in l.strip().split(" | ")] for l in lines if l.strip()]
    if mode.strip() == "grid":
        cards = "".join(
            f'<div class="lcard"><span class="lp">{r[0]}</span><span class="li">{r[0]}</span><span class="lc">{r[0]}</span></div>'
            for r in rows
        )
        head = '<div class="lcard lhead"><span class="lp">print</span><span class="li">italic</span><span class="lc2">handwritten</span></div>'
        return f'<div class="lgrid">{head}{cards}</div>'
    out = ['<div class="crow chead"><span>Print</span><span>Italic</span><span>Handwritten</span><span></span></div>']
    for r in rows:
        note = r[1] if len(r) > 1 else ""
        out.append(
            f'<div class="crow"><span class="lp">{r[0]}</span><span class="li">{r[0]}</span>'
            f'<span class="lc">{r[0]}</span><span class="en">{note}</span></div>'
        )
    return f'<div class="cursive">{"".join(out)}</div>'


def render_keyboard(lines):
    """Each line is a keyboard row of tokens like й:q (Cyrillic letter : Latin legend of the same key)."""
    rows = []
    for i, l in enumerate(x for x in lines if x.strip()):
        keys = []
        for tok in l.split():
            ru, _, lat = tok.partition(":")
            keys.append(f'<span class="key"><b>{html.escape(ru)}</b><i>{html.escape(lat)}</i></span>')
        rows.append(f'<div class="krow k{i}">{"".join(keys)}</div>')
    return f'<div class="keyboard" role="img" aria-label="Russian keyboard layout">{"".join(rows)}</div>'


def render_figure(name, lines):
    svg = (ROOT / "assets" / "figures" / f"{name.strip()}.svg").read_text(encoding="utf-8").strip()
    cap = md("\n".join(lines).strip())
    return f'<figure class="fig">{svg}<figcaption>{cap}</figcaption></figure>'


def render_blocks_inside(text):
    return md(text)


def collect():
    parts = []
    for d in sorted((ROOT / "parts").iterdir()):
        if not d.is_dir():
            continue
        pp = d.name[:2]
        secs = []
        for f in sorted(d.glob("*.md")):
            nn = f.name[:2]
            sid = f"s-{pp}-{nn}"
            number = "" if pp == "00" else f"{int(pp)}.{int(nn)}"
            title, sec_html = render_section(f.read_text(encoding="utf-8"), sid, number, f.relative_to(ROOT).as_posix())
            secs.append((sid, number, title, sec_html))
        if secs:
            parts.append((pp, secs))
    return parts


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "guide.html"
    parts = collect()
    ids = {sid for _, secs in parts for sid, *_ in secs}
    nav, home, sections = [], [], []
    for pp, secs in parts:
        ptitle, pdesc = PARTS.get(pp, (pp, ""))
        plabel = "" if pp == "00" else f"Part {int(pp)}"
        items = "".join(
            f'<li><a href="#{sid}"><span class="num">{number}</span><span class="ttl">{html.escape(title)}{marks(sid)}</span></a></li>'
            for sid, number, title, _ in secs
        )
        nav.append(
            f'<details class="navpart" data-part="{pp}"><summary><span class="plabel">{plabel}</span>{html.escape(ptitle)}</summary><ul>{items}</ul></details>'
        )
        home.append(
            f'<div class="homepart"><h3><span class="plabel">{plabel}</span>{html.escape(ptitle)}</h3><p>{html.escape(pdesc)}</p><ol>{items}</ol></div>'
        )
        for sid, number, title, sec_html in secs:
            crumb = (
                f'<div class="crumb">{plabel + " · " if plabel else ""}{html.escape(ptitle)}'
                f'{marks(sid, long=True)}</div>'
            )
            sections.append(sec_html.replace("<h2>", crumb + "<h2>", 1))
    body = "".join(sections)
    broken = sorted({m for m in re.findall(r'href="#(s-\d\d-\d\d)"', body) if m not in ids})
    if broken:
        print("WARNING: links to missing sections:", ", ".join(broken))
    ph_key = os.environ.get("GUIDE_POSTHOG_KEY", "").strip()
    analytics = ANALYTICS.replace("__KEY__", ph_key) if ph_key else ""
    font = base64.b64encode((ROOT / "assets" / "fonts" / "MarckScript-Regular.ttf").read_bytes()).decode()
    page = (
        TEMPLATE.replace("{{ANALYTICS}}", analytics).replace("{{CURSIVE_FONT}}", font).replace("{{TITLE}}", TITLE)
        .replace("{{REPO}}", REPO)
        .replace("{{NAV}}", "".join(nav))
        .replace("{{HOME}}", "".join(home))
        .replace("{{SECTIONS}}", body)
    )
    out.write_text(page, encoding="utf-8")
    n_secs = sum(len(s) for _, s in parts)
    print(f"wrote {out} — {len(parts)} parts, {n_secs} sections, {len(page) / 1e6:.2f} MB")


ANALYTICS = r"""<script>
/* PostHog: pageviews per section (hash changes), link clicks, page leave */
!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once unregister identify alias set_config reset opt_in_capturing opt_out_capturing has_opted_out_capturing get_distinct_id get_property".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
posthog.init("__KEY__", {
  api_host: "https://us.i.posthog.com",
  defaults: "2025-05-24",
  person_profiles: "identified_only",
  autocapture: { element_allowlist: ["a", "button"], dom_event_allowlist: ["click"] },
  capture_pageleave: true,
});
posthog.register({ site: "andrew.ma", guide: "russian" });
// sections are hash routes, which PostHog does not count as pageviews: one event per section opened
(function () {
  function seen() {
    var id = location.hash.slice(1), sec = id && document.getElementById(id);
    if (!sec || !/^s-\d\d-\d\d$/.test(id)) return;
    var h = sec.querySelector("h2");
    posthog.capture("guide_section_viewed", { section: id, section_title: h ? h.textContent.trim() : "" });
  }
  window.addEventListener("hashchange", seen);
  window.addEventListener("DOMContentLoaded", seen);
})();
</script>
"""

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<meta name="description" content="A free, book-length Russian grammar for English speakers, in the spirit of Tae Kim’s guide to Japanese: Russian explained on its own terms, from the alphabet to officialese. Written by Claude Fable 5.2.">
<meta name="author" content="Claude Fable 5.2 (Anthropic)">
<style>
/* Marck Script by Denis Masharov and Marck Fogel, SIL Open Font License 1.1 (assets/fonts/MarckScript-OFL.txt) */
@font-face { font-family: "Guide Cursive"; src: url(data:font/ttf;base64,{{CURSIVE_FONT}}) format("truetype"); font-display: swap; }
:root {
  --paper: #faf6ef; --panel: #f1ebe0; --ink: #221d17; --muted: #6f6558; --rule: #ddd3c3;
  --accent: #a8322a; --accent-soft: #f3dcd6; --blue: #23557a; --blue-soft: #dfeaf2;
  --gold-soft: #f6ecc9; --green-soft: #e1ecdc; --card: #fffdf9;
  --serif: "PT Serif", "Charter", "Georgia", "Times New Roman", serif;
  --sans: "PT Sans", -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #1b1917; --panel: #23201d; --ink: #ebe4d8; --muted: #a39a8c; --rule: #3a3530;
    --accent: #e98274; --accent-soft: #46271f; --blue: #8dbbe0; --blue-soft: #1f3445;
    --gold-soft: #3d3620; --green-soft: #24341f; --card: #211e1b;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--serif); font-size: 18px; line-height: 1.62; }
a { color: var(--blue); text-decoration-thickness: 1px; text-underline-offset: 2px; }
.layout { display: grid; grid-template-columns: 320px minmax(0, 1fr); min-height: 100vh; }
nav.side { position: sticky; top: 0; height: 100vh; overflow-y: auto; background: var(--panel); border-right: 1px solid var(--rule); padding: 20px 16px 40px; font-family: var(--sans); font-size: 15px; }
nav.side .brand { display: block; font-family: var(--serif); font-weight: 700; font-size: 20px; line-height: 1.25; color: var(--ink); text-decoration: none; margin: 4px 6px 4px; }
nav.side .brand small { display: block; font-family: var(--sans); font-weight: 400; font-size: 13px; color: var(--muted); margin-top: 4px; }
.search { width: 100%; margin: 14px 0 6px; padding: 8px 10px; font: inherit; border: 1px solid var(--rule); border-radius: 6px; background: var(--card); color: var(--ink); }
.toggles { display: flex; flex-wrap: wrap; gap: 6px 14px; margin: 6px 4px 14px; color: var(--muted); font-size: 13.5px; }
.toggles label { cursor: pointer; white-space: nowrap; }
.navpart { border-top: 1px solid var(--rule); }
.navpart summary { cursor: pointer; padding: 9px 6px; font-weight: 700; list-style: none; }
.navpart summary::-webkit-details-marker { display: none; }
.plabel { display: block; font-size: 11.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
.navpart ul { list-style: none; margin: 0 0 10px; padding: 0; }
.mk { margin-left: 6px; font-family: var(--sans); font-weight: 700; white-space: nowrap; }
.mk.star { color: var(--accent); }
.mk.fun { color: var(--blue); }
.navpart li a.active .mk { color: #fff; }
.crumb .mk { margin-left: 12px; letter-spacing: .04em; }
.passes { margin-top: 12px; }
.passes b { color: var(--ink); }
.passes .mk { margin: 0 2px 0 0; }
.navpart li a { display: flex; gap: 8px; padding: 4px 6px; border-radius: 5px; color: var(--ink); text-decoration: none; line-height: 1.3; }
.navpart li a:hover { background: var(--rule); }
.navpart li a.active { background: var(--accent); color: #fff; }
.navpart li a.active .num { color: #fff; }
.num { color: var(--muted); font-variant-numeric: tabular-nums; min-width: 2.1em; flex: none; }
#results { list-style: none; margin: 0 0 12px; padding: 0; }
#results li a { display: block; padding: 6px; border-radius: 5px; color: var(--ink); text-decoration: none; line-height: 1.3; }
#results li a:hover { background: var(--rule); }
#results .snip { display: block; color: var(--muted); font-size: 13px; }
#results mark { background: var(--gold-soft); color: inherit; }
main { padding: 36px 48px 120px; min-width: 0; }
.col { max-width: 800px; margin: 0 auto; }
.menu-btn { display: none; }
h1 { font-size: 46px; line-height: 1.1; margin: 30px 0 10px; letter-spacing: -.01em; }
.sub { font-size: 21px; color: var(--muted); margin: 0 0 30px; }
.crumb { font-family: var(--sans); font-size: 13px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); margin-top: 10px; }
section.sec h2 { font-size: 36px; line-height: 1.15; margin: 4px 0 26px; padding-bottom: 14px; border-bottom: 2px solid var(--ink); }
section.sec h2 .num { color: var(--muted); font-weight: 400; margin-right: 6px; }
h3 { font-size: 25px; line-height: 1.25; margin: 44px 0 10px; }
h4 { font-size: 19px; margin: 30px 0 6px; font-family: var(--sans); }
p { margin: 0 0 16px; }
ul, ol { padding-left: 1.3em; margin: 0 0 16px; }
li { margin-bottom: 5px; }
strong, b { font-weight: 700; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 32px 0; }
.table-wrap { overflow-x: auto; margin: 18px 0 22px; }
table { border-collapse: collapse; font-family: var(--sans); font-size: 16px; line-height: 1.4; min-width: 50%; }
th, td { border-bottom: 1px solid var(--rule); padding: 7px 14px 7px 10px; text-align: left; vertical-align: top; }
thead th { border-bottom: 2px solid var(--ink); font-size: 13.5px; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); white-space: nowrap; }
tbody tr:hover { background: var(--panel); }
td strong { color: var(--accent); }
.ex, .dialogue { margin: 18px 0 24px; border-left: 3px solid var(--accent); background: var(--card); border-radius: 0 8px 8px 0; padding: 6px 18px; box-shadow: 0 1px 0 var(--rule); }
.dialogue { border-left-color: var(--blue); }
.ex .row, .dialogue .row { padding: 9px 0; border-bottom: 1px dashed var(--rule); }
.ex .row:last-child, .dialogue .row:last-child { border-bottom: 0; }
.ru { font-size: 20px; line-height: 1.4; }
.ex .ru b, .dialogue .ru b { color: var(--accent); }
.en { color: var(--muted); font-family: var(--sans); font-size: 15.5px; }
.lit { color: var(--muted); font-family: var(--sans); font-size: 14px; font-style: italic; opacity: .9; }
.lit::before { content: "↳ "; font-style: normal; }
.dialogue .row { display: grid; grid-template-columns: auto 1fr; gap: 12px; }
.dialogue .who { font-family: var(--sans); font-weight: 700; font-size: 14px; color: var(--blue); padding-top: 5px; min-width: 1.6em; }
.vocab { margin: 18px 0 24px; padding: 12px 18px 14px; background: var(--panel); border-radius: 8px; columns: 2 300px; column-gap: 34px; }
.block-label { font-family: var(--sans); font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); column-span: all; margin-bottom: 6px; }
.vrow { display: flex; gap: 10px; align-items: baseline; break-inside: avoid; padding: 2px 0; }
.vrow .ru { font-size: 18px; font-weight: 700; flex: none; }
.vnote { font-style: italic; opacity: .85; }
.vnote::before { content: "· "; font-style: normal; }
.callout { margin: 22px 0; padding: 14px 20px 4px; border-radius: 8px; background: var(--blue-soft); font-size: 17px; }
.callout.warn { background: var(--accent-soft); }
.callout.aside { background: var(--panel); }
.callout.summary { background: var(--green-soft); }
.callout-title { font-family: var(--sans); font-size: 13px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; margin-bottom: 6px; }
.callout.warn .callout-title { color: var(--accent); }
.callout.note .callout-title { color: var(--blue); }
.callout table { background: transparent; }
.lp { font-family: var(--serif); }
.li { font-family: var(--serif); font-style: italic; }
.lc { font-family: "Guide Cursive", cursive; }
.cursive { margin: 18px 0 24px; background: var(--card); border-radius: 8px; padding: 6px 18px; box-shadow: 0 1px 0 var(--rule); overflow-x: auto; }
.crow { display: grid; grid-template-columns: minmax(110px, 1fr) minmax(110px, 1fr) minmax(130px, 1.2fr) 1.4fr; gap: 6px 22px; align-items: baseline; padding: 8px 0; border-bottom: 1px dashed var(--rule); min-width: 520px; }
.crow:last-child { border-bottom: 0; }
.crow .lp, .crow .li { font-size: 22px; }
.crow .lc { font-size: 31px; line-height: 1.15; }
.chead, .lhead { font-family: var(--sans); font-size: 12px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }
.lgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 8px; margin: 18px 0 24px; }
.lcard { display: flex; flex-direction: column; align-items: center; gap: 2px; background: var(--card); border: 1px solid var(--rule); border-radius: 8px; padding: 8px 4px 10px; }
.lcard .lp, .lcard .li { font-size: 20px; line-height: 1.3; }
.lcard .lc { font-size: 34px; line-height: 1.2; color: var(--accent); }
.lcard.lhead { justify-content: space-around; text-transform: none; letter-spacing: 0; font-weight: 400; font-size: 12.5px; }
.lcard.lhead .lp, .lcard.lhead .li { font-size: 13px; font-family: var(--sans); }
.lcard.lhead .li { font-style: italic; }
.lcard.lhead .lc2 { color: var(--accent); }
.keyboard { margin: 20px 0 24px; overflow-x: auto; padding-bottom: 4px; }
.krow { display: flex; gap: 5px; margin-bottom: 5px; }
.krow.k1 { margin-left: 68px; } .krow.k2 { margin-left: 82px; } .krow.k3 { margin-left: 108px; }
.key { position: relative; flex: none; width: 46px; height: 46px; border: 1px solid var(--rule); border-bottom-width: 3px; border-radius: 7px; background: var(--card); }
.key b { position: absolute; left: 9px; bottom: 3px; font: 700 21px var(--sans); color: var(--ink); }
.key i { position: absolute; right: 6px; top: 3px; font: 400 11.5px var(--sans); color: var(--muted); text-transform: uppercase; }
.fig { margin: 26px 0; }
.fig svg { display: block; width: 100%; height: auto; }
.fig figcaption { font-family: var(--sans); font-size: 14.5px; color: var(--muted); margin-top: 8px; }
.fig figcaption p { margin: 0; }
.fig .f-ru { font: 700 21px var(--serif); fill: var(--ink); }
.fig .f-ru2 { font: 400 17px var(--serif); fill: var(--ink); }
.fig .f-en { font: 400 14px var(--sans); fill: var(--muted); }
.fig .f-lab { font: 700 11.5px var(--sans); letter-spacing: .09em; fill: var(--accent); }
.fig .f-pre { font: 700 20px var(--serif); fill: var(--accent); }
.fig .f-line { stroke: var(--rule); stroke-width: 2; fill: none; }
.fig .f-ink { stroke: var(--ink); stroke-width: 1.6; fill: none; }
.fig .f-box { fill: var(--panel); stroke: var(--ink); stroke-width: 1.6; }
.fig .f-acc { stroke: var(--accent); stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.fig .f-dash { stroke-dasharray: 2 7; }
.fig .f-accfill { fill: var(--accent); }
.fig .f-inkfill { fill: var(--ink); }
.fig .f-cell { fill: var(--card); stroke: var(--rule); stroke-width: 1; }
.invite { margin-top: 12px; }
.invite b { color: var(--ink); }
.fixme { font-family: var(--sans); font-size: 14px; color: var(--muted); margin: 44px 0 0; padding-top: 14px; border-top: 1px solid var(--rule); }
.pager { display: flex; justify-content: space-between; gap: 20px; margin-top: 60px; padding-top: 20px; border-top: 1px solid var(--rule); font-family: var(--sans); font-size: 16px; }
.pager a { text-decoration: none; max-width: 48%; }
.pager a span { display: block; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.pager .next { text-align: right; margin-left: auto; }
.homegrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 8px 44px; margin-top: 30px; }
.homepart h3 { font-size: 23px; margin: 26px 0 4px; }
.homepart p { color: var(--muted); font-size: 16px; margin-bottom: 8px; }
.homepart ol { list-style: none; padding: 0; font-family: var(--sans); font-size: 16px; }
.homepart li a { display: flex; gap: 8px; text-decoration: none; padding: 2px 0; }
.homepart li a:hover { text-decoration: underline; }
.byline { font-family: var(--sans); font-size: 15px; color: var(--muted); border-left: 3px solid var(--rule); padding-left: 14px; margin: 26px 0 0; max-width: 640px; }
.navnote { font-size: 12.5px; color: var(--muted); margin: 18px 6px 0; padding-top: 12px; border-top: 1px solid var(--rule); }
.start { display: inline-block; font-family: var(--sans); font-weight: 700; background: var(--accent); color: #fff; padding: 11px 20px; border-radius: 7px; text-decoration: none; margin-right: 12px; }
body.paged section.sec, body.paged #home { display: none; }
body.paged section.sec.current, body.paged #home.current { display: block; }
body.hide-en .ex .en, body.hide-en .dialogue .en, body.hide-en .ex .lit, body.hide-en .dialogue .lit { filter: blur(5px); cursor: pointer; transition: filter .15s; }
body.hide-en .row:hover .en, body.hide-en .row:hover .lit, body.hide-en .row.show .en, body.hide-en .row.show .lit { filter: none; }
@media (max-width: 900px) {
  .layout { display: block; }
  nav.side { position: fixed; z-index: 10; width: min(86vw, 340px); transform: translateX(-102%); transition: transform .2s; box-shadow: 0 0 40px rgba(0,0,0,.3); }
  body.nav-open nav.side { transform: none; }
  .menu-btn { display: inline-block; position: fixed; z-index: 11; right: 14px; bottom: 14px; font: 700 15px var(--sans); background: var(--ink); color: var(--paper); border: 0; border-radius: 22px; padding: 11px 18px; }
  main { padding: 20px 18px 110px; }
  h1 { font-size: 36px; } section.sec h2 { font-size: 29px; }
}
@media print {
  nav.side, .menu-btn, .pager, .start, .fixme { display: none !important; }
  .layout { display: block; } main { padding: 0; }
  body { font-size: 11.5pt; background: #fff; }
  body.paged section.sec, body.paged #home { display: block; }
  section.sec { break-before: page; }
  .ex, .dialogue, .callout, .vrow, tr { break-inside: avoid; }
}
</style>
{{ANALYTICS}}</head>
<body>
<div class="layout">
<nav class="side" id="side">
  <a class="brand" href="#home">{{TITLE}}<small>Russian explained on its own terms</small></a>
  <input class="search" id="search" type="search" placeholder="Search the guide…" autocomplete="off">
  <ul id="results"></ul>
  <div class="toggles">
    <label><input type="checkbox" id="t-stress" checked> stress marks</label>
    <label><input type="checkbox" id="t-en" checked> translations</label>
    <label><input type="checkbox" id="t-all"> one long page</label>
    <label title="Previous and Next step through the ★ sections only"><input type="checkbox" id="t-lv"> ★ route</label>
  </div>
  <div id="navparts">{{NAV}}</div>
  <p class="navnote">Written by Claude Fable 5.2 (Anthropic), November 2026. <a href="{{REPO}}">Source and corrections on GitHub</a>.</p>
</nav>
<main><div class="col">
  <div id="home">
    <h1>{{TITLE}}</h1>
    <p class="sub">Russian explained on its own terms, from the alphabet to officialese — in the spirit of <a href="https://www.guidetojapanese.org/grammar_guide.pdf">Tae Kim’s guide to Japanese</a>.</p>
    <p><a class="start" href="#s-00-01">Start reading</a> <a href="#s-01-01">Skip to the alphabet</a></p>
    <p class="byline">Written by Claude Fable 5.2, an AI model made by Anthropic, in November 2026. Every part was independently re-read and the stress marks were checked against a dictionary. A native speaker has read much of it, though not every section, and found that it holds up. The <a href="{{REPO}}">source is open</a>.</p>
    <p class="byline invite"><b>Help shape it.</b> This guide is meant to be argued with. If something is wrong, tell us. If something is missing, badly explained, in the wrong order, or not worth the space it takes, tell us that too: <a href="{{REPO}}/issues/new/choose">open an issue on GitHub</a>, or use the links at the bottom of any section. Suggestions about structure are as welcome as corrections.</p>
    <p class="byline passes"><b>New to Russian? Don’t read it all.</b>
      <span class="mk star">★</span> marks the sections that are particularly important: about thirty of them, enough to read, make sentences and understand what cases and aspect are for. Read those first.
      <span class="mk fun">☺︎</span> marks the ones that are particularly fun. Tick “★ route” in the sidebar and the Next link will take you through the starred sections only.</p>
    <div class="homegrid">{{HOME}}</div>
  </div>
  {{SECTIONS}}
  <div class="pager" id="pager"></div>
</div></main>
</div>
<button class="menu-btn" id="menu-btn">Contents</button>
<script>
(function () {
  var secs = Array.prototype.slice.call(document.querySelectorAll('section.sec'));
  var home = document.getElementById('home');
  var pager = document.getElementById('pager');
  var navLinks = {};
  document.querySelectorAll('#navparts a').forEach(function (a) { navLinks[a.getAttribute('href').slice(1)] = a; });
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var allMode = store.get('rg-all') === '1';
  var lvFilter = store.get('rg-lv') === '1' ? 1 : 0;

  function show(id, scroll) {
    var target = document.getElementById(id);
    var sec = target && target.closest ? (target.closest('section.sec') || (id === 'home' ? home : null)) : null;
    if (!sec) { sec = home; id = 'home'; }
    document.body.classList.toggle('paged', !allMode);
    secs.concat([home]).forEach(function (s) { s.classList.toggle('current', s === sec); });
    Object.keys(navLinks).forEach(function (k) { navLinks[k].classList.toggle('active', k === sec.id); });
    if (navLinks[sec.id]) { var d = navLinks[sec.id].closest('details'); d.open = true; if (navLinks[sec.id].scrollIntoView) navLinks[sec.id].scrollIntoView({ block: 'nearest' }); }
    var i = secs.indexOf(sec), h = '';
    if (!allMode) {
      // with a reading pass chosen, Previous and Next step through that pass only
      var inPass = function (s) { return !lvFilter || s.dataset.lv === '1'; };
      var p = i - 1, n = i + 1;
      while (p >= 0 && !inPass(secs[p])) p--;
      while (n < secs.length && !inPass(secs[n])) n++;
      var passNote = lvFilter ? ' ★' : '';
      if (i > 0 && p >= 0) h += '<a class="prev" href="#' + secs[p].id + '"><span>← Previous' + passNote + '</span>' + secs[p].dataset.title + '</a>';
      if (i === 0 || (i > 0 && p < 0)) h += '<a class="prev" href="#home"><span>← Back</span>Contents</a>';
      if (i >= 0 && n < secs.length) h += '<a class="next" href="#' + secs[n].id + '"><span>Next' + passNote + ' →</span>' + secs[n].dataset.title + '</a>';
    }
    pager.innerHTML = h;
    document.title = (sec === home ? '' : sec.dataset.title + ' — ') + '{{TITLE}}';
    document.body.classList.remove('nav-open');
    if (scroll !== false) { if (allMode && sec !== home) sec.scrollIntoView(); else window.scrollTo(0, 0); }
    store.set('rg-last', sec.id);
  }
  function route(scroll) { show(decodeURIComponent(location.hash.slice(1)) || 'home', scroll); }
  window.addEventListener('hashchange', function () { route(); });

  // toggles
  var tStress = document.getElementById('t-stress'), tEn = document.getElementById('t-en'), tAll = document.getElementById('t-all');
  var originals = null;
  function applyStress() {
    var content = document.querySelector('main');
    if (!originals) {
      originals = [];
      var w = document.createTreeWalker(content, NodeFilter.SHOW_TEXT), n;
      while ((n = w.nextNode())) if (n.nodeValue.indexOf('́') !== -1) originals.push([n, n.nodeValue]);
    }
    originals.forEach(function (p) { p[0].nodeValue = tStress.checked ? p[1] : p[1].replace(/́/g, ''); });
    store.set('rg-stress', tStress.checked ? '1' : '0');
  }
  tStress.addEventListener('change', applyStress);
  if (store.get('rg-stress') === '0') { tStress.checked = false; applyStress(); }
  function applyEn() { document.body.classList.toggle('hide-en', !tEn.checked); store.set('rg-en', tEn.checked ? '1' : '0'); }
  tEn.addEventListener('change', applyEn);
  if (store.get('rg-en') === '0') { tEn.checked = false; applyEn(); }
  document.addEventListener('click', function (e) {
    var row = e.target.closest && e.target.closest('.row');
    if (row && document.body.classList.contains('hide-en')) row.classList.toggle('show');
  });
  var tLv = document.getElementById('t-lv');
  function applyLv() { tLv.checked = !!lvFilter; }
  tLv.addEventListener('change', function () { lvFilter = tLv.checked ? 1 : 0; store.set('rg-lv', String(lvFilter)); applyLv(); route(false); });
  applyLv();
  tAll.checked = allMode;
  tAll.addEventListener('change', function () { allMode = tAll.checked; store.set('rg-all', allMode ? '1' : '0'); route(); });
  document.getElementById('menu-btn').addEventListener('click', function () { document.body.classList.toggle('nav-open'); });

  // search
  function norm(s) { return s.toLowerCase().replace(/́/g, '').replace(/ё/g, 'е'); }
  var index = null, input = document.getElementById('search'), results = document.getElementById('results');
  function esc(s) { return s.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
  input.addEventListener('input', function () {
    var q = norm(input.value.trim());
    if (q.length < 2) { results.innerHTML = ''; return; }
    if (!index) index = secs.map(function (s) { var raw = s.textContent.replace(/́/g, ''); return { id: s.id, title: s.dataset.title, raw: raw, text: norm(raw) }; });
    var hits = [];
    index.forEach(function (d) {
      var i = d.text.indexOf(q), count = 0, first = i;
      while (i !== -1) { count++; i = d.text.indexOf(q, i + q.length); }
      if (count) hits.push({ d: d, count: count + (norm(d.title).indexOf(q) !== -1 ? 1000 : 0), first: first });
    });
    hits.sort(function (a, b) { return b.count - a.count; });
    results.innerHTML = hits.slice(0, 12).map(function (h) {
      var a = Math.max(0, h.first - 30), snip = h.d.raw.slice(a, h.first + q.length + 50).replace(/\s+/g, ' ');
      var k = h.first - a;
      return '<li><a href="#' + h.d.id + '">' + esc(h.d.title) + '<span class="snip">…' + esc(snip.slice(0, k)) + '<mark>' + esc(snip.slice(k, k + q.length)) + '</mark>' + esc(snip.slice(k + q.length)) + '…</span></a></li>';
    }).join('') || '<li><a>No matches</a></li>';
  });

  route(false);
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
