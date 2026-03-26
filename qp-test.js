// Número de perguntas por sessão
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
  }
  // Aqui vamos depois adicionar mais perguntas (Filter, Control, etc.)
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

totalSpan.textContent = QUESTIONS_PER_RUN;

// shuffle helper
function shuffle(array) {
  return array
    .map((item) => ({ sort: Math.random(), value: item }))
    .sort((a, b) => a.sort - b.sort)
    .map((item) => item.value);
}

function startTest() {
  totalScore = 0;
  reactionScore = 0;
  filterScore = 0;
  controlScore = 0;
  currentIndex = 0;

  // escolhe perguntas aleatórias
  const shuffled = shuffle(qpQuestions);
  currentQuestions = shuffled.slice(0, QUESTIONS_PER_RUN);

  resultSection.classList.add("qp-result-hidden");
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
  progressBar.style.setProperty("--qp-progress", `${progressPercent}%`);
  progressBar.style.setProperty("width", "100%"); // fallback

  // cria HTML da pergunta
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
      <p class="qp-question-label">${q.level.toUpperCase()}</p>
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
  if (currentIndex >= QUESTIONS_PER_RUN) {
    showResult();
  } else {
    renderQuestion();
  }
}

function showResult() {
  // aqui depois vamos transformar scores em perfis (Reactive / Aware / Controlled)
  resultSection.classList.remove("qp-result-hidden");
  questionContainer.innerHTML = "";

  // placeholders para já
  document.getElementById("qp-result-title").textContent =
    "You’re operating in reaction mode.";
  document.getElementById("qp-result-text").textContent =
    "You move fast. But speed is not control. You’re reacting more than you think.";

  document.getElementById("qp-reaction-score").textContent =
    "Reaction score: " + reactionScore;
  document.getElementById("qp-filter-score").textContent =
    "Filter score: " + filterScore;
  document.getElementById("qp-control-score").textContent =
    "Control score: " + controlScore;
}

if (startBtn) {
  startBtn.addEventListener("click", startTest);
}
