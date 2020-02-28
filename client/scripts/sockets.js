
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
  console.log("sending: " + m);
  ws.send(m);
}

function beginSocket() {
  // handler for socket open
  playerID = Number.parseInt(getCookie("playerID"));
  gameID = Number.parseInt(getCookie("gameID"));
  if (Number.isNaN(playerID)) { playerID = -1; }
  if (Number.isNaN(gameID)) { gameID = -1; }
  var lastID = {
    type: "lastID",
    playerID: playerID,
    gameID: gameID
  };
  sendMessage(lastID);
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
      setCookie("playerID", r.playerID, 1);
      setCookie("gameID", r.gameID, 1);
      setID(r.playerID);
    break;
    case "playerstate":
      if (r.name) { setName(r.name); }
      if (r.color) { setTeamRole("team", r.color); }
      if (r.role) { setTeamRole("role", r.role); }
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
        updateRoom(r.players);
      }
    break;
    default:
      console.log("unknown message " + r.type);
  }
}


function setID(id) {
  PLAYERID = id;
  if (PLAYERID == 0) {
    var start_container = document.getElementById("start_container");
    start_container.className = "";
  }
}
