# App Store Setup Guide

A website where you share apps (APKs) stored on Telegram, organized by category,
with a hidden admin panel only you can use.

## 1. Telegram Bot (file storage)

1. Open Telegram, message **@BotFather**, run `/newbot`, get your bot **token**.
2. Create a **private channel** (e.g. "My App Storage") and add your bot as admin.
3. To upload an APK and get its `file_id`:
   - Send the APK as a **document** to your private channel.
   - Use this URL in your browser to see recent updates and find the `file_id`:
     ```
     https://api.telegram.org/bot<TOKEN>/getUpdates
     ```
   - In the JSON response, find `"document": { "file_id": "...", "file_name": "..." }`.
   - Copy that `file_id` — you'll paste it into the admin panel later.

   (Tip: easier method — create a tiny Telegram bot script later that auto-extracts
   file_id when you forward a file to it. For now, manual via getUpdates works fine.)

## 2. Supabase (database + auth)

1. Create a free project at https://supabase.com
2. Go to **SQL Editor**, paste and run `supabase-schema.sql` (included).
3. Go to **Authentication > Users**, manually create ONE user — this is your admin login
   (e.g. your email + a strong password). No public signup is exposed anywhere.
4. Go to **Project Settings > API**, copy:
   - `Project URL` → used as `SUPABASE_URL`
   - `anon` public key → used in admin panel frontend (`SUPABASE_ANON_KEY`)
   - `service_role` key → used ONLY in backend `.env` (`SUPABASE_SERVICE_ROLE_KEY`, keep secret!)

## 3. Backend (Render)

1. Push the `backend/` folder to a GitHub repo.
2. On Render: New → Web Service → connect repo → root directory = `backend`.
3. Build command: `npm install`  |  Start command: `npm start`
4. Add Environment Variables (from `.env.example`):
   - `TELEGRAM_BOT_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `ALLOWED_ORIGINS` (your frontend URL, e.g. `https://yourname.github.io`)
5. Deploy. Note your backend URL, e.g. `https://your-backend.onrender.com`

## 4. Frontend

1. In `frontend/index.html`, set:
   ```js
   const API_BASE = "https://your-backend.onrender.com";
   ```
2. In `frontend/admin/index.html`, set:
   ```js
   const SUPABASE_URL = "https://your-project.supabase.co";
   const SUPABASE_ANON_KEY = "your-anon-key";
   const API_BASE = "https://your-backend.onrender.com";
   ```
3. Host `frontend/` on GitHub Pages, Netlify, or Render static site.

## 5. Admin Panel Access

- Public site: `https://yourname.github.io/index.html`
- Admin panel: `https://yourname.github.io/admin/index.html`
  - NOT linked from the public site — only you know the URL.
  - Login with the Supabase user you created in step 2.
  - Add categories (Movies, Music, Sports, etc).
  - Add an app: name, description, icon, category, version.
  - Add Download Links — for apps needing 2 files (e.g. YouTube + MicroG),
    add TWO link rows with their own `file_id` + label. Visitors clicking
    that app see a popup with both download buttons.
  - For single-link apps, clicking the card downloads directly — no popup.

## 6. How downloads work (no Telegram visible to users)

`yoursite.com` → click app → `your-backend.onrender.com/download/<linkId>`
→ backend calls Telegram `getFile` → streams the APK bytes directly to the
user's browser. The user never sees `api.telegram.org`.

## Notes

- Telegram bot file size limit: 50MB (regular bot). For larger APKs, you may
  need a premium account / userbot approach — let me know if needed.
- `getFile` links expire (~1hr) but the backend re-fetches fresh each time,
  so this isn't an issue.
- Admin panel security relies on Supabase Auth — keep your password strong
  and don't share the `/admin` URL.
