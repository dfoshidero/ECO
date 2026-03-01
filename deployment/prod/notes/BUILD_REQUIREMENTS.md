# Build requirements

What you need to run the prod build script.

**Required**
- Bash (e.g. Git Bash, WSL)
- Python 3 (`python`, `python3`, or `py` in PATH)
- Docker (running)

**Run from repo root**
```bash
./deployment/prod/build.sh test
./deployment/prod/build.sh release patch   # or minor / major
```

**Before first build**
- Model `.pkl` files must be in `deployment/dev/models/v1/` (see `manifest.json`). Run the trainer first if needed: `cd trainers/v1 && python model_train_validate.py`
- Don’t edit `version.json` — the script manages it

**Optional (major release only)**  
For uploading a data zip to GitHub Release you need `gh` (GitHub CLI) and `zip`. If missing, the script skips that step and still builds the image.

**Windows / Git Bash**  
If `docker` or `gh` aren’t found, add them to PATH in `~/.bashrc`:
```bash
export PATH="$PATH:/c/Program Files/Docker/Docker/resources/bin"
export PATH="$PATH:/c/Program Files/GitHub CLI"
```
