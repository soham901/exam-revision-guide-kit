# exam-revision-guide-kit

Turn lecture slides into **print-ready exam revision guides**: multi-page A4 PDFs in a clean black / white / lime design. Each guide has a cover with a contents list and a concept map, one section per topic, exam-trap boxes, formula cards, quick-check questions, and a one-page **30-Second Revision** sheet at the end.

It's built with plain HTML + CSS and printed to PDF by headless Chrome. The text is real, selectable and searchable, diagrams are vector, and fonts are embedded.

![Sample content page](docs/sample-page.png)

## What's inside

| File | Purpose |
|---|---|
| `guide.css` | The design system: palette, typography, A4 page rules, running headers and footers, all components |
| `build.py` | Two-pass build. Renders the PDF, fills in the contents page numbers, sets per-section page markers, and checks that the 30-second page is the single last page and that fonts are embedded |
| `preview.sh` | Renders every page as a PNG plus a contact sheet for visual QA |
| `sample.html` | Minimal skeleton showing every component. Copy it to start a unit |
| `LEARNINGS.md` | Full playbook: workflow, design decisions, component reference, pitfalls and fixes, and a brief for an AI agent per unit |

## Requirements

- Google Chrome or Chromium, version 131 or newer (needed for `@page` margin boxes and named pages)
- Python 3
- poppler-utils (`pdftotext`, `pdftoppm`, `pdffonts`)
- ImageMagick (`montage`, used only by `preview.sh`)
- The [Inter](https://rsms.me/inter/) font installed system-wide

If Chrome isn't on your PATH as `google-chrome`, point to it:
```bash
export CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS
export CHROME=chromium                                                          # Linux alt
```

## Quick start

```bash
git clone https://github.com/soham901/exam-revision-guide-kit && cd exam-revision-guide-kit
python3 build.py sample.html sample.pdf      # builds the demo guide
./preview.sh sample.pdf                      # sample-p-*.png + sample-sheet.png
```

## Making a guide for your subject

1. Extract your slides to text: `pdftotext -layout unit1.pdf src/unit1.txt`. For slides that are mostly images, render them with `pdftoppm` and read them visually.
2. `cp sample.html unit1.html`, then edit the first line, which is the running header:
   ```html
   <!-- HDR: SUBJECT NAME · UNIT 1 — UNIT TITLE -->
   ```
3. Write one `<section class="sec" id="sN" data-title="Topic">` per topic, using the components (see the table in `LEARNINGS.md`). End with `<section class="rev30" id="rev30">`.
4. Contents page numbers fill in automatically from `<span class="pg" data-sec="sN"></span>`.
5. Build, preview, fix, repeat.

The guides work well as an AI-assisted workflow: give an LLM agent the extracted slides plus the brief in `LEARNINGS.md` §7, one agent per unit. The core rule is **facts only from the source**. Anything missing or unreadable gets marked `SOURCE UNCLEAR` instead of being filled in from general knowledge.

## Design rules

- Only black, white and lime (`#A3E635`). Light grey is allowed only for table rows and hairlines.
- Lime is never used for small text on white. Text on lime is always black.
- Body text is 10pt or larger; tables and compact text never go below 9pt.
- Every section starts on a new page, and boxes, tables and traps never split across pages.

## License

MIT. Fork it, restyle it, use it for any subject.
