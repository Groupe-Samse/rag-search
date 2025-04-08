function checkEnter(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

document.addEventListener("DOMContentLoaded", elastic_button);
document.addEventListener("DOMContentLoaded", opensearch_button);
document.addEventListener("DOMContentLoaded", create_and_deploy_agent);
document.addEventListener("DOMContentLoaded", delete_agent);
document.addEventListener("DOMContentLoaded", override_prompt);
document.addEventListener("DOMContentLoaded", display_fine_tune);
document.addEventListener("DOMContentLoaded", display_prompt);

function sendMessage() {
    let userInput = document.getElementById("user-input");
    let chatBox = document.getElementById("chat-box");

    if (userInput.value.trim() === "") return;

    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = userInput.value;
    chatBox.appendChild(userMessage);

    let userText = userInput.value;

    setTimeout(() => {
        let botMessage = document.createElement("div");
        botMessage.classList.add("message", "bot");
        botMessage.textContent = "Je réfléchis...";
        chatBox.appendChild(botMessage);

        fetchResponse(userText).then(response => {
            let messageText = response.message;
            let isError = response.isError;

            if (isError) {
                botMessage.classList.add("error");
            }
            botMessage.textContent = ""
            const html = marked.parse(messageText);
            botMessage.innerHTML = html;
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

function override_prompt() {
    let logOutput = document.getElementById("log-output");
    document.getElementById("override-prompt").addEventListener("click", function() {
        document.getElementById("popup").style.display = "flex";
    });

    document.getElementById("close-popup").addEventListener("click", function() {
        document.getElementById("popup").style.display = "none";
    });

    document.getElementById("submit-prompt").addEventListener("click", function() {
        const userPrompt = document.getElementById("user-prompt").value;
        let resultDiv = document.getElementById("result-message")

        if (userPrompt) {
            resultDiv.innerText = "Prompt soumis avec succès.";
            resultDiv.style.color = "green";
            popup.style.display = "none";
            fetch("/override_prompt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: userPrompt })
            })
            .then(response => response.json())
            .then(data => {
                logOutput.innerText = JSON.stringify(data, null, 2);
            })
        .catch(error => {
            logOutput.innerText = "Erreur : " + error;
        });
        } else {
            resultDiv.innerText = "Veuillez entrer un texte.";
            resultDiv.style.color = "red";
        }
    });
}

function create_and_deploy_agent() {
    let logOutput = document.getElementById("log-output");
    let fetchButton = document.getElementById("create-agent");

    fetchButton.replaceWith(fetchButton.cloneNode(true));

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

    document.getElementById("delete-agent").addEventListener("click", function() {
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

function display_fine_tune() {
    let logOutput = document.getElementById("log-output-default-data");
    let fetchButton = document.getElementById("display-fine-tune");

    fetchButton.replaceWith(fetchButton.cloneNode(true));

    document.getElementById("display-fine-tune").addEventListener("click", function() {
        fetch("display_fine_tune", {
            method: "GET",
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

function display_prompt() {
    let logOutput = document.getElementById("log-output-default-data");
    let fetchButton = document.getElementById("display-prompt");

    fetchButton.replaceWith(fetchButton.cloneNode(true));

    document.getElementById("display-prompt").addEventListener("click", function() {
        fetch("display_prompt", {
            method: "GET",
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
