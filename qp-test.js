const QUESTIONS_PER_RUN = 7;

const qpQuestions = [
  // LEVEL 1 — REACTION
  {
    id: "L1-Q1",
    level: "reaction",
    question: "You receive unexpected criticism. What do you do first?",
    options: [
      {
        label: "Reply immediately to defend yourself",
        score: 0,
        punchline: "Fast feels strong. It isn’t."
      },
      {
        label: "Pause and process it before replying",
        score: 1,
        punchline: "Control starts where reaction ends."
      }
    ]
  },
  {
    id: "L1-Q2",
    level: "reaction",
    question: "Someone leaves your message on read. How do you react?",
    options: [
      {
        label: "Keep checking and replaying the conversation in your head",
        score: 0,
        punchline: "Overthinking is just loud reaction."
      },
      {
        label: "Move on with your day and reply when it actually matters",
        score: 1,
        punchline: "Quiet power doesn’t chase attention."
      }
    ]
  },
  {
    id: "L1-Q3",
    level: "reaction",
    question: "You have a packed day. How do you start?",
    options: [
      {
        label: "Open everything and tackle whatever screams the loudest",
        score: 0,
        punchline: "Urgency loves chaos. So does reactivity."
      },
      {
        label: "Pick one key task and start only with that",
        score: 1,
        punchline: "Focus is the first move of control."
      }
    ]
  },

  // LEVEL 2 — FILTER
  {
    id: "L2-Q1",
    level: "filter",
    question: "You see 20 new notifications. What’s your first move?",
    options: [
      {
        label: "Open everything so you don’t miss anything",
        score: 0,
        punchline: "If everything matters, nothing does."
      },
      {
        label: "Only check what’s connected to today’s priorities",
        score: 1,
        punchline: "Filtering is choosing what deserves your mind."
      }
    ]
  },
  {
    id: "L2-Q2",
    level: "filter",
    question: "You get conflicting information about a decision.",
    options: [
      {
        label: "Get stuck comparing every detail before acting",
        score: 0,
        punchline: "Endless comparison is just fancy hesitation."
      },
      {
        label: "Set 1–2 clear criteria and decide based on that",
        score: 1,
        punchline: "Clarity comes from simple rules, not more data."
      }
    ]
  },

  // LEVEL 3 — CONTROL
  {
    id: "L3-Q1",
    level: "control",
    question: "You planned 2 hours of deep work. A distraction appears.",
    options: [
      {
        label: "You follow the distraction and plan to restart later",
        score: 0,
        punchline: "Every interruption you accept trains the next one."
      },
      {
        label: "You notice it, park it, and return to the plan",
        score: 1,
        punchline: "Control is keeping the plan when the world doesn’t."
      }
    ]
  },
  {
    id: "L3-Q2",
    level: "control",
    question: "You’re tired, but you had a commitment with yourself.",
    options: [
      {
        label: "You postpone again and promise that tomorrow is serious",
        score: 0,
        punchline: "Motivation talks. Control shows up."
      },
      {
        label: "You do a smaller version, but keep the promise",
        score: 1,
        punchline: "Quiet power is consistency, not intensity."
      }
    ]
  }
];

let currentIndex = 0;
let currentQuestions = [];
let totalScore = 0;
let reactionScore = 0;
let filterScore = 0;
let controlScore = 0;

const startBtn = document.querySelector(".qp-start-btn");
const questionContainer = document.getElementById("qp-question-container");
const progressBar = document.getElementById("qp-progress-bar");
const currentSpan = document.getElementById("qp-current");
const totalSpan = document.getElementById("qp-total");
const resultSection = document.getElementById("qp-result");

if (totalSpan) {
  totalSpan.textContent = QUESTIONS_PER_RUN;
}

function shuffle(array) {
  return array
    .map((item) => ({ sort: Math.random(), value: item }))
    .sort((a, b) => a.sort - b.sort)
    .map((item) => item.value);
}

function setProgress() {
  const progressPercent = currentQuestions.length
    ? Math.round((currentIndex / currentQuestions.length) * 100)
    : 0;

  if (currentSpan) {
    currentSpan.textContent = String(Math.min(currentIndex, QUESTIONS_PER_RUN));
  }

  if (progressBar) {
    progressBar.style.setProperty("--qp-progress-value", `${progressPercent}%`);
  }
}

function startTest() {
  totalScore = 0;
  reactionScore = 0;
  filterScore = 0;
  controlScore = 0;
  currentIndex = 0;

  currentQuestions = shuffle(qpQuestions).slice(0, QUESTIONS_PER_RUN);

  resultSection.classList.add("qp-result-hidden");
  setProgress();
  renderQuestion();
}

function renderQuestion() {
  const q = currentQuestions[currentIndex];

  if (!q) {
    showResult();
    return;
  }

  currentSpan.textContent = currentIndex + 1;
  const progressPercent = ((currentIndex) / QUESTIONS_PER_RUN) * 100;
  progressBar.style.setProperty("--qp-progress-value", `${progressPercent}%`);

  const optionsHtml = shuffle(q.options)
    .map(
      (opt) => `
      <button type="button" class="qp-option-btn" data-score="${opt.score}" data-level="${q.level}">
        <span>${opt.label}</span>
        <span class="qp-option-punchline">${opt.punchline}</span>
      </button>
    `
    )
    .join("");

  questionContainer.innerHTML = `
    <div class="qp-question-card">
      <p class="qp-question-label">${q.level.toUpperCase()} · Question ${currentIndex + 1} of ${currentQuestions.length}</p>
      <p class="qp-question-text">${q.question}</p>
      <div class="qp-options">
        ${optionsHtml}
      </div>
    </div>
  `;

  document.querySelectorAll(".qp-option-btn").forEach((btn) => {
    btn.addEventListener("click", () => handleAnswer(btn));
  });
}

function handleAnswer(button) {
  const score = Number(button.dataset.score);
  const level = button.dataset.level;

  totalScore += score;
  if (level === "reaction") reactionScore += score;
  if (level === "filter") filterScore += score;
  if (level === "control") controlScore += score;

  currentIndex += 1;
  setProgress();

  if (currentIndex >= currentQuestions.length) {
    showResult();
  } else {
    renderQuestion();
  }
}

function showResult() {
  resultSection.classList.remove("qp-result-hidden");
  questionContainer.innerHTML = "";

  const reactionMax = currentQuestions.filter((q) => q.level === "reaction").length;
  const filterMax = currentQuestions.filter((q) => q.level === "filter").length;
  const controlMax = currentQuestions.filter((q) => q.level === "control").length;

  const reactionPct = reactionMax ? Math.round((reactionScore / reactionMax) * 100) : 0;
  const filterPct = filterMax ? Math.round((filterScore / filterMax) * 100) : 0;
  const controlPct = controlMax ? Math.round((controlScore / controlMax) * 100) : 0;

  let title = "";
  let text = "";

  if (reactionPct >= 60 && filterPct < 60 && controlPct < 60) {
    title = "You’re operating in reaction mode.";
    text = "You move fast. But speed is not control. You’re reacting more than you think.";
  } else if (reactionPct < 60 && filterPct >= 60 && controlPct >= 60) {
    title = "You move on your own signal.";
    text = "You choose when to act. Noise doesn’t own your attention anymore.";
  } else {
    title = "You see the patterns, but don’t own them yet.";
    text = "You already notice the noise. Now you need structure, not more insight.";
  }

  document.getElementById("qp-result-title").textContent = title;
  document.getElementById("qp-result-text").textContent = text;

  document.getElementById("qp-reaction-score").textContent =
    `Reaction: ${reactionPct}% quiet, ${100 - reactionPct}% reactive`;
  document.getElementById("qp-filter-score").textContent =
    `Filter: ${filterPct}% clear, ${100 - filterPct}% noisy`;
  document.getElementById("qp-control-score").textContent =
    `Control: ${controlPct}% consistent, ${100 - controlPct}% fragile`;

  if (progressBar) {
    progressBar.style.setProperty("--qp-progress-value", "100%");
  }
  if (currentSpan) {
    currentSpan.textContent = String(currentQuestions.length);
  }
}

if (startBtn) {
  startBtn.addEventListener("click", startTest);
}

setProgress();
