# MathCodeBench pipeline

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run order
1. extract CodeContests
2. extract LiveCodeBench
3. detect math candidates
4. create annotation template
5. manually/LLM annotate and validate
6. deduplicate
7. make leakage-aware splits
8. validate every split

See the commands in the ChatGPT response that accompanied this package.
