# FIN 67110 setup

Verified October 28, 2026:
- Python 3.14.7 runs setup_check.py from a terminal.
- Git installed; local repository initialized.
- Codex CLI installed and signed in with ChatGPT.
- Antigravity CLI 1.4.5 installed; user confirmed sign-in and that it is open in the adjacent terminal.
- User confirmed access to LSEG Workspace, WRDS, and S&P Capital IQ.
- Purdue GenAI Studio key added to .env; successful model-backed COST and MSFT reports show that requests ran.
- .env is ignored by Git.
- GitHub CLI is authenticated; Git remote points to https://github.com/ShachiKaushik1742/Equity-Analyst-Project.git.
- A post-commit hook pushes new commits to origin/main.
- Initial push verified: .env is absent from the GitHub repository.

Still to verify:
- Repository visibility remains to confirm. The unauthenticated GitHub API returned 404 for the configured remote; this is consistent with the private repository behavior, while authenticated pushes succeed. The course prerequisite requires a public repository.
- Checkpoint 1 still needs the latest commit permalink submitted in Brightspace.

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
