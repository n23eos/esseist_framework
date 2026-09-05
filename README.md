# esseist_framework

**esseist_framework is a Claude Code skill that produces a finished text by interviewing you in small batches of questions instead of asking for a draft.** You provide a topic, answer three to five short questions at a time, and the skill stitches your answers into a piece written in your own voice. It supports blog essays, Medium articles, YouTube scripts with hooks and duration estimates, Telegram posts under 900 characters, short and long X posts, and X threads of 5–10 posts. A style questionnaire builds a voice fingerprint so drafts sound like you rather than like a model. All state lives in files under `essays/`, so you can stop halfway through and resume a week later. Facts, opinions, and examples come only from your answers, and the synthesis pass applies fact-checking and anti-slop gates before the text is considered finished.

<div align="center">

[![Star on GitHub](https://img.shields.io/github/stars/n23eos/esseist_framework?style=for-the-badge&logo=github&label=Star%20this%20repo&color=FFD700&labelColor=1a1a1a)](https://github.com/n23eos/esseist_framework)

</div>

**The idea:** you provide a topic → Claude interviews you with small batches of simple questions (3–5 at a time) → your answers are stitched into a finished piece in your own voice. All state is stored in files, so you can stop halfway through and return a week later—the pipeline resumes exactly where you left off.

**Formats:** blog essay · Medium article (curation, AI disclosure, tags) · YouTube script (hook, stage directions, duration estimate) · Telegram post (≤900 characters, single pass) · short X post (≤280 weighted units) · long X post (up to 25,000 weighted units) · X thread (5–10 posts).

## How it works

1. **Setup** — topic plus a few framing questions: audience, core idea, platform/length, and tone. Short formats reduce this to 0–2 questions.
2. **Interview** — a question map (9–15 questions for an essay, 3–6 for a post or thread), delivered in batches of 3–5 with a progress indicator such as “questions 5–8 of 12.” Each question can be answered in 1–3 sentences from your phone, including by voice. Commands: “skip,” “stop,” “stitch it together,” and “save this idea.”
3. **Follow-up** — at most one optional batch of clarifying questions about weak or missing details.
4. **Synthesis** — outline approval for long-form pieces → draft in your voice → anti-slop pass → length check. Hard rule: facts, opinions, and examples must come from your answers; the skill never invents content on your behalf.
5. **Publishing** — on the “publish” command: deploy the essay to a blog, with an optional labeled English translation. The process lives in `references/publish.md` and is tailored to one specific site, so replace it with your own publishing configuration.

Each piece gets its own `essays/<slug>/` directory containing `session.md` (all questions, answers, and status) and `draft.md` (the finished text). Every piece is stored under one base directory regardless of where the skill was launched. Fleeting ideas can be added to `essays/_ideas.md` with the “save this idea” command; the skill will suggest them the next time you start writing.

## Installation

This is a skill for [Claude Code](https://claude.com/claude-code):

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/essayist" ~/.claude/skills/essayist
```

Use a symlink rather than a copy: the installed skill will stay in sync with the repository and receive updates through `git pull`. A copied directory (`cp -r`) silently falls behind—this has been tested the hard way.

You can then invoke `/essayist` from any directory and ask it to write an essay about X. Use the same command to resume an unfinished piece.

All work is stored in a single base directory. Its path is hardcoded in `SKILL.md` under “Files”; change it to your own path before the first run.

## Your own voice

Add a description of your writing voice—vocabulary, rhythm, phrases to avoid, and sample lines—below the divider in `essayist/style/blueprint.md`. It becomes the primary style source during synthesis. Without it, the skill looks for a personal voice skill (the default is `nikolai-voice`; replace it with yours in `SKILL.md`) or writes in a neutral, natural voice.

## Project structure

```text
essayist/
├── SKILL.md                      # orchestrator: phases, formats, commands, resume protocol
├── references/
│   ├── question-craft.md         # how to generate questions: six coverage areas, bad → good
│   ├── interview-rules.md        # ADHD-friendly interview rules: batches, progress, answers
│   ├── synthesis.md              # synthesis rules: boundaries, outline, anti-slop, length
│   ├── ru-slop.md                # Russian anti-slop: 34 patterns, metrics, voice protection
│   ├── en-slop.md                # English anti-slop: 27 patterns, voice transfer into English
│   ├── fingerprint.md            # voice fingerprint questionnaire: 3 layers, 6 blocks, calibration
│   ├── revision.md               # revision protocol: 8 passes from structure to wording
│   ├── sources.md                # source ingestion: vault note → interview only for missing details
│   ├── publish.md                # blog deployment plus EN translation: general workflow
│   ├── publish-raincoat.md       # platform config (raincoat.cc example)—replace with your own
│   └── formats/
│       ├── youtube-script.md     # video script: hook, stage directions, words per minute
│       ├── medium-article.md     # Medium article: curation, AI disclosure, tags
│       ├── tg-post.md            # single-pass post of ≤900 characters
│       ├── x-post.md             # short X post of ≤280 weighted units
│       ├── x-longform.md         # long X post or Article of up to 25,000 weighted units
│       └── x-thread.md           # thread of 5–10 posts, each ≤280 units
├── assets/
│   └── session-template.md       # session-state file template
└── style/
    └── blueprint.md              # slot for your voice; the questionnaire creates
                                  # two personal files beside it, both kept in .gitignore
```

## Verification

There is no application code in this repository, so verification focuses on instruction consistency: working links, absence of exposed credentials, valid skill frontmatter, agreement between the README tree and files on disk, session statuses, and storage paths.

```bash
./check.sh
```

Finished drafts can also be checked with the deterministic L1 gate, which catches banned phrases, copy-paste artifacts, emoji, mathematical symbols, and format limits:

```bash
python3 evals/voice/l1_guardrails.py essays/<slug>/draft.md --format essay
```

The complete evaluation loop—L1/L2/L3, held-out samples, and a blind pairwise judge—is documented in `evals/voice/README.md`.

## Example

The first essay produced with this pipeline was [“The Tool of All Tools”](https://raincoat.cc/blog.html?post=tool-of-all-tools): approximately 5,000 characters, 12 questions, 3 batches, and an outline accepted on the first pass.
