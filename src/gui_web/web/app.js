const $ = (id) => document.getElementById(id);

const viewLogin = $("viewLogin");
const viewRegister = $("viewRegister");
const viewRegisterAccessibility = $("viewRegisterAccessibility");
const viewMenu = $("viewMenu");
const viewInteraction = $("viewInteraction");
const viewAprendizaje = $("viewAprendizaje");
const viewEvaluacionConfig = $("viewEvaluacionConfig");
const viewEvaluacionRun = $("viewEvaluacionRun");
const viewEvaluacionResultados = $("viewEvaluacionResultados");
const viewEvaluacionHistorial = $("viewEvaluacionHistorial");
const viewSettings = $("viewSettings");

// Evaluation elements
const evalRequestedLetter = $("evalRequestedLetter");
const evalDetectedLetter = $("evalDetectedLetter");
const evalTime = $("evalTime");
const evalScore = $("evalScore");
const evalHits = $("evalHits");
const evalErrors = $("evalErrors");
const evalResultScore = $("evalResultScore");
const evalResultHits = $("evalResultHits");
const evalResultErrors = $("evalResultErrors");
const evalResultDuration = $("evalResultDuration");
const evalResultHitLetters = $("evalResultHitLetters");
const evalResultErrorLetters = $("evalResultErrorLetters");
const evaluationHistoryList = $("evaluationHistoryList");
const evaluationHistoryEmpty = $("evaluationHistoryEmpty");
const evaluationHistorySummary = $("evaluationHistorySummary");
const evaluationHistoryMeta = $("evaluationHistoryMeta");
const historyHitLetters = $("historyHitLetters");
const historyErrorLetters = $("historyErrorLetters");
const evaluationScoreProgress = $("evaluationScoreProgress");
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
const settingsColorBlindMode = $("settingsColorBlindMode");
const settingsAccessibleReadingMode = $("settingsAccessibleReadingMode");
const settingsNightMode = $("settingsNightMode");
const btnSaveSettings = $("btnSaveSettings");
const settingsError = $("settingsError");

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
const REPASO_STREAK_TO_CONFIRM = 3;

function buildRepasoList(){
  repasoList = Array.from(favoriteLetters).sort();
  if(repasoIndex >= repasoList.length){
    repasoIndex = 0;
  }
}

function resetRepasoFeedback(){
  repasoIsCorrect = false;
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

function updateRepasoFeedback(detectedLetterRaw){
  const detected = (detectedLetterRaw && String(detectedLetterRaw).trim()) ? String(detectedLetterRaw).trim().toUpperCase() : null;
  if(repasoDetected){
    repasoDetected.textContent = detected || "-";
  }

  if(!detected){
    repasoSameStreak = 0;
    repasoLastDetected = null;
    return;
  }

  if(detected === repasoLastDetected){
    repasoSameStreak += 1;
  }else{
    repasoSameStreak = 1;
    repasoLastDetected = detected;
  }

  const isMatch = (detected === repasoTargetLetter);

  if(isMatch && repasoSameStreak >= REPASO_STREAK_TO_CONFIRM){
    if(!repasoIsCorrect){
      repasoIsCorrect = true;
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
let accessibilitySettingsDirty = false;
const LEARNING_STREAK_TO_CONFIRM = 3;

function setView(name){
  viewLogin.classList.toggle("hidden", name !== "login");
  viewRegister.classList.toggle("hidden", name !== "register");
  viewRegisterAccessibility.classList.toggle("hidden", name !== "register_accessibility");
  viewMenu.classList.toggle("hidden", name !== "menu");
  viewInteraction.classList.toggle("hidden", name !== "interaction");
  viewAprendizaje.classList.toggle("hidden", name !== "aprendizaje");
  viewEvaluacionConfig.classList.toggle("hidden", name !== "evaluacion_config");
  viewEvaluacionRun.classList.toggle("hidden", name !== "evaluacion_run");
  viewEvaluacionResultados.classList.toggle("hidden", name !== "evaluacion_resultados");
  viewEvaluacionHistorial.classList.toggle("hidden", name !== "evaluacion_historial");
  viewSettings.classList.toggle("hidden", name !== "settings");
  if(typeof viewRepaso !== 'undefined') viewRepaso.classList.toggle("hidden", name !== "repaso");
  viewReto.classList.toggle("hidden", name !== "reto");
}

function currentView(){
  if(!viewRegisterAccessibility.classList.contains("hidden")) return "register_accessibility";
  if(typeof viewRepaso !== 'undefined' && !viewRepaso.classList.contains("hidden")) return "repaso";
  if(!viewEvaluacionRun.classList.contains("hidden")) return "evaluacion_run";
  if(!viewEvaluacionConfig.classList.contains("hidden")) return "evaluacion_config";
  if(!viewEvaluacionResultados.classList.contains("hidden")) return "evaluacion_resultados";
  if(!viewEvaluacionHistorial.classList.contains("hidden")) return "evaluacion_historial";
  if(!viewSettings.classList.contains("hidden")) return "settings";
  if(!viewReto.classList.contains("hidden")) return "reto";
  if(!viewAprendizaje.classList.contains("hidden")) return "aprendizaje";
  if(!viewInteraction.classList.contains("hidden")) return "interaction";
  if(!viewMenu.classList.contains("hidden")) return "menu";
  if(!viewRegister.classList.contains("hidden")) return "register";
  return "login";
}

function applyColorBlindMode(enabled, syncControl = true){
  document.body.classList.toggle("color-blind-mode", !!enabled);
  if(syncControl && settingsColorBlindMode){
    settingsColorBlindMode.checked = !!enabled;
  }
}

function applyAccessibleReadingMode(enabled, syncControl = true){
  document.body.classList.toggle("accessible-reading-mode", !!enabled);
  if(syncControl && settingsAccessibleReadingMode){
    settingsAccessibleReadingMode.checked = !!enabled;
  }
}

function applyNightMode(enabled, syncControl = true){
  const isEnabled = !!enabled;
  document.body.classList.toggle("night-mode", isEnabled);
  if(syncControl && settingsNightMode){
    settingsNightMode.checked = isEnabled;
  }
}

function applyAccessibilityPreferences(colorBlindMode, accessibleReadingMode, nightMode, syncControls = true){
  applyColorBlindMode(colorBlindMode, syncControls);
  applyAccessibleReadingMode(accessibleReadingMode, syncControls);
  applyNightMode(nightMode, syncControls);
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

  // ===== INICIO: identifica si la letra es correcta y pinta el marco =====
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
  // ===== FIN: identifica si la letra es correcta y pinta el marco =====
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
      if(!accessibilitySettingsDirty){
        applyAccessibilityPreferences(st.color_blind_mode, st.accessible_reading_mode, st.night_mode);
      }
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

      // Si estamos en modo evaluación, mostrar el estado calculado por backend.
      try{
        if(typeof videoEvaluacion !== 'undefined') renderFrame(st.frame_jpeg_b64, videoEvaluacion, videoFallbackEvaluacion, st.camera_error);
        if(typeof evalDetectedLetter !== 'undefined'){
          evalDetectedLetter.textContent = st.evaluation_detected || st.letter || "-";
          evalRequestedLetter.textContent = st.evaluation_target || "-";
          evalTime.textContent = "Tiempo: " + formatTimeSec(st.evaluation_remaining || 0);
          evalScore.textContent = "Puntaje: " + (st.evaluation_score || 0);
          evalHits.textContent = "Aciertos: " + (st.evaluation_hits || 0);
          evalErrors.textContent = "Errores: " + (st.evaluation_errors || 0);
          if(currentView() === "evaluacion_run" && !st.evaluation_active && st.evaluation_duration){
            stopEvaluation();
          }
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
      // No interrumpir el registro mientras todavía no existe una sesión.
      if(["interaction", "menu", "aprendizaje", "reto", "evaluacion_run", "evaluacion_config", "evaluacion_resultados", "settings"].includes(currentView())){
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
      accessibilitySettingsDirty = false;
      applyColorBlindMode(false);
      applyAccessibleReadingMode(false);
      applyNightMode(false);
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
  if(!res.ok){
    loginError.textContent = res.msg || "Error";
    return;
  }
  accessibilitySettingsDirty = false;
  const state = await window.pywebview.api.get_state();
  if(state && state.logged_in){
    applyAccessibilityPreferences(
      state.color_blind_mode,
      state.accessible_reading_mode,
      state.night_mode,
    );
  }
};
$("btnGoRegister").onclick = () => { loginError.textContent=""; setView("register"); };
$("btnGoLogin").onclick = () => { regError.textContent=""; setView("login"); };
$("btnContinueRegister").onclick = () => {
  regError.textContent = "";
  const username = $("regUser").value.trim();
  const password = $("regPass").value;
  const confirmation = $("regPass2").value;
  if(!username || !password || !confirmation){
    regError.textContent = "Completa todos los campos para continuar";
    return;
  }
  setView("register_accessibility");
};
$("btnBackRegister").onclick = () => {
  $("regAccessibilityError").textContent = "";
  setView("register");
};
$("btnRegister").onclick = async () => {
  regError.textContent = "";
  $("regAccessibilityError").textContent = "";
  const u = $("regUser").value.trim();
  const p = $("regPass").value;
  const p2 = $("regPass2").value;
  const colorBlindMode = $("regColorBlindMode").checked;
  const accessibleReadingMode = $("regAccessibleReadingMode").checked;
  const res = await window.pywebview.api.register(u, p, p2, colorBlindMode, accessibleReadingMode);
  if(!res.ok) {
    $("regAccessibilityError").textContent = res.msg || "Error";
  }
  else{
    // limpiar por seguridad
    $("regPass").value = "";
    $("regPass2").value = "";
    $("regColorBlindMode").checked = false;
    $("regAccessibleReadingMode").checked = false;
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

$("btnOpenSettings").onclick = () => {
  settingsError.textContent = "";
  accessibilitySettingsDirty = false;
  setView("settings");
};
$("btnBackSettings").onclick = () => {
  accessibilitySettingsDirty = false;
  setView("menu");
};
settingsColorBlindMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyColorBlindMode(settingsColorBlindMode.checked, false);
};
settingsAccessibleReadingMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyAccessibleReadingMode(settingsAccessibleReadingMode.checked, false);
};
settingsNightMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyNightMode(settingsNightMode.checked, false);
};
btnSaveSettings.onclick = async () => {
  settingsError.textContent = "";
  btnSaveSettings.disabled = true;
  const result = await window.pywebview.api.set_accessibility_preferences(
    settingsColorBlindMode.checked,
    settingsAccessibleReadingMode.checked,
    settingsNightMode.checked,
  );
  btnSaveSettings.disabled = false;
  if(!result || !result.ok){
    settingsError.textContent = result?.msg || "No se pudo guardar la preferencia";
    btnSaveSettings.disabled = false;
    return;
  }
  accessibilitySettingsDirty = false;
  applyAccessibilityPreferences(result.color_blind_mode, result.accessible_reading_mode, result.night_mode);
  btnSaveSettings.disabled = false;
  setView("menu");
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
  $("btnBackRepaso").onclick = () => setView("menu");
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

$("btnBackInteraction").onclick = () => {
  if(recording) return;
  setView("menu");
};
$("btnBackAprendizaje").onclick = () => setView("menu");
$("btnBackEvaluacionRun").onclick = () => {
  stopEvaluation(false);
};

// Evaluación state
let evalTimerId = null;
let evalFeedbackTimeoutId = null;
let evaluationStopPending = false;
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

async function startEvaluationWithDuration(seconds){
  const result = await window.pywebview.api.eval_start(seconds);
  if(!result || !result.ok) return;
  evaluationStopPending = false;
  clearEvalFeedback();
  evalRequestedLetter.textContent = result.target_letter || "-";
  evalDetectedLetter.textContent = "-";
  evalTime.textContent = "Tiempo: " + formatTimeSec(seconds);
  evalScore.textContent = "Puntaje: 0";
  evalHits.textContent = "Aciertos: 0";
  evalErrors.textContent = "Errores: 0";
  setView("evaluacion_run");
}

async function stopEvaluation(showResults = true){
  if(evaluationStopPending) return;
  evaluationStopPending = true;
  let response;
  try{
    response = await window.pywebview.api.eval_stop();
  }catch(e){
    evaluationStopPending = false;
    return;
  }
  if(!response || !response.ok){
    evaluationStopPending = false;
    return;
  }
  if(!showResults){
    evaluationStopPending = false;
    setView("menu");
    return;
  }
  const results = response.results || {};
  saveEvaluationSession(results);
  evalResultScore.textContent = results.score || 0;
  evalResultHits.textContent = results.hits || 0;
  evalResultErrors.textContent = results.errors || 0;
  evalResultDuration.textContent = formatTimeSec(results.elapsed_seconds || results.duration_seconds || 0);
  renderEvaluationLetters(evalResultHitLetters, results.hit_letters, "Sin aciertos");
  renderEvaluationLetters(evalResultErrorLetters, results.error_letters, "Sin errores");
  evalRequestedLetter.textContent = '-';
  evalDetectedLetter.textContent = '-';
  clearEvalFeedback();
  evaluationStopPending = false;
  setView("evaluacion_resultados");
}

function renderEvaluationLetters(container, letters, emptyText){
  container.innerHTML = "";
  if(!Array.isArray(letters) || letters.length === 0){
    container.textContent = emptyText;
    return;
  }
  letters.forEach((letter) => {
    const pill = document.createElement("span");
    pill.className = "evaluation-letter-pill";
    pill.textContent = letter;
    container.appendChild(pill);
  });
}

function evaluationHistoryKey(){
  const user = favoriteUsername || "guest";
  return `traductor.evaluationHistory.${user}`;
}

function loadEvaluationHistory(){
  try{
    const history = JSON.parse(localStorage.getItem(evaluationHistoryKey()) || "[]");
    return Array.isArray(history) ? history : [];
  }catch(e){
    return [];
  }
}

function saveEvaluationSession(results){
  const session = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    date: new Date().toISOString(),
    duration_seconds: Number(results.duration_seconds || 0),
    score: Number(results.score || 0),
    hits: Number(results.hits || 0),
    errors: Number(results.errors || 0),
    hit_letters: Array.isArray(results.hit_letters) ? results.hit_letters.slice() : [],
    error_letters: Array.isArray(results.error_letters) ? results.error_letters.slice() : []
  };
  const history = [session, ...loadEvaluationHistory()];
  try{
    localStorage.setItem(evaluationHistoryKey(), JSON.stringify(history));
  }catch(e){
    // La evaluación y sus resultados siguen disponibles aunque el navegador no permita persistir.
  }
  return session;
}

function formatEvaluationDate(isoDate){
  const date = new Date(isoDate);
  if(Number.isNaN(date.getTime())) return "Fecha desconocida";
  return date.toLocaleDateString("es-ES", {day:"2-digit", month:"2-digit", year:"numeric"});
}

function formatEvaluationDateTime(isoDate){
  const date = new Date(isoDate);
  if(Number.isNaN(date.getTime())) return "Fecha desconocida";
  return date.toLocaleString("es-ES", {day:"2-digit", month:"2-digit", year:"numeric", hour:"2-digit", minute:"2-digit"});
}

function formatEvaluationDuration(seconds){
  const total = Math.max(0, Number(seconds) || 0);
  if(total < 60) return `${total} segundos`;
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return rest ? `${minutes} min ${rest} s` : `${minutes} ${minutes === 1 ? "minuto" : "minutos"}`;
}

function showEvaluationHistorySession(session){
  if(!session) return;
  evaluationHistoryEmpty.classList.add("hidden");
  evaluationHistorySummary.classList.remove("hidden");
  evaluationHistoryMeta.textContent = `${formatEvaluationDateTime(session.date)} — ${formatEvaluationDuration(session.duration_seconds)} — ${session.score} puntos — ${session.hits} aciertos — ${session.errors} errores`;
  renderEvaluationLetters(historyHitLetters, session.hit_letters, "Sin aciertos");
  renderEvaluationLetters(historyErrorLetters, session.error_letters, "Sin errores");
  document.querySelectorAll(".evaluation-history-item").forEach((item) => {
    item.classList.toggle("selected", item.dataset.sessionId === session.id);
  });
}

function renderEvaluationHistory(){
  const history = loadEvaluationHistory();
  evaluationHistoryList.innerHTML = "";
  if(history.length === 0){
    evaluationHistoryList.innerHTML = '<p class="muted">Todavía no hay evaluaciones guardadas.</p>';
    evaluationHistoryEmpty.classList.remove("hidden");
    evaluationHistorySummary.classList.add("hidden");
  }else{
    history.forEach((session) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "evaluation-history-item";
      item.dataset.sessionId = session.id;
      item.innerHTML = `<strong>${formatEvaluationDate(session.date)}</strong><span>${formatEvaluationDuration(session.duration_seconds)} — ${session.score} puntos — ${session.hits} aciertos — ${session.errors} errores</span>`;
      item.onclick = () => showEvaluationHistorySession(session);
      evaluationHistoryList.appendChild(item);
    });
    showEvaluationHistorySession(history[0]);
  }

  evaluationScoreProgress.innerHTML = "";
  if(history.length === 0){
    evaluationScoreProgress.innerHTML = '<p class="muted">Completa una evaluación para ver tu progreso.</p>';
    return;
  }
  const maxMagnitude = Math.max(1, ...history.map((session) => Math.abs(Number(session.score) || 0)));
  history.slice(0, 12).reverse().forEach((session, index) => {
    const row = document.createElement("div");
    row.className = "evaluation-score-row";
    const width = Math.max(4, Math.round(Math.abs(session.score || 0) / maxMagnitude * 100));
    row.innerHTML = `<span>#${index + 1}</span><div class="evaluation-score-track"><i class="${session.score < 0 ? "negative" : ""}" style="width:${width}%"></i></div><strong>${session.score}</strong>`;
    evaluationScoreProgress.appendChild(row);
  });
}

// Handlers for evaluation controls
$("btnCancelEvaluation").onclick = () => setView('menu');
$("btnStopEvaluation").onclick = () => stopEvaluation();
$("btnRetryEvaluation").onclick = () => setView("evaluacion_config");
$("btnResultsMenu").onclick = () => setView("menu");
$("btnOpenEvaluacionHistorial").onclick = () => {
  renderEvaluationHistory();
  setView("evaluacion_historial");
};
$("btnBackEvaluacionHistorial").onclick = () => setView("menu");
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

applyNightMode(false);
startPolling();