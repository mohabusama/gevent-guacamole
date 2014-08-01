/*
 * Copyright (C) 2014 Mohab Usama
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

 var GuacG = GuacG || {};

 GuacG.App = function(displayId, tunnelUri) {

    var app = this;

    var started = false,
        guacgClient = null,
        guacgTunnel = null,
        originalOnInstruction = null,
        display = null
        keyboard,
        mouse;

    var instructionHandlers = {

        'controlreq': function(parameters) {
            if (app.onControlReq) {
                onControlReq(parameters);
            }
        },

        'error': function(parameters) {

        },

        'guestjoined': function(parameters) {
            if (app.onGuestJoined) {
                app.onGuestJoined(parameters);
            }
        },

        'guestleft': function(parameters) {
            if (app.onGuestLeft) {
                app.onGuestLeft(parameters);
            }
        },
    };

    this.start = function(args) {

        display = document.getElementById(displayId);

        guacgTunnel = new Guacamole.WebSocketTunnel(tunnelUri);
        guacgClient = new Guacamole.Client(guacgTunnel);

        display.appendChild(guacgClient.getDisplay().getElement());

        // Connect
        guacgClient.connect();

        // Patch tunnel oninstruction to intercept GuacG custom instructions
        originalOnInstruction = guacgTunnel.oninstruction;
        guacgTunnel.oninstruction = app.oninstruction;

        // Send *custom* connection args
        var connectionArgs = args || {};
        app.send('args', JSON.stringify(connectionArgs))

        app.setHandlers();
    }

    this.pause = function(args) {
        var connectionArgs = args || {};

        // Pause/Save session
        app.send('pause', JSON.stringify(connectionArgs));
    }

    this.resume = function(sessionId, args) {
        var connectionArgs = args || {};

        connectionArgs.sessionId = sessionId;
        connectionArgs.resume = true;

        app.start(connectionArgs);
    }

    this.join = function(sessionId, args) {
        var connectionArgs = args || {};

        // SessionId to join
        connectionArgs.sessionId = sessionId;
        connectionArgs.guest = true;

        app.start(connectionArgs);
    }

    this.terminate = function() {
        if (! guacgClient) return;

        guacgClient.disconnect();
        started = false;
    }

    this.send = function(opcode, message) {
        guacgTunnel.sendMessage('guacg', opcode, message);
    }

    this.oninstruction = function(opcode, parameters) {
        if (opcode !== 'guacg') {
            return originalOnInstruction(opcode, parameters);
        }

        // This is actually our custom instruction
        var _opcode = parameters[0];
        if (_opcode in instructionHandlers) {
            parameters.splice(0, 1);
            instructionHandlers[_opcode](parameters);
        }
    }

    this.setHandlers = function() {

        // Default handlers
        window.onunload = function() {
            guacgClient.disconnect();
        }

        // Mouse
        mouse = new Guacamole.Mouse(guacgClient.getDisplay().getElement());

        mouse.onmousedown =
        mouse.onmouseup   =
        mouse.onmousemove = function(mouseState) {
            guacgClient.sendMouseState(mouseState);
        };

        // Keyboard
        keyboard = new Guacamole.Keyboard(document);

        keyboard.onkeydown = function (keysym) {
            guacgClient.sendKeyEvent(1, keysym);
        };

        keyboard.onkeyup = function (keysym) {
            guacgClient.sendKeyEvent(0, keysym);
        };
    }

    this.control = function() {
        app.send('control');
    }

    this.removeGuest = function(guestId, args) {
        var connectionArgs = args || {};

        connectionArgs.guestId = guestId;

        app.send('remove', JSON.stringify(connectionArgs));
    }

    this.controlGrant = function() {
        app.send('accept');
    }

    this.controlReject = function() {
        app.send('reject');
    }

    this.onControlReq = null;

    this.onGuestJoined = null;

    this.onGuestLeft = null;
 }

