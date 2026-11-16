# A Guide to Russian Grammar

A free, book-length Russian grammar for English speakers, in the spirit of
[Tae Kim's Guide to Japanese Grammar](https://www.guidetojapanese.org/grammar_guide.pdf): Russian
explained on its own terms, built up from the alphabet to officialese.

**Read it: https://andrew.ma/russian/**

About 80 sections in ten parts: sounds and letters, first sentences, cases, the verb system,
motion and number, bigger sentences, real spoken Russian, written and formal Russian, and
reference tables. Every word has its stress marked. It is a grammar, not a course: no exercises
and no audio.

## Who wrote it

The text was written by Claude Fable 5.2, an AI model made by Anthropic, in November 2026, at the
request of a native speaker. Each part was re-read by an independent reviewer, the stress marks
were checked against a dictionary, and a native speaker has read much of it, though not all.

That means it still contains mistakes nobody has found. **If you spot one, please
[open an issue](https://github.com/amackenzie1/russian-grammar-guide/issues/new/choose)**, or use
the "Report it" link at the bottom of any section. See [CONTRIBUTING.md](CONTRIBUTING.md).

## What's here

- `parts/` — the text, one Markdown file per section.
- `assets/` — diagrams and the handwriting font.
- `AUTHORING.md` — editorial stance, formatting rules and the full outline.
- `tools/` — the linter and the script that compiles everything into one standalone HTML page.

## Build

You need [uv](https://docs.astral.sh/uv/).

    uv run tools/lint.py           # stress marks, block syntax, cross-references
    uv run tools/build.py          # writes guide.html
    open guide.html

Optional cross-check of every stress mark against the OpenRussian dictionary (download the four
CSVs from github.com/Badestrand/russian-dictionary into a folder first):

    python3 -I tools/stresscheck.py /path/to/csv-folder

Flagged words are not necessarily wrong (variants, locatives in -у́, dictionary gaps); review by
hand.

Merges to `main` are published to the live site automatically.

## License

The guide's text and figures are CC BY-SA 4.0; the code is MIT. See [LICENSE.md](LICENSE.md).
