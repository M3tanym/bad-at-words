// Initialization
function init() {
  // call these routines when the page has finished loading
  initializeEvents();
  initializeSocket();
}

// global for all the input elements for probe data
var dataElements = [];

// global variable for the WebSocket
var ws;

// player id
var PLAYERID = 42;
var TEAM;
var ROLE;
var STARTED = false;
var OBSERVER = false;

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
  var r = JSON.parse(msg);
  processCommand(r);
}

function sendMessage(msg) {
  // simple send
  var m = JSON.stringify(msg);
  console.log("sending: " + m)
  ws.send(m);
}

function beginSocket() {
  // handler for socket open
}

function endSocket() {
  // ask the user to reload the page if the socket is lost
  // if (confirm("Lost connection to server. Reload page?")) {
  //   location.reload(true);
  // }
}

function processCommand(r) {
  switch(r.type) {
    case "playerid":
      setID(r.value);
    break;
    case "board":
      STARTED = true;
      updateBoard(r.spaces);
    break;
    case "visible":
      makeVisible(r.word);
    break;
    case "turn":
      if (STARTED) {
        updateTurn(r);
      }
    break;
    case "win":
      showWin(r);
    break;
    case "room":
      if (OBSERVER) {
        updateRoom(r);
      }
    break;
    default:
      console.log("unknown command " + r.type);
  }
}

function setID(id) {
  PLAYERID = id;
  if (PLAYERID == 0){
    var start_container = document.getElementById("start_container");
    start_container.className = "";
  }
}

function makeVisible(word) {
  var w = document.getElementById("_" + word + "_");
  w.className = "";
  w.classList.add("content");
  w.classList.add(w.name);
  w.classList.add("invis");
}

function showWin(r) {
  var banner = document.getElementById("banner");
  var banner_text = document.getElementById("banner_text");
  var banner_reason = document.getElementById("banner_reason");
  banner_text.innerText = r.team + " wins!";
  banner_reason.innerText = r.method;
  banner.className = "";
  banner.classList.add(r.team);
}

function updateRoom(r) {
  var setup = document.getElementById("setup");
  setup.classList.add("hidden");
  console.log(r);
}

function updateBoard(words) {
  var setup = document.getElementById("setup");
  setup.classList.add("hidden");
  var container = document.getElementById("table_container");
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }
  var table = document.createElement("table");
  var j = 0;
  while (j < words.length) {
    var tr = document.createElement("tr");
    for (var i = 0; i < 5; i++) {
      var w = words[j]
      var td = document.createElement("td");
      var outer = document.createElement("div");
      var inner = document.createElement("div");
      inner.classList.add("content");
      inner.id = "_" + w.word + "_";
      inner.innerText = w.word;
      inner.name = w.color;
      if (ROLE == "codemaster" || w.visible) {
        inner.classList.add(w.color);
      }
      else  {
        inner.classList.add("white");
        inner.addEventListener("click", touchWord);
      }

      if (w.visible) {
        inner.classList.add("invis");
      }

      outer.classList.add("box");
      outer.appendChild(inner);
      td.appendChild(outer);
      tr.appendChild(td);
      j++;
    }
    table.appendChild(tr);
  }
  container.appendChild(table);
}

function updateTurn(r) {
  var turn_text = document.getElementById("turn_text");
  var text = r.team + " turn - ";
  if (r.touches > 0) {
    text += r.touches + " guesses left";
  }
  else {
    text += "awaiting codemaster";
  }
  turn_text.innerText = text
  turn_text.className = "";
  turn_text.classList.add(r.team);
  setAgentsLeft(r.red, "red");
  setAgentsLeft(r.blue, "blue");

  var pass_container = document.getElementById("pass_container");
  var guess_container = document.getElementById("guess_container");
  if (r.team === TEAM) {
    if (ROLE == "codemaster") {
      guess_container.className = "";
    }
    else {
      pass_container.className = "";
    }
  }
  else {
    pass_container.classList.add("hidden");
    guess_container.classList.add("hidden");
  }
}

function touchWord(e) {
  var msg = {
    type: "touch",
    player: PLAYERID,
    word: e.target.innerText
  };
  sendMessage(msg);
}

function passTurn() {
  var msg = {
    type: "pass",
    player: PLAYERID,
  };
  sendMessage(msg);
}

function setTeamRole(which, value) {
  if (which === "role") {
    var role_text = document.getElementById("role_text");
    role_text.innerText = value;
    ROLE = value;
  }
  else if (which === "team") {
    var bar = document.getElementById("bar");
    bar.className = "";
    bar.classList.add(value);
    TEAM = value;
  }
  var msg = {
    type: "set",
    player: PLAYERID,
    which: which,
    value: value
  };
  sendMessage(msg);
}

function setName(name) {
  var name_text = document.getElementById("name_text");
  name_text.innerText = name;
  var msg = {
    type: "set",
    player: PLAYERID,
    which: "name",
    value: name
  };
  sendMessage(msg);
}

function setAgentsLeft(num, color) {
  var agents = document.getElementById(color + "agents");
  while (agents.childElementCount > num) {
    agents.removeChild(agents.firstChild);
  }
  while (agents.childElementCount < num) {
    agents.appendChild(generateAgent(color));
  }
}

function generateAgent(color) {
  let s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  let u = document.createElementNS("http://www.w3.org/2000/svg", "use");
  u.setAttributeNS("http://www.w3.org/1999/xlink", "xlink:href", "#agent");
  s.classList.add("agent");
  s.classList.add(color + "agent");
  s.appendChild(u);
  return s;
}

function startGame() {
  var start_container = document.getElementById("start_container");
  start_container.classList.add("hidden");
  var msg = {
    type: "start",
    player: PLAYERID
  };
  sendMessage(msg);
}

function submitGuesses(v) {
  var msg = {
    type: "submit",
    player: PLAYERID,
    value: v
  };
  sendMessage(msg);
}

function processChoice(e) {
  if (e.target.classList.contains("option_box")) {
    return;
  }
  var parent = e.target.parentElement.parentElement;
  var elem = e.target.parentElement;
  var value = e.target.getAttribute("name");
  var which = parent.getAttribute("name");

  for (var i = 0; i < parent.children.length; i++) {
    parent.children[i].classList.remove("selected");
  }
  elem.classList.add("selected");
  if (elem.id === "pick_observer") {
    OBSERVER = true;
  }
  else {
    setTeamRole(which, value);
  }
}

function initializeEvents() {
  // Set up the event handlers
  var red = document.getElementById("pick_red");
  var blue = document.getElementById("pick_blue");
  var codemaster = document.getElementById("pick_codemaster");
  var guesser = document.getElementById("pick_guesser");
  var observer = document.getElementById("pick_observer");
  red.addEventListener("click", processChoice);
  blue.addEventListener("click", processChoice);
  guesser.addEventListener("click", processChoice);
  codemaster.addEventListener("click", processChoice);
  observer.addEventListener("click", processChoice);

  var start = document.getElementById("start");
  start.addEventListener("click", startGame);

  var name = document.getElementById("name");
  name.addEventListener("change", function() {
    setName(name.value);
  });

  var pass = document.getElementById("pass");
  pass.addEventListener("click", passTurn);

  var guess = document.getElementById("guess");
  guess.addEventListener("click", function() {
    var num = document.getElementById("number").value * 1;
    submitGuesses(num);
  });
}

// Page init
window.addEventListener("load", init, false);
