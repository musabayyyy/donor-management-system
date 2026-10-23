# HopeGive — Donation Management System

A Python donation management project with a console interface and a Tkinter desktop application. Manage donors, receivers, and donation records using local text-file storage.

> Educational demo only. Do not use this version with real personal or financial records. It uses demo credentials and plaintext password storage.

## Features

- Add, view, update, and delete donors, receivers, and donations
- Admin, donor, and receiver roles
- CNIC, phone number, and donation amount validation
- Duplicate ID and CNIC prevention
- Automatic saving after changes
- Dashboard with totals, recent donations, and top donors
- Search and sortable tables in the desktop application
- Confirmation prompts before deletion
- Protection against deleting donors or receivers with linked donations

## Requirements

- Python 3.8 or newer
- Tkinter available in your Python installation for the desktop version
- No third-party pip packages required

## Project Structure

```text
.
├── README.md
├── .gitignore
├── .gitattributes
├── donor.py         # Backend logic and console interface
└── donor_app.py     # Tkinter desktop application
```

Runtime data is stored locally in `donors.txt`, `receivers.txt`, `donations.txt`, and `users.txt`. Missing files are handled on startup; files are created when user accounts or records are saved. These filenames are listed in `.gitignore` and should not be committed.

## Getting Started

Clone the repository and enter its directory:

```bash
git clone https://github.com/musabayyyy/donor-management-system.git
cd donor-management-system
```

Run the desktop application:

```bash
python donor_app.py
```

Or run the console interface:

```bash
python donor.py
```

Keep `donor.py` and `donor_app.py` together. Run commands from the project directory so local data files stay in that directory.

## Demo Accounts

| Role | Username | Password |
|---|---|---|
| Admin | admin | admin123 |
| Donor | donor1 | 123 |
| Receiver | receiver1 | 123 |

These are public demo credentials, not secure production accounts. Donor and receiver defaults are created when no users are loaded. The admin credentials are defined in `donor.py`.

## User Roles

| Role | Access |
|---|---|
| Admin | Manage donors, receivers, and donations |
| Donor | View donations and receivers |
| Receiver | View donations and donors |

Accounts are not currently linked to individual donor or receiver records. Users with the same role share the same view rather than a private personal dashboard.

## Architecture

```text
Desktop interface (donor_app.py)
              ↓
Backend and validation (donor.py)
              ↓
Local text files
```

The desktop interface imports the backend from `donor.py`. The console interface uses the same record-management methods, keeping validation and storage logic in one place.

## Data Privacy

- Use fictional data for demonstrations and screenshots.
- Keep generated records and login files on your computer, outside version control.
- When uploading through GitHub's website, manually exclude private files and `__pycache__`; do not rely on `.gitignore` to filter browser uploads.
- `.gitignore` does not remove files or personal information already committed to history.

## Current Limitations

- Passwords are stored in plaintext, and admin credentials are hard-coded.
- Records use text files rather than a database.
- Donations have no date or timestamp.
- User accounts are not linked to individual records.
- This project is a learning demo, not a production-ready charity system.

## Future Improvements

- Secure password hashing and configurable administrator credentials
- SQLite storage
- Donation dates and monthly reports
- Excel or PDF exports
- Registration and account-specific record access

## Credits

- Backend and core logic: Musab Mehmood
- Desktop UI/UX: developed with AI assistance
- Bug fixes and input-validation improvements: developed with AI assistance
