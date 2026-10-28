# Agent instructions: building exam revision guides

You are turning the user's study material (slide PDFs, notes) into A4 revision-guide PDFs using this kit. Read `LEARNINGS.md` before starting. It holds the design rules, the component reference (§4), the known pitfalls (§5) and a per-unit brief (§7).

## Workflow

1. **Clarify first.** If the request is missing the subject, the unit(s), length or orientation, ask once, with all questions together. Also ask whether a question bank or past papers exist; they are used for exam-frequency badges.
2. **Extract sources** into `src/`. Use `pdftotext -layout <deck>.pdf src/<deck>.txt`. When a slide's text comes out garbled or missing (diagrams, tables, formulas shown as images), render that slide with `pdftoppm -r 70 -png -f N -l N <deck>.pdf img/s` and look at it.
3. **Write `unitN.html`, one per unit, starting from `sample.html`.**
   - The first line is the running header: `<!-- HDR: SUBJECT · UNIT N — TITLE -->`.
   - The cover holds a contents list (`<span class="pg" data-sec="sN"></span>`) and an SVG concept map.
   - Each topic is a `<section class="sec" id="sN" data-title="...">` following the 9-part template: What is it, Key points, Steps, Terms, Comparison, Formulas, Exam traps, Mnemonics, Quick check. Skip a part only if the source has nothing for it.
   - The final section is `<section class="rev30" id="rev30">`, and it must fit on one page.
4. **Build:** `python3 build.py unitN.html out/Unit-N.pdf`.
5. **QA:** copy the PDF next to `preview.sh`, run `./preview.sh <copy>.pdf`, and **look at every page image**. Fix each of these:
   - clipped or overflowing text, or overlapping elements;
   - boxes or tables split across pages;
   - gaps larger than 25% of a page (rebalance or merge thin sections; never pad);
   - a 30-second page that isn't exactly the single last page;
   - SVG labels under 9pt.

   Rebuild until the output is clean.
6. When there are several units and your tool supports subagents, run **one subagent per unit in parallel** using the brief in `LEARNINGS.md` §7. Then rebuild all units and spot-check them.

## Hard rules

- **Facts come only from the user's source material.** No outside knowledge, no corrections. Anything unclear or missing gets `<span class="unclear">SOURCE UNCLEAR</span>`. If you derive anything (worked answers, walk-throughs), label it as derived.
- Only black, white and lime `#A3E635`, with light grey for table rows and hairlines only. Never use lime for small text on white; text on lime is always black.
- Body text is 10pt or larger; tables and compact text are 9pt or larger.
- Do not write `§N` anywhere in the content; `build.py` uses it to detect section starts. Write "Sec N" for cross-references.
- Do not edit `guide.css` or `build.py` for one unit's needs. Put a `<style>` block inside that unit's HTML instead.
- Never commit the user's course material or generated PDFs; `.gitignore` already excludes them.
