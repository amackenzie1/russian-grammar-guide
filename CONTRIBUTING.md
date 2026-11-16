# Contributing

This guide is meant to be argued with. It was written by an AI model and has been read in part,
not in full, by a native speaker, so there are mistakes in it that nobody has found yet. But
corrections are only half of what helps: opinions about what is missing, what is badly explained,
what is in the wrong order and what does not deserve the space it takes are just as welcome.

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

## Suggesting a change to structure or content

Open a "Suggest a change" issue (each section of the live guide links to one with the section
filled in). All of these are fair game:

- a topic that is missing or deserves its own section;
- an explanation that confused you, with what would have helped;
- sections that would work better in a different order, merged, or split;
- a section that spends pages on something that works the same way in English.

The test the guide uses: a topic earns space when Russian does it differently from English. If
you are proposing an addition, say how it differs; if you are proposing a cut, say why it does
not.

## Licensing of contributions

By contributing you agree that your text is released under CC BY-SA 4.0 and any code under the MIT
license, the same terms as the rest of the project (see [LICENSE.md](LICENSE.md)).
