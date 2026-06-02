## Project nature
`asset-pricing` is a notebooks-only project. `nb_utils` is the only installable package — it exists solely to share notebook setup utilities without path manipulation.
`pyproject.toml` declares dependencies and registers `nb_utils` as a package. Do not add src/ layout or additional package discovery config — this is intentional.

## Commits
The user stages files and writes commits themselves.
When a commit is needed, suggest a concise message only — do not run `git add` or `git commit`.

## Notebook formatting
All notebooks share a single base setup via `from nb_utils.setup import base`. Do not add inline `plt.rcParams`, `pd.set_option`, `import numpy as np`, or similar boilerplate to notebooks — it belongs in `nb_utils/setup.py`.

## nb-clean
nb-clean is configured as a git filter (`nb-clean add-filter --preserve-cell-outputs`).
It strips execution counts and metadata noise on `git add` but keeps cell outputs.

## How we work together
Do not make changes to code directly. When something is wrong, explain what the problem is and suggest a correction — the user applies it.
Do not run `git add`, `git commit`, or any destructive bash commands.
Do not add unrequested dependencies, files, or configuration.
When asked for a commit message, suggest one concise line only.
If something is unclear, ask before assuming.