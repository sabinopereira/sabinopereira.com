const QUESTIONS_PER_RUN = 7;

const qpQuestions = [
  {
    id: "L1-Q1",
    level: "reaction",
    question: "Recebes uma crítica inesperada. O que fazes primeiro?",
    options: [
      {
        label: "Respondo imediatamente para me defender",
        score: 0,
        punchline: "Fast feels strong. It isn’t."
      },
      {
        label: "Pauso e analiso antes de responder",
        score: 1,
        punchline: "Control starts where reaction ends."
      }
    ]
  },
  {
    id: "L1-Q2",
    level: "reaction",
    question: "Alguém ignora a tua mensagem. Reages como?",
    options: [
      {
        label: "Fico a ruminar e releio a conversa várias vezes",
        score: 0,
        punchline: "Overthinking is just loud reaction."
      },
      {
        label: "Sigo com o dia e respondo quando fizer sentido",
        score: 1,
        punchline: "Quiet power doesn’t chase attention."
      }
    ]
  },
  {
    id: "L1-Q3",
    level: "reaction",
    question: "Tens um dia cheio de tarefas. Como começas?",
    options: [
      {
        label: "Abro tudo ao mesmo tempo e faço o que grita mais alto",
        score: 0,
        punchline: "Urgency loves chaos. So does reactivity."
      },
      {
        label: "Escolho uma tarefa chave e começo só por aí",
        score: 1,
        punchline: "Focus is the first move of control."
      }
    ]
  },
  {
    id: "L2-Q1",
    level: "filter",
    question: "Tens 20 notificações novas. O que fazes primeiro?",
    options: [
      {
        label: "Abro tudo para não perder nada",
        score: 0,
        punchline: "If everything matters, nothing does."
      },
      {
        label: "Ves só o que está ligado ao que é importante hoje",
        score: 1,
        punchline: "Filtering is choosing what deserves your mind."
      }
    ]
  },
  {
    id: "L2-Q2",
    level: "filter",
    question: "Recebes informação contraditória sobre uma decisão.",
    options: [
      {
        label: "Ficas preso a comparar tudo em detalhe",
        score: 0,
        punchline: "Endless comparison is just fancy hesitation."
      },
      {
        label: "Defines 1–2 critérios e decides com base nisso",
        score: 1,
        punchline: "Clarity comes from simple rules, not more data."
      }
    ]
  },
  {
    id: "L3-Q1",
    level: "control",
    question: "Planeaste 2 horas de foco, mas aparece distração.",
    options: [
      {
        label: "Respondes à distração e recomeças mais tarde",
        score: 0,
        punchline: "Every interruption you accept trains the next one."
      },
      {
        label: "Registas a distração e voltas ao plano original",
        score: 1,
        punchline: "Control is keeping the plan when the world doesn’t."
      }
    ]
  },
  {
    id: "L3-Q2",
    level: "control",
    question: "Estás cansado, mas tinhas combinado algo contigo próprio.",
    options: [
      {
        label: "Adias outra vez e prometes que “amanhã é a sério”",
        score: 0,
        punchline: "Motivation talks. Control shows up."
      },
      {
        label: "Fazes uma versão menor, mas cumpres o combinado",
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
