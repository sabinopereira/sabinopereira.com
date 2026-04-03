const scenarios = [
  {
    title: "Check your phone",
    description: "A customer taps the counter and whispers that your phone just lit up again.",
    choices: [
      {
        text: "Leave it face down and finish the current task",
        correct: true,
        metrics: { focus: 2, impulsivity: -1, emotionalReactivity: 0, discipline: 2 }
      },
      {
        text: "Check it quickly while no one is looking",
        correct: false,
        metrics: { focus: -1, impulsivity: 2, emotionalReactivity: 0, discipline: -1 }
      },
      {
        text: "Unlock it and scroll for a minute",
        correct: false,
        metrics: { focus: -2, impulsivity: 3, emotionalReactivity: 0, discipline: -2 }
      }
    ]
  },
  {
    title: "Reply instantly to message",
    description: "A regular insists that every message must be answered right now.",
    choices: [
      {
        text: "Queue the reply for your next communication block",
        correct: true,
        metrics: { focus: 2, impulsivity: -1, emotionalReactivity: -1, discipline: 2 }
      },
      {
        text: "Answer immediately so it stops bothering you",
        correct: false,
        metrics: { focus: -1, impulsivity: 2, emotionalReactivity: 1, discipline: -1 }
      },
      {
        text: "Open the chat and over-explain everything",
        correct: false,
        metrics: { focus: -2, impulsivity: 1, emotionalReactivity: 2, discipline: -1 }
      }
    ]
  },
  {
    title: "Scroll social media",
    description: "The room gets quiet. The easiest move would be to fill the gap with noise.",
    choices: [
      {
        text: "Stay with the pause and return to the task in front of you",
        correct: true,
        metrics: { focus: 2, impulsivity: -1, emotionalReactivity: -1, discipline: 2 }
      },
      {
        text: "Scroll for inspiration until something useful appears",
        correct: false,
        metrics: { focus: -1, impulsivity: 2, emotionalReactivity: 0, discipline: -1 }
      },
      {
        text: "Hop across three apps to wake your brain up",
        correct: false,
        metrics: { focus: -2, impulsivity: 3, emotionalReactivity: 1, discipline: -2 }
      }
    ]
  },
  {
    title: "Stay focused on task",
    description: "A difficult task is in front of you, and a more entertaining one is calling from the side.",
    choices: [
      {
        text: "Keep the hard task open and take the next clear step",
        correct: true,
        metrics: { focus: 3, impulsivity: -1, emotionalReactivity: 0, discipline: 2 }
      },
      {
        text: "Switch tasks so you can feel productive faster",
        correct: false,
        metrics: { focus: -2, impulsivity: 2, emotionalReactivity: 0, discipline: -1 }
      },
      {
        text: "Rearrange your desk before deciding what to do",
        correct: false,
        metrics: { focus: -1, impulsivity: 1, emotionalReactivity: 0, discipline: -2 }
      }
    ]
  },
  {
    title: "Overthink decision",
    description: "A customer asks for certainty when the real need is a good-enough next move.",
    choices: [
      {
        text: "Choose the strongest available option and move",
        correct: true,
        metrics: { focus: 2, impulsivity: -1, emotionalReactivity: -1, discipline: 2 }
      },
      {
        text: "Keep comparing every option until you feel perfect",
        correct: false,
        metrics: { focus: -1, impulsivity: -1, emotionalReactivity: 1, discipline: -1 }
      },
      {
        text: "Ask three more people before deciding anything",
        correct: false,
        metrics: { focus: -1, impulsivity: 0, emotionalReactivity: 1, discipline: -1 }
      }
    ]
  },
  {
    title: "React emotionally",
    description: "Someone brings a sharp comment to the counter and waits for a quick reaction.",
    choices: [
      {
        text: "Pause, breathe, and respond after the first emotion passes",
        correct: true,
        metrics: { focus: 1, impulsivity: -1, emotionalReactivity: -2, discipline: 2 }
      },
      {
        text: "Answer with the same tone immediately",
        correct: false,
        metrics: { focus: -1, impulsivity: 2, emotionalReactivity: 3, discipline: -1 }
      },
      {
        text: "Replay the comment in your head and spiral",
        correct: false,
        metrics: { focus: -2, impulsivity: 0, emotionalReactivity: 2, discipline: -2 }
      }
    ]
  },
  {
    title: "Someone interrupts you",
    description: "A noisy customer arrives while you are in the middle of something important.",
    choices: [
      {
        text: "Acknowledge it briefly and protect the current block",
        correct: true,
        metrics: { focus: 2, impulsivity: -1, emotionalReactivity: -1, discipline: 2 }
      },
      {
        text: "Drop everything because the interruption feels urgent",
        correct: false,
        metrics: { focus: -2, impulsivity: 2, emotionalReactivity: 1, discipline: -1 }
      },
      {
        text: "Complain internally while doing neither thing well",
        correct: false,
        metrics: { focus: -2, impulsivity: 0, emotionalReactivity: 2, discipline: -2 }
      }
    ]
  },
  {
    title: "You feel bored",
    description: "The work feels slow. A customer offers novelty instead of depth.",
    choices: [
      {
        text: "Stay with the task long enough for depth to return",
        correct: true,
        metrics: { focus: 2, impulsivity: -1, emotionalReactivity: -1, discipline: 2 }
      },
      {
        text: "Open tabs until something exciting appears",
        correct: false,
        metrics: { focus: -2, impulsivity: 3, emotionalReactivity: 0, discipline: -2 }
      },
      {
        text: "Quit the task because boredom means it is wrong",
        correct: false,
        metrics: { focus: -2, impulsivity: 2, emotionalReactivity: 1, discipline: -2 }
      }
    ]
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
    emotionalReactivity: 0,
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

function resolveIdentity() {
  const metrics = behavioralMetrics || createEmptyMetrics();
  const profileScore = {
    calmStrategist: (metrics.focus * 2) + (metrics.discipline * 2) - metrics.impulsivity - metrics.emotionalReactivity,
    reactiveOperator: (metrics.impulsivity * 2) + (metrics.emotionalReactivity * 2) - metrics.focus - metrics.discipline,
    disciplinedBuilder: (metrics.discipline * 2) + metrics.focus - metrics.impulsivity,
    emotionalResponder: (metrics.emotionalReactivity * 2) + metrics.impulsivity - metrics.discipline
  };

  const profiles = [
    {
      key: "calmStrategist",
      title: "The Calm Strategist",
      lines: [
        "You slow the room down before it drags you.",
        "Composure is not delay. It is selective force."
      ],
      cta: { label: "Start fixing it", href: "/quiet-power.html" }
    },
    {
      key: "reactiveOperator",
      title: "The Reactive Operator",
      lines: [
        "You move fast. Too fast.",
        "Speed feels like control. It isn't."
      ],
      cta: { label: "Start fixing it", href: "/test.html" }
    },
    {
      key: "disciplinedBuilder",
      title: "The Disciplined Builder",
      lines: [
        "You trust repeatable standards more than passing mood.",
        "Your strength is not intensity. It is consistency."
      ],
      cta: { label: "Start fixing it", href: "/quiet-power.html" }
    },
    {
      key: "emotionalResponder",
      title: "The Emotional Responder",
      lines: [
        "The room gets inside you too quickly.",
        "The first feeling arrives before the better decision does."
      ],
      cta: { label: "Start fixing it", href: "/quiet-thought-what-is-quiet-power.html" }
    }
  ];

  return profiles.reduce((best, profile) => {
    const candidateScore = profileScore[profile.key];
    if (!best || candidateScore > best.score) {
      return { ...profile, score: candidateScore };
    }
    return best;
  }, null);
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
  scenarioDescriptionEl.textContent = scenario.description;
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

  shuffle(scenario.choices).forEach((choice) => {
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

  if (choice.correct) {
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

  applyMetricsChange(choice.metrics, {
    outcome: choice.correct ? "correct" : "wrong",
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
    { focus: -1, impulsivity: 0, emotionalReactivity: 1, discipline: -1 },
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
