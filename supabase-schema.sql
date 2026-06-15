-- =========================================================
-- APP STORE SCHEMA (Supabase / Postgres)
-- =========================================================

-- 1. Categories table
create table categories (
  id          uuid primary key default gen_random_uuid(),
  name        text not null unique,         -- e.g. "Movies", "Music", "Sports", "Tools"
  sort_order  int default 0,
  created_at  timestamptz default now()
);

-- 2. Apps table
create table apps (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,              -- e.g. "YouTube"
  description   text,                       -- editable description
  icon_url      text,                       -- icon image url (stored in Supabase Storage or external)
  category_id   uuid references categories(id) on delete set null,
  version       text,
  is_published  boolean default true,       -- toggle visibility on public site
  sort_order    int default 0,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

-- 3. App download links (supports multi-app bundles, e.g. YouTube + MicroG)
create table app_links (
  id                uuid primary key default gen_random_uuid(),
  app_id            uuid references apps(id) on delete cascade,
  label             text not null,          -- e.g. "YouTube" / "MicroG Services"
  telegram_file_id  text not null,          -- file_id from your Telegram storage bot
  file_name         text,                   -- e.g. "youtube.apk" (used for Content-Disposition)
  sort_order        int default 0,
  created_at        timestamptz default now()
);

-- =========================================================
-- ROW LEVEL SECURITY
-- Public (anon) can READ published apps + their links + categories.
-- Only authenticated admin (you) can INSERT/UPDATE/DELETE.
-- =========================================================

alter table categories enable row level security;
alter table apps enable row level security;
alter table app_links enable row level security;

-- Public read access
create policy "Public read categories"
  on categories for select
  using (true);

create policy "Public read published apps"
  on apps for select
  using (is_published = true);

create policy "Public read app links of published apps"
  on app_links for select
  using (
    exists (
      select 1 from apps
      where apps.id = app_links.app_id
      and apps.is_published = true
    )
  );

-- Admin (authenticated) full access
create policy "Admin manage categories"
  on categories for all
  using (auth.role() = 'authenticated')
  with check (auth.role() = 'authenticated');

create policy "Admin manage apps"
  on apps for all
  using (auth.role() = 'authenticated')
  with check (auth.role() = 'authenticated');

create policy "Admin manage app_links"
  on app_links for all
  using (auth.role() = 'authenticated')
  with check (auth.role() = 'authenticated');

-- Admin needs to see UNPUBLISHED apps too (separate policy)
create policy "Admin read all apps"
  on apps for select
  using (auth.role() = 'authenticated');

create policy "Admin read all app_links"
  on app_links for select
  using (auth.role() = 'authenticated');

-- =========================================================
-- SEED CATEGORIES (optional - run once)
-- =========================================================
insert into categories (name, sort_order) values
  ('Movies', 1),
  ('Music', 2),
  ('Sports', 3),
  ('Tools', 4),
  ('Games', 5);
