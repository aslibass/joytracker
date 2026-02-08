# JoyBucket 🍯✨

> **Shifting church culture toward gratitude.**

JoyBucket is a "friction-free" Progressive Web App (PWA) designed for the Awesome Rock congregation to log daily moments of joy and gratitude. The app uses AI to automatically classify entries, identify spiritual themes, and alert leaders to potential crises.

---

## 🌟 Key Features

- **Pastoral Command Center**: A professional, high-density 3-column dashboard for rapid community oversight.
- **Member Soul Trends**: Track individual spiritual health history with custom SVG **Sparklines**.
- **Soul Trajectory Tracking**: Automatically identifies members who are *Thriving*, *Steady*, or *Struggling*.
- **AI-Powered Analysis**: Deep sentiment analysis and crisis detection via Gemini 2.0 Flash.
- **Crisis Alert System**: Real-time notifications via Email and SMS for urgent pastoral needs.
- **PWA Ready**: Installable "Golden Hour" themed interface for friction-free joy logging.

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Frontend**: [HTMX](https://htmx.org/) + [Tailwind CSS](https://tailwindcss.com/) + Jinja2 Templates
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Recommended: [Neon.tech](https://neon.tech/))
- **AI Engine**: [Google Gemini 1.5 Flash](https://ai.google.dev/)
- **Auth**: Google OAuth 2.0 via `fastapi-sso`
- **Alerts**: [Brevo](https://www.brevo.com/) (Email) & [Twilio](https://www.twilio.com/) (SMS)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A PostgreSQL database (e.g., Neon or local)
- Google Cloud Console Project (for OAuth 2.0 credentials)
- Google AI Studio API Key (for Gemini)
- Brevo Account (for SMTP relay)
- Twilio Account (Optional, for SMS alerts)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/viren/joytracker.git
   cd joytracker
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```
   The app will be available at `http://localhost:8000`.

---

## ⚙️ Environment Variables

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | Your PostgreSQL connection string. |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID from Google Cloud Console. |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client Secret from Google Cloud Console. |
| `GEMINI_API_KEY` | API Key for Google Generative AI (Gemini 1.5 Flash). |
| `SMTP_LOGIN` | Brevo SMTP login (email address). |
| `SMTP_PASSWORD` | Brevo SMTP master password or API key. |
| `LEADER_EMAILS` | Comma-separated list of emails to receive alerts. |
| `LEADER_PHONES` | Comma-separated list of phone numbers for SMS alerts. |
| `ENABLE_SMS` | Set to `True` to enable Twilio SMS alerts. |
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID. |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token. |
| `TWILIO_NUMBER` | Your Twilio phone number. |
| `SECRET_KEY` | A long, random string for session security. |

---

## 📱 PWA Installation

To install JoyBucket on your mobile device:
1. Open the app URL in your mobile browser (Safari on iOS, Chrome on Android).
2. Tap the **Share/Menu** icon.
3. Select **"Add to Home Screen"**.

---

## 🛡️ Admin Access

To grant a user admin privileges, update the `is_admin` column in the `users` table for their record:
```sql
UPDATE users SET is_admin = True WHERE email = 'pastor@example.com';
```
Admins can access the dashboard at `/dashboard`.

---

## 🗄️ Database Migrations

JoyBucket uses **Alembic** to manage database schema changes.

### Initial Setup (Already Done)
The project comes with an initial migration that creates the `users` and `joy_entries` tables.

### Running Migrations
To bring your database up to date with the latest schema:
```bash
alembic upgrade head
```

### Creating New Migrations
If you modify `models.py`, generate a new migration script:
```bash
alembic revision --autogenerate -m "Describe your changes"
```
Then apply it:
```bash
alembic upgrade head
```
