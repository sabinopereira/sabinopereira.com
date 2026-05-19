-- OutOfLoop MVP Beta Core schema

create extension if not exists pgcrypto;

create type public.mission_mode as enum ('coragem', 'social', 'familia', 'saude', 'recomeco');
create type public.mission_intensity as enum ('leve', 'real', 'coragem');
create type public.mission_duration_label as enum ('micro', 'leve', 'realista', 'plano', 'maior');
create type public.cost_tier as enum ('gratis', 'low_cost', 'medio', 'especial');
create type public.circle_category as enum ('familia', 'amigos', 'gym', 'futebol', 'escola_pais', 'igreja_comunidade', 'trabalho', 'bairro', 'outro');
create type public.circle_role as enum ('owner', 'host', 'helper', 'member');
create type public.circle_member_status as enum ('invited', 'active', 'removed', 'left');
create type public.mission_assignment_status as enum ('suggested', 'accepted', 'completed', 'skipped', 'saved', 'expired', 'paused');
create type public.today_not_available_reason as enum ('sem_tempo', 'sem_energia', 'dificil_demais', 'tipo_errado', 'mau_dia', 'guardar', 'mais_leve');
create type public.event_status as enum ('draft', 'open', 'confirmed', 'cancelled', 'completed', 'archived');
create type public.event_participant_status as enum ('invited', 'interested', 'accepted', 'declined', 'attended', 'no_show', 'cancelled');
create type public.noise_level as enum ('quiet', 'moderate', 'loud', 'unknown');
create type public.walking_distance_level as enum ('low', 'medium', 'high', 'unknown');
create type public.report_status as enum ('open', 'reviewing', 'resolved', 'dismissed');
create type public.moderation_action_type as enum ('warning', 'comment_hidden', 'user_removed', 'user_blocked', 'event_cancelled', 'content_deleted');

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null,
  avatar_url text,
  city text,
  area text,
  age_range text,
  main_routine text,
  has_children boolean,
  living_situation text,
  primary_mode public.mission_mode,
  secondary_mode public.mission_mode,
  preferred_intensity public.mission_intensity default 'leve',
  preferred_cost_tier public.cost_tier default 'low_cost',
  distance_km int default 5 check (distance_km > 0),
  social_comfort text,
  new_people_preference text,
  community_preference text default 'private_first',
  energy_type text,
  mission_paused boolean default false,
  preferred_notification_time time,
  onboarding_completed boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create trigger set_profiles_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

create table public.profile_availability (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  day_of_week int not null check (day_of_week between 0 and 6),
  time_block text not null,
  is_available boolean default true,
  created_at timestamptz default now()
);

create table public.accessibility_preferences (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  step_free_access boolean default false,
  seated_activity boolean default false,
  quiet_places boolean default false,
  short_walking_distance boolean default false,
  predictable_plan boolean default false,
  support_companion boolean default false,
  small_groups boolean default false,
  text_communication boolean default false,
  audio_communication boolean default false,
  notes text,
  share_with_hosts_by_default boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create trigger set_accessibility_preferences_updated_at
before update on public.accessibility_preferences
for each row execute function public.set_updated_at();

create table public.circles (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  category public.circle_category not null,
  description text,
  privacy text default 'invite_only',
  owner_id uuid not null references public.profiles(id) on delete cascade,
  code_of_conduct_accepted boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  archived_at timestamptz
);

create trigger set_circles_updated_at
before update on public.circles
for each row execute function public.set_updated_at();

create table public.circle_members (
  id uuid primary key default gen_random_uuid(),
  circle_id uuid not null references public.circles(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  role public.circle_role default 'member',
  status public.circle_member_status default 'active',
  invited_by uuid references public.profiles(id),
  joined_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique (circle_id, user_id)
);

create trigger set_circle_members_updated_at
before update on public.circle_members
for each row execute function public.set_updated_at();

create table public.invites (
  id uuid primary key default gen_random_uuid(),
  circle_id uuid not null references public.circles(id) on delete cascade,
  created_by uuid not null references public.profiles(id),
  token text unique not null,
  max_uses int,
  uses_count int default 0,
  expires_at timestamptz,
  created_at timestamptz default now(),
  revoked_at timestamptz
);

create table public.missions (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  description text not null,
  mode public.mission_mode not null,
  intensity public.mission_intensity not null,
  cost_tier public.cost_tier default 'gratis',
  estimated_minutes int not null check (estimated_minutes > 0),
  duration_label public.mission_duration_label not null,
  recommended_day_mask int,
  recommended_time_blocks text[],
  solo_enabled boolean default true,
  pair_enabled boolean default true,
  group_enabled boolean default true,
  family_enabled boolean default false,
  accessibility_notes text,
  accessible_alternative_title text,
  accessible_alternative_description text,
  active boolean default true,
  created_at timestamptz default now()
);

create table public.mission_assignments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  mission_id uuid references public.missions(id),
  assigned_for date not null,
  status public.mission_assignment_status default 'suggested',
  accepted_at timestamptz,
  completed_at timestamptz,
  expires_at timestamptz,
  source text default 'rules_engine',
  personalization_reason text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique (user_id, assigned_for)
);

create trigger set_mission_assignments_updated_at
before update on public.mission_assignments
for each row execute function public.set_updated_at();

create table public.mission_feedback (
  id uuid primary key default gen_random_uuid(),
  assignment_id uuid not null references public.mission_assignments(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  liked boolean,
  difficulty text,
  would_repeat boolean,
  done_with text,
  felt_energy boolean,
  felt_connection boolean,
  felt_courage boolean,
  felt_calm boolean,
  today_not_available_reason public.today_not_available_reason,
  note text,
  created_at timestamptz default now()
);

create table public.events (
  id uuid primary key default gen_random_uuid(),
  circle_id uuid not null references public.circles(id) on delete cascade,
  created_by uuid not null references public.profiles(id),
  host_id uuid references public.profiles(id),
  helper_id uuid references public.profiles(id),
  mission_assignment_id uuid references public.mission_assignments(id),
  title text not null,
  description text,
  status public.event_status default 'draft',
  starts_at timestamptz not null,
  ends_at timestamptz,
  acceptance_deadline timestamptz not null,
  place_name text,
  place_address text,
  location_note text,
  cost_tier public.cost_tier default 'gratis',
  min_participants int default 2 check (min_participants > 0),
  max_participants int check (max_participants is null or max_participants > 0),
  memories_enabled boolean default true,
  public_place_required boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  cancelled_at timestamptz,
  completed_at timestamptz
);

create trigger set_events_updated_at
before update on public.events
for each row execute function public.set_updated_at();

create table public.event_accessibility (
  event_id uuid primary key references public.events(id) on delete cascade,
  step_free_access boolean,
  accessible_bathroom text default 'unknown',
  seating_available boolean,
  public_transport_nearby boolean,
  parking_nearby boolean,
  noise_level public.noise_level default 'unknown',
  walking_distance public.walking_distance_level default 'unknown',
  standing_required boolean,
  family_friendly boolean default false,
  support_companion_allowed boolean default true,
  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create trigger set_event_accessibility_updated_at
before update on public.event_accessibility
for each row execute function public.set_updated_at();

create table public.event_participants (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  status public.event_participant_status default 'accepted',
  wants_host_welcome boolean default false,
  bringing_support_companion boolean default false,
  support_companion_count int default 0 check (support_companion_count >= 0),
  shared_accessibility_note text,
  checked_in_at timestamptz,
  checked_out_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique (event_id, user_id)
);

create trigger set_event_participants_updated_at
before update on public.event_participants
for each row execute function public.set_updated_at();

create table public.event_feedback (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  liked boolean,
  felt_included boolean,
  would_repeat boolean,
  felt_safe boolean,
  accessibility_ok boolean,
  cost_ok boolean,
  note text,
  created_at timestamptz default now(),
  unique (event_id, user_id)
);

create table public.private_memories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  mission_assignment_id uuid references public.mission_assignments(id) on delete set null,
  type text not null check (type in ('photo', 'text')),
  photo_url text,
  text_body text,
  created_at timestamptz default now(),
  deleted_at timestamptz
);

create table public.event_memories (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  type text not null check (type in ('photo', 'text')),
  photo_url text,
  text_body text,
  status text default 'active',
  created_at timestamptz default now(),
  removed_at timestamptz,
  removed_by uuid references public.profiles(id)
);

create table public.host_roles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  scope text not null,
  circle_id uuid references public.circles(id) on delete cascade,
  level text default 'helper',
  verified_at timestamptz,
  created_by uuid references public.profiles(id),
  created_at timestamptz default now(),
  revoked_at timestamptz
);

create table public.reports (
  id uuid primary key default gen_random_uuid(),
  reporter_id uuid not null references public.profiles(id),
  target_type text not null,
  target_id uuid not null,
  circle_id uuid references public.circles(id),
  event_id uuid references public.events(id),
  reason text not null,
  details text,
  status public.report_status default 'open',
  created_at timestamptz default now(),
  resolved_at timestamptz,
  resolved_by uuid references public.profiles(id)
);

create table public.moderation_actions (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references public.profiles(id),
  action_type public.moderation_action_type not null,
  target_type text not null,
  target_id uuid not null,
  circle_id uuid references public.circles(id),
  event_id uuid references public.events(id),
  reason text,
  metadata jsonb,
  created_at timestamptz default now()
);

create table public.blocks (
  id uuid primary key default gen_random_uuid(),
  blocker_id uuid not null references public.profiles(id) on delete cascade,
  blocked_id uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz default now(),
  unique (blocker_id, blocked_id),
  check (blocker_id <> blocked_id)
);

create index profiles_city_area_idx on public.profiles(city, area);
create index circle_members_user_status_idx on public.circle_members(user_id, status);
create index circle_members_circle_status_idx on public.circle_members(circle_id, status);
create index events_circle_status_starts_idx on public.events(circle_id, status, starts_at);
create index events_host_starts_idx on public.events(host_id, starts_at);
create index events_acceptance_deadline_idx on public.events(acceptance_deadline);
create index event_participants_user_status_idx on public.event_participants(user_id, status);
create index event_participants_event_status_idx on public.event_participants(event_id, status);
create index event_memories_event_status_created_idx on public.event_memories(event_id, status, created_at);
create index private_memories_user_created_idx on public.private_memories(user_id, created_at);
create index mission_assignments_user_assigned_idx on public.mission_assignments(user_id, assigned_for);
create index mission_feedback_user_created_idx on public.mission_feedback(user_id, created_at);
create index reports_status_created_idx on public.reports(status, created_at);

create or replace function public.is_circle_member(circle_uuid uuid, user_uuid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.circle_members cm
    where cm.circle_id = circle_uuid
      and cm.user_id = user_uuid
      and cm.status = 'active'
  );
$$;

create or replace function public.is_circle_host(circle_uuid uuid, user_uuid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.circle_members cm
    where cm.circle_id = circle_uuid
      and cm.user_id = user_uuid
      and cm.status = 'active'
      and cm.role in ('owner', 'host', 'helper')
  );
$$;

create or replace function public.is_event_participant(event_uuid uuid, user_uuid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.event_participants ep
    where ep.event_id = event_uuid
      and ep.user_id = user_uuid
      and ep.status in ('accepted', 'attended')
  );
$$;

create or replace function public.is_event_host(event_uuid uuid, user_uuid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.events e
    where e.id = event_uuid
      and (e.host_id = user_uuid or e.helper_id = user_uuid or e.created_by = user_uuid)
  );
$$;

create or replace function public.can_view_event(event_uuid uuid, user_uuid uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.events e
    where e.id = event_uuid
      and public.is_circle_member(e.circle_id, user_uuid)
  );
$$;

create or replace function public.shares_circle(user_a uuid, user_b uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.circle_members a
    join public.circle_members b on b.circle_id = a.circle_id
    where a.user_id = user_a
      and b.user_id = user_b
      and a.status = 'active'
      and b.status = 'active'
  );
$$;

create or replace function public.assign_daily_mission(target_date date default current_date)
returns public.mission_assignments
language plpgsql
security definer
set search_path = public
as $$
declare
  current_user_id uuid := auth.uid();
  profile_row public.profiles%rowtype;
  existing_assignment public.mission_assignments%rowtype;
  chosen_mission_id uuid;
  new_assignment public.mission_assignments%rowtype;
begin
  if current_user_id is null then
    raise exception 'assign_daily_mission requires an authenticated user';
  end if;

  select *
  into existing_assignment
  from public.mission_assignments
  where user_id = current_user_id
    and assigned_for = target_date;

  if found then
    return existing_assignment;
  end if;

  select *
  into profile_row
  from public.profiles
  where id = current_user_id;

  if not found then
    raise exception 'profile not found for current user';
  end if;

  select m.id
  into chosen_mission_id
  from public.missions m
  where m.active = true
    and (
      profile_row.primary_mode is null
      or m.mode = profile_row.primary_mode
      or m.mode = profile_row.secondary_mode
    )
    and (
      profile_row.community_preference is distinct from 'private_first'
      or m.solo_enabled = true
    )
  order by
    case when m.mode = profile_row.primary_mode then 6 else 0 end +
    case when m.mode = profile_row.secondary_mode then 3 else 0 end +
    case when m.intensity = profile_row.preferred_intensity then 2 else 0 end +
    case when m.cost_tier = profile_row.preferred_cost_tier then 2 else 0 end +
    case when m.cost_tier = 'gratis' then 1 else 0 end +
    case when profile_row.has_children = true and m.family_enabled = true then 2 else 0 end +
    random()
  desc
  limit 1;

  if chosen_mission_id is null then
    select m.id
    into chosen_mission_id
    from public.missions m
    where m.active = true
    order by random()
    limit 1;
  end if;

  insert into public.mission_assignments (
    user_id,
    mission_id,
    assigned_for,
    status,
    expires_at,
    personalization_reason
  )
  values (
    current_user_id,
    chosen_mission_id,
    target_date,
    'suggested',
    (target_date + interval '1 day')::timestamptz,
    'Chosen by mode, intensity, cost, family context, and community preference.'
  )
  returning *
  into new_assignment;

  return new_assignment;
end;
$$;

alter table public.profiles enable row level security;
alter table public.profile_availability enable row level security;
alter table public.accessibility_preferences enable row level security;
alter table public.circles enable row level security;
alter table public.circle_members enable row level security;
alter table public.invites enable row level security;
alter table public.missions enable row level security;
alter table public.mission_assignments enable row level security;
alter table public.mission_feedback enable row level security;
alter table public.events enable row level security;
alter table public.event_accessibility enable row level security;
alter table public.event_participants enable row level security;
alter table public.event_feedback enable row level security;
alter table public.private_memories enable row level security;
alter table public.event_memories enable row level security;
alter table public.host_roles enable row level security;
alter table public.reports enable row level security;
alter table public.moderation_actions enable row level security;
alter table public.blocks enable row level security;

create policy "profiles_select_own_or_shared_circle" on public.profiles
for select using (id = auth.uid() or public.shares_circle(id, auth.uid()));
create policy "profiles_insert_own" on public.profiles for insert with check (id = auth.uid());
create policy "profiles_update_own" on public.profiles for update using (id = auth.uid()) with check (id = auth.uid());

create policy "profile_availability_owner_all" on public.profile_availability
for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "accessibility_preferences_owner_all" on public.accessibility_preferences
for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "circles_select_members" on public.circles
for select using (public.is_circle_member(id, auth.uid()));
create policy "circles_insert_owner" on public.circles
for insert with check (owner_id = auth.uid());
create policy "circles_update_hosts" on public.circles
for update using (public.is_circle_host(id, auth.uid())) with check (public.is_circle_host(id, auth.uid()));

create policy "circle_members_select_circle_members" on public.circle_members
for select using (public.is_circle_member(circle_id, auth.uid()) or user_id = auth.uid());
create policy "circle_members_insert_hosts" on public.circle_members
for insert with check (
  public.is_circle_host(circle_id, auth.uid())
  or (
    user_id = auth.uid()
    and exists (
      select 1
      from public.circles c
      where c.id = circle_id
        and c.owner_id = auth.uid()
    )
  )
);
create policy "circle_members_update_self_or_hosts" on public.circle_members
for update using (user_id = auth.uid() or public.is_circle_host(circle_id, auth.uid()))
with check (user_id = auth.uid() or public.is_circle_host(circle_id, auth.uid()));

create policy "invites_select_hosts" on public.invites
for select using (public.is_circle_host(circle_id, auth.uid()));
create policy "invites_insert_hosts" on public.invites
for insert with check (public.is_circle_host(circle_id, auth.uid()));
create policy "invites_update_hosts" on public.invites
for update using (public.is_circle_host(circle_id, auth.uid())) with check (public.is_circle_host(circle_id, auth.uid()));

create policy "missions_select_active" on public.missions
for select to authenticated using (active = true);

create policy "mission_assignments_owner_all" on public.mission_assignments
for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "mission_feedback_owner_all" on public.mission_feedback
for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "events_select_circle_members" on public.events
for select using (public.is_circle_member(circle_id, auth.uid()));
create policy "events_insert_circle_members" on public.events
for insert with check (public.is_circle_member(circle_id, auth.uid()) and created_by = auth.uid());
create policy "events_update_hosts" on public.events
for update using (public.is_event_host(id, auth.uid()) or public.is_circle_host(circle_id, auth.uid()))
with check (public.is_event_host(id, auth.uid()) or public.is_circle_host(circle_id, auth.uid()));

create policy "event_accessibility_select_event_viewers" on public.event_accessibility
for select using (public.can_view_event(event_id, auth.uid()));
create policy "event_accessibility_insert_hosts" on public.event_accessibility
for insert with check (public.is_event_host(event_id, auth.uid()));
create policy "event_accessibility_update_hosts" on public.event_accessibility
for update using (public.is_event_host(event_id, auth.uid())) with check (public.is_event_host(event_id, auth.uid()));

create policy "event_participants_select_event_viewers" on public.event_participants
for select using (public.can_view_event(event_id, auth.uid()));
create policy "event_participants_insert_self" on public.event_participants
for insert with check (user_id = auth.uid() and public.can_view_event(event_id, auth.uid()));
create policy "event_participants_update_self_or_hosts" on public.event_participants
for update using (user_id = auth.uid() or public.is_event_host(event_id, auth.uid()))
with check (user_id = auth.uid() or public.is_event_host(event_id, auth.uid()));

create policy "event_feedback_insert_self_participant" on public.event_feedback
for insert with check (user_id = auth.uid() and public.is_event_participant(event_id, auth.uid()));
create policy "event_feedback_select_own" on public.event_feedback
for select using (user_id = auth.uid());
create policy "event_feedback_update_own" on public.event_feedback
for update using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "private_memories_owner_all" on public.private_memories
for all using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "event_memories_select_participants" on public.event_memories
for select using (status = 'active' and public.is_event_participant(event_id, auth.uid()));
create policy "event_memories_insert_participants" on public.event_memories
for insert with check (user_id = auth.uid() and public.is_event_participant(event_id, auth.uid()));
create policy "event_memories_update_author_or_hosts" on public.event_memories
for update using (user_id = auth.uid() or public.is_event_host(event_id, auth.uid()))
with check (user_id = auth.uid() or public.is_event_host(event_id, auth.uid()));

create policy "host_roles_select_own_or_circle_hosts" on public.host_roles
for select using (user_id = auth.uid() or (circle_id is not null and public.is_circle_host(circle_id, auth.uid())));

create policy "reports_insert_own" on public.reports
for insert with check (reporter_id = auth.uid());
create policy "reports_select_own" on public.reports
for select using (reporter_id = auth.uid());

create policy "blocks_owner_all" on public.blocks
for all using (blocker_id = auth.uid()) with check (blocker_id = auth.uid());
