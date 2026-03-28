const qpQuestions = [
  {
    question: "You receive an urgent message while focused.",
    options: [
      { key: "A", text: "I reply immediately", trait: "reaction" },
      { key: "B", text: "I pause, but feel pulled to respond", trait: "filter" },
      { key: "C", text: "I finish what I’m doing, then decide", trait: "control" }
    ]
  },
  {
    question: "Your day gets disrupted unexpectedly.",
    options: [
      { key: "A", text: "I react and adjust on the fly", trait: "reaction" },
      { key: "B", text: "I try to reorganize quickly", trait: "filter" },
      { key: "C", text: "I step back and reset priorities", trait: "control" }
    ]
  },
  {
    question: "Someone challenges your opinion.",
    options: [
      { key: "A", text: "I respond instantly", trait: "reaction" },
      { key: "B", text: "I defend but try to stay calm", trait: "filter" },
      { key: "C", text: "I pause and choose if it’s worth engaging", trait: "control" }
    ]
  },
  {
    question: "You have too many things to do.",
    options: [
      { key: "A", text: "I jump between tasks", trait: "reaction" },
      { key: "B", text: "I try to organize but get distracted", trait: "filter" },
      { key: "C", text: "I choose what matters and ignore the rest", trait: "control" }
    ]
  },
  {
    question: "You feel pressure to decide fast.",
    options: [
      { key: "A", text: "I decide quickly to move on", trait: "reaction" },
      { key: "B", text: "I hesitate but still rush", trait: "filter" },
      { key: "C", text: "I slow down and think clearly", trait: "control" }
    ]
  },
  {
    question: "You consume information (news, social, etc.)",
    options: [
      { key: "A", text: "I check frequently", trait: "reaction" },
      { key: "B", text: "I try to limit but still consume", trait: "filter" },
      { key: "C", text: "I filter aggressively and ignore most", trait: "control" }
    ]
  },
  {
    question: "You want to improve your life.",
    options: [
      { key: "A", text: "I try new things often", trait: "reaction" },
      { key: "B", text: "I follow ideas but inconsistently", trait: "filter" },
      { key: "C", text: "I build systems and stick to them", trait: "control" }
    ]
  }
];

const profiles = {
  reaction: {
    name: "Reactive Mode",
    description:
      "You operate in reaction mode.\n\nFast responses.\nLow filtering.\nConstant adjustment.\n\nYou are active — but not always in control.",
    nextStep:
      "Next step: Start with awareness. Then reduce unnecessary reactions.",
    ctaLabel: "Buy Workbook 1",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
  },
  filter: {
    name: "Aware but Unstable",
    description:
      "You are starting to filter the noise.\n\nBut consistency is not yet stable.\n\nYou see what matters.\nYou just don’t always act on it.",
    nextStep:
      "Next step: Strengthen your decisions. Reduce hesitation.",
    ctaLabel: "Buy Workbook 2",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-2-filter-quiet-power-system"
  },
  control: {
    name: "Quiet Operator",
    description:
      "You operate with control.\n\nYou choose before reacting.\nYou filter what matters.\nYou move with intention.\n\nYou are building Quiet Power.",
    nextStep:
      "Next step: Maintain consistency. Build long-term systems.",
    ctaLabel: "Buy Workbook 3",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-3-control-quiet-power-system"
  },
  reactionFilter: {
    name: "Between Reaction and Filter",
    description:
      "You notice more than a fully reactive person, but your responses are still inconsistent.\n\nYou are not fully lost in noise.\nYou are also not reliably in control yet.",
    nextStep:
      "Next step: Build awareness first, then practise filtering what gets your energy.",
    ctaLabel: "Buy Workbook 1",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
  },
  filterControl: {
    name: "Between Filter and Control",
    description:
      "You already filter better than most people.\n\nThe next step is steadiness.\nYou do many things with intention, but your control is not fully consistent yet.",
    nextStep:
      "Next step: Turn selective awareness into durable control.",
    ctaLabel: "Buy Workbook 2",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-2-filter-quiet-power-system"
  },
  reactionControl: {
    name: "Split Between Reaction and Control",
    description:
      "You show moments of strong control, but they alternate with reactive patterns.\n\nThat usually means your system is not stable yet.",
    nextStep:
      "Next step: Reduce volatility so control becomes your default, not your best day.",
    ctaLabel: "Buy Workbook 1",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
  },
  balanced: {
    name: "Balanced but Undefined",
    description:
      "Your answers are spread evenly across reaction, filtering, and control.\n\nThat suggests flexibility, but also a pattern that is not stable enough to read as one clear operating mode.",
    nextStep:
      "Next step: Start with awareness and identify which pattern shows up most often in real life.",
    ctaLabel: "Buy Workbook 1",
    ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
  }
};

let currentIndex = 0;
let scores = {
  reaction: 0,
  filter: 0,
  control: 0
};

const introScreen = document.getElementById("qp-intro-screen");
const startBtn = document.querySelector(".qp-start-btn");
const testArea = document.getElementById("qp-test-area");
const questionContainer = document.getElementById("qp-question-container");
const resultSection = document.getElementById("qp-result");
const resultTitle = document.getElementById("qp-result-title");
const resultText = document.getElementById("qp-result-text");
const resultNext = document.getElementById("qp-result-next");
const reactionScore = document.getElementById("qp-reaction-score");
const filterScore = document.getElementById("qp-filter-score");
const controlScore = document.getElementById("qp-control-score");
const resultCta = document.getElementById("qp-result-cta");
const restartBtn = document.getElementById("qp-restart-btn");
const shareText = document.getElementById("qp-share-text");
const shareX = document.getElementById("qp-share-x");
const shareLinkedIn = document.getElementById("qp-share-linkedin");
const shareWhatsApp = document.getElementById("qp-share-whatsapp");
const shareCopy = document.getElementById("qp-share-copy");

function buildShareState(profile) {
  const url = "https://sabinopereira.com/test.html";
  const text = `I got "${profile.name}" on the Quiet Power Assessment. Take the test: ${url}`;
  return {
    text,
    x: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
    whatsapp: `https://wa.me/?text=${encodeURIComponent(text)}`
  };
}

function updateShareLinks(profile) {
  const shareState = buildShareState(profile);

  if (shareText) {
    shareText.textContent = `I got "${profile.name}" on the Quiet Power Assessment. Share it or invite someone else to take the test.`;
  }

  if (shareX) {
    shareX.href = shareState.x;
  }

  if (shareLinkedIn) {
    shareLinkedIn.href = shareState.linkedin;
  }

  if (shareWhatsApp) {
    shareWhatsApp.href = shareState.whatsapp;
  }

  if (shareCopy) {
    shareCopy.dataset.copyText = shareState.text;
    shareCopy.textContent = "Copy link";
  }
}

function resetAssessment() {
  currentIndex = 0;
  scores = { reaction: 0, filter: 0, control: 0 };
  resultSection.classList.add("qp-result-hidden");
  introScreen.classList.add("qp-intro-hidden");
  testArea.classList.remove("qp-test-hidden");
  renderQuestion();
}

function renderQuestion() {
  const currentQuestion = qpQuestions[currentIndex];

  if (!currentQuestion) {
    showResults();
    return;
  }

  const progressValue = ((currentIndex + 1) / qpQuestions.length) * 100;

  questionContainer.innerHTML = `
    <div class="test-wrap fade">
      <div class="progress">
        <div class="progress-bar" style="width: ${progressValue}%"></div>
      </div>
      <p class="step">Question ${currentIndex + 1} of ${qpQuestions.length}</p>
      <h2 class="question">${currentQuestion.question}</h2>
      <div class="answers">
        ${currentQuestion.options
          .map(
            (option, index) => `
              <button type="button" class="answer" data-trait="${option.trait}">
                <span class="answer-key">${String.fromCharCode(65 + index)}</span>
                <span class="answer-copy">${option.text}</span>
              </button>
            `
          )
          .join("")}
      </div>
    </div>
  `;

  document.querySelectorAll(".answer").forEach((button) => {
    button.addEventListener("click", () => handleAnswer(button));
  });
}

function handleAnswer(button) {
  const trait = button.dataset.trait;
  scores[trait] += 1;

  document.querySelectorAll(".answer").forEach((option) => {
    option.disabled = true;
    option.classList.remove("selected");
  });
  button.classList.add("selected");

  window.setTimeout(() => {
    currentIndex += 1;
    renderQuestion();
  }, 550);
}

function getProfile() {
  const ranking = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  const topScore = ranking[0][1];
  const leaders = ranking.filter(([, score]) => score === topScore).map(([trait]) => trait);

  if (leaders.length === 1) {
    return profiles[leaders[0]];
  }

  if (leaders.length === 3) {
    return profiles.balanced;
  }

  const tieKey = [...leaders].sort().join("-");
  const tieMap = {
    "control-filter": profiles.filterControl,
    "control-reaction": profiles.reactionControl,
    "filter-reaction": profiles.reactionFilter
  };

  if (tieMap[tieKey]) {
    return tieMap[tieKey];
  }

  return profiles.balanced;
}

function showResults() {
  const profile = getProfile();

  testArea.classList.add("qp-test-hidden");
  resultSection.classList.remove("qp-result-hidden");

  resultTitle.textContent = profile.name;
  resultText.innerHTML = profile.description.replace(/\n/g, "<br>");
  resultNext.textContent = profile.nextStep;
  reactionScore.textContent = String(scores.reaction);
  filterScore.textContent = String(scores.filter);
  controlScore.textContent = String(scores.control);

  if (resultCta) {
    resultCta.textContent = profile.ctaLabel;
    resultCta.href = profile.ctaHref;
  }

  updateShareLinks(profile);
}

if (startBtn) {
  startBtn.addEventListener("click", resetAssessment);
}

if (restartBtn) {
  restartBtn.addEventListener("click", resetAssessment);
}

if (shareCopy) {
  shareCopy.addEventListener("click", async () => {
    const text = shareCopy.dataset.copyText || "https://sabinopereira.com/test.html";

    try {
      await navigator.clipboard.writeText(text);
      shareCopy.textContent = "Copied";
      window.setTimeout(() => {
        shareCopy.textContent = "Copy link";
      }, 1400);
    } catch (error) {
      shareCopy.textContent = "Copy failed";
      window.setTimeout(() => {
        shareCopy.textContent = "Copy link";
      }, 1400);
    }
  });
}
