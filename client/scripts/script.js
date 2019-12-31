// Initialization
function init() {
  // call these routines when the page has finished loading
  initializeEvents();
  initializeSocket();
}

// global for all the input elements for probe data
let dataElements = [];

// global letiable for the WebSocket
let ws;

// player id
let PLAYERID = 42;

function initializeSocket() {
  // Open the WebSocket and set up its handlers
  loc = "ws://" + location.host + "/ws";
  ws = new WebSocket(loc);
  ws.onopen = beginSocket;
  ws.onmessage = function(evt) { receiveMessage(evt.data) };
  ws.onclose = endSocket;
  ws.onerror = endSocket;
}

function receiveMessage(msg) {
  // receiveMessage is called when any message from the server arrives on the WebSocket
  console.log("recieved: " + msg);
  let r = JSON.parse(msg);
  processCommand(r);
}

function sendMessage(msg) {
  // simple send
  let m = JSON.stringify(msg);
  console.log("sending: " + m)
  ws.send(m);
}

function beginSocket() {
  // handler for socket open
}

function endSocket() {
  // ask the user to reload the page if the socket is lost
  if (confirm("Lost connection to server. Reload page?")) {
    location.reload(true);
  }
}

function processCommand(r) {
  switch(r.type) {
    case "test":
      console.log("test!");
    break;
    case "playerid":
      PLAYERID = r.value;
    break;
    case "board":
      updateBoard(r.spaces);
    break;
    case "turn":
      setTurn(r);
    break;
    default:
      console.log("unknown command " + r.type);
  }
}

function updateBoard(words) {
  let setup = document.getElementById("setup");
  setup.classList.add("hidden");
  let container = document.getElementById("table_container");
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }
  let table = document.createElement("table");
  let j = 0;
  while (j < words.length) {
    let tr = document.createElement("tr");
    for (let i = 0; i < 5; i++) {
      let w = words[j]
      let td = document.createElement("td");
      let outer = document.createElement("div");
      let inner = document.createElement("div");
      inner.classList.add("content");
      inner.innerText = "\xa0";
      if (w.visible) {
        inner.classList.add(w.color);
      }
      else {
        inner.classList.add("white");
        inner.innerText = w.word;
      }
      outer.classList.add("box");
      outer.appendChild(inner);
      td.appendChild(outer);
      tr.appendChild(td);
      inner.addEventListener("click", touchWord);
      j++;
    }
    table.appendChild(tr);
  }
  container.appendChild(table);
  let pass_container = document.getElementById("pass_container");
  pass_container.className = "";
}

function touchWord(e) {
  let msg = {
    type: "touch",
    player: PLAYERID,
    word: e.target.innerText
  };
  sendMessage(msg);
}

function passTurn() {
  let msg = {
    type: "pass",
    player: PLAYERID,
  };
  sendMessage(msg);
}

function initializeEvents() {
  // Set up the event handlers
  let red = document.getElementById("pick_red");
  let blue = document.getElementById("pick_blue");
  let codemaster = document.getElementById("pick_codemaster");
  let guesser = document.getElementById("pick_guesser");
  red.addEventListener("click", function() {
    red.classList.add("selected");
    blue.classList.remove("selected");
    setTeamRole("team", "red");
  });
  blue.addEventListener("click", function() {
    red.classList.remove("selected");
    blue.classList.add("selected");
    setTeamRole("team", "blue");
  });
  codemaster.addEventListener("click", function() {
    codemaster.classList.add("selected");
    guesser.classList.remove("selected");
    setTeamRole("role", "codemaster");
  });
  guesser.addEventListener("click", function() {
    codemaster.classList.remove("selected");
    guesser.classList.add("selected");
    setTeamRole("role", "guesser");
  });

  let start = document.getElementById("start");
  start.addEventListener("click", startGame);

  let name = document.getElementById("name");
  name.addEventListener("change", function() {
    setName(name.value);
  });

  let pass = document.getElementById("pass");
  pass.addEventListener("click", passTurn);
}

function setTeamRole(which, value) {
  if (which == "role") {
    let role_text = document.getElementById("role_text");
    role_text.innerText = value;
  }
  else {
    let bar = document.getElementById("bar");
    bar.className = "";
    bar.classList.add(value);
  }
  let msg = {
    type: "set",
    player: PLAYERID,
    which: which,
    value: value
  };
  sendMessage(msg);
}

function setName(name) {
  let name_text = document.getElementById("name_text");
  name_text.innerText = name;
  let msg = {
    type: "set",
    player: PLAYERID,
    which: "name",
    value: name
  };
  sendMessage(msg);
}

function setTurn(r) {
  let turn = document.getElementById("turn");
  turn.innerText = r.team + " Turn - " + r.touches + " guesses left"
  turn.className = "";
  turn.classList.add(r.team);
}

function startGame() {
  let msg = {
    type: "start",
    player: PLAYERID
  };
  sendMessage(msg);
}

// xhr sample
// function loadFields() {
//   let xhr = new XMLHttpRequest();
//   xhr.onreadystatechange = function()
//   {
//     if(this.readyState == 4 && this.status == 200)
//     {
//       let r = JSON.parse(xhr.responseText);
//       addFields(r.values);
//     }
//   };
//   xhr.open("GET", "v1/fields/", true);
//   xhr.send();
// }

// Page init
window.addEventListener("load", init, false);
