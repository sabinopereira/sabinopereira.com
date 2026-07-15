# OutOfLoop Mobile Wireframes

Purpose: define the MVP Beta Core screens before implementation.

The first version should feel calm, human, safe, and practical. The app should not look like a social feed. It should feel like a place where a person receives a small nudge, turns it into a real plan, and comes back with a story.

## 1. MVP Navigation

Bottom tabs:

- Hoje
- Circulos
- Alinhar
- Memorias
- Perfil

Rationale:

- Hoje is the daily action.
- Circulos is where community lives.
- Alinhar is where plans become real.
- Memorias is the emotional archive.
- Perfil holds rhythm, privacy, accessibility, and safety settings.

## 2. First Launch Flow

### Screen 1: Welcome

Goal: establish the emotional promise.

Content:

- Logo/name: OutOfLoop
- Headline: "Sai do automatico."
- Subtext: "Missoes simples para viver mais historias com pessoas reais."
- Primary button: "Comecar"
- Secondary link: "Ja tenho conta"

Notes:

- No marketing carousel.
- Keep this screen direct and warm.

### Screen 2: Account

Fields:

- name
- email or phone
- password or magic link

Primary button:

- "Criar conta"

MVP decision:

- email login is acceptable for early beta
- phone verification can be added before broader local discovery

### Screen 3: Current Loop

Question:

> O que queres mexer na tua rotina?

Selectable cards:

- Quero conhecer melhor as pessoas a minha volta
- Quero sair mais de casa
- Quero fazer mais coisas em familia
- Quero recuperar energia
- Quero ter mais coragem social
- Quero criar planos com amigos

Input:

- Optional free text: "O meu loop agora e..."

Primary button:

- "Continuar"

### Screen 4: Modes

Question:

> Que tipo de missoes fazem sentido agora?

MVP mode choices:

- Coragem
- Social
- Familia
- Saude
- Recomeço

Interaction:

- choose 1 primary mode
- choose 1 optional secondary mode

Primary button:

- "Guardar modos"

### Screen 5: Rhythm

Question:

> Quando tens mais energia?

Choices:

- Cedo de manha
- Manha
- Almoco
- Fim de tarde
- Noite
- Depende do dia

Question:

> Como e a tua semana normal?

Inputs:

- working days
- best availability blocks
- weekend availability

Primary button:

- "Definir ritmo"

### Screen 6: Social Comfort

Question:

> Como preferes comecar?

Choices:

- Sozinho/a
- Com uma pessoa
- Grupo pequeno
- Familia
- Circulo privado

Question:

> Planos com pessoas novas?

Choices:

- Ainda nao
- So em grupo
- Talvez, com anfitriao

If user chooses "Sozinho/a" and "Ainda nao":

- set onboarding path to private-first
- do not force circle creation
- show solo missions first
- keep "Quem alinha?" available but secondary

Primary button:

- "Continuar"

### Screen 7: Budget And Distance

Question:

> Que tipo de planos queres ver?

Cost choices:

- Gratis
- Low cost
- Medio
- Especial

Distance choices:

- Ate 2 km
- Ate 5 km
- Ate 10 km
- Ate 25 km
- Online/tambem a distancia

Primary button:

- "Guardar preferencias"

### Screen 8: Accessibility Preferences

Intro:

> Queres indicar alguma preferencia para tornar missoes e eventos mais faceis para ti?

Privacy note:

> Isto fica privado por defeito.

Choices:

- Acesso sem escadas
- Atividade sentada
- Locais calmos
- Pouca caminhada
- Plano previsivel
- Posso levar acompanhante/cuidador
- Prefiro grupos pequenos
- Comunicacao por texto
- Comunicacao por audio
- Nao preciso agora

Primary button:

- "Guardar"

### Screen 9: First Circle

Question:

> Escolhe um circulo para comecar.

Circle templates:

- Familia
- Amigos
- Gym
- Futebol
- Escola/Pais
- Igreja/Comunidade
- Trabalho
- Outro

Primary action:

- "Criar circulo"

Secondary action:

- "Saltar por agora"

After creation:

> Queres adicionar outro?

Options:

- "Adicionar outro"
- "Ir para a minha primeira missao"

If skipped:

- route directly to Hoje with a private solo mission
- suggest circle creation later only after useful moments

## 3. Hoje Tab

### Screen: Today Home

Purpose: present the user's daily mission without overload.

Top:

- greeting: "Bom dia, Sabino"
- rhythm cue: "Hoje vamos pequeno." or "Sexta pede uma historia."

Mission card:

- mode label: Coragem / Social / Familia / Saude / Recomeço
- intensity: Leve / Real / Coragem
- cost tag: Gratis / Low cost / Medio / Especial
- duration label: Micro / Leve / Realista / Plano / Maior
- time estimate: 3 min / 10 min / 30 min / 60 min
- accessibility badge if relevant: "opcao calma", "sentado", "sem escadas"
- mission title
- short description

Primary actions:

- "Aceitar"
- "Convidar"
- "Quem alinha?"

Secondary actions:

- "Hoje nao da"
- "Trocar"
- "Fazer em privado" if mission has social variants

Footer:

- acceptance timer if active
- "Tens ate as 20:00 para aceitar."

### State: Mission Accepted

Mission card changes:

- status: "Missao aceite"
- next step: "Faz isto ate hoje as 22:00" or chosen schedule

Actions:

- "Concluir"
- "Transformar em plano"
- "Cancelar sem stress"

### State: No Mission Because Paused

Message:

> Hoje estas em modo pausa.

Actions:

- "Quero uma missao leve"
- "Retomar ritmo"

## 4. Hoje Nao Da Flow

### Modal: Reason

Title:

> Sem stress. O que falhou hoje?

Options:

- Sem tempo
- Sem energia
- Missao dificil demais
- Nao era o tipo certo
- Mau dia
- Quero guardar para depois
- Da-me uma mais leve

Actions:

- "Confirmar"
- "Voltar"

### Result States

Sem tempo:

- show 5-minute alternative
- button: "Aceitar esta"

Sem energia:

- show Recomeço mission
- button: "Hoje pequeno"

Missao dificil demais:

- lower intensity
- button: "Tentar versao leve"

Quero guardar:

- save mission
- message: "Guardada para quando fizer sentido."

Design note:

- never show guilt language
- never show "falhaste"

## 5. Mission Detail

Purpose: provide enough confidence to act.

Sections:

- title
- why this mission
- duration label
- estimated time
- cost
- intensity
- best time to do it
- solo/pair/group options
- accessibility notes
- privacy notes

Actions:

- "Aceitar"
- "Convidar alguem"
- "Quem alinha?"
- "Fazer so para mim"
- "Hoje nao da"

Example copy:

> Esta missao foi escolhida porque e sexta ao fim do dia, tens modo Social ativo e preferes planos low cost.

## 6. Circulos Tab

### Screen: Circles Home

Purpose: show the user's real communities without making it a feed.

Header:

- "Os teus circulos"
- button: "+"

Circle cards:

- circle name
- type: Familia / Amigos / Gym / Igreja / etc.
- members count
- active mission/event
- next event date
- host/helper marker

Actions:

- tap card to open
- create circle
- join via invite code

### Screen: Circle Detail

Top:

- circle name
- member count
- privacy label: "Privado"
- host/helper names

Primary card:

- active circle mission or next event

Actions:

- "Criar missao"
- "Quem alinha?"
- "Convidar membros"

Sections:

- Proximos planos
- Memorias recentes
- Membros
- Regras do circulo

Safety actions:

- report circle
- leave quietly
- mute notifications

### Screen: Create Circle

Fields:

- circle name
- category
- privacy: invite-only in MVP
- code of conduct checkbox
- optional description

Actions:

- "Criar circulo"
- "Cancelar"

After create:

- invite link
- share via native share sheet

## 7. Alinhar Tab

### Screen: Plans To Join

Purpose: show missions/events where the user can join.

MVP content:

- events from user's circles
- events the user created
- no public discovery in beta

Cards:

- event title
- circle
- date/time
- location
- cost tag
- accessibility summary
- participants: "2/5 alinharam"
- deadline: "fecha hoje as 18:00"
- host

Actions:

- "Alinhar"
- "Ver detalhes"

Empty state:

> Ainda nao ha planos abertos. Podes transformar a missao de hoje num "Quem alinha?"

Action:

- "Criar plano"

## 8. Create Event / Quem Alinha

### Screen: Create Plan

Entry points:

- Today mission -> Quem alinha?
- Circle detail -> Criar plano
- Alinhar tab -> Criar plano

Fields:

- title
- short description
- circle
- date/time
- public meeting place
- cost tag
- minimum people
- maximum people
- acceptance deadline
- host
- helper optional

Accessibility fields:

- step-free access
- seating available
- quiet/moderate/loud
- walking distance low/medium/high
- accessible bathroom known/unknown
- support companion allowed
- accessibility notes

Safety defaults:

- public place required for people meeting outside close private circles
- album/memories enabled by default
- code of conduct linked

Actions:

- "Publicar no circulo"
- "Guardar rascunho"

### Confirmation

Message:

> Plano criado. Agora falta ver quem alinha.

Show:

- deadline
- minimum participants
- share button

## 9. Event Detail

### State: Open For Acceptance

Top:

- event title
- status: "Aberto"
- deadline timer

Key info:

- date/time
- place
- host/helper
- circle
- cost
- accessibility summary
- minimum/maximum participants

Actions:

- "Alinhar"
- "Vou sozinho/a, quero ser acolhido/a"
- "Tenho uma pergunta"
- "Nao posso"

Safety:

- code of conduct
- report
- block/mute if needed

### State: Confirmed

Status:

- "Confirmado"

Actions:

- "Vou"
- "Ja nao consigo ir"
- "Ver ponto de encontro"
- "Contactar anfitriao"

Day-of-event actions:

- "Cheguei"
- "Ja sai"

### State: Not Enough People

Message:

> Ainda nao chegou ao minimo.

Actions:

- "Reagendar"
- "Fazer em dupla"
- "Transformar em missao solo"

## 10. Post-Event Check-Out

Trigger:

- event end time
- participant taps "Ja sai"
- host marks event completed

### Screen: Como Correu?

Question:

> Como correu?

Options:

- Gostei
- Nao gostei
- Senti-me incluido/a
- Faria outra vez

Follow-up:

- "Sentiste-te seguro/a?"
- "O evento era acessivel para ti ou para quem veio contigo?"
- "O custo foi adequado?"

Optional text:

- "Queres deixar uma nota?"

Actions:

- "Enviar feedback"
- "Saltar"

Safety link:

- "Reportar problema"

## 11. Memorias

### Screen: Add Memory

Prompt:

> Queres guardar uma memoria deste plano?

Options:

- add photo
- write short text

Privacy note:

> So quem participou neste evento consegue ver.

Actions:

- "Publicar nas Memorias"
- "Agora nao"

### Screen: Event Memories

Content:

- event title/date
- participant-only label
- photo grid
- text memories

Actions:

- add memory
- report memory
- request removal from photo

Rules:

- no public sharing in MVP
- no comments in MVP
- reactions can be added later

## 12. Host Dashboard

MVP host dashboard should be simple.

Entry:

- Perfil tab
- Circle detail if user is host/helper

Sections:

- Eventos que estou a organizar
- Pessoas novas nos eventos
- Pessoas que escolheram "vou sozinho/a"
- Feedback recebido
- Problemas/reportes

Actions:

- create event
- assign helper
- message participants with event update
- mark event complete
- review/report issue

Host prompts:

- "Ha alguem novo neste evento."
- "Esta pessoa vem sozinha e pediu acolhimento."
- "Confirma se o local tem acesso adequado."

Limits:

- host cannot see private accessibility preferences unless user shared them for the event
- host cannot access private feedback except aggregated or moderation-relevant reports

## 13. Perfil Tab

Sections:

- profile
- modes
- rhythm
- budget and distance
- accessibility preferences
- privacy
- safety
- notifications
- account

Important controls:

- pause missions
- resume missions
- change notification time
- update accessibility preferences
- blocked users
- report history/status
- leave beta feedback

## 14. Notification Rules

MVP notifications:

- daily mission at user's preferred time
- event acceptance deadline reminder
- event confirmed
- event cancelled/rescheduled
- day-of-event reminder
- post-event feedback reminder

Avoid:

- public pressure notifications
- "you failed" language
- too many nudges per day

Copy examples:

- "A tua missao de hoje esta pronta."
- "Ainda vais a tempo de alinhar."
- "O plano foi confirmado."
- "Como correu?"

## 15. Core Beta Flows

### Flow A: Solo Mission

1. Open Hoje.
2. See daily mission.
3. Accept.
4. Complete.
5. Check out.
6. Give feedback.

### Flow A2: Private-First User

1. User chooses "Sozinho/a" and "Ainda nao" during onboarding.
2. User skips first circle creation.
3. App opens Hoje with a private solo mission.
4. User completes mission.
5. User saves a private memory or reflection.
6. App offers either another solo mission or a one-to-one mission later.

### Flow B: Mission Becomes Plan

1. Open Hoje.
2. Tap "Quem alinha?"
3. Create plan in a circle.
4. Members accept before deadline.
5. Event confirms.
6. Participants attend.
7. Check out.
8. Share memories.

### Flow C: User Has No Energy

1. Open Hoje.
2. Tap "Hoje nao da".
3. Choose "Sem energia".
4. Receive lighter Recomeço mission.
5. Accept or pause.

### Flow D: New Person Joins Event

1. User sees circle event.
2. Taps "Alinhar".
3. Selects "Vou sozinho/a, quero ser acolhido/a".
4. Host receives alert.
5. Host welcomes user at event.
6. User checks out and rates inclusion.

### Flow E: Accessibility-Aware Event

1. Host creates event.
2. Host completes accessibility fields.
3. User sees accessibility summary before joining.
4. User joins and optionally brings support companion.
5. Post-event feedback asks whether accessibility was adequate.

## 16. Design Tone

Use:

- warm but direct copy
- calm layouts
- large touch targets
- clear hierarchy
- no public popularity signals
- no infinite feed
- plain language

Avoid:

- influencer language
- streak pressure
- public leaderboards
- guilt copy
- dense onboarding forms
- hidden safety controls

## 17. Build Notes For React Native

Initial routes:

- `/onboarding/welcome`
- `/onboarding/account`
- `/onboarding/loop`
- `/onboarding/modes`
- `/onboarding/rhythm`
- `/onboarding/social`
- `/onboarding/budget`
- `/onboarding/accessibility`
- `/onboarding/first-circle`
- `/tabs/today`
- `/tabs/circles`
- `/tabs/align`
- `/tabs/memories`
- `/tabs/profile`
- `/mission/[id]`
- `/circle/[id]`
- `/circle/new`
- `/event/new`
- `/event/[id]`
- `/event/[id]/checkout`
- `/event/[id]/memories`
- `/host`

MVP component groups:

- MissionCard
- CircleCard
- EventCard
- CostTag
- IntensityBadge
- AccessibilitySummary
- DeadlineTimer
- PrimaryActionButton
- SafetyLink
- FeedbackOptions
- MemoryGrid
- HostAlert

## 18. Open Design Decisions

- Should "Alinhar" be a tab, or should it live inside Circulos for MVP?
- Should onboarding ask accessibility before or after first circle?
- Should Memories allow only photos/text, or also audio in beta?
- Should private memories live inside Memorias or a separate private journal view?
- Should a support companion be a full participant or a guest attached to a participant?
- Should event updates replace chat in MVP?
- Should the first beta remove "Trocar" and keep only "Hoje nao da" to learn better?
- Should the first circle step be skippable for everyone or only private-first users?
