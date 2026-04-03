const scenarios = [
  {
    title: "Check your phone",
    description: "A customer taps the counter and whispers that your phone just lit up again.",
    choices: [
      { text: "Leave it face down and finish the current task", correct: true },
      { text: "Check it quickly while no one is looking", correct: false },
      { text: "Unlock it and scroll for a minute", correct: false }
    ]
  },
  {
    title: "Reply instantly to message",
    description: "A regular insists that every message must be answered right now.",
    choices: [
      { text: "Queue the reply for your next communication block", correct: true },
      { text: "Answer immediately so it stops bothering you", correct: false },
      { text: "Open the chat and over-explain everything", correct: false }
    ]
  },
  {
    title: "Scroll social media",
    description: "The room gets quiet. The easiest move would be to fill the gap with noise.",
    choices: [
      { text: "Stay with the pause and return to the task in front of you", correct: true },
      { text: "Scroll for inspiration until something useful appears", correct: false },
      { text: "Hop across three apps to wake your brain up", correct: false }
    ]
  },
  {
    title: "Stay focused on task",
    description: "A difficult task is in front of you, and a more entertaining one is calling from the side.",
    choices: [
      { text: "Keep the hard task open and take the next clear step", correct: true },
      { text: "Switch tasks so you can feel productive faster", correct: false },
      { text: "Rearrange your desk before deciding what to do", correct: false }
    ]
  },
  {
    title: "Overthink decision",
    description: "A customer asks for certainty when the real need is a good-enough next move.",
    choices: [
      { text: "Choose the strongest available option and move", correct: true },
      { text: "Keep comparing every option until you feel perfect", correct: false },
      { text: "Ask three more people before deciding anything", correct: false }
    ]
  },
  {
    title: "React emotionally",
    description: "Someone brings a sharp comment to the counter and waits for a quick reaction.",
    choices: [
      { text: "Pause, breathe, and respond after the first emotion passes", correct: true },
      { text: "Answer with the same tone immediately", correct: false },
      { text: "Replay the comment in your head and spiral", correct: false }
    ]
  },
  {
    title: "Someone interrupts you",
    description: "A noisy customer arrives while you are in the middle of something important.",
    choices: [
      { text: "Acknowledge it briefly and protect the current block", correct: true },
      { text: "Drop everything because the interruption feels urgent", correct: false },
      { text: "Complain internally while doing neither thing well", correct: false }
    ]
  },
  {
    title: "You feel bored",
    description: "The work feels slow. A customer offers novelty instead of depth.",
    choices: [
      { text: "Stay with the task long enough for depth to return", correct: true },
      { text: "Open tabs until something exciting appears", correct: false },
      { text: "Quit the task because boredom means it is wrong", correct: false }
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
const restartButtonEl = document.getElementById("restart-button");
const startButtonEl = document.getElementById("start-button");

const GAME_DURATION = 60;
const START_DECISION_TIME = 10;
const MIN_DECISION_TIME = 7;

let score = 0;
let gameTimeRemaining = GAME_DURATION;
let decisionTimeRemaining = START_DECISION_TIME;
let currentScenario = null;
let gameTimerId = null;
let decisionTimerId = null;
let roundLocked = false;
let gameRunning = false;

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
}

function updateGameClock() {
  gameTimeEl.textContent = `${gameTimeRemaining}s`;
}

function setFeedback(message, tone = "positive") {
  feedbackEl.textContent = message;
  feedbackEl.classList.remove("is-negative", "is-neutral");

  if (tone === "negative") {
    feedbackEl.classList.add("is-negative");
  } else if (tone === "neutral") {
    feedbackEl.classList.add("is-neutral");
  }
}

function clearDecisionTimer() {
  if (decisionTimerId) {
    window.clearInterval(decisionTimerId);
    decisionTimerId = null;
  }
}

function renderScenario(scenario) {
  currentScenario = scenario;
  roundLocked = false;
  decisionTimeRemaining = getScenarioTime();

  scenarioTitleEl.textContent = scenario.title;
  scenarioDescriptionEl.textContent = scenario.description;
  decisionTimeEl.textContent = `${Math.ceil(decisionTimeRemaining)}s`;
  timerBarEl.style.transform = "scaleX(1)";
  setFeedback("Choose the quietest strong response.");

  gameScreenEl.classList.remove("is-visible");
  void gameScreenEl.offsetWidth;
  gameScreenEl.classList.add("is-visible");

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

  if (choice.correct) {
    score += 10;
    updateScore();
    setFeedback("+10 Calm choice. The room stays steady.");
  } else {
    score -= 5;
    updateScore();
    setFeedback("-5 Noise got in. Try the calmer move next time.", "negative");
  }

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
  updateScore();
  updateGameClock();
  decisionTimeEl.textContent = `${START_DECISION_TIME}s`;
  timerBarEl.style.transform = "scaleX(1)";
  scenarioTitleEl.textContent = "Quiet Power Cafe";
  scenarioDescriptionEl.textContent = "Serve calm choices under pressure before the shift ends.";
  setFeedback("Stay focused. One customer at a time.", "neutral");
}

function startGame() {
  resetGameState();
  gameRunning = true;
  gameOverEl.classList.add("hidden");
  gameScreenEl.classList.remove("hidden");
  startGameTimer();
  renderScenario(scenarios[Math.floor(Math.random() * scenarios.length)]);
}

startButtonEl.addEventListener("click", startGame);
restartButtonEl.addEventListener("click", startGame);
