# JoyBucket 🍯✨

> **Shifting church culture toward gratitude.**

JoyBucket is a "friction-free" Progressive Web App (PWA) designed for the Awesome Rock congregation to log daily moments of joy and gratitude. The app uses AI to automatically classify entries, identify spiritual themes, and alert leaders to potential crises.

---

## 🌟 Key Features

- **Instant Joy Logging**: A simple, fast interface to capture moments of gratitude.
- **AI-Powered Analysis**: Uses Gemini 1.5 Flash to auto-tag entries, score sentiment, and detect crises.
- **Crisis Alert System**: Automatically notifies church leaders via Email (Brevo) and SMS (Twilio) if an urgent entry is detected.
- **Admin Dashboard**: A secure view for pastors to oversee recent entries and high-priority alerts.
- **Progressive Web App (PWA)**: Installable on any mobile device for a native-app feel without the app store.
- **Golden Hour Aesthetic**: A warm, premium design using Tailwind CSS.

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
