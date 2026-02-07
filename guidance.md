# Project Specification: JoyBucket (Awesome Rock Church)

## 1. Executive Summary
**Goal:** A "friction-free" Progressive Web App (PWA) for the Awesome Rock congregation to log daily moments of joy and gratitude.
**Core Value:** Shifting church culture toward gratitude. The app uses AI to auto-classify entries, identify spiritual themes, and alert leaders to potential crises.
**Target Audience:** ~100 members of Awesome Rock Church (Asquith/Hornsby).

## 2. Technical Architecture ("The $0 Stack")

### **Infrastructure**
* **Framework:** Python **FastAPI** (High performance, easy async).
* **Frontend:** **HTMX** + **Tailwind CSS** (Server-side rendering, SPA feel without React complexity).
* **Database:** **PostgreSQL** via **Neon.tech** (Serverless, scales to zero cost).
    * *Why:* Cheaper and more reliable than Railway's native container for intermittent use.
* **Hosting:** **Railway** (Stateless Service).
    * *Configuration:* No persistent volume needed.
* **AI Engine:** **Gemini 1.5 Flash** (via Google Generative AI SDK).
    * *Role:* Auto-tagging, sentiment analysis, and crisis detection.

### **External Services (Free Tiers)**
* **Authentication:** **Google OAuth 2.0** (Primary).
    * *Library:* `fastapi-sso`.
* **Email (Alerts):** **Brevo** (SMTP Relay).
    * *Role:* Sending discreet crisis alerts to leaders.
* **SMS (Optional):** **Twilio** (Pay-as-you-go).
    * *Role:* Urgent alerts (controlled by Feature Flag).

## 3. User Experience (UX)

### **Authentication & Onboarding**
* **Login:** Single button: **"Continue with Google"**.
* **Session:** **1-Year Cookie** (Long-lived session to prevent "forgot password" friction).
* **Installation:** **PWA Manifest** (`manifest.json`) triggers "Add to Home Screen" prompt.

### **The "Joy Loop"**
1.  **Open App:** Instant load (cached).
2.  **Log Joy:** Large **Gold FAB (+)** opens a simple modal.
3.  **Input:** Text area + "Mic" icon for voice-to-text.
4.  **Save:** Instant "Confetti Pop" feedback (via JS/Canvas).
5.  **Feed:** Masonry/Grid view of personal history.
6.  **Aesthetics:** Use a modern, premium look with soft shadows (`shadow-md`), large rounded corners (`rounded-2xl`), and clean typography (Inter/Outfit).

## 4. Database Schema (SQLAlchemy)

### `User`
* `id`: Integer, Primary Key.
* `email`: String (Unique).
* `google_sub`: String (Google ID).
* `avatar_url`: String.
* `is_admin`: Boolean (True for Pastors).
* `created_at`: DateTime.

### `JoyEntry`
* `id`: Integer, Primary Key.
* `user_id`: ForeignKey(`User.id`).
* `content`: Text (Raw input).
* `created_at`: DateTime (Standardize on **UTC**).
* **AI Fields:**
    * `category`: String (*Faith, Family, Provision, Health, Nature, Work, Other*).
    * `tags`: JSON (List of strings).
    * `sentiment_score`: Integer (1-10).
    * `is_urgent`: Boolean (Crisis Flag).
    * `pastor_summary`: String (Short summary).

## 5. The "Crisis Alert" System (Logic Flow)

**Trigger:** `JoyEntry` saved -> Background Task (Gemini) -> Returns `is_urgent=True`.

**Action:**
1.  **Check Env Var:** `LEADER_EMAILS` (List of strings).
2.  **Send Email (Default):** via Brevo SMTP.
    * *Subject:* "🔴 JoyBucket Alert"
    * *Body:* "Urgent entry logged by [Name]. Check Dashboard."
3.  **Check Env Var:** `ENABLE_SMS` (Boolean).
    * **If True:** Send SMS via Twilio to `LEADER_PHONES`.
    * *Body:* "URGENT JoyBucket: Crisis entry detected. Check admin dashboard."

---

## 6. The Master Prompt for Antigravity

**Copy and paste the text below into your chat to generate the codebase:**

> "Build a **FastAPI** web app called 'JoyBucket'.
>
> **1. Core Stack:**
> * **Backend:** FastAPI with `uvicorn`.
> * **Frontend:** Jinja2 Templates + **Tailwind CSS** (CDN) + **HTMX** (CDN).
> * **Database:** SQLAlchemy with **PostgreSQL**. Configure it to connect to an external URL (Neon) via `DATABASE_URL`.
> * **Deployment:** Optimize for **Railway** (read PORT env var).
>
> **2. Authentication (Google Only):**
> * Use `fastapi-sso` to implement **Google OAuth 2.0**.
> * Create a `/login/google` route and a callback route.
> * On success, set a **1-year HTTP-only session cookie**.
> * Protect routes: If no cookie, redirect to a Landing Page with a single 'Continue with Google' button.
>
> **3. Data Models:**
> * `User`: id, email, google_sub, avatar_url, is_admin (bool).
> * `JoyEntry`: id, user_id, content, created_at, category, sentiment_score, is_urgent (bool).
>
> **4. AI Automation (Gemini 1.5 Flash):**
> * Create a background task that runs on every new entry.
> * Send text to Gemini. **System Prompt:** 'Analyze text. Return JSON: category (Faith, Family, Work, Health, Nature), sentiment (1-10), is_urgent (Boolean - True if self-harm/abuse/crisis detected).'
> * Update the DB record with results.
>
> **5. Crisis Alert System:**
> * If `is_urgent` is True:
>     * **Email:** Send an alert to `LEADER_EMAILS` (env var) using **Brevo SMTP** settings (`smtp-relay.brevo.com`).
>     * **SMS (Feature Flag):** If `ENABLE_SMS` is 'True', send an SMS to `LEADER_PHONES` using the `twilio` library.
>
> **6. UI Theme ('Golden Hour'):**
> * **Colors:** Primary `Amber-500`, Background `Slate-50`.
> * **Home:** A 'Masonry Grid' feed of the user's past entries.
> * **Action:** A large Floating Action Button (FAB) that opens a modal to log joy.
> * **Dashboard:** Admin-only view (`/dashboard`) showing a list of recent entries and a high-priority 'Alerts' box.
>
> **7. PWA:**
> * Generate `manifest.json` for 'Add to Home Screen' functionality."