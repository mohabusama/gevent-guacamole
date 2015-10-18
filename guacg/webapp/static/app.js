/*
 * Copyright (C) 2014 - 2015 Mohab Usama
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

var guac = new GuacG.App('display', '/ws/');
var sessionId = null;

var connection_args = {
    width: window.innerWidth,
    height: window.innerHeight,

    /**
     * CONNECTION PROTOCOL AND BROWSER CAPABILITIES [OPTIONAL]
     */
    // protocol: 'rdp',
    // audio: [],
    // video: [],

    /**
     * SERVER CONNECTION DETAILS [OPTIONAL]
     */
    // hostname: '192.168.20.14',
    // port: 3389,
    // security: '',

    /**
     * CREDENTIALS and DOMAIN [OPTIONAL]
     */
    // username: 'user',
    // password: 'pass',
    // domain: 'AD-DOMAIN',

    /**
     * REMOTE APP [OPTIONAL]
     */
    // remote_app: 'notepad',
};

guac.start(connection_args);


/**
 * MENU HANDLERS
*/
$(document).ready(function() {

    $('#resume').click(function() {
        var $btn = $(this);

        if ($btn.attr('data-attr-status') == 'on') {
            sessionId = guac.sessionId;
            // We are pausing an active session.
            guac.pause();

            $btn.attr('data-attr-status', 'off');

            toggleResumeButton($btn, 'off');
        } else {

            guac = new GuacG.App('display', '/ws/');

            // resume session.
            guac.resume(sessionId, connection_args);

            $btn.attr('data-attr-status', 'on');
            toggleResumeButton($btn, 'on');
        }
    });

    function toggleResumeButton(btn, status) {
        var span = btn.children('span');

        if (status == 'on') {
            span.removeClass('glyphicon-play');
            span.addClass('glyphicon-pause');
        } else {
            span.removeClass('glyphicon-pause');
            span.addClass('glyphicon-play');
        }
    }

});
