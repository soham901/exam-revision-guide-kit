#!/usr/bin/env python3
"""Build a unit study guide PDF.

usage: build.py unitN.html out.pdf

The unit file is an HTML body fragment. Its first line must be:
  <!-- HDR: DISTRIBUTED OPERATING SYSTEM · UNIT 3 — SYNCHRONIZATION & NAMING -->
Sections:  <section class="sec" id="s3" data-title="Clock Synchronization"> ...
TOC page numbers: <span class="pg" data-sec="s3"></span>  (filled in pass 2)
Final page: <section class="rev30" id="rev30"> ... (must be the last element)
"""
import html, os, shutil, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME", "google-chrome")


def css_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def page_css(src):
    hdr = re.search(r"<!--\s*HDR:\s*(.*?)\s*-->", src).group(1)
    rules = [
        "@page { @top-left { content: %s; } }" % css_str(hdr),
    ]
    marker = ("font: 800 7.5pt 'Inter'; color:#0A0A0A; padding: 0 0 2mm;"
              "vertical-align: bottom; letter-spacing:.06em; border-bottom: 4pt solid #A3E635;")
    secs = re.findall(r'<section class="sec[^"]*" id="(s\d+)" data-title="([^"]*)"', src)
    for sid, title in secs:
        n = int(sid[1:])
        title = html.unescape(title)
        rules.append("#%s { page: %s; }" % (sid, sid))
        rules.append("@page %s { @top-right { content: %s; %s } }"
                     % (sid, css_str("§%d  %s" % (n, title.upper())), marker))
    rules.append("@page rev30 { @top-right { content: %s; %s } }"
                 % (css_str("30-SECOND REVISION"), marker))
    return "\n".join(rules), secs


def render(src, extra_css, out_pdf):
    css = open(os.path.join(HERE, "guide.css")).read()
    doc = ("<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Revision Guide</title>"
           "<style>%s\n%s</style></head><body>%s</body></html>" % (css, extra_css, src))
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=HERE, delete=False) as f:
        f.write(doc)
        tmp = f.name
    prof = tempfile.mkdtemp(prefix="chrome-", dir=HERE)
    try:
        subprocess.run([CHROME, "--headless=new", "--user-data-dir=" + prof, "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
                        "--print-to-pdf=" + os.path.abspath(out_pdf), "file://" + tmp],
                       check=True, capture_output=True)
    finally:
        os.unlink(tmp)
        shutil.rmtree(prof, ignore_errors=True)


def page_texts(pdf):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    return txt.split("\f")[:-1] if txt.endswith("\f") else txt.split("\f")


def main():
    unit, out = sys.argv[1], sys.argv[2]
    src = open(unit).read()
    extra, secs = page_css(src)
    render(src, extra, out)
    pages = page_texts(out)
    start = {}
    for sid, _ in secs:
        tok = r"§%d\s+\S" % int(sid[1:])
        for i, t in enumerate(pages):
            head = next((l for l in t.splitlines() if l.strip()), "")
            if i > 0 and re.search(tok, head):
                start[sid] = i + 1
                break
    start["rev30"] = next((i + 1 for i, t in enumerate(pages) if "30-SECOND REVISION" in t and i > 0), None)

    def fill(m):
        return m.group(1) + str(start.get(m.group(2), "?")) + m.group(3)
    src2 = re.sub(r'(<span class="pg" data-sec="([^"]+)">)[^<]*(</span>)', fill, src)
    src2 = re.sub(r'(<span class="ref" data-sec="([^"]+)">)[^<]*(</span>)',
                  lambda m: m.group(1) + "p.%s" % start.get(m.group(2), "?") + m.group(3), src2)
    render(src2, extra, out)
    pages = page_texts(out)

    # ---- QA ----
    print("pages:", len(pages))
    print("section starts:", start)
    rev_pages = [i + 1 for i, t in enumerate(pages) if "30-SECOND REVISION" in t and i > 0]
    print("30-second pages:", rev_pages, "(OK)" if rev_pages == [len(pages)] else "(PROBLEM: must be exactly the last page)")
    missing = [s for s, _ in secs if s not in start]
    if missing:
        print("PROBLEM: sections not found:", missing)
    fonts = subprocess.run(["pdffonts", out], capture_output=True, text=True).stdout
    print(fonts)


if __name__ == "__main__":
    main()
