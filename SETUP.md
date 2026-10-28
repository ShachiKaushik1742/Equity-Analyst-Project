# FIN 67110 setup

Verified October 22, 2026:
- Python 3.14.7 runs setup_check.py from a terminal.
- Git installed; local repository initialized.
- Codex CLI installed and signed in with ChatGPT.
- Antigravity CLI 1.4.5 installed; authentication still to verify.
- .env contains placeholders only and is ignored by Git.

Still to verify:
- Orca project FIN67110 added at /Users/shachi/Documents/FIN67110.
- Codex and Antigravity launched side by side in the main workspace.
- Codex displays its ready prompt.
- Antigravity awaits review of Terms of Service & Data Use; sign-in and a model-response check remain.
- One provider API key works (separate from coding-agent sign-in).
- Public GitHub repository created and pushed; confirm .env is absent online.
- WRDS and Capital IQ access confirmed by user; LSEG registration approval pending.

## Terminal checks

```sh
cd ~/Documents/FIN67110
python --version
python setup_check.py
codex login status
agy --version
git check-ignore .env
```

Launch `agy` in this folder and complete Google sign-in. Launch `codex` in the same folder. In Orca, open this folder and launch each agent.

## Account links

- Course prerequisites: https://cinderzhang.github.io/FIN67110-Fall2026/grading.html#prerequisites--your-setup-is-yours
- GitHub repository creation: https://github.com/new (choose Public)
- OpenAI API keys: https://platform.openai.com/api-keys
- Alternative Google API keys: https://aistudio.google.com/apikey
- LSEG: https://guides.lib.purdue.edu/refinitivworkspace
- WRDS: https://guides.lib.purdue.edu/WRDS
- Capital IQ via Purdue: https://blogs.lib.purdue.edu/news/2024/04/08/featured-databases-sp-capital-iq/

Enter keys locally in .env; do not paste them into chat or upload the entire folder through GitHub web upload (which bypasses .gitignore). Git push respects the ignore rule for untracked files.

Before publishing course work, append the course-required disclosure and personally verify the sources:

This is a learning exercise, not financial advice.
AI assistance: [the tools you used]. I verified the sources myself; the judgments are mine.
Any remaining errors are my own.
