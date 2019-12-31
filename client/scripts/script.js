// Initialization
function init() {
  // call these routines when the page has finished loading
  initializeEvents();
  initializeSocket();
  sendMessage("hello!");
}

// global for all the input elements for probe data
var dataElements = [];

// global variable for the WebSocket
var ws;

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
  // console.log(msg);
  var r = JSON.parse(msg);
  if (r.type == "test") {
    alert("test!");
  }
}

function sendMessage(msg) {
  // simple send
  ws.send(msg);
}

function endSocket() {
  // ask the user to reload the page if the socket is lost
  if (confirm("Lost connection to server. Reload page?")) {
    location.reload(true);
  }
}

function beginSocket() {
  // empty begin handler
}

function initializeEvents() {
  // Set up the event handlers
}

// xhr sample
function loadFields()
{
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function()
  {
    if(this.readyState == 4 && this.status == 200)
    {
      var r = JSON.parse(xhr.responseText);
      addFields(r.values);
    }
  };
  xhr.open("GET", "v1/fields/", true);
  xhr.send();
}

// Page init
window.addEventListener("load", init, false);
