-- 유튜브 실시간 연동을 위한 추가 스키마
-- Supabase SQL Editor에서 schema.sql, seed_data.sql 다음에 실행하세요.

-- 추적할 채널 목록 (채널 없어도 우선 테이블만 생성, 나중에 Table Editor에서 행 추가)
create table if not exists tracked_channels (
  channel_id text primary key,
  channel_handle text,
  category text not null,
  added_at timestamptz not null default now()
);
alter table tracked_channels enable row level security;
-- 정책을 하나도 만들지 않음 → anon key로는 절대 조회/수정 불가, service_role만 접근 가능 (내부 설정용 테이블)

-- rankings 테이블에 실데이터 연동용 컬럼 추가
alter table rankings add column if not exists channel_id text unique;
alter table rankings add column if not exists subs_count bigint;
alter table rankings add column if not exists updated_at timestamptz;

-- rank는 매일 재계산되며 값이 서로 자리를 바꾸는 컬럼이라 primary key로 부적합하다.
-- 대신 surrogate id를 primary key로 두고 rank는 일반 정수 컬럼으로 바꾼다.
alter table rankings drop constraint if exists rankings_pkey;
alter table rankings alter column rank drop not null;
alter table rankings add column if not exists id bigserial;
alter table rankings add primary key (id);

-- 구독자 수 추이 기록 (주간 증감 계산용)
create table if not exists ranking_snapshots (
  id bigserial primary key,
  channel_id text not null,
  subs_count bigint not null,
  captured_at timestamptz not null default now()
);
alter table ranking_snapshots enable row level security;
-- 정책 없음 → service_role만 접근

-- subs_count 기준으로 rank 컬럼을 재계산하는 함수 (동기화 스크립트가 마지막에 호출)
create or replace function refresh_rankings_ranks()
returns void
language sql
security definer
as $$
  update rankings r
  set rank = sub.rn
  from (
    select channel_id, row_number() over (order by subs_count desc) as rn
    from rankings
    where subs_count is not null
  ) sub
  where sub.channel_id = r.channel_id;
$$;
