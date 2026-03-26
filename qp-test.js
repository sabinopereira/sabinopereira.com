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

const qpContainer = document.getElementById("qp-question-container");
const qpResult = document.getElementById("qp-result");
const qpProgressBar = document.getElementById("qp-progress-bar");
const qpCurrent = document.getElementById("qp-current");
const qpTotal = document.getElementById("qp-total");
const qpStartBtn = document.querySelector(".qp-start-btn");

let qpIndex = 0;
let qpScores = {
  reaction: 0,
  filter: 0,
  control: 0
};

qpTotal.textContent = String(qpQuestions.length);

function qpSetProgress() {
  const percent = (qpIndex / qpQuestions.length) * 100;
  qpCurrent.textContent = String(Math.min(qpIndex, qpQuestions.length));
  qpProgressBar.style.setProperty("--qp-progress", `${percent}%`);
  qpProgressBar.style.setProperty("width", "100%");
  qpProgressBar.dataset.progress = `${percent}%`;
}

function qpRenderQuestion() {
  const item = qpQuestions[qpIndex];

  if (!item) {
    qpShowResult();
    return;
  }

  qpContainer.innerHTML = `
    <div class="qp-question-card">
      <p class="qp-question-label">${item.level.toUpperCase()} · Question ${qpIndex + 1} of ${qpQuestions.length}</p>
      <p class="qp-question-text">${item.question}</p>
      <div class="qp-options">
        ${item.options.map((option, optionIndex) => `
          <button type="button" class="qp-option-btn" data-option="${optionIndex}">
            <span>${option.label}</span>
            <span class="qp-option-punchline">${option.punchline}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;

  qpContainer.querySelectorAll(".qp-option-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const selected = item.options[Number(button.dataset.option)];
      qpScores[item.level] += selected.score;
      qpIndex += 1;
      qpSetProgress();
      qpRenderQuestion();
    });
  });
}

function qpShowResult() {
  const total = qpScores.reaction + qpScores.filter + qpScores.control;
  let title = "Calm in progress";
  let text = "You are building control, but pressure still moves parts of your system faster than it should.";

  if (total >= 11) {
    title = "Quiet Power is visible";
    text = "You hold more calm, filtration, and internal control than most people under pressure.";
  } else if (total <= 5) {
    title = "Noise still gets in";
    text = "Your reactions are still too available to pressure, urgency, and external noise.";
  }

  document.getElementById("qp-result-title").textContent = title;
  document.getElementById("qp-result-text").textContent = text;
  document.getElementById("qp-reaction-score").textContent = `${qpScores.reaction} / 3`;
  document.getElementById("qp-filter-score").textContent = `${qpScores.filter} / 2`;
  document.getElementById("qp-control-score").textContent = `${qpScores.control} / 2`;

  qpContainer.innerHTML = "";
  qpResult.classList.remove("qp-result-hidden");
  qpCurrent.textContent = String(qpQuestions.length);
  qpProgressBar.dataset.progress = "100%";
}

qpStartBtn.addEventListener("click", () => {
  qpIndex = 0;
  qpScores = { reaction: 0, filter: 0, control: 0 };
  qpResult.classList.add("qp-result-hidden");
  qpSetProgress();
  qpRenderQuestion();
});

qpSetProgress();
