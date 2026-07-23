-- 유소년 축구 채널 랭킹 스키마
-- Supabase SQL Editor에서 실행하세요. (기존 schema.sql 등과 독립적으로 실행 가능)

create table if not exists youth_channels (
  channel_id text primary key,
  name text not null,
  handle text,                    -- 예: '@kickofflife'
  thumbnail_url text,
  subs_count bigint not null default 0,
  video_count bigint,
  latest_video_id text,
  latest_video_title text,
  latest_upload_at timestamptz,
  is_pinned boolean not null default false,  -- kickofflife 같은 고정 채널
  updated_at timestamptz not null default now()
);

alter table youth_channels enable row level security;
drop policy if exists "public read youth_channels" on youth_channels;
create policy "public read youth_channels" on youth_channels
  for select using (true);
-- 쓰기 정책 없음 → anon key로는 조회만 가능, 갱신은 service_role(동기화 스크립트)만 가능
