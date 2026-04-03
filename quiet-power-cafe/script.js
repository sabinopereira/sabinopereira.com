const scenarios = [
  {
    title: "Notification Pull",
    text: "Your phone lights up while you're focused.",
    choices: ["Check it quickly", "Ignore and continue working", "Pick it up but don't open anything"],
    correctAnswerIndex: 1
  },
  {
    title: "Instant Reply Trap",
    text: "Someone messages you. It feels urgent.",
    choices: ["Reply immediately", "Finish your task first", "Send a quick short reply"],
    correctAnswerIndex: 1
  },
  {
    title: "Boredom Drift",
    text: "You feel bored in the middle of a task.",
    choices: ["Switch to something easier", "Push through the discomfort", "Take a random break"],
    correctAnswerIndex: 1
  },
  {
    title: "Emotional Trigger",
    text: "Someone says something that annoys you.",
    choices: ["Respond immediately", "Pause before reacting", "Respond sarcastically"],
    correctAnswerIndex: 1
  },
  {
    title: "Overthinking Loop",
    text: "You're unsure about a decision.",
    choices: ["Keep thinking more", "Make a decision with available info", "Ask others before deciding"],
    correctAnswerIndex: 1
  },
  {
    title: "Easy Escape",
    text: "You think about watching something instead of working.",
    choices: ["Start watching", "Stay on task", "Watch just one short video"],
    correctAnswerIndex: 1
  },
  {
    title: "Pressure Spike",
    text: "You have too many things to do.",
    choices: ["Try to do everything fast", "Prioritize one thing and start", "Jump between tasks"],
    correctAnswerIndex: 1
  },
  {
    title: "Mental Fatigue",
    text: "You feel mentally tired.",
    choices: ["Stop everything", "Slow down but continue", "Switch to something random"],
    correctAnswerIndex: 1
  },
  {
    title: "Social Distraction",
    text: "Someone starts talking to you while you work.",
    choices: ["Fully engage", "Politely delay the conversation", "Half listen while working"],
    correctAnswerIndex: 1
  },
  {
    title: "False Urgency",
    text: "A task suddenly feels urgent.",
    choices: ["Drop everything and do it", "Evaluate if it truly matters first", "Start it while doing other things"],
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
const gameScreenEl = document.getElementById("game-screen");
const gameOverEl = document.getElementById("game-over");
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

let score = 0;
let gameTimeRemaining = GAME_DURATION;
let decisionTimeRemaining = START_DECISION_TIME;
let currentScenario = null;
let gameTimerId = null;
let decisionTimerId = null;
let roundLocked = false;
let gameRunning = false;
let soundEnabled = true;
let audioContext = null;
let behavioralMetrics = null;
let decisionHistory = [];

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
    outcome: meta.outcome || "decision",
    choice: meta.choice || null,
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

function resolveIdentity() {
  const metrics = behavioralMetrics || createEmptyMetrics();
  const distraction = Math.max(0, -metrics.focus) + Math.max(0, -metrics.discipline) + Math.max(0, metrics.impulsivity - 2);

  if (metrics.focus >= 8 && metrics.discipline >= 8 && metrics.impulsivity <= 2) {
    return {
      title: "The Calm Strategist",
      lines: [
        "You don't rush. You don't react. You decide.",
        "You don't chase control. You operate from it."
      ],
      cta: { label: "Improve your Quiet Power", href: "/quiet-power.html" }
    };
  }

  if (metrics.impulsivity >= 8) {
    return {
      title: "The Reactive Operator",
      lines: [
        "You move fast. Too fast. You react before you think.",
        "You don't lack effort. You lack pause."
      ],
      cta: { label: "Improve your Quiet Power", href: "/test.html" }
    };
  }

  if (distraction >= 8) {
    return {
      title: "The Distracted Drifter",
      lines: [
        "You don't choose. You drift. Small distractions keep pulling you away.",
        "You're not lost. You're just not deciding."
      ],
      cta: { label: "Improve your Quiet Power", href: "/quiet-thought-while-you-wait-they-build.html" }
    };
  }

  return {
    title: "The Controlled Performer",
    lines: [
      "You handle pressure well. You stay composed.",
      "You're close. Now refine it."
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
  feedbackEl.classList.remove("is-negative", "is-neutral", "is-animated");

  if (tone === "negative") {
    feedbackEl.classList.add("is-negative");
  } else if (tone === "neutral") {
    feedbackEl.classList.add("is-neutral");
  }

  void feedbackEl.offsetWidth;
  feedbackEl.classList.add("is-animated");
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

  scenarioTitleEl.textContent = scenario.title;
  scenarioDescriptionEl.textContent = scenario.text;
  decisionTimeEl.textContent = `${Math.ceil(decisionTimeRemaining)}s`;
  timerBarEl.style.transform = "scaleX(1)";
  timerBarEl.classList.remove("is-low");
  decisionTimeEl.classList.remove("is-low");
  setFeedback("Choose the quietest strong response.");
  setCardState();

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

function startDecisionTimer() {
  clearDecisionTimer();

  const total = decisionTimeRemaining;

  decisionTimerId = window.setInterval(() => {
    decisionTimeRemaining = Math.max(0, decisionTimeRemaining - 0.1);
    const ratio = total === 0 ? 0 : decisionTimeRemaining / total;

    timerBarEl.style.transform = `scaleX(${ratio})`;
    decisionTimeEl.textContent = `${Math.ceil(decisionTimeRemaining)}s`;
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
      renderScenario(scenarios[Math.floor(Math.random() * scenarios.length)]);
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

  if (isCorrect) {
    score += 10;
    updateScore();
    setFeedback("+10 Calm choice. The room stays steady.");
    setCardState("is-success");
    clickedButton?.classList.add("is-correct");
    playSuccessSound();
    navigator.vibrate?.(18);
  } else {
    score -= 5;
    updateScore();
    setFeedback("-5 Noise got in. Try the calmer move next time.", "negative");
    setCardState("is-danger");
    clickedButton?.classList.add("is-wrong");
    playErrorSound();
    navigator.vibrate?.([24, 40, 24]);
  }

  applyMetricsChange(metricsChange, {
    outcome: isCorrect ? "correct" : "wrong",
    choice: choice.text
  });

  scheduleNextScenario();
}

function handleTimeout() {
  if (roundLocked || !gameRunning) {
    return;
  }

  lockChoices();
  score -= 3;
  updateScore();
  setFeedback("-3 Too slow. The customer left with the noise.", "negative");
  setCardState("is-danger");
  playErrorSound();
  applyMetricsChange(
    { focus: -1, impulsivity: 0, discipline: -1 },
    { outcome: "timeout" }
  );
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
  updateScore();
  updateGameClock();
  decisionTimeEl.textContent = `${START_DECISION_TIME}s`;
  timerBarEl.style.transform = "scaleX(1)";
  scenarioTitleEl.textContent = "Quiet Power Cafe";
  scenarioDescriptionEl.textContent = "Serve calm choices under pressure before the shift ends.";
  setFeedback("Stay focused. One customer at a time.", "neutral");
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
  renderScenario(scenarios[Math.floor(Math.random() * scenarios.length)]);
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
