# OutOfLoop Supabase Schema

Purpose: define the MVP Beta Core database model, privacy boundaries, and RLS direction before implementation.

This is a product schema spec, not yet a final SQL migration. The goal is to make ownership, visibility, and safety rules clear before writing code.

## 1. Schema Principles

- Supabase Auth owns authentication.
- `profiles.id` should match `auth.users.id`.
- Every private object must have an explicit visibility path.
- Circle data is visible only to circle members.
- Event memories are visible only to confirmed event participants.
- Accessibility preferences are private by default.
- Solo/private-first users must be supported without requiring circle membership.
- Hosts can manage events, but should not see private user data unless explicitly shared.
- Reports and moderation actions must be protected from normal users.
- Avoid public discovery in the MVP beta.

## 2. Enum Types

Recommended Postgres enums:

```sql
mission_mode: coragem, social, familia, saude, recomeco
mission_intensity: leve, real, coragem
mission_duration_label: micro, leve, realista, plano, maior
cost_tier: gratis, low_cost, medio, especial
circle_category: familia, amigos, gym, futebol, escola_pais, igreja_comunidade, trabalho, bairro, outro
circle_role: owner, host, helper, member
circle_member_status: invited, active, removed, left
mission_assignment_status: suggested, accepted, completed, skipped, saved, expired, paused
today_not_available_reason: sem_tempo, sem_energia, dificil_demais, tipo_errado, mau_dia, guardar, mais_leve
event_status: draft, open, confirmed, cancelled, completed, archived
event_participant_status: invited, interested, accepted, declined, attended, no_show, cancelled
noise_level: quiet, moderate, loud, unknown
walking_distance_level: low, medium, high, unknown
feedback_rating: positive, negative, neutral
report_status: open, reviewing, resolved, dismissed
moderation_action_type: warning, comment_hidden, user_removed, user_blocked, event_cancelled, content_deleted
```

Notes:

- Use `recomeco` without special character in database values.
- User-facing labels can remain Portuguese with accents.

## 3. Tables

## 3.1 profiles

One row per user.

Columns:

- `id uuid primary key references auth.users(id) on delete cascade`
- `display_name text not null`
- `avatar_url text`
- `city text`
- `area text`
- `age_range text`
- `main_routine text`
- `has_children boolean`
- `living_situation text`
- `primary_mode mission_mode`
- `secondary_mode mission_mode`
- `preferred_intensity mission_intensity default 'leve'`
- `preferred_cost_tier cost_tier default 'low_cost'`
- `distance_km int default 5`
- `social_comfort text`
- `new_people_preference text`
- `community_preference text default 'private_first'`
- `energy_type text`
- `mission_paused boolean default false`
- `preferred_notification_time time`
- `onboarding_completed boolean default false`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

Visibility:

- user can read and update own profile
- circle members can read limited public profile fields for users in same circle

Implementation note:

- expose full profile through direct table access only to owner
- create a `public_profiles` view later if needed

## 3.2 profile_availability

Stores weekly availability blocks.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid references profiles(id) on delete cascade`
- `day_of_week int not null check (day_of_week between 0 and 6)`
- `time_block text not null`
- `is_available boolean default true`
- `created_at timestamptz default now()`

Example `time_block` values:

- early_morning
- morning
- lunch
- afternoon
- evening
- night

Visibility:

- owner only in MVP

## 3.3 accessibility_preferences

Private user preferences.

Columns:

- `user_id uuid primary key references profiles(id) on delete cascade`
- `step_free_access boolean default false`
- `seated_activity boolean default false`
- `quiet_places boolean default false`
- `short_walking_distance boolean default false`
- `predictable_plan boolean default false`
- `support_companion boolean default false`
- `small_groups boolean default false`
- `text_communication boolean default false`
- `audio_communication boolean default false`
- `notes text`
- `share_with_hosts_by_default boolean default false`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

Visibility:

- owner only
- never visible to circle hosts unless explicitly copied/shared into event participant accessibility notes

## 3.4 circles

Private groups.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `name text not null`
- `category circle_category not null`
- `description text`
- `privacy text default 'invite_only'`
- `owner_id uuid references profiles(id)`
- `code_of_conduct_accepted boolean default true`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`
- `archived_at timestamptz`

Visibility:

- active members can read
- owner/host can update limited fields
- owner can archive

## 3.5 circle_members

Membership and roles.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `circle_id uuid references circles(id) on delete cascade`
- `user_id uuid references profiles(id) on delete cascade`
- `role circle_role default 'member'`
- `status circle_member_status default 'active'`
- `invited_by uuid references profiles(id)`
- `joined_at timestamptz`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

Constraints:

- unique `(circle_id, user_id)`

Visibility:

- active members can read members of same circle
- owner/host/helper can invite
- owner/host can change roles below their own authority
- user can leave circle by setting own status to `left`

## 3.6 invites

Invitation links/codes.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `circle_id uuid references circles(id) on delete cascade`
- `created_by uuid references profiles(id)`
- `token text unique not null`
- `max_uses int`
- `uses_count int default 0`
- `expires_at timestamptz`
- `created_at timestamptz default now()`
- `revoked_at timestamptz`

Visibility:

- circle hosts/helpers can create and read active invites
- joining by token should be handled through an RPC function

## 3.7 missions

Mission library.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `slug text unique not null`
- `title text not null`
- `description text not null`
- `mode mission_mode not null`
- `intensity mission_intensity not null`
- `cost_tier cost_tier default 'gratis'`
- `estimated_minutes int`
- `duration_label mission_duration_label not null`
- `recommended_day_mask int`
- `recommended_time_blocks text[]`
- `solo_enabled boolean default true`
- `pair_enabled boolean default true`
- `group_enabled boolean default true`
- `family_enabled boolean default false`
- `accessibility_notes text`
- `accessible_alternative_title text`
- `accessible_alternative_description text`
- `active boolean default true`
- `created_at timestamptz default now()`

Visibility:

- authenticated users can read active missions
- only admins/service role can write

MVP note:

- seed a small curated mission library first
- avoid complex AI generation until beta data exists

## 3.8 mission_assignments

Daily/user-specific mission instances.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid references profiles(id) on delete cascade`
- `mission_id uuid references missions(id)`
- `assigned_for date not null`
- `status mission_assignment_status default 'suggested'`
- `accepted_at timestamptz`
- `completed_at timestamptz`
- `expires_at timestamptz`
- `source text default 'rules_engine'`
- `personalization_reason text`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

Constraints:

- unique `(user_id, assigned_for)`

Visibility:

- owner only

## 3.9 mission_feedback

Feedback for missions and "Hoje nao da".

Columns:

- `id uuid primary key default gen_random_uuid()`
- `assignment_id uuid references mission_assignments(id) on delete cascade`
- `user_id uuid references profiles(id) on delete cascade`
- `liked boolean`
- `difficulty text`
- `would_repeat boolean`
- `done_with text`
- `felt_energy boolean`
- `felt_connection boolean`
- `felt_courage boolean`
- `felt_calm boolean`
- `today_not_available_reason today_not_available_reason`
- `note text`
- `created_at timestamptz default now()`

Visibility:

- owner can create/read own feedback
- service/admin can aggregate

## 3.10 events

Plans created from missions or circles.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `circle_id uuid references circles(id) on delete cascade`
- `created_by uuid references profiles(id)`
- `host_id uuid references profiles(id)`
- `helper_id uuid references profiles(id)`
- `mission_assignment_id uuid references mission_assignments(id)`
- `title text not null`
- `description text`
- `status event_status default 'draft'`
- `starts_at timestamptz not null`
- `ends_at timestamptz`
- `acceptance_deadline timestamptz not null`
- `place_name text`
- `place_address text`
- `location_note text`
- `cost_tier cost_tier default 'gratis'`
- `min_participants int default 2`
- `max_participants int`
- `memories_enabled boolean default true`
- `public_place_required boolean default true`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`
- `cancelled_at timestamptz`
- `completed_at timestamptz`

Visibility:

- active circle members can read
- host/helper/owner can update
- creator can update while draft

MVP:

- event must belong to a circle
- no fully public local events yet

## 3.11 event_accessibility

Public accessibility info for an event.

Columns:

- `event_id uuid primary key references events(id) on delete cascade`
- `step_free_access boolean`
- `accessible_bathroom text default 'unknown'`
- `seating_available boolean`
- `public_transport_nearby boolean`
- `parking_nearby boolean`
- `noise_level noise_level default 'unknown'`
- `walking_distance walking_distance_level default 'unknown'`
- `standing_required boolean`
- `family_friendly boolean default false`
- `support_companion_allowed boolean default true`
- `notes text`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

Visibility:

- visible to active members of the event circle before joining
- editable by event host/helper

## 3.12 event_participants

Tracks who aligns, attends, asks for welcome, and check-in/check-out.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `event_id uuid references events(id) on delete cascade`
- `user_id uuid references profiles(id) on delete cascade`
- `status event_participant_status default 'accepted'`
- `wants_host_welcome boolean default false`
- `bringing_support_companion boolean default false`
- `support_companion_count int default 0`
- `shared_accessibility_note text`
- `checked_in_at timestamptz`
- `checked_out_at timestamptz`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

Constraints:

- unique `(event_id, user_id)`

Visibility:

- event participants can see other participant names/statuses
- event host/helper can see `wants_host_welcome`
- host/helper can see `shared_accessibility_note` only for their event
- support companion info visible to host for planning

## 3.13 event_feedback

Post-event check-out.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `event_id uuid references events(id) on delete cascade`
- `user_id uuid references profiles(id) on delete cascade`
- `liked boolean`
- `felt_included boolean`
- `would_repeat boolean`
- `felt_safe boolean`
- `accessibility_ok boolean`
- `cost_ok boolean`
- `note text`
- `created_at timestamptz default now()`

Constraints:

- unique `(event_id, user_id)`

Visibility:

- owner can read own feedback
- host can see aggregate counts, not raw private notes unless explicitly shared later
- service/admin can read for safety and beta analysis

## 3.14 private_memories

Private memories or reflections from solo missions.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid references profiles(id) on delete cascade`
- `mission_assignment_id uuid references mission_assignments(id) on delete set null`
- `type text not null check (type in ('photo', 'text'))`
- `photo_url text`
- `text_body text`
- `created_at timestamptz default now()`
- `deleted_at timestamptz`

Visibility:

- owner only

Storage:

- Supabase Storage bucket: `private-memories`
- path: `users/{user_id}/private-memories/{memory_id}`
- owner-only access

## 3.15 event_memories

Private event memories.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `event_id uuid references events(id) on delete cascade`
- `user_id uuid references profiles(id) on delete cascade`
- `type text not null check (type in ('photo', 'text'))`
- `photo_url text`
- `text_body text`
- `status text default 'active'`
- `created_at timestamptz default now()`
- `removed_at timestamptz`
- `removed_by uuid references profiles(id)`

Visibility:

- confirmed/attended event participants can read active memories
- author can create
- author can remove own memory
- host/helper can hide memory for event safety
- reports can trigger moderation

Storage:

- Supabase Storage bucket: `event-memories`
- path: `events/{event_id}/{memory_id}`
- access through signed URLs or storage policies restricted by event participation

## 3.16 host_roles

Optional explicit host capability beyond circle role.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid references profiles(id) on delete cascade`
- `scope text not null`
- `circle_id uuid references circles(id) on delete cascade`
- `level text default 'helper'`
- `verified_at timestamptz`
- `created_by uuid references profiles(id)`
- `created_at timestamptz default now()`
- `revoked_at timestamptz`

MVP note:

- use simple circle roles first
- keep this table for future verified host progression

## 3.17 reports

Reports for users, events, memories, circles, or comments later.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `reporter_id uuid references profiles(id)`
- `target_type text not null`
- `target_id uuid not null`
- `circle_id uuid references circles(id)`
- `event_id uuid references events(id)`
- `reason text not null`
- `details text`
- `status report_status default 'open'`
- `created_at timestamptz default now()`
- `resolved_at timestamptz`
- `resolved_by uuid references profiles(id)`

Visibility:

- reporter can create
- reporter can read their own report status
- moderators/admins can read relevant reports
- normal users cannot read reports against others

## 3.18 moderation_actions

Audit log of moderation actions.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `actor_id uuid references profiles(id)`
- `action_type moderation_action_type not null`
- `target_type text not null`
- `target_id uuid not null`
- `circle_id uuid references circles(id)`
- `event_id uuid references events(id)`
- `reason text`
- `metadata jsonb`
- `created_at timestamptz default now()`

Visibility:

- admins/service role
- possibly circle owners for actions in their circle, later

## 3.19 blocks

User blocking.

Columns:

- `id uuid primary key default gen_random_uuid()`
- `blocker_id uuid references profiles(id) on delete cascade`
- `blocked_id uuid references profiles(id) on delete cascade`
- `created_at timestamptz default now()`

Constraints:

- unique `(blocker_id, blocked_id)`
- check `blocker_id <> blocked_id`

Visibility:

- owner only

## 4. RLS Helper Functions

Recommended SQL helper functions:

```sql
is_circle_member(circle_uuid uuid, user_uuid uuid) returns boolean
is_circle_host(circle_uuid uuid, user_uuid uuid) returns boolean
is_event_participant(event_uuid uuid, user_uuid uuid) returns boolean
is_event_host(event_uuid uuid, user_uuid uuid) returns boolean
can_view_event(event_uuid uuid, user_uuid uuid) returns boolean
shares_circle(user_a uuid, user_b uuid) returns boolean
assign_daily_mission(target_date date default current_date) returns mission_assignments
```

These keep RLS readable and reduce copy-paste policy risk.

`assign_daily_mission` is the v1 rules engine for the `Hoje` screen. It chooses from active missions using:

- primary/secondary mode
- preferred intensity
- preferred cost tier
- family context
- private-first preference
- random tie-breaking

## 5. RLS Policy Direction

## 5.1 profiles

- Select own full profile.
- Update own profile.
- Insert own profile after signup.
- Select limited profile fields through a view for users sharing a circle or event.

## 5.2 accessibility_preferences

- Select/insert/update/delete own row only.
- No host access to this table.

## 5.3 circles

- Select if active member.
- Insert authenticated user as owner.
- Update if owner or host.
- Archive if owner.

## 5.4 circle_members

- Select if active member of the same circle.
- Insert if host/helper creates invite flow or RPC validates invite.
- Update own row to leave.
- Update roles/status if owner/host, with guardrails.

## 5.5 missions

- Select active missions for authenticated users.
- Write only service/admin.

## 5.6 mission_assignments and mission_feedback

- Owner can select/insert/update own assignments and feedback.
- Service/admin can generate assignments.

## 5.7 events

- Select if active member of event circle.
- Insert if active circle member.
- Update if creator while draft, host/helper, or circle owner.
- Cancel if host/helper/owner.

## 5.8 event_accessibility

- Select if can view event.
- Insert/update if event host/helper.

## 5.9 event_participants

- Select if can view event.
- Insert own row if active circle member and event is open.
- Update own status/check-in/check-out.
- Host/helper can update attendance status for event.

## 5.10 event_feedback

- Insert own feedback if participant.
- Select own feedback.
- Host sees aggregate through a view/RPC, not raw rows.

## 5.11 event_memories

- Select if participant in event.
- Insert if participant in event.
- Update/delete own memory.
- Host/helper can set status to hidden/removed for event.

## 5.12 private_memories

- Select/insert/update/delete own private memories only.
- No host/circle access.

## 5.13 reports

- Insert own report.
- Select own report status.
- Admin/service role handles full review.

## 6. Critical Privacy Cases

Case: private circle

- A user outside the circle cannot see circle, members, events, memories, or invite list.

Case: event memory

- Only confirmed/attended participants can see memory content.
- A user who was invited but declined should not see memories.

Case: private memory

- A private-first user's memory is visible only to them.
- It is not attached to a circle or event unless the user explicitly shares it later.

Case: accessibility preferences

- A user's private preferences never leak to a host.
- User can share a specific note for a specific event through `event_participants.shared_accessibility_note`.

Case: "vou sozinho/a"

- `wants_host_welcome` is visible to host/helper, not necessarily all participants.

Case: feedback

- Raw feedback is private.
- Hosts get aggregate signals and safety-relevant reports only.

Case: blocked user

- MVP can hide direct interactions and future event invitations.
- Full block semantics across shared circles can be expanded after beta.

## 7. Indexes

Recommended indexes:

```sql
profiles(city, area)
circle_members(user_id, status)
circle_members(circle_id, status)
events(circle_id, status, starts_at)
events(host_id, starts_at)
events(acceptance_deadline)
event_participants(user_id, status)
event_participants(event_id, status)
event_memories(event_id, status, created_at)
private_memories(user_id, created_at)
mission_assignments(user_id, assigned_for)
mission_feedback(user_id, created_at)
reports(status, created_at)
```

## 8. Storage Buckets

## 8.1 avatars

- profile avatars
- public or signed URL depending on privacy choice

## 8.2 event-memories

- private bucket
- only event participants can read
- users can upload only for events they participate in
- host/helper can remove/hide via database state, not necessarily delete original immediately

## 8.3 private-memories

- private bucket
- owner-only access
- for solo mission reflections and private photos

## 9. Seed Data For Beta

Minimum seed:

- 120 missions
- 5 modes
- 3 intensities
- 5 duration labels
- low-cost/free majority
- at least 10 accessibility-friendly missions
- at least 10 solo/private-first missions
- at least 10 family missions
- at least 10 social/courage missions
- at least 5 recomeço low-energy missions

Duration labels:

- `micro`: 2-5 minutes
- `leve`: 6-15 minutes
- `realista`: 16-30 minutes
- `plano`: 31-60 minutes
- `maior`: more than 60 minutes or multi-step/weekend missions

Example mission categories:

- message someone
- invite someone
- short walk/roll
- family dinner prompt
- church/community service
- gym buddy
- coffee with someone
- local free event
- quiet solo reflection
- private city exploration
- host-led group plan

## 10. MVP Build Order

1. Auth + profiles.
2. Onboarding data: profiles, availability, accessibility.
3. Mission library + daily assignment.
4. Hoje actions: accept, complete, Hoje nao da.
5. Circles + members + invites.
6. Events + participants + deadlines.
7. Event accessibility.
8. Check-in/check-out.
9. Feedback.
10. Memories + storage policies.
11. Reports + basic moderation.
12. Host dashboard queries.

## 11. Open Schema Decisions

- Use Postgres enums or text with check constraints?
- Use direct RLS-heavy reads or RPC functions for complex screens?
- Should `event_participants.status` distinguish accepted vs attended vs checked out more explicitly?
- Should support companions become separate participant rows later?
- Should host aggregate feedback be a materialized view or RPC?
- Should invite joining be fully RPC-based from the start?
- How much admin tooling is needed for beta moderation?
