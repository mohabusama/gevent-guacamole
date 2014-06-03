// Get display div from document
var display = document.getElementById("display");

// Instantiate client, using an HTTP tunnel for communications.
var guac = new Guacamole.Client(
    new Guacamole.WebSocketTunnel("/ws/")
);

// Add client to display div
display.appendChild(guac.getDisplay());

// Error handler
guac.onerror = function(error) {
    console.log(error);
};

// Connect
guac.connect();

// Disconnect on close
window.onunload = function() {
    guac.disconnect();
}

// Mouse
var mouse = new Guacamole.Mouse(guac.getDisplay());

mouse.onmousedown =
mouse.onmouseup   =
mouse.onmousemove = function(mouseState) {
    guac.sendMouseState(mouseState);
};

// Keyboard
var keyboard = new Guacamole.Keyboard(document);

keyboard.onkeydown = function (keysym) {
    guac.sendKeyEvent(1, keysym);
};

keyboard.onkeyup = function (keysym) {
    guac.sendKeyEvent(0, keysym);
};
