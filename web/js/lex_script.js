// lex client
var lexruntime = new AWS.LexRuntime();
var lexUserId = 'AIBot' + Date.now();

// set the focus to the input box
document.getElementById("wisdom").focus();

// welcome message
document.addEventListener("DOMContentLoaded", function (event) {
    showResponse("Hello! How can I help you?");
});

// bot request
function pushChat() {
    // if there is text to be sent...
    var wisdomText = document.getElementById('wisdom');
    if (wisdomText && wisdomText.value && wisdomText.value.trim().length > 0) {
        // disable input to show we're sending it
        var input_message = wisdomText.value.trim();
        wisdomText.value = 'Enviando...';
        wisdomText.disabled = true;

        showRequest(input_message);
        sendToBot(input_message);
    }
    // we always cancel form submission
    return false;
}

// send message to lex
function sendToBot(input_message) {
    var sessionAttributes = {};
    var params = {
        botAlias: 'prod',
        botName: 'AIBot',
        inputText: input_message,
        userId: lexUserId,
        sessionAttributes: sessionAttributes
    };

    lexruntime.postText(params, function (err, data) {
        if (err) {
            console.log(err, err.stack);
            showError('Error:  ' + err.message + ' (see console for details)')
        }
        if (data) {
            // capture the sessionAttributes for the next cycle
            sessionAttributes = data.sessionAttributes;
            // show response and/or error/dialog status
            showResponse(data.message);
        }
    });
}

// show user input chat box
function showRequest(user_input) {
    var conversationDiv = document.getElementById('conversation');
    var requestPara = document.createElement("P");
    requestPara.className = 'userRequest';
    requestPara.appendChild(document.createTextNode(user_input));
    conversationDiv.appendChild(requestPara);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

// show lex output chat box
function showResponse(lex_output) {
    var conversationDiv = document.getElementById('conversation');
    var responsePara = document.createElement("P");
    responsePara.className = 'lexResponse';
    if (lex_output) {
        lex_output = lex_output.replace(/&lt;/g, "<");
        lex_output = lex_output.replace(/&gt;/g, ">");
        responsePara.innerHTML = lex_output;
    }
    conversationDiv.appendChild(responsePara);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;

    // re-enable input
    var wisdomText = document.getElementById('wisdom');
    wisdomText.value = '';
    wisdomText.disabled = false;
    wisdomText.focus();
}

function showError(error_output) {
    var conversationDiv = document.getElementById('conversation');
    var errorPara = document.createElement("P");
    errorPara.className = 'lexError';
    errorPara.appendChild(document.createTextNode(error_output));
    conversationDiv.appendChild(errorPara);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}