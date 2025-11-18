const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.innerHTML = text.replace(/\n/g, "<br>");
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    addMessage(text, "user");
    userInput.value = "";

    try {
        const response = await fetch("http://localhost:8000/consultar-tramites", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ query: text })
});

const data = await response.json();

if (data.response && data.response.trim() !== "") {
    addMessage(data.response, "bot");
} else {
    addMessage("Lo siento, no tengo información suficiente en mi base de conocimiento para responder esa consulta.", "bot");
}


    } catch (error) {
        addMessage("Error al conectar con el servidor.", "bot");
    }
}

// Enviar mensaje con botón
sendBtn.addEventListener("click", sendMessage);

// Enviar con Enter
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

// Limpiar chat
clearBtn.addEventListener("click", () => {
    chatBox.innerHTML = "";
});
