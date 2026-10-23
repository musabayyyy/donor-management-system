# HopeGive — Donation Management System

A Python-based **Donation Management System** with both a console interface and a Tkinter desktop application. It helps manage donors, receivers, and donations using simple text-file storage.

## Features

- Add, view, update, and delete donors, receivers, and donations
- Admin, donor, and receiver roles
- Login system with role-based access
- Input validation for CNIC, phone number, and donation amount
- Duplicate ID and duplicate CNIC prevention
- Automatic saving after every change
- Dashboard with total donations, donor/receiver counts, recent donations, and top donors
- Search and sortable tables in the desktop app
- Confirmation prompts before deleting records

## Tech Stack

- Python 3.8+
- Tkinter for the desktop UI
- Text files for data storage
- No external packages required

## Project Structure

```text
donation.py      # Backend logic and console version
donor_app.py     # Tkinter desktop application
donors.txt       # Donor records
receivers.txt    # Receiver records
donations.txt    # Donation records
users.txt        # Donor and receiver login records
```

The `.txt` files are created automatically when the program runs for the first time.

## How to Run

1. Clone this repository:

```bash
git clone <your-repository-url>
cd <repository-folder>
```

2. Make sure `donation.py` and `donor_app.py` are in the same folder.

3. Run the desktop application:

```bash
python donor_app.py
```

4. Or run the console version:

```bash
python donation.py
```

## Demo Logins

| Role | Username | Password |
|---|---|---|
| Admin | admin | admin123 |
| Donor | donor1 | 123 |
| Receiver | receiver1 | 123 |

> **Note:** These are demo credentials for educational use only. Change them before using the system for any real purpose.

## User Roles

| Role | Access |
|---|---|
| Admin | Full control: add, view, update, and delete donors, receivers, and donations |
| Donor | View donations and receivers |
| Receiver | View donations and donors |

## Architecture

The desktop application does not access the text files directly. It calls functions from `donation.py`, which handles validation, business rules, and file storage.

```text
User → donor_app.py → donation.py → text files
```

This separation keeps the same rules working for both the console and desktop versions.

## Screenshots

Add screenshots here after uploading the project:

- Login screen
- Dashboard
- Donors page
- Receivers page
- Donations page
- Console menu

Example:

```markdown
![Dashboard](screenshots/dashboard.png)
```

## Limitations

- Passwords are stored in plain text
- Data is stored in text files rather than a database
- Donations do not currently include dates or timestamps
- Donor and receiver accounts are not linked to individual records
- Every donor or receiver user can see the same data

## Future Improvements

- Hash passwords securely
- Move data storage to SQLite
- Add donation dates and monthly reports
- Export records to Excel or PDF
- Allow donors and receivers to sign up
- Link each user account to its own donor or receiver record

 

## License

This project is for educational purposes. You can add an MIT License if you want others to reuse or modify it.
