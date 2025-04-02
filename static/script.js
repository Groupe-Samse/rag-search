function checkEnter(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

document.addEventListener("DOMContentLoaded", elastic_button);
document.addEventListener("DOMContentLoaded", opensearch_button);
document.addEventListener("DOMContentLoaded", create_and_deploy_agent);
document.addEventListener("DOMContentLoaded", delete_agent);

function sendMessage() {
    let userInput = document.getElementById("user-input");
    let chatBox = document.getElementById("chat-box");

    if (userInput.value.trim() === "") return;

    // Ajout du message utilisateur
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = userInput.value;
    chatBox.appendChild(userMessage);

    let userText = userInput.value;

    // Simuler une réponse du bot avec animation
    setTimeout(() => {
        let botMessage = document.createElement("div");
        botMessage.classList.add("message", "bot");
        chatBox.appendChild(botMessage);

        fetchResponse(userText).then(response => {
            let messageText = response.message;
            let isError = response.isError;

            if (isError) {
                botMessage.classList.add("error");
            }

            typeWriter(botMessage, messageText);
        });

        chatBox.scrollTop = chatBox.scrollHeight;
    }, 1000);

    userInput.value = "";
}

async function fetchResponse(userText) {
    try {
        let response = await fetch("/get_response", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userText })
        });

        let data = await response.json();
        if (data.error) {
            return { message: data.error, isError: true };
        }
        return { message: data.response, isError: false };
    } catch (error) {
        console.error("Erreur de connexion :", error);
        return "Erreur de connexion au serveur.";
    }
}

// Effet machine à écrire
function typeWriter(element, text, i = 0, step = 3, speed = 20) {
    if (i < text.length) {
        element.textContent += text.substring(i, i + step);
        setTimeout(() => typeWriter(element, text, i + step, step, speed), speed);
    }
}

function elastic_button() {
    let logOutput = document.getElementById("log-output");
    let fetchButton = document.getElementById("fetch-data");

    fetchButton.replaceWith(fetchButton.cloneNode(true));
    fetchButton = document.getElementById("fetch-data");

    fetchButton.addEventListener("click", function() {
        logOutput.innerText = "Chargement...";

        fetch("/download_from_elastic", {
            method: "GET"
        })
        .then(response => response.json())
        .then(data => {
            logOutput.innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            logOutput.innerText = "Erreur : " + error;
        });
    });
}

function opensearch_button() {
    let logOutput = document.getElementById("log-output");
    let fetchButton = document.getElementById("upload-data");

    fetchButton.replaceWith(fetchButton.cloneNode(true));
    fetchButton = document.getElementById("upload-data");

    fetchButton.addEventListener("click", function() {
        logOutput.innerText = "Chargement...";
        fetch("/upload_to_opensearch", {
            method: "GET"
        })
        .then(response => response.json())
        .then(data => {
            logOutput.innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            logOutput.innerText = "Erreur : " + error;
        });
    });
}

function create_and_deploy_agent() {
    let logOutput = document.getElementById("log-output");
    let fetchButton = document.getElementById("create-agent");

    fetchButton.replaceWith(fetchButton.cloneNode(true));
    fetchButton = document.getElementById("create-agent");

    document.getElementById("create-agent").addEventListener("click", function() {
        logOutput.innerText = "Chargement...";
    fetch("/create_and_deploy_agent", {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        logOutput.innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        logOutput.innerText = "Erreur : " + error;
    });
});
}

function delete_agent() {
    let logOutput = document.getElementById("log-output");
    let fetchButton = document.getElementById("delete-agent");

    fetchButton.replaceWith(fetchButton.cloneNode(true));
    fetchButton = document.getElementById("delete-agent");

    document.getElementById("delete-agent").addEventListener("click", function() {
        logOutput.innerText = "Chargement...";
    fetch("delete_agent", {
        method: "DELETE",
    })
    .then(response => response.json())
    .then(data => {
        logOutput.innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        logOutput.innerText = "Erreur : " + error;
    });
});
}
