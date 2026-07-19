-- 뉴스/영상 실시간 연동 스키마

create table if not exists news_articles (
  id bigserial primary key,
  title text not null,
  summary text not null default '',
  link text not null unique,
  source text,
  published_at timestamptz,
  fetched_at timestamptz not null default now()
);
alter table news_articles enable row level security;
drop policy if exists "public read news" on news_articles;
create policy "public read news" on news_articles
  for select using (true);

create table if not exists videos (
  video_id text primary key,
  section text not null,          -- 'training' | 'youth' | 'review'
  title text not null,
  channel_title text not null,
  thumbnail_url text not null,
  view_count bigint not null default 0,
  published_at timestamptz not null,
  fetched_at timestamptz not null default now()
);
alter table videos enable row level security;
drop policy if exists "public read videos" on videos;
create policy "public read videos" on videos
  for select using (true);
