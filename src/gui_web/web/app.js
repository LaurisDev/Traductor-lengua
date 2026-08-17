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
const evalUpcoming = $("evalUpcoming");
const videoEvaluacion = $("videoEvaluacion");
const videoFallbackEvaluacion = $("videoFallbackEvaluacion");

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
const btnLogout = $("btnLogout");

const LETTERS = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","Ñ","O","P","Q","R","S","T","U","V","W","X","Y","Z"];
let pollTimer = null;
let recording = false;
let lastLoggedIn = null;
let learningIndex = 0;

function setView(name){
  viewLogin.classList.toggle("hidden", name !== "login");
  viewRegister.classList.toggle("hidden", name !== "register");
  viewMenu.classList.toggle("hidden", name !== "menu");
  viewInteraction.classList.toggle("hidden", name !== "interaction");
  viewAprendizaje.classList.toggle("hidden", name !== "aprendizaje");
  viewEvaluacionConfig.classList.toggle("hidden", name !== "evaluacion_config");
  viewEvaluacionRun.classList.toggle("hidden", name !== "evaluacion_run");
}

function currentView(){
  if(!viewEvaluacionRun.classList.contains("hidden")) return "evaluacion_run";
  if(!viewEvaluacionConfig.classList.contains("hidden")) return "evaluacion_config";
  if(!viewAprendizaje.classList.contains("hidden")) return "aprendizaje";
  if(!viewInteraction.classList.contains("hidden")) return "interaction";
  if(!viewMenu.classList.contains("hidden")) return "menu";
  if(!viewRegister.classList.contains("hidden")) return "register";
  return "login";
}

function renderFrame(frameB64, videoEl, fallbackEl){
  if(frameB64){
    videoEl.src = "data:image/jpeg;base64," + frameB64;
    videoEl.style.display = "block";
    fallbackEl.style.display = "none";
  }else{
    videoEl.style.display = "none";
    fallbackEl.style.display = "grid";
  }
}

function syncLearningView(letter, progressText){
  const letterValue = (letter && letter.trim()) ? letter.trim().toUpperCase() : "A";
  const idx = LETTERS.indexOf(letterValue);
  const finalIndex = idx >= 0 ? idx : 0;
  const progressValue = progressText || `${finalIndex + 1}/${LETTERS.length}`;
  const placeholder = learningReferenceArt.querySelector(".reference-placeholder-text");

  learningLetter.textContent = letterValue;
  learningProgress.textContent = `${letterValue} — ${progressValue}`;

  const imageName = letterValue.toLowerCase();
  learningReferenceImage.src = `./assets/letras/${imageName}.png`;
  learningReferenceImage.alt = `Seña de la letra ${letterValue}`;
  learningReferenceImage.style.display = "block";
  placeholder.style.display = "none";
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
      if(currentView() === "login" || currentView() === "register"){
        setView("menu");
      }

      signText.value = st.sign_text || "";
      letterPill.textContent = "Letra: " + (st.letter || "-");

      if(currentView() !== "aprendizaje"){
        syncLearningView(st.letter || "A", "1/27");
      }

      renderFrame(st.frame_jpeg_b64, videoInteraction, videoFallbackInteraction);
      renderFrame(st.frame_jpeg_b64, videoAprendizaje, videoFallbackAprendizaje);
      // Si estamos en modo evaluación, actualizar video y letra detectada
      try{
        if(typeof videoEvaluacion !== 'undefined') renderFrame(st.frame_jpeg_b64, videoEvaluacion, videoFallbackEvaluacion);
      }catch(e){}

      try{
        if(typeof evalDetectedLetter !== 'undefined') evalDetectedLetter.textContent = st.letter || "-";
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
      if(["interaction", "menu", "aprendizaje"].includes(currentView())){
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
  $("loginUser").value = "";
  $("loginPass").value = "";
  setView("login");
};

$("btnLogoutMenu").onclick = async () => {
  await window.pywebview.api.logout();
  chat.innerHTML = "";
  setView("login");
};

$("btnOpenInteraction").onclick = () => setView("interaction");
$("btnOpenAprendizaje").onclick = () => {
  learningIndex = 0;
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

// Evaluación state
let evalTimerId = null;
let evalChangeId = null;
let evalRemaining = 0;
let evalScoreVal = 0;
let evalChangeInterval = 5; // segundos por letra
let evalUpcomingList = [];

function formatTimeSec(s){
  const mm = Math.floor(s/60).toString().padStart(2,'0');
  const ss = (s%60).toString().padStart(2,'0');
  return `${mm}:${ss}`;
}

function pickRandomLetter(){
  return LETTERS[Math.floor(Math.random()*LETTERS.length)];
}

function renderUpcoming(){
  evalUpcoming.innerHTML = '';
  for(const l of evalUpcomingList.slice(0,10)){
    const el = document.createElement('div');
    el.className = 'pill';
    el.style.padding = '6px 10px';
    el.textContent = l;
    evalUpcoming.appendChild(el);
  }
}

async function startEvaluationWithDuration(seconds){
  // prepare
  evalRemaining = seconds;
  evalScoreVal = 0;
  evalUpcomingList = [];
  evalTime.textContent = 'Tiempo: ' + formatTimeSec(evalRemaining);
  evalScore.textContent = 'Puntaje: ' + evalScoreVal;
  evalRequestedLetter.textContent = '-';
  renderUpcoming();

  setView('evaluacion_run');

  // Generate initial upcoming letters
  const totalSteps = Math.ceil(seconds / evalChangeInterval);
  for(let i=0;i<totalSteps;i++) evalUpcomingList.push(pickRandomLetter());
  renderUpcoming();

  // show first requested
  evalRequestedLetter.textContent = evalUpcomingList.shift() || '-';
  renderUpcoming();

  // Change requested letter periodically
  evalChangeId = setInterval(() => {
    evalRequestedLetter.textContent = evalUpcomingList.shift() || pickRandomLetter();
    // refill upcoming so list remains populated
    evalUpcomingList.push(pickRandomLetter());
    renderUpcoming();
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
  evalUpcomingList = [];
  renderUpcoming();
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

