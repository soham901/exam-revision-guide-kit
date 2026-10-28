# Exam Revision Guide Generator: Learnings & Playbook

These notes come from building five unit guides for a university Distributed Operating Systems (DOS) course (Oct 2026). Use them to make the same kind of guide for any other subject.

The toolkit sits next to this file:

| File | Purpose |
|---|---|
| `guide.css` | Shared design system: black, white and lime; Inter font; A4 portrait; all components |
| `build.py` | Two-pass Chrome render. It fills in contents page numbers, sets the running headers and section markers, and runs the QA checks |
| `preview.sh` | Renders every page as a PNG at 90 dpi and makes one contact-sheet image for visual QA |
| `sample.html` | Minimal skeleton that uses every component. Start each new unit from this file |

---

## 1. Workflow that worked

1. **Fill the placeholders first.** The prompt template had `[SUBJECT NAME]`, `[UNIT]`, `[LENGTH]` and `[ORIENTATION]` left blank. Ask once, in a single multi-question prompt, about:
   - which units
   - orientation and length (A4 portrait, "as long as needed" worked well)
   - whether to use the question bank and past papers for exam-frequency badges (yes, this is valuable)
2. **Extract all sources to text:**
   ```bash
   mkdir -p src && for f in *.pdf; do pdftotext -layout "$f" "src/${f%.pdf}.txt"; done
   ```
   Check the word count per unit. Slide decks that have few words but many pages are image-heavy (DOS U3 and U4 were 30–60 MB). For those, render individual slides and look at them:
   ```bash
   pdftoppm -r 70 -png -f N -l N deck.pdf img/s
   ```
3. **Build the design system and pipeline once, and test it on `sample.html`** before writing any content. Look at the rendered PNG of the sample page.
4. **Parallelise: one agent (fork) per unit.**
   - Each fork writes only its own `unitN.html`.
   - Forks must **not** edit `guide.css` or `build.py`. Unit-specific styling goes in a `<style>` block inside the unit file.
   - Each fork builds its PDF, looks at the PNGs, and fixes problems itself. It then reports back: output path, page count, section list, SOURCE UNCLEAR items, and anything it could not fix.
   - Timing for 5 units of 64–151 slides: about 10–18 minutes each, running in parallel.
5. **Final pass by the orchestrator:**
   - Rebuild all units with the final `build.py`.
   - Make one contact sheet of the cover, one content page and the last page of every PDF.
   - Spot-check it, then report.

## 2. Rendering stack (Linux)

- **Google Chrome headless** prints the PDF. WeasyPrint was not installed and wasn't needed. Chrome 131+ supports `@page` margin boxes (`@top-left`, `@bottom-right` with `counter(page)`) and **named pages** (`page: s3`).
- Command (as in `build.py`):
  ```bash
  google-chrome --headless=new --user-data-dir=<unique tmp> --no-pdf-header-footer \
    --run-all-compositor-stages-before-draw --virtual-time-budget=4000 --print-to-pdf=out.pdf file:///x.html
  ```
  **Give every parallel build its own `--user-data-dir`.** Without it, concurrent Chrome instances clash over the shared profile.
- `print-color-adjust: exact` is required, or Chrome drops the background fills.
- QA tools: `pdftotext` (detecting page starts), `pdffonts` (checking font embedding), `pdftoppm` + ImageMagick `montage` (visual contact sheet).

## 3. Design-system decisions

- **Palette:**
  - ink `#0A0A0A`
  - white
  - lime `#A3E635` for fills, large headings and markers
  - deep lime `#65A30D`, only for arrows and bullets that need contrast on white
  - lime tint `#ECFCCB` for soft boxes
  - grey `#F3F3F3` for table rows and `#D9D9D9` for hairlines
- **Lime is never used for small text on white.** Text on a lime fill is always black. The one inverse style is **lime text on a black fill** (labels, badges, mnemonic words); it reads well and is distinctive.
- **Fonts: use `Inter` only. Do not use `Inter Display`.** Inter Display is installed as OTF/CFF, and Chrome embeds it as **Type 3** fonts: `pdffonts` shows "Type 3" and Poppler warns "Bad bounding box". Inter (TTF) embeds as proper CID TrueType. Use heavy weights (800/900) of Inter for display text.
- Symbols such as ■ ✕ → ⚠ fall back to DejaVu Sans or Noto Math. That is acceptable, because those fonts are embedded too. Emoji ⚠️ is avoided: the trap icon is a CSS `clip-path` triangle with "!" in it (`.warn-ico`), so it is vector and uses only palette colours.
- **Section marker on every page:** `build.py` generates one named page per section. Each named page gets `@page sN { @top-right { content: "§N TITLE"; border-bottom: 4pt solid lime } }`. Named pages also force each section onto a new page.
- **Two section-marker styles were tried.** A tall lime background tab in the margin box looked heavy and ran into the non-printable area. A thick lime underline looks cleaner.
- The cover uses `@page cover`, which turns off the header and footer, **including the page-number box**. Remember to null `@bottom-right` as well.

## 4. Component vocabulary (classes in `guide.css`)

| Element | Class / markup |
|---|---|
| Cover | `.cover`, `.label`, `h1 .unit`, `ol.toc` with `<span class="pg" data-sec="sN">` |
| Section | `<section class="sec" id="sN" data-title="Title">` + `.sec-head` (`.num`, `h2`, `.kick`) |
| Template headings 1–9 | `<h3 class="sh" data-n="1">What is it?</h3>` |
| Definition | `.what` |
| Bullets | `ul.kp`; layout helpers `.cols2` / `.grid2` / `.grid3` |
| Steps | `.flow` (horizontal: `.step` + `.arr`), `.vflow` (vertical, numbered) |
| Terms | `dl.terms` |
| Comparison | plain `table`; `tr.key` highlights the key-difference row |
| Formula card | `.formula` > `.fh`, `.eq`, `.body` |
| Exam trap | `.trap` > `.th` (with `.warn-ico`) + `ul` |
| Mnemonic | `.mnem .m` > `.w` (word), `.x` (expansion) |
| Classification tree | `.tree` nested `ul` with `.node` / `.node.root` / `.node.l` |
| Quick check | `.qc` > `ol li` + `.a` (answer) |
| Badges | `.pyq` ("PYQ 7M", "QB 4M"), `.unclear` (SOURCE UNCLEAR), `.tag` |
| Final page | `<section class="rev30" id="rev30">` > `.rev-head` + `.rev` (2 columns, `h5` group labels, `.r` rows, `.r.trap-r`, `<span class="ref" data-sec="sN">` for page cross-refs) |

## 5. Pitfalls hit (and fixes)

1. **Section start detection:** `build.py` looks for `§N TITLE` in the PDF text. Originally it matched anywhere on the page, so:
   - a "§1" label on the cover concept map, or a "see §4" cross-reference in the body, produced wrong contents page numbers;
   - the regex `§N\s` failed because pdftotext collapses spaces.

   **Fixed:** it now matches `§N\s+\S` in the **first non-empty line (the running header) of pages after the cover**. Still, write in-body cross-references as "Sec 4" or use `.ref` spans.
2. **Forcing every section onto a new page creates large gaps.** Fixes used:
   - Merge thin source topics into one section (e.g. "Design Issues I & II", or small security sub-topics).
   - Rebalance content with `.cols2` / `.grid2`.

   Accept a part-filled *last* page of a multi-page section rather than padding or cramming it. The spec asks for no gaps over 25% of a page, which is not always achievable; report the exceptions honestly.
3. **SVG labels end up too small**, about 7pt, when a diagram is scaled to fit. Design SVGs with a `viewBox` close to the printed size (width ≈ 180 mm → `viewBox` width ≈ 510 px at 1 px ≈ 0.35 mm), and set labels to `font-size` ≥ 9 in those units. Several units still have about 7pt labels. **Fix this up front next time.**
4. **The 30-second page must be exactly one page.** `build.py` checks that "30-SECOND REVISION" appears only on the last page. If it spills over, cut rows, not font size (9pt minimum).
5. **Garbled text from animation-overlay slides** (DOS U2 slides 68–70) had text repeated or merged. Use the clean summary slide for the same content and reconstruct from it.
6. **Formulas or values embedded as images do not come through `pdftotext`.** Render the slide. If the image is unreadable or missing, mark it SOURCE UNCLEAR; never fill it in from general knowledge. In DOS U3 this happened to Cristian's formula, and a PYQ numerical depends on that formula, so the guide flags it.
7. **Answers you derive yourself are allowed only when labelled.** Mark them as "worked by applying the slide's method, not given in source" (e.g. deadlock safe/unsafe answers, Bully walk-through).
8. **Inconsistencies in the source:** keep both versions and turn them into an EXAM TRAP. Examples: two different definitions of "integrity"; "strong" vs "strict" consistency; a diagram label that is wrong, such as a reply labelled "Request Packet".
9. Unit 4 reported odd spacing around hyphens ("sender - inaugurated"). **Unverified:** this may be the source text's own " - " rather than CSS. Check this before blaming `font-feature-settings`.

## 6. Exam-frequency badges

- Parse the question bank (`Sr | Unit | Question | Marks`) and the previous-year paper. Tag section headings and contents entries:
  - `QB 7M` = in the question bank, worth 7 marks
  - `PYQ 4M` = in the previous-year paper, worth 4 marks
  - `PYQ ×2` = asked twice
- Put a badge legend on the cover. One unit also added a "What gets asked" table on the cover; it was useful.
- Badges affect **emphasis and space** (high-mark topics get a full page). They never change facts.

## 7. Agent brief template (one per unit)

```
You are the fork for UNIT N (<Unit title>, <deck>.pdf). Build the full study guide per the user's spec,
using the design system + pipeline in <toolkit dir>.
- Facts ONLY from src/<deck>.txt and the slides (render garbled/diagram slides with pdftoppm and look).
  Cover every topic. Gaps → <span class="unclear">SOURCE UNCLEAR</span>.
- Use qb.txt / PYQ txt only to place QB/PYQ badges on headings + TOC; legend on cover.
- Write unitN.html following sample.html (HDR comment, cover w/ TOC + SVG concept map,
  <section class="sec" id="sN" data-title> using the 9-part template, final rev30 on ONE page).
  Mnemonics only when they faithfully map to source lists. SVG labels ≥ 9pt printed.
  No "§N" text anywhere except the generated header; use "Sec N" for cross-refs.
- Do NOT edit guide.css/build.py; extra styles go in a <style> block in your file (palette only).
- Build: python3 build.py unitN.html <out.pdf>; ./preview.sh on a copy; LOOK at pages; fix overflow,
  split boxes, overlaps, >25% gaps, rev30 not single last page, tiny labels. Iterate.
- Report: path, page count, sections, SOURCE UNCLEAR items, unfixed QA issues.
```

## 8. Reusing for a new subject

```bash
git clone https://github.com/soham901/exam-revision-guide-kit <new-subject>/guide-build && cd <new-subject>/guide-build
mkdir -p ../src && for f in ../*.pdf; do pdftotext -layout "$f" "../src/$(basename "${f%.pdf}").txt"; done
cp sample.html unit1.html           # edit HDR line: <!-- HDR: SUBJECT · UNIT 1 — TITLE -->
python3 build.py unit1.html ../revision-guides/Unit-1.pdf && cp ../revision-guides/Unit-1.pdf u1.pdf && ./preview.sh u1.pdf
```

`build.py` prints the page count, section start pages, whether the 30-second page is OK, and the `pdffonts` table. Check that every font says `emb yes` and none is Type 3, except symbol fallbacks.

Things to change per subject: the HDR line, the cover subject/code lines and the footer label. The footer label is in `guide.css` under `@bottom-left`.

## 9. Result benchmarks (DOS)

| Unit | Slides | Guide pages | Sections |
|---|---|---|---|
| U1 Concepts | 81 | 15 | 9 |
| U2 IPC & Remote Comm | 130 | 20 | 17 |
| U3 Sync & Naming | 151 | 20 | 11 |
| U4 DSM & Resource Mgmt | 85 | 20 | 13 |
| U5 Security | 64 | 10 | 8 |

As a rule of thumb, expect about 1 guide page per 5–8 slides, depending on how dense each slide is.
