const $ = (id) => document.getElementById(id);

const viewLogin = $("viewLogin");
const viewRegister = $("viewRegister");
const viewInteraction = $("viewInteraction");

const loginError = $("loginError");
const regError = $("regError");
const voiceError = $("voiceError");

const chat = $("chat");
const video = $("video");
const videoFallback = $("videoFallback");
const letterPill = $("letterPill");
const signText = $("signText");
const btnLogout = $("btnLogout");

let pollTimer = null;
let recording = false;
let lastLoggedIn = null;

function setView(name){
  viewLogin.classList.toggle("hidden", name !== "login");
  viewRegister.classList.toggle("hidden", name !== "register");
  viewInteraction.classList.toggle("hidden", name !== "interaction");
}

function currentView(){
  if(!viewInteraction.classList.contains("hidden")) return "interaction";
  if(!viewRegister.classList.contains("hidden")) return "register";
  return "login";
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
      if(viewInteraction.classList.contains("hidden")){
        setView("interaction");
      }

      signText.value = st.sign_text || "";
      letterPill.textContent = "Letra: " + (st.letter || "-");

      if(st.frame_jpeg_b64){
        video.src = "data:image/jpeg;base64," + st.frame_jpeg_b64;
        video.style.display = "block";
        videoFallback.style.display = "none";
      }else{
        video.style.display = "none";
        videoFallback.style.display = "grid";
      }

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
      if(currentView() === "interaction"){
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

function startPolling(){
  if(pollTimer) return;
  pollTimer = setInterval(poll, 220);
  poll();
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

