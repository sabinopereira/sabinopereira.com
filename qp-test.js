const qpQuestions = [
  {
    question: "You receive an urgent message while focused.",
    options: [
      { key: "A", text: "I reply immediately", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I pause, but feel pulled to respond", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I finish what I’m doing, then decide", trait: "control", feedback: "Controlled response" }
    ]
  },
  {
    question: "Your day gets disrupted unexpectedly.",
    options: [
      { key: "A", text: "I react and adjust on the fly", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I try to reorganize quickly", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I step back and reset priorities", trait: "control", feedback: "Controlled response" }
    ]
  },
  {
    question: "Someone challenges your opinion.",
    options: [
      { key: "A", text: "I respond instantly", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I defend but try to stay calm", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I pause and choose if it’s worth engaging", trait: "control", feedback: "Controlled response" }
    ]
  },
  {
    question: "You have too many things to do.",
    options: [
      { key: "A", text: "I jump between tasks", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I try to organize but get distracted", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I choose what matters and ignore the rest", trait: "control", feedback: "Controlled response" }
    ]
  },
  {
    question: "You feel pressure to decide fast.",
    options: [
      { key: "A", text: "I decide quickly to move on", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I hesitate but still rush", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I slow down and think clearly", trait: "control", feedback: "Controlled response" }
    ]
  },
  {
    question: "You consume information (news, social, etc.)",
    options: [
      { key: "A", text: "I check frequently", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I try to limit but still consume", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I filter aggressively and ignore most", trait: "control", feedback: "Controlled response" }
    ]
  },
  {
    question: "You want to improve your life.",
    options: [
      { key: "A", text: "I try new things often", trait: "reaction", feedback: "Fast reaction" },
      { key: "B", text: "I follow ideas but inconsistently", trait: "filter", feedback: "Partial control" },
      { key: "C", text: "I build systems and stick to them", trait: "control", feedback: "Controlled response" }
    ]
  }
];

const profiles = {
  reaction: {
    name: "Reactive Mode",
    description:
      "You operate in reaction mode.\n\nFast responses.\nLow filtering.\nConstant adjustment.\n\nYou are active — but not always in control.",
    nextStep:
      "Next step: Start with awareness. Then reduce unnecessary reactions."
  },
  filter: {
    name: "Aware but Unstable",
    description:
      "You are starting to filter the noise.\n\nBut consistency is not yet stable.\n\nYou see what matters.\nYou just don’t always act on it.",
    nextStep:
      "Next step: Strengthen your decisions. Reduce hesitation."
  },
  control: {
    name: "Quiet Operator",
    description:
      "You operate with control.\n\nYou choose before reacting.\nYou filter what matters.\nYou move with intention.\n\nYou are building Quiet Power.",
    nextStep:
      "Next step: Maintain consistency. Build long-term systems."
  }
};

let currentIndex = 0;
let scores = {
  reaction: 0,
  filter: 0,
  control: 0
};

const introScreen = document.getElementById("qp-intro-screen");
const progressWrap = document.getElementById("qp-progress");
const progressBar = document.getElementById("qp-progress-bar");
const currentLabel = document.getElementById("qp-current");
const totalLabel = document.getElementById("qp-total");
const startBtn = document.querySelector(".qp-start-btn");
const testArea = document.getElementById("qp-test-area");
const questionContainer = document.getElementById("qp-question-container");
const answerFeedback = document.getElementById("qp-answer-feedback");
const resultSection = document.getElementById("qp-result");
const resultTitle = document.getElementById("qp-result-title");
const resultText = document.getElementById("qp-result-text");
const resultNext = document.getElementById("qp-result-next");
const reactionScore = document.getElementById("qp-reaction-score");
const filterScore = document.getElementById("qp-filter-score");
const controlScore = document.getElementById("qp-control-score");

if (totalLabel) {
  totalLabel.textContent = String(qpQuestions.length);
}

function resetAssessment() {
  currentIndex = 0;
  scores = { reaction: 0, filter: 0, control: 0 };
  resultSection.classList.add("qp-result-hidden");
  introScreen.classList.add("qp-intro-hidden");
  progressWrap.classList.remove("qp-progress-hidden");
  testArea.classList.remove("qp-test-hidden");
  updateProgress();
  renderQuestion();
}

function updateProgress() {
  if (currentLabel) {
    currentLabel.textContent = String(currentIndex + 1);
  }

  if (progressBar) {
    const value = (currentIndex / qpQuestions.length) * 100;
    progressBar.style.setProperty("--qp-progress-value", `${value}%`);
  }
}

function renderQuestion() {
  const currentQuestion = qpQuestions[currentIndex];

  if (!currentQuestion) {
    showResults();
    return;
  }

  updateProgress();
  answerFeedback.classList.add("qp-answer-feedback-hidden");
  answerFeedback.textContent = "";

  questionContainer.innerHTML = `
    <div class="qp-question-card">
      <p class="qp-question-label">Question ${currentIndex + 1} of ${qpQuestions.length}</p>
      <h2 class="qp-question-text">${currentQuestion.question}</h2>
      <div class="qp-options">
        ${currentQuestion.options
          .map(
            (option) => `
              <button type="button" class="qp-option-btn" data-trait="${option.trait}" data-feedback="${option.feedback}">
                <span class="qp-option-key">${option.key}</span>
                <span class="qp-option-copy">${option.text}</span>
              </button>
            `
          )
          .join("")}
      </div>
    </div>
  `;

  document.querySelectorAll(".qp-option-btn").forEach((button) => {
    button.addEventListener("click", () => handleAnswer(button));
  });
}

function handleAnswer(button) {
  const trait = button.dataset.trait;
  const feedback = button.dataset.feedback;
  scores[trait] += 1;

  answerFeedback.textContent = feedback;
  answerFeedback.classList.remove("qp-answer-feedback-hidden");

  document.querySelectorAll(".qp-option-btn").forEach((option) => {
    option.disabled = true;
    option.classList.remove("is-selected");
  });
  button.classList.add("is-selected");

  window.setTimeout(() => {
    currentIndex += 1;
    renderQuestion();
  }, 550);
}

function getProfile() {
  if (scores.control >= scores.filter && scores.control >= scores.reaction) {
    return profiles.control;
  }

  if (scores.filter >= scores.reaction && scores.filter >= scores.control) {
    return profiles.filter;
  }

  return profiles.reaction;
}

function showResults() {
  const profile = getProfile();

  progressBar.style.setProperty("--qp-progress-value", "100%");
  progressWrap.classList.add("qp-progress-hidden");
  testArea.classList.add("qp-test-hidden");
  resultSection.classList.remove("qp-result-hidden");

  resultTitle.textContent = profile.name;
  resultText.innerHTML = profile.description.replace(/\n/g, "<br>");
  resultNext.textContent = profile.nextStep;
  reactionScore.textContent = String(scores.reaction);
  filterScore.textContent = String(scores.filter);
  controlScore.textContent = String(scores.control);
}

if (startBtn) {
  startBtn.addEventListener("click", resetAssessment);
}
