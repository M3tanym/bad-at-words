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
var ROLE;
var words = [];

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
      words = r.spaces;
      updateBoard();
    break;
    case "visible":
      makeVisible(r.word);
    break;
    case "turn":
      updateTurn(r);
    break;
    case "win":
      showWin(r);
    break;
    default:
      console.log("unknown command " + r.type);
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

function updateBoard() {
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

  if (ROLE == "codemaster") {
    var guess_container = document.getElementById("guess_container");
    guess_container.className = "";
  }
  else {
    var pass_container = document.getElementById("pass_container");
    pass_container.className = "";
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

function initializeEvents() {
  // Set up the event handlers
  var red = document.getElementById("pick_red");
  var blue = document.getElementById("pick_blue");
  var codemaster = document.getElementById("pick_codemaster");
  var guesser = document.getElementById("pick_guesser");
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

function setTeamRole(which, value) {
  if (which == "role") {
    var role_text = document.getElementById("role_text");
    role_text.innerText = value;
    ROLE = value;
  }
  else {
    var bar = document.getElementById("bar");
    bar.className = "";
    bar.classList.add(value);
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

function updateTurn(r) {
  var turn_text = document.getElementById("turn_text");
  turn_text.innerText = r.team + " turn - " + r.touches + " guesses left"
  turn_text.className = "";
  turn_text.classList.add(r.team);
  var turn = document.getElementById("turn_text");
}

function startGame() {
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

// Page init
window.addEventListener("load", init, false);
