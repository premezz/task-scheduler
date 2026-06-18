# 📬 Outlook Email Sorter

An AI-powered web app that reads unread emails from Microsoft Outlook and automatically sorts them into predefined folders using Claude AI.

---

## What It Does

1. User signs in with their Microsoft account via a secure popup (OAuth 2.0 PKCE)
2. The app fetches up to 25 unread emails from the Outlook Inbox via Microsoft Graph API
3. Claude AI reads each email's subject, sender, and preview and assigns it to a folder
4. User reviews the AI's categorization and can override any decision
5. Clicks "Move All" and the emails are moved into the correct Outlook folders

---

## Target Folders

The app categorizes emails into these three Outlook folders (must exist in Outlook already):

| Folder | What goes here |
|--------|---------------|
| **Quotes** | Price quotes, estimates, bids, proposals, pricing requests |
| **Voicemails** | Voicemail notification emails and transcriptions |
| **Sam S** | Emails from or about a person named Sam S (last name starting with S) |
| **Uncategorized** | Anything that doesn't fit the above — left in Inbox untouched |

---

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JavaScript (single file, no framework)
- **Auth:** Microsoft OAuth 2.0 with PKCE (no external auth libraries — uses native `crypto.subtle`)
- **Email API:** Microsoft Graph API (`/v1.0/me/mailFolders`, `/v1.0/me/messages`)
- **AI:** Anthropic Claude API (`claude-sonnet-4-6`) for email categorization
- **No backend required** — runs entirely in the browser

---

## File Structure

```
task-scheduler/
├── email-sorter.html       # Main app (single file, self-contained)
├── README.md               # This file
└── .gitignore
```

---

## Azure App Registration Setup (One-Time)

Before using the app, you need a free Microsoft Azure App Registration:

1. Go to [Azure App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
   - Name: `Email Sorter` (or anything)
   - Supported account types: **Accounts in any organizational directory and personal Microsoft accounts (Multitenant)**
3. After registering, go to **Authentication**
   - Add a platform → **Single-page application (SPA)**
   - Redirect URI: `https://claude.ai` (or your hosted URL)
4. Go to **Manifest** and set:
   ```json
   "requestedAccessTokenVersion": 2
   ```
5. Go to **API permissions → Add → Microsoft Graph → Delegated**
   - Add `Mail.Read`
   - Add `Mail.ReadWrite`
6. Copy the **Application (client) ID** from the Overview page

---

## How to Run

Since this is a single HTML file, just open it in a browser:

```bash
# Option 1 — open directly
start email-sorter.html

# Option 2 — serve locally (avoids any browser restrictions)
npx serve .
# then open http://localhost:3000/email-sorter.html
```

---

## Known Considerations

- **Admin consent:** If your Microsoft account is part of a company Azure AD tenant, your IT admin may need to grant consent for the Mail permissions. They can do so at:
  ```
  https://login.microsoftonline.com/common/adminconsent?client_id=YOUR_CLIENT_ID
  ```
- **Folder names must match exactly** — the app looks for folders named `Quotes`, `Voicemails`, and `Sam S` in Outlook. Capitalization and spacing must match.
- **Token expiry:** The Microsoft access token expires after ~1 hour. If it expires mid-session, sign out and sign back in.
- **Popup blockers:** The Microsoft sign-in uses a popup window. Make sure popups are allowed for the domain you're running the app from.

---

## Future Improvements

- [ ] Add more folders / categories via a settings UI
- [ ] Auto-run on a schedule (requires a backend + refresh tokens)
- [ ] Show email count badges per folder
- [ ] Support moving emails across multiple Outlook accounts
- [ ] Add a backend (Flask/FastAPI) for more reliable OAuth and token refresh
