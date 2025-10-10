# alert-bot (Google Sheets → Telegram)

Small Python script that watches a Google Sheet and posts alerts to a Telegram group when items expire.

What it does
- Reads worksheet `Current` from a Google Sheet (range `A1:I`).
- Expects these headers at minimum: `Appeal Number`, `End time`, `Status`, `URLs`.
- Filters rows where:
  - `URLs` is not empty, and
  - `End time` is not empty, and
  - `Status` is NOT one of `Done` or `Completed by others`.
- If a row’s `End time` is within the last 5 minutes, sends a Telegram message:
  - Message format: `Appeal no: <Appeal Number>\nExpired at: <End time>`

Important date/time details
- `End time` must be a string in the exact format `%m/%d/%Y %H:%M:%S` (e.g., `10/15/2025 17:00:00`).
- The script uses the machine’s local time for “now”; ensure your server timezone matches the sheet’s interpretation.
- Because the window is “expired within the last 5 minutes,” if you run this every minute, a single row will be sent multiple times during that 5-minute window. Adjust logic if you need strict one-time delivery.

Prerequisites
- Python 3.10+ recommended.
- A Google Cloud Service Account with the Google Sheets API enabled.
  - Share the target Google Sheet with the service account email so it can read the sheet.
- A Telegram Bot API token from @BotFather.
- The numeric chat ID of your Telegram group (e.g., from bots like @RawDataBot or @userinfobot).

Project layout
- `main.py` — core script; reads the sheet and sends messages.
- `requirements.txt` — Python dependencies.
- `Secrets/` — ignored by git; holds your local `secrets.json` and any logs.

Setup
1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Create `Secrets/secrets.json`

Place a file at `Secrets/secrets.json` with this structure (placeholders shown):

```json
{
  "GOOGLE_SHEETS_CREDENTIALS": "<the entire service-account JSON, as a single JSON-escaped string>",
  "GOOGLE_SHEETS_ID": "<your_google_sheet_id>",
  "TELEGRAM_BOT_TOKEN": "<your_telegram_bot_token>",
  "TELEGRAM_GROUP_CHAT_ID": "<your_group_chat_id>"
}
```

Notes on credentials
- `GOOGLE_SHEETS_CREDENTIALS` is the full Service Account key JSON embedded as a string.
  - One way to produce the JSON-escaped string from a file `sa.json` is:
    - macOS/Linux (zsh):

      ```bash
      python -c 'import json,sys; print(json.dumps(open("sa.json").read()))'
      ```

    - Then paste the output into `GOOGLE_SHEETS_CREDENTIALS`.
- `GOOGLE_SHEETS_ID` is the ID portion of the sheet URL: `https://docs.google.com/spreadsheets/d/<THIS_PART>/edit`.

Run it

```bash
python main.py
```

If there are rows that expired within the last 5 minutes (and match the filters), the script will send a message to your Telegram group.

Scheduling (optional)
- To run every minute via cron:

```bash
* * * * * cd /path/to/alert-bot && . .venv/bin/activate && python main.py >> Secrets/output.log 2>&1
```

- On macOS, you can also use launchd or a process supervisor (pm2, supervisord, systemd on Linux, etc.).

Customizing
- Sheet name/range: edit `SHEET_NAME` and `SHEET_RANGE` constants in `main.py`.
- Filter logic: update the pandas filtering section in `main.py` to match your rules.
- Message format: change the construction of the `Message` column in `main.py`.

Troubleshooting
- Google auth errors: ensure the service account has access to the sheet and that `GOOGLE_SHEETS_CREDENTIALS` is valid JSON (as a JSON string).
- Sheet not found: verify `GOOGLE_SHEETS_ID` and that the sheet is shared with the service account email.
- Telegram errors: double-check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_GROUP_CHAT_ID`.
- No messages: confirm the row actually meets all filters and that `End time` is in the expected format and window.
- Duplicate messages: expected if the job runs multiple times within the 5-minute window; adjust logic if undesired.

Security
- `Secrets/` is git-ignored; keep your keys here and never commit them.
- Rotate tokens/keys if exposed.

License
- This project is licensed under the GPL-3.0 (see `LICENSE`).
