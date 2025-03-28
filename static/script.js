function checkEnter(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

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
            typeWriter(botMessage, response);
        });

        chatBox.scrollTop = chatBox.scrollHeight; // Scroll vers le bas
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
        return data.response;
    } catch (error) {
        console.error("Erreur de connexion :", error);
        return "Erreur de connexion au serveur.";
    }
}

// Effet machine à écrire
function typeWriter(element, text, i = 0, step = 3, speed = 20) {
    if (i < text.length) {
        element.textContent += text.substring(i, i + step); // Ajoute plusieurs caractères à la fois
        setTimeout(() => typeWriter(element, text, i + step, step, speed), speed);
    }
}

function elastic_button() {
    let logOutput = document.getElementById("log-output");
    console.log(logOutput.style.display);

    if (logOutput.style.display === "none" || logOutput.style.display === "") {
        logOutput.style.display = "block";
    } else {
        logOutput.style.display = "none";
    }

    document.getElementById("fetch-data").addEventListener("click", function() {
    fetch("/download_from_elastic", {
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("log-output").innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        document.getElementById("log-output").innerText = "Erreur : " + error;
    });
});
}

function opensearch_button() {
    let logOutput = document.getElementById("log-opensearch-output");
    console.log(logOutput.style.display);

    if (logOutput.style.display === "none" || logOutput.style.display === "") {
        logOutput.style.display = "block";
    } else {
        logOutput.style.display = "none";
    }

    document.getElementById("upload-data").addEventListener("click", function() {
    fetch("/upload_to_opensearch", {
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("log-opensearch-output").innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        document.getElementById("log-opensearch-output").innerText = "Erreur : " + error;
    });
});
}

function create_and_deploy_agent() {
    let logOutput = document.getElementById("log-agent-output");
    console.log(logOutput.style.display);

    if (logOutput.style.display === "none" || logOutput.style.display === "") {
        logOutput.style.display = "block";
    } else {
        logOutput.style.display = "none";
    }

    document.getElementById("create-agent").addEventListener("click", function() {
    fetch("/create_and_deploy_agent", {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("log-agent-output").innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        document.getElementById("log-agent-output").innerText = "Erreur : " + error;
    });
});
}
