const $ = (id) => document.getElementById(id);

const viewLogin = $("viewLogin");
const viewRegister = $("viewRegister");
const viewMenu = $("viewMenu");
const viewInteraction = $("viewInteraction");
const viewAprendizaje = $("viewAprendizaje");
const viewEvaluacionConfig = $("viewEvaluacionConfig");
const viewEvaluacionRun = $("viewEvaluacionRun");

// Evaluation elements
const evalRequestedLetter = $("evalRequestedLetter");
const evalDetectedLetter = $("evalDetectedLetter");
const evalTime = $("evalTime");
const evalScore = $("evalScore");
const videoEvaluacion = $("videoEvaluacion");
const videoFallbackEvaluacion = $("videoFallbackEvaluacion");
const evalVideoWrap = $("evalVideoWrap");
const evalOverlay = $("evalOverlay");
const viewReto = $("viewReto");

const loginError = $("loginError");
const regError = $("regError");
const voiceError = $("voiceError");

const chat = $("chat");
const videoInteraction = $("videoInteraction");
const videoFallbackInteraction = $("videoFallbackInteraction");
const videoAprendizaje = $("videoAprendizaje");
const videoFallbackAprendizaje = $("videoFallbackAprendizaje");
const letterPill = $("letterPill");
const signText = $("signText");
const learningProgress = $("learningProgress");
const learningLetter = $("learningLetter");
const learningReferenceArt = $("learningReferenceArt");
const learningReferenceImage = $("learningReferenceImage");
const learningVideoWrap = $("learningVideoWrap");
const learningOverlay = $("learningOverlay");
const learningDetected = $("learningDetected");
const learningStatusPill = $("learningStatusPill");
const learningCaption = $("learningCaption");
const learningCounter = $("learningCounter");
const btnStarLetter = $("btnStarLetter");
const starIcon = $("starIcon");
const learningDifficultCount = $("learningDifficultCount");
const learningAssistantCard = $("learningAssistantCard");
const learningAssistantMessage = $("learningAssistantMessage");
const learningAssistantLetter = $("learningAssistantLetter");
const learningAssistantCorrect = $("learningAssistantCorrect");
const learningAssistantAccuracy = $("learningAssistantAccuracy");
const learningAssistantAttempts = $("learningAssistantAttempts");
const learningAssistantRecommendation = $("learningAssistantRecommendation");
const btnAssistantFavorite = $("btnAssistantFavorite");
const btnPracticeNow = $("btnPracticeNow");
const btnLogout = $("btnLogout");

// Repaso (letras marcadas con estrella)
const viewRepaso = $("viewRepaso");
const repasoEmptyState = $("repasoEmptyState");
const repasoPracticeWrap = $("repasoPracticeWrap");
const repasoProgress = $("repasoProgress");
const repasoReferenceArt = $("repasoReferenceArt");
const repasoReferenceImage = $("repasoReferenceImage");
const repasoLetter = $("repasoLetter");
const repasoDetected = $("repasoDetected");
const repasoStatusPill = $("repasoStatusPill");
const repasoCaption = $("repasoCaption");
const repasoVideoWrap = $("repasoVideoWrap");
const repasoOverlay = $("repasoOverlay");
const videoRepaso = $("videoRepaso");
const videoFallbackRepaso = $("videoFallbackRepaso");
const btnUnstarRepaso = $("btnUnstarRepaso");
// Asistente IA de Repaso
const repasoAssistantCard = $("repasoAssistantCard");
const repasoAssistantTitle = $("repasoAssistantTitle");
const repasoAssistantMessage = $("repasoAssistantMessage");
const repasoAssistantTip = $("repasoAssistantTip");

// Reto (deletrea tu nombre)
const videoReto = $("videoReto");
const videoFallbackReto = $("videoFallbackReto");
const retoWord = $("retoWord");
const retoGrid = $("retoGrid");
const retoLetter = $("retoLetter");
const retoReferenceArt = $("retoReferenceArt");
const retoReferenceImage = $("retoReferenceImage");
const retoCaption = $("retoCaption");
const retoSubtitle = $("retoSubtitle");
const retoProgressFill = $("retoProgressFill");
const retoEmpty = $("retoEmpty");
const retoComplete = $("retoComplete");

const LETTERS = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","Ñ","O","P","Q","R","S","T","U","V","W","X","Y","Z"];

// --- Favoritos del usuario autenticado ---
let favoriteLetters = new Set();
let favoriteUsername = null;

function updateDifficultCount(){
  if(learningDifficultCount){
    learningDifficultCount.textContent = `Letras favoritas: ${favoriteLetters.size}`;
  }
}

function updateStarButton(letter){
  const isStarred = favoriteLetters.has(letter);
  if(btnStarLetter){
    btnStarLetter.classList.toggle("starred", isStarred);
    btnStarLetter.setAttribute("aria-pressed", isStarred ? "true" : "false");
    btnStarLetter.title = isStarred ? "Quitar de favoritos" : "Guardar en favoritos";
    btnStarLetter.setAttribute("aria-label", isStarred ? "Quitar letra de favoritos" : "Guardar letra en favoritos");
  }
  if(starIcon){
    starIcon.textContent = isStarred ? "★" : "☆";
  }
}

function updateAssistantFavoriteButton(letter){
  if(!btnAssistantFavorite) return;
  const isFavorite = favoriteLetters.has(letter);
  btnAssistantFavorite.textContent = isFavorite ? "★ Quitar de favoritos" : "⭐ Guardar en favoritos";
  btnAssistantFavorite.setAttribute("aria-pressed", isFavorite ? "true" : "false");
}

async function refreshFavoriteLetters(){
  try{
    const result = await window.pywebview.api.get_favorite_letters();
    if(!result || !result.ok) return;
    favoriteLetters = new Set(result.letters || []);
    updateDifficultCount();
    updateStarButton(learningTargetLetter);
    updateAssistantFavoriteButton(learningTargetLetter);
    if(currentView() === "repaso") syncRepasoView();
  }catch(e){
    // Conserva los favoritos ya cargados si la consulta falla.
  }
}

async function toggleFavoriteLetter(letter){
  if(!letter) return;
  const target = letter.toUpperCase();
  const isFavorite = !favoriteLetters.has(target);
  try{
    const result = await window.pywebview.api.set_favorite_letter(target, isFavorite);
    if(!result || !result.ok) return;
    favoriteLetters = new Set(result.letters || []);
    updateDifficultCount();
    updateStarButton(target);
    updateAssistantFavoriteButton(target);
    if(currentView() === "repaso") syncRepasoView();
  }catch(e){
    // No cambia la UI si el guardado no fue confirmado por el backend.
  }
}

// --- Vista de Repaso (practica solo las letras marcadas con estrella) ---
let repasoList = [];
let repasoIndex = 0;
let repasoInitialLetter = null;
let repasoTargetLetter = null;
let repasoSameStreak = 0;
let repasoLastDetected = null;
let repasoIsCorrect = false;
let repasoAttemptLogged = false;
let repasoAwaitingNewAttempt = false;
let repasoResetTimer = null;
const REPASO_STREAK_TO_CONFIRM = 3;

function buildRepasoList(){
  repasoList = Array.from(favoriteLetters).sort();
  if(repasoIndex >= repasoList.length){
    repasoIndex = 0;
  }
}

function resetRepasoFeedback(){
  if(repasoResetTimer){
    clearTimeout(repasoResetTimer);
    repasoResetTimer = null;
  }
  repasoIsCorrect = false;
  repasoAttemptLogged = false;
  repasoAwaitingNewAttempt = false;
  repasoSameStreak = 0;
  repasoLastDetected = null;
  if(repasoVideoWrap){
    repasoVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  }
  if(repasoOverlay){
    repasoOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    repasoOverlay.textContent = "";
  }
  if(repasoStatusPill){
    repasoStatusPill.className = "learning-status-pill";
    repasoStatusPill.textContent = "Esperando seña…";
  }
  if(repasoCaption){
    repasoCaption.textContent = "Repite la seña";
  }
  if(repasoDetected){
    repasoDetected.textContent = "-";
  }
  if(repasoAssistantCard){
    repasoAssistantCard.classList.add("hidden");
  }
}

function syncRepasoView(){
  buildRepasoList();

  if(repasoList.length === 0){
    if(repasoEmptyState) repasoEmptyState.classList.remove("hidden");
    if(repasoPracticeWrap) repasoPracticeWrap.classList.add("hidden");
    return;
  }

  if(repasoEmptyState) repasoEmptyState.classList.add("hidden");
  if(repasoPracticeWrap) repasoPracticeWrap.classList.remove("hidden");

  if(repasoInitialLetter){
    const initialIndex = repasoList.indexOf(repasoInitialLetter);
    if(initialIndex >= 0) repasoIndex = initialIndex;
    repasoInitialLetter = null;
  }

  const letterValue = repasoList[repasoIndex];
  repasoTargetLetter = letterValue;

  if(repasoLetter) repasoLetter.textContent = letterValue;
  if(repasoProgress) repasoProgress.textContent = `${letterValue} — ${repasoIndex + 1}/${repasoList.length}`;

  if(repasoReferenceImage && repasoReferenceArt){
    const placeholder = repasoReferenceArt.querySelector(".reference-placeholder-text");
    const imageName = letterValue.toLowerCase();
    repasoReferenceImage.src = `./assets/letras/${imageName}.png`;
    repasoReferenceImage.alt = `Seña de la letra ${letterValue}`;
    repasoReferenceImage.style.display = "block";
    if(placeholder) placeholder.style.display = "none";
  }

  resetRepasoFeedback();
}

function moveRepaso(step){
  if(repasoList.length === 0) return;
  repasoIndex = (repasoIndex + step + repasoList.length) % repasoList.length;
  syncRepasoView();
}

async function openRepasoForLetter(letter){
  const target = (letter || "").trim().toUpperCase();
  if(!target) return;
  try{
    const result = await window.pywebview.api.set_favorite_letter(target, true);
    if(!result || !result.ok) return;
    favoriteLetters = new Set(result.letters || []);
    updateDifficultCount();
    repasoInitialLetter = target;
    repasoIndex = 0;
    setView("repaso");
    syncRepasoView();
  }catch(e){
    // No navega si la recomendacion no pudo guardarse para el usuario.
  }
}

function renderRepasoFeedback(feedback){
  if(!feedback || !repasoAssistantCard) return;
  if(repasoAssistantTitle){
    repasoAssistantTitle.textContent = feedback.correct ? "¡Bien hecho! 👋" : "🤖 " + (feedback.title || "Revisa tu seña");
  }
  if(repasoAssistantMessage){
    repasoAssistantMessage.textContent = feedback.message || "";
  }
  if(repasoAssistantTip){
    repasoAssistantTip.textContent = feedback.tip || "";
  }
  repasoAssistantCard.classList.remove("hidden");
}

function showRepasoRetry(attemptNumber, attemptLimit){
  const number = attemptNumber || 1;
  const limit = attemptLimit || 5;
  if(repasoCaption){
    repasoCaption.textContent = `❌ Intento ${number}/${limit}: No coincide. Inténtalo nuevamente.`;
  }
  if(repasoResetTimer) clearTimeout(repasoResetTimer);
  repasoResetTimer = setTimeout(() => {
    if(currentView() !== "repaso" || repasoIsCorrect) return;
    if(repasoVideoWrap){
      repasoVideoWrap.classList.remove("learning-incorrect");
    }
    if(repasoOverlay){
      repasoOverlay.classList.remove("learning-overlay-incorrect");
      repasoOverlay.textContent = "";
    }
    if(repasoStatusPill){
      repasoStatusPill.className = "learning-status-pill";
      repasoStatusPill.textContent = `Intento ${number}/${limit} — Intenta de nuevo`;
    }
  }, 850);
}

function logRepasoAttempt(detectedLetter){
  if(repasoAttemptLogged) return;
  repasoAttemptLogged = true;
  window.pywebview.api.review_attempt(repasoTargetLetter, detectedLetter).then((result) => {
    if(result && result.ok && result.feedback){
      const details = result.feedback.details || [];
      const isComparativeFeedback = details.includes("attempts_analyzed=5");
      // Los primeros cuatro intentos conservan la indicacion corta de la
      // camara. La explicacion de IA se reserva para la comparacion final.
      if(isComparativeFeedback || result.feedback.correct){
        renderRepasoFeedback(result.feedback);
      }
      if(detectedLetter !== repasoTargetLetter){
        repasoAttemptLogged = false;
        repasoAwaitingNewAttempt = true;
        showRepasoRetry(result.review_attempt, result.review_attempt_limit);
      }
    }
  }).catch(() => {
    repasoAttemptLogged = false;
  });
}

function updateRepasoFeedback(detectedLetterRaw){
  const detected = (detectedLetterRaw && String(detectedLetterRaw).trim()) ? String(detectedLetterRaw).trim().toUpperCase() : null;
  if(repasoDetected){
    repasoDetected.textContent = detected || "-";
  }

  if(!detected){
    repasoSameStreak = 0;
    repasoLastDetected = null;
    repasoAwaitingNewAttempt = false;
    return;
  }

  // Tras un error, exigir que el usuario cambie o retire la mano antes de
  // confirmar otro intento. Asi una misma seña sostenida no suma intentos
  // repetidos en cada frame.
  if(repasoAwaitingNewAttempt && detected === repasoLastDetected){
    return;
  }
  if(repasoAwaitingNewAttempt){
    repasoAwaitingNewAttempt = false;
  }

  if(detected === repasoLastDetected){
    repasoSameStreak += 1;
  }else{
    repasoSameStreak = 1;
    repasoLastDetected = detected;
  }

  const isMatch = (detected === repasoTargetLetter);

  if(isMatch && repasoSameStreak >= REPASO_STREAK_TO_CONFIRM){
    if(repasoResetTimer){
      clearTimeout(repasoResetTimer);
      repasoResetTimer = null;
    }
    if(!repasoIsCorrect){
      repasoIsCorrect = true;
      logRepasoAttempt(detected);
    }
    if(repasoVideoWrap){
      repasoVideoWrap.classList.add("learning-correct");
      repasoVideoWrap.classList.remove("learning-incorrect");
    }
    if(repasoOverlay){
      repasoOverlay.classList.add("learning-overlay-correct");
      repasoOverlay.classList.remove("learning-overlay-incorrect");
      repasoOverlay.textContent = "✓ Correcto";
    }
    if(repasoStatusPill){
      repasoStatusPill.className = "learning-status-pill learning-status-correct";
      repasoStatusPill.textContent = "¡Correcto!";
    }
    if(repasoCaption){
      repasoCaption.textContent = "¡Bien hecho! Presiona Siguiente para continuar";
    }
  }else if(!isMatch && repasoSameStreak >= REPASO_STREAK_TO_CONFIRM){
    repasoIsCorrect = false;
    logRepasoAttempt(detected);
    if(repasoVideoWrap){
      repasoVideoWrap.classList.add("learning-incorrect");
      repasoVideoWrap.classList.remove("learning-correct");
    }
    if(repasoOverlay){
      repasoOverlay.classList.add("learning-overlay-incorrect");
      repasoOverlay.classList.remove("learning-overlay-correct");
      repasoOverlay.textContent = "✗ Intenta de nuevo";
    }
    if(repasoStatusPill){
      repasoStatusPill.className = "learning-status-pill learning-status-incorrect";
      repasoStatusPill.textContent = `Se detectó: ${detected}`;
    }
    if(repasoCaption){
      repasoCaption.textContent = `Busca la seña de la letra ${repasoTargetLetter}`;
    }
  }
}

let pollTimer = null;
let recording = false;
let lastLoggedIn = null;
let learningIndex = 0;
let learningTargetLetter = "A";
let learningCorrectCount = 0;
let learningSameStreak = 0;
let learningLastDetected = null;
let learningIsCorrect = false;
let learningAttemptLogged = false;
let learningAnalysis = null;
const LEARNING_STREAK_TO_CONFIRM = 3;

function setView(name){
  viewLogin.classList.toggle("hidden", name !== "login");
  viewRegister.classList.toggle("hidden", name !== "register");
  viewMenu.classList.toggle("hidden", name !== "menu");
  viewInteraction.classList.toggle("hidden", name !== "interaction");
  viewAprendizaje.classList.toggle("hidden", name !== "aprendizaje");
  viewEvaluacionConfig.classList.toggle("hidden", name !== "evaluacion_config");
  viewEvaluacionRun.classList.toggle("hidden", name !== "evaluacion_run");
  if(typeof viewRepaso !== 'undefined') viewRepaso.classList.toggle("hidden", name !== "repaso");
  viewReto.classList.toggle("hidden", name !== "reto");
}

function currentView(){
  if(typeof viewRepaso !== 'undefined' && !viewRepaso.classList.contains("hidden")) return "repaso";
  if(!viewEvaluacionRun.classList.contains("hidden")) return "evaluacion_run";
  if(!viewEvaluacionConfig.classList.contains("hidden")) return "evaluacion_config";
  if(!viewReto.classList.contains("hidden")) return "reto";
  if(!viewAprendizaje.classList.contains("hidden")) return "aprendizaje";
  if(!viewInteraction.classList.contains("hidden")) return "interaction";
  if(!viewMenu.classList.contains("hidden")) return "menu";
  if(!viewRegister.classList.contains("hidden")) return "register";
  return "login";
}

function renderReto(st){
  const letters = st.challenge_letters || [];
  const idx = st.challenge_index || 0;
  const done = !!st.challenge_done;

  if(letters.length === 0){
    retoEmpty.classList.remove("hidden");
    retoGrid.classList.add("hidden");
    retoWord.classList.add("hidden");
    retoComplete.classList.add("hidden");
    return;
  }
  retoEmpty.classList.add("hidden");
  retoWord.classList.remove("hidden");

  retoWord.innerHTML = "";
  letters.forEach((l, i) => {
    const tile = document.createElement("div");
    let cls = "reto-letter-tile";
    if(i < idx || done) cls += " done";
    else if(i === idx) cls += " current";
    tile.className = cls;
    tile.textContent = l;
    retoWord.appendChild(tile);
  });

  if(done){
    retoGrid.classList.add("hidden");
    retoComplete.classList.remove("hidden");
    retoSubtitle.textContent = "¡Nombre completo!";
    return;
  }

  retoGrid.classList.remove("hidden");
  retoComplete.classList.add("hidden");

  const target = letters[idx];
  retoLetter.textContent = target;
  retoReferenceImage.src = `./assets/letras/${target.toLowerCase()}.png`;
  retoReferenceImage.alt = `Seña de la letra ${target}`;
  retoReferenceImage.style.display = "block";
  retoReferenceArt.querySelector(".reference-placeholder-text").style.display = "none";
  retoCaption.textContent = `Haz la seña de la letra "${target}"`;
  retoSubtitle.textContent = `Letra ${idx + 1} de ${letters.length}`;

  const progress = Math.max(0, Math.min(1, st.challenge_progress || 0));
  retoProgressFill.style.width = (progress * 100) + "%";
}

function renderFrame(frameB64, videoEl, fallbackEl, errorMsg){
  if(frameB64){
    videoEl.src = "data:image/jpeg;base64," + frameB64;
    videoEl.style.display = "block";
    fallbackEl.style.display = "none";
  }else{
    videoEl.style.display = "none";
    fallbackEl.style.display = "grid";
    fallbackEl.textContent = errorMsg || "Iniciando cámara…";
  }
}

function resetLearningFeedback(){
  learningIsCorrect = false;
  learningAttemptLogged = false;
  learningSameStreak = 0;
  learningLastDetected = null;
  if(learningVideoWrap){
    learningVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  }
  if(learningOverlay){
    learningOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    learningOverlay.textContent = "";
  }
  if(learningStatusPill){
    learningStatusPill.className = "learning-status-pill";
    learningStatusPill.textContent = "Esperando seña…";
  }
  if(learningCaption){
    learningCaption.textContent = "Repite la seña";
  }
  if(learningDetected){
    learningDetected.textContent = "-";
  }
}

function logLearningAttempt(detectedLetter){
  if(learningAttemptLogged) return;
  learningAttemptLogged = true;
  window.pywebview.api.learning_attempt(learningTargetLetter, detectedLetter).then((result) => {
    if(result && result.ok && result.analysis){
      renderLearningAssistant(result.analysis, result.letter);
    }
  }).catch(() => {
    learningAttemptLogged = false;
  });
}

function renderLearningAssistant(analysis, letter){
  if(!analysis) return;
  learningAnalysis = analysis;
  learningAssistantLetter.textContent = letter || learningTargetLetter || "-";
  learningAssistantCorrect.textContent = `${analysis.correct}/${analysis.attempts || 5}`;
  learningAssistantAccuracy.textContent = `${analysis.accuracy}%`;
  learningAssistantAttempts.textContent = `${analysis.attempts}/5`;
  learningAssistantMessage.textContent = analysis.message || "";
  learningAssistantRecommendation.textContent = analysis.recommendation === "practice"
    ? "⚠️ Necesitas practicar más esta letra."
    : analysis.recommendation === "optional_practice"
      ? "💡 Puedes practicar esta letra nuevamente si lo deseas."
      : analysis.recommendation === "good"
        ? "✅ Tu desempeño es bueno."
        : "";
  updateAssistantFavoriteButton(letter || learningTargetLetter);
}

async function refreshLearningAssistant(letter){
  try{
    const result = await window.pywebview.api.learning_performance(letter);
    if(result && result.ok) renderLearningAssistant(result.analysis, result.letter);
  }catch(e){
    // El asistente conserva el ultimo analisis valido si la consulta falla.
  }
}

function syncLearningView(letter, progressText){
  const letterValue = (letter && letter.trim()) ? letter.trim().toUpperCase() : "A";
  const idx = LETTERS.indexOf(letterValue);
  const finalIndex = idx >= 0 ? idx : 0;
  const progressValue = progressText || `${finalIndex + 1}/${LETTERS.length}`;
  const placeholder = learningReferenceArt.querySelector(".reference-placeholder-text");

  learningTargetLetter = letterValue;
  learningLetter.textContent = letterValue;
  learningProgress.textContent = `${letterValue} — ${progressValue}`;

  const imageName = letterValue.toLowerCase();
  learningReferenceImage.src = `./assets/letras/${imageName}.png`;
  learningReferenceImage.alt = `Seña de la letra ${letterValue}`;
  learningReferenceImage.style.display = "block";
  placeholder.style.display = "none";

  updateStarButton(letterValue);
  updateAssistantFavoriteButton(letterValue);
  resetLearningFeedback();
  refreshLearningAssistant(letterValue);
}

function updateLearningFeedback(detectedLetterRaw){
  const detected = (detectedLetterRaw && String(detectedLetterRaw).trim()) ? String(detectedLetterRaw).trim().toUpperCase() : null;
  if(learningDetected){
    learningDetected.textContent = detected || "-";
  }

  if(!detected){
    learningSameStreak = 0;
    learningLastDetected = null;
    if(!learningIsCorrect){
      if(learningVideoWrap){
        learningVideoWrap.classList.remove("learning-correct", "learning-incorrect");
      }
      if(learningOverlay){
        learningOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
        learningOverlay.textContent = "";
      }
      if(learningStatusPill){
        learningStatusPill.className = "learning-status-pill";
        learningStatusPill.textContent = "Esperando seña…";
      }
      if(learningCaption){
        learningCaption.textContent = "Repite la seña";
      }
    }
    return;
  }

  if(detected === learningLastDetected){
    learningSameStreak += 1;
  }else{
    learningSameStreak = 1;
    learningLastDetected = detected;
  }

  const isMatch = (detected === learningTargetLetter);

  if(isMatch && learningSameStreak >= LEARNING_STREAK_TO_CONFIRM){
    if(!learningIsCorrect){
      learningIsCorrect = true;
      learningCorrectCount += 1;
      logLearningAttempt(detected);
      if(learningCounter){
        learningCounter.textContent = `Correctas: ${learningCorrectCount}`;
      }
    }
    if(learningVideoWrap){
      learningVideoWrap.classList.add("learning-correct");
      learningVideoWrap.classList.remove("learning-incorrect");
    }
    if(learningOverlay){
      learningOverlay.classList.add("learning-overlay-correct");
      learningOverlay.classList.remove("learning-overlay-incorrect");
      learningOverlay.textContent = "✓ Correcto";
    }
    if(learningStatusPill){
      learningStatusPill.className = "learning-status-pill learning-status-correct";
      learningStatusPill.textContent = "¡Correcto!";
    }
    if(learningCaption){
      learningCaption.textContent = "¡Bien hecho! Presiona Siguiente para continuar";
    }
  }else if(!isMatch && learningSameStreak >= LEARNING_STREAK_TO_CONFIRM){
    learningIsCorrect = false;
    logLearningAttempt(detected);
    if(learningVideoWrap){
      learningVideoWrap.classList.add("learning-incorrect");
      learningVideoWrap.classList.remove("learning-correct");
    }
    if(learningOverlay){
      learningOverlay.classList.add("learning-overlay-incorrect");
      learningOverlay.classList.remove("learning-overlay-correct");
      learningOverlay.textContent = "✗ Intenta de nuevo";
    }
    if(learningStatusPill){
      learningStatusPill.className = "learning-status-pill learning-status-incorrect";
      learningStatusPill.textContent = `Se detectó: ${detected}`;
    }
    if(learningCaption){
      learningCaption.textContent = `Busca la seña de la letra ${learningTargetLetter}`;
    }
  }
}

function addBubble(who, text){
  const div = document.createElement("div");
  div.className = "bubble " + (who.includes("voz") ? "me" : "other");
  const whoDiv = document.createElement("div");
  whoDiv.className = "who";
  whoDiv.textContent = who;
  const txt = document.createElement("div");
  txt.textContent = text;
  div.appendChild(whoDiv);
  div.appendChild(txt);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function poll(){
  try{
    const st = await window.pywebview.api.get_state();
    if(st && st.logged_in){
      btnLogout.classList.remove("hidden");
      if(st.username && favoriteUsername !== st.username){
        favoriteUsername = st.username;
        refreshFavoriteLetters();
      }
      if(currentView() === "login" || currentView() === "register"){
        setView("menu");
      }

      signText.value = st.sign_text || "";
      letterPill.textContent = "Letra: " + (st.letter || "-");

      if(currentView() !== "aprendizaje"){
        syncLearningView(st.letter || "A", "1/27");
      }else{
        updateLearningFeedback(st.letter);
      }

      renderFrame(st.frame_jpeg_b64, videoInteraction, videoFallbackInteraction, st.camera_error);
      renderFrame(st.frame_jpeg_b64, videoAprendizaje, videoFallbackAprendizaje, st.camera_error);
      renderFrame(st.frame_jpeg_b64, videoReto, videoFallbackReto, st.camera_error);
      renderReto(st);

      // Si estamos en modo evaluación, actualizar video y letra detectada
      try{
        if(typeof videoEvaluacion !== 'undefined') renderFrame(st.frame_jpeg_b64, videoEvaluacion, videoFallbackEvaluacion, st.camera_error);
      }catch(e){}

      try{
        if(typeof evalDetectedLetter !== 'undefined'){
          evalDetectedLetter.textContent = st.letter || "-";
          if(currentView() === 'evaluacion_run') updateEvaluationScoring(st.letter);
        }
      }catch(e){}

      // Si estamos en modo Repaso, actualizar video y detección
      try{
        if(typeof videoRepaso !== 'undefined') renderFrame(st.frame_jpeg_b64, videoRepaso, videoFallbackRepaso, st.camera_error);
        if(currentView() === 'repaso') updateRepasoFeedback(st.letter);
      }catch(e){}

      // append new messages
      if(Array.isArray(st.new_messages)){
        for(const m of st.new_messages){
          addBubble(m.who, m.text);
        }
      }

      voiceError.textContent = st.voice_error || "";
    }else{
      btnLogout.classList.add("hidden");
      // No forzar login si el usuario está en "Crear cuenta"
      if(["interaction", "menu", "aprendizaje", "reto"].includes(currentView())){
        setView("login");
      }

      // Solo limpiar campos cuando ocurre transición de logueado -> deslogueado
      if(lastLoggedIn === true){
        $("loginUser").value = "";
        $("loginPass").value = "";
        $("regUser").value = "";
        $("regPass").value = "";
        $("regPass2").value = "";
      }
      favoriteLetters = new Set();
      favoriteUsername = null;
      updateDifficultCount();
    }
    lastLoggedIn = !!(st && st.logged_in);
  }catch(e){
    // silent
  }
}

function moveLearning(step) {
  learningIndex = (learningIndex + step + LETTERS.length) % LETTERS.length;
  const current = LETTERS[learningIndex];
  syncLearningView(current, `${learningIndex + 1}/${LETTERS.length}`);
}

function startPolling(){
  if(pollTimer) return;
  pollTimer = setInterval(poll, 220);
  poll();
  syncLearningView(LETTERS[learningIndex], `${learningIndex + 1}/${LETTERS.length}`);
}

// Auth
$("btnLogin").onclick = async () => {
  loginError.textContent = "";
  const u = $("loginUser").value.trim();
  const p = $("loginPass").value;
  const res = await window.pywebview.api.login(u, p);
  if(!res.ok) loginError.textContent = res.msg || "Error";
};
$("btnGoRegister").onclick = () => { loginError.textContent=""; setView("register"); };
$("btnGoLogin").onclick = () => { regError.textContent=""; setView("login"); };
$("btnRegister").onclick = async () => {
  regError.textContent = "";
  const u = $("regUser").value.trim();
  const p = $("regPass").value;
  const p2 = $("regPass2").value;
  const res = await window.pywebview.api.register(u, p, p2);
  if(!res.ok) regError.textContent = res.msg || "Error";
  else{
    // limpiar por seguridad
    $("regPass").value = "";
    $("regPass2").value = "";
    setView("login");
  }
};
$("btnLogout").onclick = async () => {
  await window.pywebview.api.logout();
  chat.innerHTML = "";
  favoriteLetters = new Set();
  favoriteUsername = null;
  $("loginUser").value = "";
  $("loginPass").value = "";
  setView("login");
};

$("btnLogoutMenu").onclick = async () => {
  await window.pywebview.api.logout();
  chat.innerHTML = "";
  favoriteLetters = new Set();
  favoriteUsername = null;
  setView("login");
};

$("btnOpenInteraction").onclick = () => setView("interaction");
$("btnOpenAprendizaje").onclick = () => {
  learningIndex = 0;
  learningCorrectCount = 0;
  if(learningCounter){
    learningCounter.textContent = "Correctas: 0";
  }
  updateDifficultCount();
  syncLearningView(LETTERS[learningIndex], `${learningIndex + 1}/${LETTERS.length}`);
  setView("aprendizaje");
};
// Abrir configuración de Modo Evaluación
$("btnOpenEvaluacion").onclick = () => {
  // reset UI
  const radios = document.getElementsByName('evalDuration');
  for(const r of radios) r.checked = (r.value === '30');
  setView('evaluacion_config');
};

$("btnPrevAprendizaje").onclick = () => moveLearning(-1);
$("btnNextAprendizaje").onclick = () => moveLearning(1);
if(btnStarLetter){
  btnStarLetter.onclick = () => toggleFavoriteLetter(learningTargetLetter);
}
if(btnAssistantFavorite){
  btnAssistantFavorite.onclick = () => toggleFavoriteLetter(learningTargetLetter);
}
if(btnPracticeNow){
  btnPracticeNow.onclick = () => openRepasoForLetter(learningAnalysis && learningAnalysis.letter || learningTargetLetter);
}
$("btnOpenLearningAssistant").onclick = () => learningAssistantCard.classList.toggle("hidden");
$("btnCloseLearningAssistant").onclick = () => learningAssistantCard.classList.add("hidden");

// Repaso
if($("btnOpenRepaso")){
  $("btnOpenRepaso").onclick = () => {
    repasoInitialLetter = null;
    repasoIndex = 0;
    refreshFavoriteLetters().then(() => syncRepasoView());
    setView("repaso");
  };
}
if($("btnBackRepaso")){
  $("btnBackRepaso").onclick = () => {
    if(window.pywebview && window.pywebview.api && window.pywebview.api.reset_review_attempts){
      window.pywebview.api.reset_review_attempts().catch(() => {});
    }
    setView("menu");
  };
}
if($("btnPrevRepaso")){
  $("btnPrevRepaso").onclick = () => moveRepaso(-1);
}
if($("btnNextRepaso")){
  $("btnNextRepaso").onclick = () => moveRepaso(1);
}
if(btnUnstarRepaso){
  btnUnstarRepaso.onclick = async () => {
    if(!repasoTargetLetter) return;
    await toggleFavoriteLetter(repasoTargetLetter);
    // Si la letra actual se quitó de la lista, ajusta el índice antes de re-sincronizar
    if(repasoIndex >= repasoList.length - 1){
      repasoIndex = 0;
    }
    syncRepasoView();
  };
}
if($("btnOpenRepasoAssistant")){
  $("btnOpenRepasoAssistant").onclick = () => repasoAssistantCard.classList.toggle("hidden");
}
if($("btnCloseRepasoAssistant")){
  $("btnCloseRepasoAssistant").onclick = () => repasoAssistantCard.classList.add("hidden");
}

$("btnBackInteraction").onclick = () => {
  if(recording) return;
  setView("menu");
};
$("btnBackAprendizaje").onclick = () => setView("menu");
$("btnBackEvaluacionRun").onclick = () => {
  stopEvaluation();
  setView("menu");
};

// Evaluación state
let evalTimerId = null;
let evalChangeId = null;
let evalRemaining = 0;
let evalScoreVal = 0;
let evalChangeInterval = 5; // segundos por letra
let evalLastDetected = null;
let evalSameStreak = 0;
let evalAlreadyScored = false;
let evalFeedbackTimeoutId = null;
const EVAL_STREAK_TO_CONFIRM = 3;
const EVAL_FEEDBACK_DURATION_MS = 1200; // cuánto dura el borde/overlay verde o rojo // frames seguidos iguales para confirmar

function formatTimeSec(s){
  const mm = Math.floor(s/60).toString().padStart(2,'0');
  const ss = (s%60).toString().padStart(2,'0');
  return `${mm}:${ss}`;
}

function pickRandomLetter(){
  return LETTERS[Math.floor(Math.random()*LETTERS.length)];
}

function clearEvalFeedback(){
  if(evalFeedbackTimeoutId){
    clearTimeout(evalFeedbackTimeoutId);
    evalFeedbackTimeoutId = null;
  }
  if(evalVideoWrap){
    evalVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  }
  if(evalOverlay){
    evalOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    evalOverlay.textContent = "";
  }
}

function showEvalFeedback(isCorrect){
  if(evalFeedbackTimeoutId){
    clearTimeout(evalFeedbackTimeoutId);
  }
  if(evalVideoWrap){
    evalVideoWrap.classList.toggle("learning-correct", isCorrect);
    evalVideoWrap.classList.toggle("learning-incorrect", !isCorrect);
  }
  if(evalOverlay){
    evalOverlay.classList.toggle("learning-overlay-correct", isCorrect);
    evalOverlay.classList.toggle("learning-overlay-incorrect", !isCorrect);
    evalOverlay.textContent = isCorrect ? "✓ Correcto" : "✗ Incorrecto";
  }
  evalFeedbackTimeoutId = setTimeout(clearEvalFeedback, EVAL_FEEDBACK_DURATION_MS);
}

function updateEvaluationScoring(detectedLetterRaw){
  const detected = (detectedLetterRaw && String(detectedLetterRaw).trim())
    ? String(detectedLetterRaw).trim().toUpperCase()
    : null;

  if(!detected){
    evalSameStreak = 0;
    return;
  }

  if(detected === evalLastDetected){
    evalSameStreak += 1;
  }else{
    evalLastDetected = detected;
    evalSameStreak = 1;
  }

  if(evalSameStreak >= EVAL_STREAK_TO_CONFIRM && !evalAlreadyScored){
    evalAlreadyScored = true;
    const target = (evalRequestedLetter.textContent || '').trim().toUpperCase();
    const isCorrect = (detected === target);

    if(isCorrect){
      evalScoreVal += 5;
    }else{
      evalScoreVal -= 2;
    }
    evalScore.textContent = 'Puntaje: ' + evalScoreVal;
    showEvalFeedback(isCorrect);
  }
}

async function startEvaluationWithDuration(seconds){
  // prepare
  evalRemaining = seconds;
  evalScoreVal = 0;
  evalLastDetected = null;
  evalSameStreak = 0;
  evalAlreadyScored = false;
  clearEvalFeedback();
  evalTime.textContent = 'Tiempo: ' + formatTimeSec(evalRemaining);
  evalScore.textContent = 'Puntaje: ' + evalScoreVal;
  evalRequestedLetter.textContent = '-';

  setView('evaluacion_run');

  // show first requested letter (aleatoria)
  evalRequestedLetter.textContent = pickRandomLetter();

  // Change requested letter periodically (aleatoria, no se muestra la siguiente)
  evalChangeId = setInterval(() => {
    evalRequestedLetter.textContent = pickRandomLetter();
    // Reinicia el estado de detección para la nueva letra pedida
    evalLastDetected = null;
    evalSameStreak = 0;
    evalAlreadyScored = false;
    clearEvalFeedback();
  }, evalChangeInterval * 1000);

  // Countdown timer
  evalTimerId = setInterval(() => {
    evalRemaining -= 1;
    evalTime.textContent = 'Tiempo: ' + formatTimeSec(evalRemaining);
    evalScore.textContent = 'Puntaje: ' + evalScoreVal;
    if(evalRemaining <= 0){
      stopEvaluation();
    }
  }, 1000);
}

function stopEvaluation(){
  if(evalTimerId){ clearInterval(evalTimerId); evalTimerId = null; }
  if(evalChangeId){ clearInterval(evalChangeId); evalChangeId = null; }
  // reset UI and go back to menu
  evalRequestedLetter.textContent = '-';
  evalDetectedLetter.textContent = '-';
  evalLastDetected = null;
  evalSameStreak = 0;
  evalAlreadyScored = false;
  clearEvalFeedback();
  setView('menu');
}

// Handlers for evaluation controls
$("btnCancelEvaluation").onclick = () => setView('menu');
$("btnStopEvaluation").onclick = () => stopEvaluation();
$("btnStartEvaluation").onclick = () => {
  const radios = document.getElementsByName('evalDuration');
  let val = 30;
  for(const r of radios){ if(r.checked) val = parseInt(r.value); }
  startEvaluationWithDuration(val);
};

// Reto: deletrea tu nombre
$("btnOpenReto").onclick = async () => {
  await window.pywebview.api.challenge_start();
  setView("reto");
};
$("btnRetoBack").onclick = async () => {
  await window.pywebview.api.challenge_stop();
  setView("menu");
};
$("btnRetoRetry").onclick = async () => {
  await window.pywebview.api.challenge_start();
};
$("btnRetoMenu").onclick = async () => {
  await window.pywebview.api.challenge_stop();
  setView("menu");
};

// Interaction actions
$("btnAccept").onclick = () => window.pywebview.api.sign_accept();
$("btnSpace").onclick = () => window.pywebview.api.sign_space();
$("btnBackspace").onclick = () => window.pywebview.api.sign_backspace();
$("btnClear").onclick = () => window.pywebview.api.sign_clear();
$("btnSendSigns").onclick = () => window.pywebview.api.sign_send();

$("btnRec").onclick = async () => {
  voiceError.textContent = "";
  if(!recording){
    recording = true;
    $("btnRec").textContent = "Detener";
    $("btnRec").classList.add("danger");
    $("btnRec").classList.remove("primary");
    await window.pywebview.api.voice_start();
  }else{
    $("btnRec").disabled = true;
    await window.pywebview.api.voice_stop();
    // UI se reactivará cuando backend marque status
    setTimeout(() => { $("btnRec").disabled = false; recording=false;
      $("btnRec").textContent = "Grabar";
      $("btnRec").classList.remove("danger");
      $("btnRec").classList.add("primary");
    }, 1200);
  }
};

startPolling();
