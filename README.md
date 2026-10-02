# Impilo Directory Bot

Automated discovery and tracking of South African business-directory listing opportunities for Impilo Drilling.

## Current capabilities
- Scans seeded directory pages
- Detects listing forms and free-listing signals
- Flags account/verification and CAPTCHA/anti-bot requirements
- Finds likely submission links on the same site
- Writes results to CSV
- GitHub Actions workflow for internet-connected scans

The bot does not bypass CAPTCHAs, anti-bot controls, or ownership verification.

## Run locally

```bash
pip install -r requirements.txt
python impilo_directory_bot.py
```

The output is written to `impilo_directory_targets.csv`.
