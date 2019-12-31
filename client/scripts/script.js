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
  if (r.type === "test") {
    alert("test!");
  }
  else if (r.type === "update") {
    var container = document.getElementById("tableContainer");
    var table = document.createElement("table");
    let j = r.words.length;
    console.log(j);
    while (j > 0) {
      var tr = document.createElement("tr");
      for (var i = 0; i < 5; i++) {
        var td = document.createElement("td");
        var outer = document.createElement("div");
        var inner = document.createElement("div");
        inner.classList.add("content");
        inner.innerText = r.words[j];
        outer.classList.add("box");
        outer.appendChild(inner);
        td.appendChild(outer);
        tr.appendChild(td);
        j--;
      }
      table.appendChild(tr);
    }
    container.appendChild(table);
  }
}

function sendMessage(msg) {
  // simple send
  ws.send(msg);
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

function beginSocket() {
  // empty begin handler
}

function initializeEvents() {
  // Set up the event handlers
}

// xhr sample
// function loadFields() {
//   var xhr = new XMLHttpRequest();
//   xhr.onreadystatechange = function()
//   {
//     if(this.readyState == 4 && this.status == 200)
//     {
//       var r = JSON.parse(xhr.responseText);
//       addFields(r.values);
//     }
//   };
//   xhr.open("GET", "v1/fields/", true);
//   xhr.send();
// }

// Page init
window.addEventListener("load", init, false);
