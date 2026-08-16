const $ = (id) => document.getElementById(id);

const viewLogin = $("viewLogin");
const viewRegister = $("viewRegister");
const viewMenu = $("viewMenu");
const viewInteraction = $("viewInteraction");
const viewAprendizaje = $("viewAprendizaje");

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
}

function currentView(){
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
$("btnPrevAprendizaje").onclick = () => moveLearning(-1);
$("btnNextAprendizaje").onclick = () => moveLearning(1);

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

