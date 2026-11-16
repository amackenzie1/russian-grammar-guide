# Authoring guide — "A Guide to Russian Grammar"

This is a free, book-length grammar guide for English speakers learning Russian, written in the
spirit of Tae Kim's *Guide to Japanese Grammar*. Every section lives in one Markdown file under
`parts/<part>/NN-slug.md`; `tools/build.py` compiles everything into `guide.html`.

## What makes it "Tae Kim-like" (the editorial stance)

1. **Explain Russian on its own terms.** Don't present Russian as English with odd endings. Say
   what the Russian form actually *means* and when a Russian speaker reaches for it, then give the
   English only as a rough translation. Where English forces a distinction Russian doesn't make
   (articles, continuous tenses) or vice versa (aspect, cases, motion verbs), say so plainly.
2. **Build strictly from the ground up.** Each section may only rely on grammar taught in earlier
   sections (see the outline below). If an example needs something not yet taught, either pick
   another example or flag it in one clause ("we'll get to this ending in the Genitive section").
3. **Concept first, then the forms, then lots of examples.** Open each section by saying, in
   plain conversational English, what problem this piece of grammar solves. Then the mechanics
   (compact tables). Then real example sentences — natural things people say, not textbook
   filler like "the pencil is on the table".
4. **Natural, modern, spoken-first Russian.** Default to `ты` among friends; show `вы` where it
   belongs. Prefer what people really say. Note register (colloquial / neutral / bookish) when
   it matters.
5. **Honest about irregularity and difficulty.** Say which rules are solid, which are tendencies,
   and what simply has to be memorised. Don't dump every exception in the main text — give the
   high-frequency ones and send the rest to the Reference part.
6. **Voice:** a knowledgeable friend talking — direct, a bit opinionated, lightly humorous, never
   cute or padded. Use "you" and "we". No linguistics jargon without an immediate plain-English
   explanation. No filler intros ("In this section we will learn..."), no cheerleading, no
   summaries that repeat the section.
7. **Accuracy is everything.** Every Russian form, stress mark and translation must be correct.
   If you are not certain of a form or a stress, check it (reason it out from the paradigm, or
   look it up) or choose a different example. A wrong stress mark is a bug.

## Hard formatting rules

### Stress marks
- Every Russian word of **two or more syllables** carries a stress mark: the combining acute
  accent U+0301 placed immediately **after** the stressed vowel: `молоко́`, `чита́ю`, `хорошо́`.
- `ё` is always stressed and never takes a mark: `ещё`, `идёт`. Always write `ё` where it belongs
  (never `е` for `ё`).
- One-syllable words get no mark: `я`, `он`, `дом`, `здесь`, `что`.
- Words with a secondary stress: mark only the main stress.
- Capital letters take the mark too: `Э́то`, `Она́`.
- Bare endings, suffixes, prefixes and single letters written with a hyphen (`-ая`, `-ого`,
  `при-`) don't need marks; the linter skips chunks that start or end with a hyphen.
- Run `uv run tools/lint.py parts/<your-part>` before finishing; it lists multi-syllable Russian
  words missing a stress mark, words with two marks, marks on one-syllable words, and broken
  blocks/links. Fix everything it reports. If something is deliberately unmarked — e.g. you are
  showing how Russians actually write, without marks, or spelling out letters — wrap that text
  in `[[ns: ... ]]` (the wrapper disappears in the output).

### File layout
- First line: `# Section title` (plain English title, as given in the outline).
- Use `##` and `###` for sub-headings inside a section. No `#` other than the title.
- Target length: **1,500–3,000 words** per section (reference tables excluded). Depth over
  breadth; do not pad.
- Ordinary Markdown: paragraphs, `**bold**`, `*italic*`, lists, pipe tables. Inline Russian in
  running prose is written plainly with stress marks; put a new form in **bold** the first time.
  Give an English gloss in parentheses or after a dash the first time a word appears in your
  part: `кни́га (book)`.
- Do **not** use raw HTML, images, footnotes, or code fences.

### Custom blocks
Blocks open with `:::kind` on its own line and close with `:::` on its own line. Blocks do not
nest. Fields inside line-based blocks are separated by ` | ` (space, pipe, space).

Example sentences (the workhorse — use it constantly):

    :::ex
    Я чита́ю кни́гу. | I'm reading a book.
    Она́ не зна́ет. | She doesn't know. | optional short note, e.g. literally "she not knows"
    :::

Inside `:::ex` and `:::dialogue`, you may highlight the form being taught with `**...**` in the
Russian. Translations should be natural English; add a literal gloss as the third field only
when it reveals structure.

Vocabulary list (put one near the top of a section for words the section introduces; 5–20 items;
third field optional):

    :::vocab
    кни́га | book | f.
    чита́ть | to read | impf.; pf. прочита́ть
    :::

Dialogue (speaker label, colon, line):

    :::dialogue
    А: Ты где? | Where are you?
    Б: До́ма. | At home.
    :::

Callouts (content is ordinary Markdown; optional title after the kind):

    :::note Why there's no "is"
    Text...
    :::

Kinds: `note` (useful extra), `warn` (a classic learner mistake or trap), `aside` (culture,
history, deeper linguistic point — skippable), `summary` (a tight recap table or 3–6 bullets at
the end of a section — only when the section really needs one).

Illustrations (used sparingly):

- `:::cursive` — each line `text | optional note` is shown in print, italic and a handwriting face;
  `:::cursive grid` makes one small card per line (for single letters). Text inside is written
  without stress marks, as in real handwriting.
- `:::keyboard` — each line is a keyboard row of tokens like `й:q` (Cyrillic : Latin legend).
- `:::figure name` — inlines `assets/figures/name.svg`; the block's content is the caption. SVGs
  use the `f-…` classes defined in `tools/build.py` so they follow the light and dark themes.

Tables: ordinary Markdown pipe tables (with a blank line before them). Keep paradigm tables
compact. Bold the endings where it helps: `кни́г**у**`.

### Cross-references
Link to other sections as `[the genitive](#s-03-04)` — the id is `s-PP-NN` from the outline
numbering below (part 3, section 4 → `s-03-04`). Use sparingly. (The linter reports links to
sections whose files don't exist yet; other writers are producing them in parallel, so those
particular warnings can be ignored as long as the id is in the outline.)

### Abbreviations
m. / f. / n. / pl.; nom. / acc. / gen. / dat. / instr. / prep.; impf. / pf.; sg. Spell the case
names out in running prose.

### Conventions for consistency
- Case order in all tables: Nominative, Accusative, Genitive, Dative, Instrumental, Prepositional.
- Gender/number order: masculine, neuter, feminine, plural.
- Aspect pairs are written imperfective / perfective: `де́лать / сде́лать`.
- People in examples: use a small recurring cast — А́ня, Ма́ша, Са́ша, Ди́ма, Ми́ша, О́ля, Ива́н,
  ба́бушка — and everyday modern situations (messages, work, food, transport, friends, family).
- Transliteration: only in Part 1. From Part 2 on, Cyrillic only.
- American spelling.
- Dialogue speaker labels are `А:` and `Б:` (Cyrillic), or names.
- File names: `NN-short-slug.md` where NN is the section number from the outline
  (e.g. `parts/03-cases/04-genitive.md`).

## Outline (ids are `s-PP-NN`)

Sections are tagged for three reading passes in `tools/build.py` (`FIRST_PASS`; Part 8 is the third pass, Part 9 is reference, everything else is the second pass). When you add a section, decide whether a beginner needs it on a first pass.

A topic earns a section because Russian does it differently from English, not because another
grammar has a chapter for it. Section ids are linked from outside, so new sections are appended
to their part rather than renumbering existing ones.

**Part 0 — Introduction** (`parts/00-introduction`)
- 00-01 How this guide works

**Part 1 — Sounds and Letters** (`parts/01-sounds-and-letters`)
- 01-01 The alphabet
- 01-02 Hard and soft consonants
- 01-03 Stress and vowel reduction
- 01-04 How consonants behave (devoicing, assimilation, silent letters, -ого, что)
- 01-05 Spelling rules
- 01-06 Handwriting, typing and the letter ё
- 01-07 Intonation: the melody that makes a question (the center; statement, yes/no, question-word, а-questions, exclamations)

**Part 2 — First Sentences** (`parts/02-first-sentences`)
- 02-01 Sentences without "to be" (это, вот, не, yes/no questions by intonation, и / а / но)
- 02-02 Gender
- 02-03 Plurals
- 02-04 Pronouns and possessives (я…они, мой/твой/наш/ваш/его/её/их, чей, этот/тот)
- 02-05 Adjectives (agreement in the nominative; какой; hard/soft/mixed stems)
- 02-06 Verbs in the present tense (the two conjugations, common irregulars, не, question words)
- 02-07 The past tense (-л forms; был; "to be" reappears)
- 02-08 Adverbs and the future of быть (хорошо, очень, уже/ещё, тоже/также; буду + infinitive preview)
- 02-09 How Russian words are built (stem + ending; root, prefix, suffix; a first look, full treatment in 08-07)

**Part 3 — Cases** (`parts/03-cases`)
- 03-01 What cases are (roles, not endings; the six cases at a glance; why word order is free)
- 03-02 The accusative: direct objects (incl. animate masculine preview; в/на + acc. for direction preview)
- 03-03 The prepositional: where and about what (в, на, о; -у locatives briefly)
- 03-04 The genitive: of, none, and some (possession, нет, у меня есть, quantities, из/от/до/без/для/после)
- 03-05 The dative: to and for whom (recipients, нравиться, мне холодно, age, к, по)
- 03-06 The instrumental: with and by means of (tool, с, быть/стать/работать кем, за/над/под/перед/между)
- 03-07 Cases in the plural (all six; genitive plural in detail; animate accusative)
- 03-08 Pronouns and determiners in all cases (меня/мне/мной…, кто/что, этот, весь, possessives; н- after prepositions)
- 03-09 Word order (old-before-new, how Russian does "a/the", emphasis, questions, neutral orders)
- 03-10 Being, having and existing (zero copula, есть, нет + gen., у меня есть, иметь, бывать, являться)
- 03-11 Animacy: who versus what (accusative = genitive, what counts as animate, numbers)

**Part 4 — The Verb System** (`parts/04-verbs`)
- 04-01 Aspect: the big idea (process vs. bounded whole; pairs; how pairs are formed)
- 04-02 Aspect in the past and the future (буду читать vs прочитаю; single/repeated/result/annulled actions)
- 04-03 Aspect with infinitives and negation (начать/кончить + impf., хочу, нельзя, не надо)
- 04-04 Conjugation patterns in depth (stems, -овать, -авать, -нуть, consonant mutation, stress shifts, key irregulars)
- 04-05 The imperative (forms, aspect in commands, давай, пусть, softeners)
- 04-06 Reflexive verbs: -ся (true reflexive, reciprocal, passive-ish, "just is" verbs, нравиться-type)
- 04-07 Would and so-that: бы and чтобы (conditional, wishes, polite requests, хочу, чтобы)
- 04-08 Possibility and necessity: можно, надо, должен, мочь (organized by Russian construction: unchanging predicate words + dative, agreeing short adjectives, real verbs; an English lookup table at the end)

**Part 5 — Motion, Space, Time and Number** (`parts/05-motion-space-time-number`)
- 05-01 Where, where to, where from (в/на/из/с/у/к/от triads; где/куда/откуда; здесь/сюда/отсюда)
- 05-02 Going: идти/ходить, ехать/ездить (one-direction vs multi-direction; пойти/поехать; past был vs ходил)
- 05-03 Prefixed verbs of motion (при-, у-, в-, вы-, под-, от-, пере-, про-, за-, до-, об-; aspect pairs)
- 05-04 Carrying, leading, running, flying (нести/носить, везти/возить, вести/водить, бежать, лететь, плыть; привезти/принести)
- 05-05 Standing, lying, sitting, putting (стоять/лежать/сидеть/висеть; ставить/класть/сажать/вешать; садиться/ложиться/вставать)
- 05-06 Verbal prefixes beyond motion (the prefix system as a meaning toolkit: по-, за-, до-, пере-, на-, вы-, раз-, с-, про-, от-, у-; secondary imperfectives)
- 05-07 Numbers and counting (1 / 2–4 / 5+ rule, один/одна, два/две, compound numbers, сколько/много/несколько, ordinal numbers)
- 05-08 Time, dates and age (clock time, days, months, years, в/на/через/назад/за/на + time, duration, мне … лет)

**Part 6 — Bigger Sentences** (`parts/06-bigger-sentences`)
- 06-01 Joining clauses (и/а/но/или/зато, потому что/поэтому/так как, если, когда/пока/как только, хотя, тоже/также)
- 06-02 That, whether, and reported speech (что vs чтобы, ли, tense is not shifted, question words as conjunctions)
- 06-03 Relative clauses: который (and кто/что/где/чей as relatives, то, что)
- 06-04 Negation (не vs нет, double negation ни-, genitive of negation, некого/нечего/некогда)
- 06-05 Someone, anyone, something: -то, -нибудь, кое-, любой
- 06-06 One's own, oneself, each other (свой, себя, сам, самый, друг друга)
- 06-07 Comparing (comparatives -ее, irregulars, чем vs genitive, более, superlatives самый / -айший, гораздо, как можно)
- 06-08 Short adjectives and predicate words (рад, готов, должен, нужен, похож; -о adverbs; такой vs так, какой vs как)
- 06-10 Verbs that English lumps together (study/teach, know/meet, ask, say/tell, look/see, remember, use, try, change, stop/leave, marry, borrow, wash)
- 06-09 Sentences without a subject (impersonal: темно, мне холодно, меня тошнит; indefinite-personal: говорят; generic ты; infinitive sentences: что делать?)

**Part 7 — Real Spoken Russian** (`parts/07-spoken-russian`)
- 07-01 Ты and вы, names, and how to address people (diminutive names, patronymics, vocative Маш!, девушка/молодой человек)
- 07-02 Particles I: же, ведь, -то, вот, ну
- 07-03 Particles II: да, уж, -ка, и, даже, хоть, разве, неужели, именно, как раз, всё-таки, просто
- 07-04 Diminutives and expressive suffixes (-ик, -чик, -ок, -ка, -очка, -енька, -ище, -ина; when they're affectionate vs ironic)
- 07-05 Hedging, seeming and hearsay (кажется, вроде, похоже, наверное/наверно, может быть, как бы, типа, мол, якобы, говорят, оказывается, видимо)
- 07-06 Wanting, liking, feeling (хотеть vs хочется, любить vs нравиться, надоело, лень, жалко, пора, неохота, скучать, бояться, state idioms)
- 07-07 Colloquial shortcuts, fillers and slang (щас, чё, тыща, ваще; ну, это, короче, значит, блин; ellipsis; a sober note on мат)
- 07-08 Everyday formulas (greetings, thanks, apologies, requests, phone, messaging, toasts, congratulations, holidays)
- 07-09 Мат: Russian obscenity (the four roots, the euphemism ladder, prefixed verbs, grammar slots, taboo and law; for recognition)

**Part 8 — Written and Formal Russian** (`parts/08-written-russian`)
- 08-01 Active participles (читающий, читавший; how to read them; replacing который)
- 08-02 Passive participles and the passive voice (читаемый, прочитанный, short forms сделано; -ся passives; instrumental agent)
- 08-03 Verbal adverbs (читая, прочитав; the same-subject rule; fossilised ones: благодаря, несмотря на)
- 08-04 Formal connectors and officialese (поскольку, в связи с, в течение, несмотря на то что, однако, то есть, а именно, verbal nouns in -ние)
- 08-05 Declining numbers, collectives and fractions (двух/трёх/пяти…, двое/трое, оба/обе, полтора, тысяча/миллион, дроби)
- 08-06 Irregular nouns and loose ends (время/имя, мать/дочь, путь, люди/дети, год/лет, fleeting vowels, second genitive, locative -у, indeclinables, surnames, pluralia tantum)
- 08-07 Word formation (roots, noun/adjective/verb-forming suffixes, compound words, abbreviations; reading unfamiliar words)
- 08-08 Advanced sentence patterns (чем… тем, что бы ни / как бы ни, не то что, стоит… как, то… то, не успел… как, было + past, чуть не, вряд ли, пусть/пускай, infinitive + бы)

**Part 9 — Reference** (`parts/09-reference`)
- 09-01 Noun declension tables
- 09-02 Adjective, pronoun and determiner tables
- 09-03 Verb conjugation tables and irregular verbs
- 09-04 Common aspect pairs
- 09-05 Prepositions and the cases they take
- 09-06 Verbs and adjectives that govern a particular case
- 09-07 Stress patterns
- 09-08 Numbers at a glance
