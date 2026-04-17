const scenarios = [
  {
    category: "focus",
    title: "Notification Pull",
    variations: [
      "Your phone lights up while you're focused.",
      "A notification appears mid-task.",
      "You hear your phone buzz during deep work."
    ],
    choices: ["Check it quickly", "Ignore and continue working", "Pick it up but don't open anything"],
    correctAnswerIndex: 1
  },
  {
    category: "focus",
    title: "Instant Reply Trap",
    variations: [
      "Someone messages you. It feels urgent.",
      "A message arrives and your mind treats it like an emergency.",
      "A new message pulls at your attention while you work."
    ],
    choices: ["Reply immediately", "Finish your task first", "Send a quick short reply"],
    correctAnswerIndex: 1
  },
  {
    category: "focus",
    title: "Boredom Drift",
    variations: [
      "You feel bored in the middle of a task.",
      "The work feels slow and your attention starts wandering.",
      "You lose stimulation halfway through something important."
    ],
    choices: ["Switch to something easier", "Push through the discomfort", "Take a random break"],
    correctAnswerIndex: 1
  },
  {
    category: "emotion",
    title: "Emotional Trigger",
    variations: [
      "Someone says something that annoys you.",
      "A comment lands badly and you feel it instantly.",
      "Someone close to you says something that gets under your skin."
    ],
    choices: ["Respond immediately", "Pause before reacting", "Respond sarcastically"],
    correctAnswerIndex: 1
  },
  {
    category: "focus",
    title: "Overthinking Loop",
    variations: [
      "You're unsure about a decision.",
      "You don't have certainty, so your mind keeps circling.",
      "A decision needs to be made, but you keep delaying the move."
    ],
    choices: ["Keep thinking more", "Make a decision with available info", "Ask others before deciding"],
    correctAnswerIndex: 1
  },
  {
    category: "focus",
    title: "Easy Escape",
    variations: [
      "You think about watching something instead of working.",
      "Entertainment suddenly feels more attractive than the task.",
      "You want a quick dopamine hit instead of staying with the work."
    ],
    choices: ["Start watching", "Stay on task", "Watch just one short video"],
    correctAnswerIndex: 1
  },
  {
    category: "deep work",
    title: "Pressure Spike",
    variations: [
      "You have too many things to do.",
      "Your list is too full and everything feels urgent.",
      "Pressure rises because too many tasks are demanding attention."
    ],
    choices: ["Try to do everything fast", "Prioritize one thing and start", "Jump between tasks"],
    correctAnswerIndex: 1
  },
  {
    category: "deep work",
    title: "Mental Fatigue",
    variations: [
      "You feel mentally tired.",
      "Your mind feels heavy halfway through the session.",
      "The work is still there, but your mental energy drops."
    ],
    choices: ["Stop everything", "Slow down but continue", "Switch to something random"],
    correctAnswerIndex: 1
  },
  {
    category: "relationships",
    title: "Social Distraction",
    variations: [
      "Someone starts talking to you while you work.",
      "A conversation begins just as you were getting into rhythm.",
      "Someone wants your attention while you're in the middle of something important."
    ],
    choices: ["Fully engage", "Politely delay the conversation", "Half listen while working"],
    correctAnswerIndex: 1
  },
  {
    category: "focus",
    title: "False Urgency",
    variations: [
      "A task suddenly feels urgent.",
      "Something new arrives and instantly feels like top priority.",
      "A task pulls hard at you before you've even evaluated it."
    ],
    choices: ["Drop everything and do it", "Evaluate if it truly matters first", "Start it while doing other things"],
    correctAnswerIndex: 1
  },
  {
    category: "relationships",
    title: "Difficult Conversation",
    variations: [
      "Someone close to you says something that bothers you.",
      "A difficult comment lands and you want to answer fast.",
      "A conversation turns sharp with someone who matters to you."
    ],
    choices: ["React immediately", "Pause and respond later with clarity", "Ignore it completely"],
    correctAnswerIndex: 1
  },
  {
    category: "relationships",
    title: "Approval Seeking",
    variations: [
      "You want someone's approval before making a move.",
      "You hesitate because you want validation first.",
      "A decision feels harder because no one has approved it yet."
    ],
    choices: ["Wait for validation", "Decide based on your own judgment", "Ask casually just to confirm"],
    correctAnswerIndex: 1
  },
  {
    category: "relationships",
    title: "Boundaries Test",
    variations: [
      "Someone asks for your time when you're busy.",
      "A request arrives right when your focus is already committed.",
      "Someone wants access to your time while you're under pressure."
    ],
    choices: ["Say yes anyway", "Politely decline or delay", "Say yes but rush everything"],
    correctAnswerIndex: 1
  },
  {
    category: "money",
    title: "Impulse Buy",
    variations: [
      "You see something you want but didn't plan.",
      "An unplanned purchase suddenly feels justified.",
      "You want to buy something that wasn't part of the plan."
    ],
    choices: ["Buy it immediately", "Wait and reconsider later", "Add to cart for later"],
    correctAnswerIndex: 1
  },
  {
    category: "money",
    title: "Lifestyle Pressure",
    variations: [
      "People around you are spending more than you.",
      "The people around you make your own plan feel small.",
      "You feel pressure to match the lifestyle around you."
    ],
    choices: ["Match their lifestyle", "Stick to your plan", "Spend a little to fit in"],
    correctAnswerIndex: 1
  },
  {
    category: "money",
    title: "Opportunity vs Distraction",
    variations: [
      "A new money-making idea appears suddenly.",
      "A fresh opportunity shows up while you're already committed elsewhere.",
      "A shiny money idea tries to pull you off your real priorities."
    ],
    choices: ["Drop current work and chase it", "Evaluate and stay focused on priorities", "Explore it briefly"],
    correctAnswerIndex: 1
  },
  {
    category: "deep work",
    title: "Hard Task Resistance",
    variations: [
      "You're about to start something mentally demanding.",
      "A hard task is in front of you and your mind wants to delay it.",
      "Deep work is waiting, but resistance shows up first."
    ],
    choices: ["Delay it", "Start anyway", "Prepare more before starting"],
    correctAnswerIndex: 1
  },
  {
    category: "deep work",
    title: "Task Switching",
    variations: [
      "You feel like switching tasks mid-work.",
      "Your attention wants novelty before the current task is done.",
      "You want to leave the current task before finishing it."
    ],
    choices: ["Switch immediately", "Finish current task first", "Open another task briefly"],
    correctAnswerIndex: 1
  },
  {
    category: "deep work",
    title: "Fake Productivity",
    variations: [
      "You consider doing small tasks instead of the important one.",
      "Busywork feels easier than the task that actually matters.",
      "You want the comfort of visible progress instead of meaningful progress."
    ],
    choices: ["Do the easy tasks", "Do the important task first", "Mix both"],
    correctAnswerIndex: 1
  },
  {
    category: "deep work",
    title: "End-of-Day Decision",
    variations: [
      "You're near the end of your work session.",
      "The session is almost over and stopping feels easy.",
      "You're close to the end of the day and tempted to coast out."
    ],
    choices: ["Stop now", "Finish one meaningful action", "Do something light"],
    correctAnswerIndex: 1
  }
];

const scoreEl = document.getElementById("score");
const gameTimeEl = document.getElementById("game-time");
const decisionTimeEl = document.getElementById("decision-time");
const timerBarEl = document.getElementById("timer-bar");
const scenarioTitleEl = document.getElementById("scenario-title");
const scenarioDescriptionEl = document.getElementById("scenario-description");
const choicesEl = document.getElementById("choices");
const feedbackEl = document.getElementById("feedback");
const insightFeedbackEl = document.getElementById("insight-feedback");
const gameScreenEl = document.getElementById("game-screen");
const gameOverEl = document.getElementById("game-over");
const gameFrameEl = document.querySelector(".game-frame");
const gameStageEl = document.querySelector(".game-stage");
const finalScoreEl = document.getElementById("final-score");
const identityTitleEl = document.getElementById("identity-title");
const identityLineOneEl = document.getElementById("identity-line-one");
const identityLineTwoEl = document.getElementById("identity-line-two");
const ecosystemPrimaryEl = document.getElementById("ecosystem-primary");
const restartButtonEl = document.getElementById("restart-button");
const startButtonEl = document.getElementById("start-button");
const shareResultButtonEl = document.getElementById("share-result-button");
const soundToggleEl = document.getElementById("sound-toggle");
const soundStatusEl = document.getElementById("sound-status");

const GAME_DURATION = 60;
const START_DECISION_TIME = 14;
const MIN_DECISION_TIME = 10;
const INSIGHT_INTERVALS = [3, 4];

const microFeedback = {
  correct: [
    "That was controlled.",
    "You stayed with it.",
    "No rush. Good.",
    "You chose, not reacted."
  ],
  wrong: [
    "Too fast.",
    "You reacted.",
    "That's how focus breaks.",
    "Impulse took over."
  ],
  timeout: [
    "You're thinking... or avoiding?",
    "Delay is a decision too.",
    "You felt it. You paused.",
    "Uncertainty slows you down."
  ]
};

const dynamicInsights = {
  impulsive: [
    "You're moving fast... but not forward.",
    "Speed is replacing clarity."
  ],
  distracted: [
    "You're slipping.",
    "Focus is leaking."
  ],
  controlled: [
    "You're holding your ground.",
    "This is rare."
  ],
  inconsistent: [
    "You're switching modes.",
    "Control... then reaction."
  ]
};

let score = 0;
let gameTimeRemaining = GAME_DURATION;
let decisionTimeRemaining = START_DECISION_TIME;
let currentScenarioTotalTime = START_DECISION_TIME;
let currentScenario = null;
let gameTimerId = null;
let decisionTimerId = null;
let roundLocked = false;
let gameRunning = false;
let soundEnabled = true;
let audioContext = null;
let behavioralMetrics = null;
let decisionHistory = [];
let lastScenarioTitle = null;
let feedbackTimeoutId = null;
let insightTimeoutId = null;
let nextInsightAt = 3;
let correctStreak = 0;
let timerFeel = "steady";

function createEmptyMetrics() {
  return {
    focus: 0,
    impulsivity: 0,
    discipline: 0
  };
}

function persistBehavioralState() {
  const payload = {
    metrics: behavioralMetrics,
    decisions: decisionHistory,
    score,
    gameTimeRemaining,
    updatedAt: new Date().toISOString()
  };

  try {
    window.sessionStorage.setItem("quietPowerCafeMetrics", JSON.stringify(payload));
  } catch (_) {
    // Silent fallback: gameplay should continue even if storage is unavailable.
  }
}

function applyMetricsChange(change = {}, meta = {}) {
  Object.entries(change).forEach(([key, value]) => {
    if (Object.prototype.hasOwnProperty.call(behavioralMetrics, key)) {
      behavioralMetrics[key] += value;
    }
  });

  decisionHistory.push({
    scenario: currentScenario?.title || "Unknown",
    category: currentScenario?.category || "unknown",
    outcome: meta.outcome || "decision",
    choice: meta.choice || null,
    responseSpeed: meta.responseSpeed || "steady",
    metrics: change,
    timestamp: Date.now()
  });

  persistBehavioralState();
}

function getChoiceMetrics(scenario, choiceIndex) {
  if (choiceIndex === scenario.correctAnswerIndex) {
    return { focus: 2, impulsivity: -1, discipline: 2 };
  }

  const choiceText = scenario.choices[choiceIndex].toLowerCase();
  const acceptableButNotIdeal = [
    "pick it up but don't open anything",
    "send a quick short reply",
    "take a random break",
    "respond sarcastically",
    "ask others before deciding",
    "watch just one short video",
    "jump between tasks",
    "switch to something random",
    "half listen while working",
    "start it while doing other things"
  ];

  if (acceptableButNotIdeal.includes(choiceText)) {
    return { focus: -1, impulsivity: 1, discipline: -1 };
  }

  return { focus: -2, impulsivity: 2, discipline: -2 };
}

function pickScenario() {
  const availableScenarios = scenarios.filter((scenario) => scenario.title !== lastScenarioTitle);
  const pool = availableScenarios.length > 0 ? availableScenarios : scenarios;
  const scenario = pool[Math.floor(Math.random() * pool.length)];
  const variation = scenario.variations[Math.floor(Math.random() * scenario.variations.length)];

  lastScenarioTitle = scenario.title;

  return {
    ...scenario,
    activeText: variation
  };
}

function resolveIdentity() {
  const metrics = behavioralMetrics || createEmptyMetrics();
  const distraction = Math.max(0, -metrics.focus) + Math.max(0, -metrics.discipline) + Math.max(0, metrics.impulsivity - 2);

  if (metrics.focus >= 8 && metrics.discipline >= 8 && metrics.impulsivity <= 2) {
    return {
      title: "The Calm Strategist",
      lines: [
        "You don't rush.",
        "You decide."
      ],
      cta: { label: "Improve your Quiet Power", href: "/quiet-power.html" }
    };
  }

  if (metrics.impulsivity >= 8) {
    return {
      title: "The Reactive Operator",
      lines: [
        "You move fast.",
        "Too fast."
      ],
      cta: { label: "Improve your Quiet Power", href: "/quiet-power-assessment.html" }
    };
  }

  if (distraction >= 8) {
    return {
      title: "The Distracted Drifter",
      lines: [
        "You don't choose.",
        "You drift."
      ],
      cta: { label: "Improve your Quiet Power", href: "/quiet-thought-while-you-wait-they-build.html" }
    };
  }

  return {
    title: "The Controlled Performer",
    lines: [
      "You stay composed.",
      "Refine it."
    ],
    cta: { label: "Improve your Quiet Power", href: "/quiet-power.html" }
  };
}

function shuffle(array) {
  const items = [...array];
  for (let i = items.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

function randomFrom(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function getScenarioTime() {
  const elapsed = GAME_DURATION - gameTimeRemaining;
  const progress = Math.min(elapsed / GAME_DURATION, 1);
  const time = START_DECISION_TIME - progress * (START_DECISION_TIME - MIN_DECISION_TIME);
  return Math.max(MIN_DECISION_TIME, Number(time.toFixed(1)));
}

function updateScore() {
  scoreEl.textContent = String(score);
  scoreEl.classList.remove("score-pop");
  void scoreEl.offsetWidth;
  scoreEl.classList.add("score-pop");
}

function updateGameClock() {
  gameTimeEl.textContent = `${gameTimeRemaining}s`;
}

function setFeedback(message, tone = "positive") {
  feedbackEl.textContent = message;
  feedbackEl.classList.remove("is-negative", "is-neutral", "is-animated", "is-whisper", "is-whisper-visible");

  if (tone === "negative") {
    feedbackEl.classList.add("is-negative");
  } else if (tone === "neutral") {
    feedbackEl.classList.add("is-neutral");
  }

  void feedbackEl.offsetWidth;
  feedbackEl.classList.add("is-animated");
}

function showMicroFeedback(type) {
  const tone = type === "correct" ? "positive" : type === "wrong" ? "negative" : "neutral";
  feedbackEl.textContent = randomFrom(microFeedback[type]);
  feedbackEl.classList.remove("is-negative", "is-neutral", "is-animated", "is-whisper", "is-whisper-visible");

  if (tone === "negative") {
    feedbackEl.classList.add("is-negative");
  } else if (tone === "neutral") {
    feedbackEl.classList.add("is-neutral");
  }

  feedbackEl.classList.add("is-whisper");
  void feedbackEl.offsetWidth;
  feedbackEl.classList.add("is-whisper-visible");

  if (feedbackTimeoutId) {
    window.clearTimeout(feedbackTimeoutId);
  }

  feedbackTimeoutId = window.setTimeout(() => {
    feedbackEl.classList.remove("is-whisper-visible");
  }, 1700);
}

function showInsight(message) {
  if (!message) {
    return;
  }

  insightFeedbackEl.textContent = message;
  insightFeedbackEl.classList.remove("is-visible");
  void insightFeedbackEl.offsetWidth;
  insightFeedbackEl.classList.add("is-visible");

  if (insightTimeoutId) {
    window.clearTimeout(insightTimeoutId);
  }

  insightTimeoutId = window.setTimeout(() => {
    insightFeedbackEl.classList.remove("is-visible");
  }, 2800);
}

function setDriftLevel(level = 0) {
  const clamped = Math.max(0, Math.min(level, 1));
  const blur = `${(clamped * 1.35).toFixed(2)}px`;
  const opacity = String((1 - clamped * 0.08).toFixed(2));
  const contrast = String((1 - clamped * 0.05).toFixed(2));

  gameScreenEl.style.setProperty("--drift-blur", blur);
  gameScreenEl.style.setProperty("--drift-opacity", opacity);
  gameScreenEl.style.setProperty("--drift-contrast", contrast);
  gameFrameEl.classList.toggle("is-distracted", clamped > 0.08);
}

function clearVisualModes() {
  gameFrameEl.classList.remove("is-controlled", "is-unstable", "is-distracted");
  setDriftLevel(0);
  timerFeel = "steady";
  timerBarEl.classList.remove("is-impulsive", "is-controlled");
}

function triggerImpulseChaos(button) {
  gameFrameEl.classList.remove("is-shaking");
  gameStageEl.classList.remove("has-impulse-flash");
  button?.classList.remove("is-snap");

  void gameFrameEl.offsetWidth;

  gameFrameEl.classList.add("is-shaking");
  gameStageEl.classList.add("has-impulse-flash");
  button?.classList.add("is-snap");

  window.setTimeout(() => {
    gameFrameEl.classList.remove("is-shaking");
    gameStageEl.classList.remove("has-impulse-flash");
    button?.classList.remove("is-snap");
  }, 190);
}

function updateBehaviorVisualState() {
  const recent = decisionHistory.slice(-4);
  const outcomes = recent.map((entry) => entry.outcome);
  const fastWrongCount = recent.filter((entry) => entry.outcome === "wrong" && entry.responseSpeed === "fast").length;
  const alternating =
    recent.length >= 4 &&
    outcomes.every((outcome, index) => index === 0 || outcome !== outcomes[index - 1]);

  gameFrameEl.classList.toggle("is-unstable", alternating);
  gameFrameEl.classList.toggle("is-controlled", correctStreak >= 2);

  if (correctStreak >= 2) {
    timerFeel = "controlled";
  } else if (fastWrongCount >= 1) {
    timerFeel = "impulsive";
  } else {
    timerFeel = "steady";
  }

  timerBarEl.classList.toggle("is-controlled", timerFeel === "controlled");
  timerBarEl.classList.toggle("is-impulsive", timerFeel === "impulsive");

  if (correctStreak >= 2) {
    setDriftLevel(0);
    gameFrameEl.classList.remove("is-distracted");
  }
}

function clearDecisionTimer() {
  if (decisionTimerId) {
    window.clearInterval(decisionTimerId);
    decisionTimerId = null;
  }
}

function focusScenarioCard() {
  window.requestAnimationFrame(() => {
    gameScreenEl.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  });
}

function ensureAudioContext() {
  if (!soundEnabled) {
    return null;
  }

  const AudioCtor = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtor) {
    return null;
  }

  if (!audioContext) {
    audioContext = new AudioCtor();
  }

  if (audioContext.state === "suspended") {
    audioContext.resume().catch(() => {});
  }

  return audioContext;
}

function playTone({ frequency, duration = 0.12, type = "sine", volume = 0.03, delay = 0 }) {
  const ctx = ensureAudioContext();
  if (!ctx) {
    return;
  }

  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();
  const startAt = ctx.currentTime + delay;
  const endAt = startAt + duration;

  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, startAt);

  gain.gain.setValueAtTime(0.0001, startAt);
  gain.gain.exponentialRampToValueAtTime(volume, startAt + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, endAt);

  oscillator.connect(gain);
  gain.connect(ctx.destination);

  oscillator.start(startAt);
  oscillator.stop(endAt);
}

function playSuccessSound() {
  playTone({ frequency: 520, duration: 0.08, type: "sine", volume: 0.035 });
  playTone({ frequency: 680, duration: 0.12, type: "sine", volume: 0.03, delay: 0.07 });
}

function playErrorSound() {
  playTone({ frequency: 240, duration: 0.12, type: "triangle", volume: 0.03 });
  playTone({ frequency: 180, duration: 0.14, type: "triangle", volume: 0.025, delay: 0.06 });
}

function playStartSound() {
  playTone({ frequency: 400, duration: 0.08, type: "sine", volume: 0.024 });
}

function playEndSound() {
  playTone({ frequency: 300, duration: 0.12, type: "sine", volume: 0.028 });
  playTone({ frequency: 220, duration: 0.18, type: "sine", volume: 0.024, delay: 0.08 });
}

function setCardState(state = "") {
  gameScreenEl.classList.remove("is-success", "is-danger", "is-warning");
  if (state) {
    gameScreenEl.classList.add(state);
  }
}

function setSoundEnabled(nextValue) {
  soundEnabled = nextValue;
  soundStatusEl.textContent = soundEnabled ? "On" : "Off";
  soundToggleEl.setAttribute("aria-pressed", String(soundEnabled));
}

function pulseLowTimeState() {
  const isLow = decisionTimeRemaining <= 4;
  decisionTimeEl.classList.toggle("is-low", isLow);
  timerBarEl.classList.toggle("is-low", isLow);
  gameScreenEl.classList.toggle("is-warning", isLow);
}

function renderScenario(scenario) {
  currentScenario = scenario;
  roundLocked = false;
  decisionTimeRemaining = getScenarioTime();
  currentScenarioTotalTime = decisionTimeRemaining;

  scenarioTitleEl.textContent = scenario.title;
  scenarioDescriptionEl.textContent = scenario.activeText;
  decisionTimeEl.textContent = `${Math.ceil(decisionTimeRemaining)}s`;
  timerBarEl.style.transform = "scaleX(1)";
  timerBarEl.classList.remove("is-low");
  timerBarEl.classList.toggle("is-controlled", timerFeel === "controlled");
  timerBarEl.classList.toggle("is-impulsive", timerFeel === "impulsive");
  decisionTimeEl.classList.remove("is-low");
  setFeedback("Choose the quietest strong response.");
  setCardState();
  if (correctStreak < 2) {
    setDriftLevel(0);
  }

  gameScreenEl.classList.remove("is-visible");
  void gameScreenEl.offsetWidth;
  gameScreenEl.classList.add("is-visible");
  focusScenarioCard();

  choicesEl.innerHTML = "";

  const shuffledChoices = shuffle(
    scenario.choices.map((text, index) => ({ text, index }))
  );

  shuffledChoices.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice-btn";
    button.textContent = choice.text;
    button.addEventListener("click", () => handleChoice(choice));
    choicesEl.appendChild(button);
  });

  startDecisionTimer();
}

function getRecentPattern() {
  const recent = decisionHistory.slice(-4);
  if (recent.length < 3) {
    return null;
  }

  const wrongFastCount = recent.filter((entry) => entry.outcome === "wrong" && entry.responseSpeed === "fast").length;
  const timeoutCount = recent.filter((entry) => entry.outcome === "timeout").length;
  const correctCount = recent.filter((entry) => entry.outcome === "correct").length;
  const mixedOutcomes = new Set(recent.map((entry) => entry.outcome)).size >= 2;

  if (wrongFastCount >= 2) {
    return "impulsive";
  }

  if (timeoutCount >= 2 || (timeoutCount >= 1 && correctCount <= 1)) {
    return "distracted";
  }

  if (correctCount >= 3) {
    return "controlled";
  }

  if (mixedOutcomes) {
    return "inconsistent";
  }

  return null;
}

function maybeShowDynamicInsight() {
  const decisionsCount = decisionHistory.length;
  if (decisionsCount < nextInsightAt) {
    return;
  }

  const pattern = getRecentPattern();
  if (pattern) {
    showInsight(randomFrom(dynamicInsights[pattern]));
  }

  nextInsightAt += randomFrom(INSIGHT_INTERVALS);
}

function startDecisionTimer() {
  clearDecisionTimer();

  const total = decisionTimeRemaining;

  decisionTimerId = window.setInterval(() => {
    decisionTimeRemaining = Math.max(0, decisionTimeRemaining - 0.1);
    const ratio = total === 0 ? 0 : decisionTimeRemaining / total;
    const visualRatio =
      timerFeel === "impulsive"
        ? Math.pow(ratio, 1.14)
        : timerFeel === "controlled"
          ? Math.pow(ratio, 0.94)
          : ratio;
    const hesitationProgress = Math.max(0, Math.min(1, (0.55 - ratio) / 0.55));

    timerBarEl.style.transform = `scaleX(${visualRatio})`;
    decisionTimeEl.textContent = `${Math.ceil(decisionTimeRemaining)}s`;
    if (correctStreak < 2) {
      setDriftLevel(hesitationProgress);
    }
    pulseLowTimeState();

    if (decisionTimeRemaining <= 0) {
      clearDecisionTimer();
      handleTimeout();
    }
  }, 100);
}

function lockChoices() {
  roundLocked = true;
  Array.from(choicesEl.querySelectorAll(".choice-btn")).forEach((button) => {
    button.disabled = true;
  });
}

function scheduleNextScenario() {
  if (!gameRunning) {
    return;
  }

  window.setTimeout(() => {
    if (gameRunning) {
      renderScenario(pickScenario());
    }
  }, 700);
}

function handleChoice(choice) {
  if (roundLocked || !gameRunning) {
    return;
  }

  clearDecisionTimer();
  lockChoices();
  const clickedButton = Array.from(choicesEl.querySelectorAll(".choice-btn")).find(
    (button) => button.textContent === choice.text
  );

  if (clickedButton) {
    clickedButton.classList.add("is-selected");
  }

  const isCorrect = choice.index === currentScenario.correctAnswerIndex;
  const metricsChange = getChoiceMetrics(currentScenario, choice.index);
  const scenarioDuration = currentScenarioTotalTime;
  const responseElapsed = Math.max(0, scenarioDuration - decisionTimeRemaining);
  const responseRatio = scenarioDuration === 0 ? 1 : responseElapsed / scenarioDuration;
  const responseSpeed = responseRatio <= 0.45 ? "fast" : responseRatio >= 0.8 ? "slow" : "steady";

  if (isCorrect) {
    correctStreak += 1;
    score += 10;
    updateScore();
    showMicroFeedback("correct");
    setCardState("is-success");
    clickedButton?.classList.add("is-correct");
    playSuccessSound();
    navigator.vibrate?.(18);
  } else {
    correctStreak = 0;
    score -= 5;
    updateScore();
    showMicroFeedback("wrong");
    setCardState("is-danger");
    clickedButton?.classList.add("is-wrong");
    playErrorSound();
    navigator.vibrate?.([24, 40, 24]);

    if (responseSpeed === "fast") {
      triggerImpulseChaos(clickedButton);
    }
  }

  applyMetricsChange(metricsChange, {
    outcome: isCorrect ? "correct" : "wrong",
    choice: choice.text,
    responseSpeed
  });

  updateBehaviorVisualState();
  maybeShowDynamicInsight();

  scheduleNextScenario();
}

function handleTimeout() {
  if (roundLocked || !gameRunning) {
    return;
  }

  lockChoices();
  correctStreak = 0;
  score -= 3;
  updateScore();
  showMicroFeedback("timeout");
  setCardState("is-danger");
  playErrorSound();
  applyMetricsChange(
    { focus: -1, impulsivity: 0, discipline: -1 },
    { outcome: "timeout", responseSpeed: "timeout" }
  );
  setDriftLevel(0.72);
  updateBehaviorVisualState();
  maybeShowDynamicInsight();
  scheduleNextScenario();
}

function endGame() {
  gameRunning = false;
  clearDecisionTimer();

  if (gameTimerId) {
    window.clearInterval(gameTimerId);
    gameTimerId = null;
  }

  gameScreenEl.classList.add("hidden");
  gameOverEl.classList.remove("hidden");
  finalScoreEl.textContent = String(score);
  const identity = resolveIdentity();
  if (identity) {
    identityTitleEl.textContent = identity.title;
    identityLineOneEl.textContent = identity.lines[0];
    identityLineTwoEl.textContent = identity.lines[1];
    ecosystemPrimaryEl.textContent = identity.cta.label;
    ecosystemPrimaryEl.href = identity.cta.href;
  }
  playEndSound();
}

function startGameTimer() {
  if (gameTimerId) {
    window.clearInterval(gameTimerId);
  }

  gameTimerId = window.setInterval(() => {
    gameTimeRemaining -= 1;
    updateGameClock();

    if (gameTimeRemaining <= 0) {
      gameTimeRemaining = 0;
      updateGameClock();
      endGame();
    }
  }, 1000);
}

function resetGameState() {
  score = 0;
  gameTimeRemaining = GAME_DURATION;
  behavioralMetrics = createEmptyMetrics();
  decisionHistory = [];
  lastScenarioTitle = null;
  nextInsightAt = 3;
  correctStreak = 0;
  if (feedbackTimeoutId) {
    window.clearTimeout(feedbackTimeoutId);
    feedbackTimeoutId = null;
  }
  if (insightTimeoutId) {
    window.clearTimeout(insightTimeoutId);
    insightTimeoutId = null;
  }
  updateScore();
  updateGameClock();
  decisionTimeEl.textContent = `${START_DECISION_TIME}s`;
  timerBarEl.style.transform = "scaleX(1)";
  scenarioTitleEl.textContent = "Quiet Power Cafe";
  scenarioDescriptionEl.textContent = "A real-time test of pressure, attention, and control.";
  setFeedback("Stay focused. One customer at a time.", "neutral");
  insightFeedbackEl.textContent = "";
  insightFeedbackEl.classList.remove("is-visible");
  clearVisualModes();
  setCardState();
  persistBehavioralState();
}

function startGame() {
  ensureAudioContext();
  resetGameState();
  gameRunning = true;
  gameOverEl.classList.add("hidden");
  gameScreenEl.classList.remove("hidden");
  focusScenarioCard();
  startGameTimer();
  playStartSound();
  renderScenario(pickScenario());
}

startButtonEl.addEventListener("click", startGame);
restartButtonEl.addEventListener("click", startGame);
soundToggleEl.addEventListener("click", () => {
  setSoundEnabled(!soundEnabled);
  if (soundEnabled) {
    playStartSound();
  }
});
shareResultButtonEl.addEventListener("click", async () => {
  const text = `${identityTitleEl.textContent} — ${identityLineOneEl.textContent} ${identityLineTwoEl.textContent}`;
  const url = `${window.location.origin}/quiet-power-cafe/`;

  if (navigator.share) {
    try {
      await navigator.share({
        title: `Quiet Power Cafe — ${identityTitleEl.textContent}`,
        text,
        url
      });
      return;
    } catch (_) {
      // Fallback to clipboard.
    }
  }

  try {
    await navigator.clipboard.writeText(`${text} ${url}`);
    shareResultButtonEl.textContent = "Result copied";
    window.setTimeout(() => {
      shareResultButtonEl.textContent = "Share your result";
    }, 1400);
  } catch (_) {
    shareResultButtonEl.textContent = "Share unavailable";
    window.setTimeout(() => {
      shareResultButtonEl.textContent = "Share your result";
    }, 1400);
  }
});
