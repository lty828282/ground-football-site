-- 그라운드 사이트 스키마
-- Supabase SQL Editor에서 실행하세요.

create table if not exists posts (
  id text primary key,
  category text not null,
  category_label text not null,
  tag text not null,
  title text not null,
  excerpt text not null,
  content text[] not null default '{}',
  icon text not null default 'ball',
  video boolean not null default false,
  duration text,
  views integer not null default 0,
  comments integer not null default 0,
  date date not null,
  popular boolean not null default false,
  rank integer
);

create table if not exists rankings (
  rank integer primary key,
  name text not null,
  subs text not null,
  delta numeric not null,
  category text not null
);

create table if not exists ticker_items (
  id serial primary key,
  label text not null,
  text text not null,
  sort_order integer not null default 0
);

-- RLS 활성화: 기본적으로 아무도 접근 못하게 막고, 아래 정책으로 "읽기만" 허용
alter table posts enable row level security;
alter table rankings enable row level security;
alter table ticker_items enable row level security;

drop policy if exists "public read posts" on posts;
create policy "public read posts" on posts
  for select using (true);

drop policy if exists "public read rankings" on rankings;
create policy "public read rankings" on rankings
  for select using (true);

drop policy if exists "public read ticker" on ticker_items;
create policy "public read ticker" on ticker_items
  for select using (true);

-- insert/update/delete 정책은 만들지 않음 → anon key로는 쓰기가 아예 불가능
