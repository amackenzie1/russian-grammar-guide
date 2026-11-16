# Contributing

Corrections are the most useful thing you can give this guide. It was written by an AI model and
has been read in part, not in full, by a native speaker, so there are mistakes in it that nobody
has found yet.

## Reporting a mistake

Every section of the [live guide](https://andrew.ma/russian/) ends with a "Report it" link that
opens an issue with the section already filled in. Say what the guide says, what it should say,
and why if you can. A one-line issue is fine.

Things worth reporting:

- a wrong form, ending or stress mark;
- a sentence that is grammatical but that nobody would say;
- a translation that misses the meaning or the register;
- a rule stated more absolutely than is true;
- slang or usage that is dated, regional or mislabeled;
- something explained in a way that confused you as a learner.

## Fixing it yourself

Each section is one Markdown file under `parts/`. The "edit the source" link at the bottom of a
section opens the right file on GitHub; change it there and open a pull request.

Before you write more than a line or two, read [AUTHORING.md](AUTHORING.md). The two rules that
matter most:

1. **Every Russian word of two or more syllables carries a stress mark**: the combining acute
   accent (U+0301) typed straight after the stressed vowel, as in `молоко́`. `ё` never takes one.
2. **Examples go in `:::ex` blocks**, one per line, Russian and English separated by ` | `.

To check your change locally (you need [uv](https://docs.astral.sh/uv/)):

    uv run tools/lint.py      # stress marks, block syntax, cross-references
    uv run tools/build.py     # writes guide.html; open it in a browser

The same two commands run on every pull request. When a pull request is merged, the live site
rebuilds by itself within a few minutes.

## Suggesting a topic

Open a "Suggest a topic" issue. The guide gives a topic space when Russian does it differently
from English, so say how yours differs.

## Licensing of contributions

By contributing you agree that your text is released under CC BY-SA 4.0 and any code under the MIT
license, the same terms as the rest of the project (see [LICENSE.md](LICENSE.md)).
