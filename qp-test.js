const qpQuestionSets = {
  en: [
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
  ],
  pt: [
    {
      question: "Recebes uma mensagem urgente enquanto estás concentrado.",
      options: [
        { key: "A", text: "Respondo imediatamente", trait: "reaction" },
        { key: "B", text: "Faço uma pausa, mas sinto vontade de responder", trait: "filter" },
        { key: "C", text: "Termino o que estou a fazer e depois decido", trait: "control" }
      ]
    },
    {
      question: "O teu dia é interrompido de forma inesperada.",
      options: [
        { key: "A", text: "Reajo e ajusto-me no momento", trait: "reaction" },
        { key: "B", text: "Tento reorganizar-me rapidamente", trait: "filter" },
        { key: "C", text: "Paro e volto a definir prioridades", trait: "control" }
      ]
    },
    {
      question: "Alguém desafia a tua opinião.",
      options: [
        { key: "A", text: "Respondo logo", trait: "reaction" },
        { key: "B", text: "Defendo-me, mas tento manter a calma", trait: "filter" },
        { key: "C", text: "Faço uma pausa e escolho se vale a pena entrar na conversa", trait: "control" }
      ]
    },
    {
      question: "Tens demasiadas coisas para fazer.",
      options: [
        { key: "A", text: "Salto entre tarefas", trait: "reaction" },
        { key: "B", text: "Tento organizar-me, mas distraio-me", trait: "filter" },
        { key: "C", text: "Escolho o que importa e ignoro o resto", trait: "control" }
      ]
    },
    {
      question: "Sentes pressão para decidir depressa.",
      options: [
        { key: "A", text: "Decido rapidamente para avançar", trait: "reaction" },
        { key: "B", text: "Hesito, mas acabo por acelerar", trait: "filter" },
        { key: "C", text: "Abrando e penso com clareza", trait: "control" }
      ]
    },
    {
      question: "Consomes informação, notícias ou redes sociais.",
      options: [
        { key: "A", text: "Vejo frequentemente", trait: "reaction" },
        { key: "B", text: "Tento limitar, mas continuo a consumir", trait: "filter" },
        { key: "C", text: "Filtro com força e ignoro a maior parte", trait: "control" }
      ]
    },
    {
      question: "Queres melhorar a tua vida.",
      options: [
        { key: "A", text: "Experimento coisas novas com frequência", trait: "reaction" },
        { key: "B", text: "Sigo ideias, mas sem consistência", trait: "filter" },
        { key: "C", text: "Crio sistemas e mantenho-os", trait: "control" }
      ]
    }
  ]
};

const profileSets = {
  en: {
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
  },
  pt: {
    reaction: {
      name: "Modo Reativo",
      description:
        "Operas em modo reativo.\n\nRespostas rápidas.\nPouco filtro.\nAjuste constante.\n\nEstás ativo — mas nem sempre em controlo.",
      nextStep:
        "Próximo passo: começa pela consciência. Depois reduz reações desnecessárias.",
      ctaLabel: "Ver Workbook 1",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
    },
    filter: {
      name: "Consciente, mas Instável",
      description:
        "Já estás a começar a filtrar o ruído.\n\nMas a consistência ainda não está estável.\n\nVês o que importa.\nSó nem sempre ages de acordo com isso.",
      nextStep:
        "Próximo passo: fortalece as decisões. Reduz a hesitação.",
      ctaLabel: "Ver Workbook 2",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-2-filter-quiet-power-system"
    },
    control: {
      name: "Operador Calmo",
      description:
        "Operas com controlo.\n\nEscolhes antes de reagir.\nFiltras o que importa.\nMoves-te com intenção.\n\nEstás a construir Quiet Power.",
      nextStep:
        "Próximo passo: manter consistência e construir sistemas de longo prazo.",
      ctaLabel: "Ver Workbook 3",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-3-control-quiet-power-system"
    },
    reactionFilter: {
      name: "Entre Reação e Filtro",
      description:
        "Notas mais do que uma pessoa totalmente reativa, mas as tuas respostas ainda são inconsistentes.\n\nNão estás completamente perdido no ruído.\nMas também ainda não estás sempre em controlo.",
      nextStep:
        "Próximo passo: constrói consciência primeiro, depois pratica filtrar o que merece energia.",
      ctaLabel: "Ver Workbook 1",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
    },
    filterControl: {
      name: "Entre Filtro e Controlo",
      description:
        "Já filtras melhor do que a maioria das pessoas.\n\nO próximo passo é estabilidade.\nFazes muitas coisas com intenção, mas o controlo ainda não é totalmente consistente.",
      nextStep:
        "Próximo passo: transformar consciência seletiva em controlo durável.",
      ctaLabel: "Ver Workbook 2",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-2-filter-quiet-power-system"
    },
    reactionControl: {
      name: "Dividido entre Reação e Controlo",
      description:
        "Mostras momentos de forte controlo, mas eles alternam com padrões reativos.\n\nNormalmente isso significa que o teu sistema ainda não está estável.",
      nextStep:
        "Próximo passo: reduzir volatilidade para o controlo ser o teu padrão, não só o teu melhor dia.",
      ctaLabel: "Ver Workbook 1",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
    },
    balanced: {
      name: "Equilibrado, mas Indefinido",
      description:
        "As tuas respostas espalham-se entre reação, filtro e controlo.\n\nIsto sugere flexibilidade, mas também um padrão que ainda não é estável o suficiente para ser lido como modo dominante.",
      nextStep:
        "Próximo passo: começa pela consciência e identifica que padrão aparece mais vezes na vida real.",
      ctaLabel: "Ver Workbook 1",
      ctaHref: "https://quiet-power-shop.fourthwall.com/products/workbook-1-reaction-quiet-power-system"
    }
  }
};

function initQuietPowerAssessment() {
  const isPortuguese = document.documentElement.lang.toLowerCase().startsWith("pt");
  const lang = isPortuguese ? "pt" : "en";
  const qpQuestions = qpQuestionSets[lang];
  const profiles = profileSets[lang];
  const copy = {
    en: {
      shareUrl: "https://sabinopereira.com/quiet-power-assessment.html",
      shareIntro: (profile) => `I got "${profile.name}" on the Quiet Power Assessment`,
      shareText: (profile) =>
        `I got "${profile.name}" on the Quiet Power Assessment. Take the test: https://sabinopereira.com/quiet-power-assessment.html`,
      sharePrompt: (profile) =>
        `I got "${profile.name}" on the Quiet Power Assessment. Share it or invite someone else to take the test.`,
      questionStep: (current, total) => `Question ${current} of ${total}`,
      copyLink: "Copy link",
      copied: "Copied",
      copyFailed: "Copy failed"
    },
    pt: {
      shareUrl: "https://sabinopereira.com/pt/teste.html",
      shareIntro: (profile) => `Obtive "${profile.name}" no teste Quiet Power`,
      shareText: (profile) =>
        `Obtive "${profile.name}" no teste Quiet Power. Faz o teste: https://sabinopereira.com/pt/teste.html`,
      sharePrompt: (profile) =>
        `Obtive "${profile.name}" no teste Quiet Power. Partilha o teu resultado ou convida alguém a fazer o teste.`,
      questionStep: (current, total) => `Pergunta ${current} de ${total}`,
      copyLink: "Copiar link",
      copied: "Copiado",
      copyFailed: "Falhou"
    }
  }[lang];

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
  const bookCta = document.getElementById("qp-book-cta");
  const bundleCta = document.getElementById("qp-bundle-cta");

  if (!startBtn || !introScreen || !testArea || !questionContainer || !resultSection) {
    return;
  }

  function trackEvent(name, params = {}) {
    if (typeof window.trackEvent === "function") {
      window.trackEvent(name, params);
    }
  }

  function buildShareState(profile) {
    const url = copy.shareUrl;
    const text = copy.shareText(profile);
    const links = window.ShareUtils
      ? window.ShareUtils.buildShareLinks(copy.shareIntro(profile), url)
      : null;

    return {
      text,
      x: links ? links.x : `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
      linkedin: links ? links.linkedin : `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
      whatsapp: links ? links.whatsapp : `https://wa.me/?text=${encodeURIComponent(text)}`
    };
  }

  function updateShareLinks(profile) {
    const shareState = buildShareState(profile);

    if (shareText) {
      shareText.textContent = copy.sharePrompt(profile);
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
      shareCopy.textContent = copy.copyLink;
    }
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
        <p class="step">${copy.questionStep(currentIndex + 1, qpQuestions.length)}</p>
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
  }

  function resetAssessment() {
    currentIndex = 0;
    scores = { reaction: 0, filter: 0, control: 0 };
    questionContainer.innerHTML = "";
    resultSection.classList.add("qp-result-hidden");
    introScreen.classList.add("qp-intro-hidden");
    testArea.classList.remove("qp-test-hidden");
    testArea.hidden = false;
    trackEvent("test_start", {
      page_path: window.location.pathname
    });
    renderQuestion();
  }

  function handleAnswer(button) {
    const trait = button.dataset.trait;

    if (!trait || !(trait in scores)) {
      return;
    }

    scores[trait] += 1;
    trackEvent("test_answer", {
      question_number: currentIndex + 1,
      selected_trait: trait
    });

    questionContainer.querySelectorAll(".answer").forEach((option) => {
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

    if (resultTitle) {
      resultTitle.textContent = profile.name;
    }

    if (resultText) {
      resultText.innerHTML = profile.description.replace(/\n/g, "<br>");
    }

    if (resultNext) {
      resultNext.textContent = profile.nextStep;
    }

    if (reactionScore) {
      reactionScore.textContent = String(scores.reaction);
    }

    if (filterScore) {
      filterScore.textContent = String(scores.filter);
    }

    if (controlScore) {
      controlScore.textContent = String(scores.control);
    }

    if (resultCta) {
      resultCta.textContent = profile.ctaLabel;
      resultCta.href = profile.ctaHref;
    }

    updateShareLinks(profile);
    trackEvent("test_complete", {
      profile: profile.name,
      reaction_score: scores.reaction,
      filter_score: scores.filter,
      control_score: scores.control
    });
  }

  startBtn.addEventListener("click", resetAssessment);

  questionContainer.addEventListener("click", (event) => {
    const button = event.target.closest(".answer");

    if (!button || button.disabled) {
      return;
    }

    handleAnswer(button);
  });

  if (restartBtn) {
    restartBtn.addEventListener("click", () => {
      trackEvent("test_restart", {
        page_path: window.location.pathname
      });
      resetAssessment();
    });
  }

  if (bookCta) {
    bookCta.addEventListener("click", () => {
      trackEvent("test_result_cta_click", {
        cta_type: "book",
        destination: bookCta.href
      });
    });
  }

  if (resultCta) {
    resultCta.addEventListener("click", () => {
      trackEvent("test_result_cta_click", {
        cta_type: "workbook",
        destination: resultCta.href,
        cta_label: resultCta.textContent.trim()
      });
    });
  }

  if (bundleCta) {
    bundleCta.addEventListener("click", () => {
      trackEvent("test_result_cta_click", {
        cta_type: "bundle",
        destination: bundleCta.href
      });
    });
  }

  if (shareX) {
    shareX.addEventListener("click", () => {
      trackEvent("test_share_click", { platform: "x" });
    });
  }

  if (shareLinkedIn) {
    shareLinkedIn.addEventListener("click", () => {
      trackEvent("test_share_click", { platform: "linkedin" });
    });
  }

  if (shareWhatsApp) {
    shareWhatsApp.addEventListener("click", () => {
      trackEvent("test_share_click", { platform: "whatsapp" });
    });
  }

  if (shareCopy) {
    if (window.ShareUtils) {
      window.ShareUtils.wireShareControls(resultSection, buildShareState(profiles.reaction));
      shareCopy.addEventListener("click", () => {
        trackEvent("test_share_click", { platform: "copy_link" });
      });
    } else {
      shareCopy.addEventListener("click", async () => {
        trackEvent("test_share_click", { platform: "copy_link" });
        const text = shareCopy.dataset.copyText || copy.shareUrl;

        try {
          await navigator.clipboard.writeText(text);
          shareCopy.textContent = copy.copied;
          window.setTimeout(() => {
            shareCopy.textContent = copy.copyLink;
          }, 1400);
        } catch (error) {
          shareCopy.textContent = copy.copyFailed;
          window.setTimeout(() => {
            shareCopy.textContent = copy.copyLink;
          }, 1400);
        }
      });
    }
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initQuietPowerAssessment);
} else {
  initQuietPowerAssessment();
}
