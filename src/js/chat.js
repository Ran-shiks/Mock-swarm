// Get DOM elements
let typingForm, chatContainer, suggestions, toggleThemeButton, deleteChatButton;

// State variables
let userMessage = null;
let isResponseGenerating = false;

// Predefined responses
const predefinedResponses = {
    "hi": "Hello! How may I assist you?",
    "hello": "Hello! How may I assist you?",
    "hello there": "Hello! How may I assist you?",
    "how are you": "I'm doing well, thank you for asking!",
    "what's your name?": "I'm Mega-Bot, your friendly AI assistant!",
    "tell me a joke": "Why don't scientists trust atoms? Because they make up everything!",
    "what is your purpose?": "My purpose is to assist you with information and tasks to the best of my ability.",
    "can you help me with my homework?": "I can certainly try! What subject are you working on?",
    "what is the weather like today?": "I don't have access to real-time weather data, but I can suggest a weather website.",
    "what is the capital of France?": "The capital of France is Paris.",
    "what programming languages do you know?": "I have knowledge of JavaScript, Python, Java, and many others.",
    "write javascript code to sum all elements in an array.": `
function sumArray(arr) {
    let sum = 0;
    for (let i = 0; i < arr.length; i++) {
        sum += arr[i];
    }
    return sum;
}
    `
};

// Load theme from local storage on page load
const loadThemeFromLocalstorage = () => {
    const isLightMode = (localStorage.getItem("themeColor") === "light_mode");
    document.body.classList.toggle("light_mode", isLightMode);
    toggleThemeButton.innerText = isLightMode ? "dark_mode" : "light_mode";
};

// Create a new message element and return it
const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
};

// Show typing effect by displaying words one by one
const showTypingEffect = (text, textElement, incomingMessageDiv) => {
    const words = text.split(' ');
    let currentWordIndex = 0;
    const typingInterval = setInterval(() => {
        textElement.innerText += (currentWordIndex === 0 ? '' : ' ') + words[currentWordIndex++];
        incomingMessageDiv.querySelector(".icon").classList.add("hide");
        if (currentWordIndex === words.length) {
            clearInterval(typingInterval);
            isResponseGenerating = false;
            incomingMessageDiv.querySelector(".icon").classList.remove("hide");
        }
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    }, 30);
};

// Show predefined response - with 1-second delay
const showPredefinedResponse = (incomingMessageDiv, textElement) => {
    setTimeout(() => {
        const normalizedUserMessage = userMessage.toLowerCase().trim();
        const response = predefinedResponses[normalizedUserMessage] || "I'm sorry, I don't have an answer for that yet. Please try another prompt.";
        showTypingEffect(response, textElement, incomingMessageDiv);
    }, 1000);
};

// Show a loading animation while waiting for the API response
const showLoadingAnimation = () => {
    const html = `<div class="message-content">
                    <img class="avatar" src="images/gemini.svg" alt="Gemini avatar">
                    <p class="text"></p>
                    <div class="loading-indicator">
                        <div class="loading-bar"></div>
                        <div class="loading-bar"></div>
                        <div class="loading-bar"></div>
                    </div>
                </div>
                <span onClick="copyMessage(this)" class="icon material-symbols-rounded">content_copy</span>`;
    const incomingMessageDiv = createMessageElement(html, "incoming", "loading");
    chatContainer.appendChild(incomingMessageDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    const textElement = incomingMessageDiv.querySelector(".text");

    showPredefinedResponse(incomingMessageDiv, textElement);
};

// Copy message text to the clipboard
const copyMessage = (copyButton) => {
    const messageText = copyButton.parentElement.querySelector(".text").innerText;
    navigator.clipboard.writeText(messageText);
    copyButton.innerText = "done";
    setTimeout(() => copyButton.innerText = "content_copy", 1000);
};

// Handle sending outgoing chat messages
const handleOutgoingChat = () => {
    userMessage = typingForm.querySelector(".typing-input").value.trim();
    if (!userMessage || isResponseGenerating) return;

    isResponseGenerating = true;

    const html = `<div class="message-content">
                    <img class="avatar" src="images/user.jpg" alt="User avatar">
                    <p class="text"></p>
                  </div>`;
    const outgoingMessageDiv = createMessageElement(html, "outgoing");
    outgoingMessageDiv.querySelector(".text").innerText = userMessage;
    chatContainer.appendChild(outgoingMessageDiv);

    typingForm.reset();
    document.body.classList.add("hide-header");
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    showLoadingAnimation();
};

// Initialize DOM elements
function initializeDOMElements() {
    typingForm = document.querySelector(".typing-form");
    chatContainer = document.querySelector(".chat-list");
    suggestions = document.querySelectorAll(".suggestion");
    toggleThemeButton = document.querySelector("#theme-toggle-button");
    deleteChatButton = document.querySelector("#delete-chat-button");
}

// Initialize DOM elements
function initializeDOMElements() {
    typingForm = document.querySelector(".typing-form");
    chatContainer = document.querySelector(".chat-list");
    suggestions = document.querySelectorAll(".suggestion");
    toggleThemeButton = document.querySelector("#theme-toggle-button");
    deleteChatButton = document.querySelector("#delete-chat-button");
}

// Export functions for use in HTML
export { handleOutgoingChat, showLoadingAnimation, copyMessage };

// Initialize everything when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    initializeDOMElements();
    
    // Load saved theme
    loadThemeFromLocalstorage();
    
    // Toggle between light and dark themes
    toggleThemeButton.addEventListener("click", () => {
        const isLightMode = document.body.classList.toggle("light_mode");
        localStorage.setItem("themeColor", isLightMode ? "light_mode" : "dark_mode");
        toggleThemeButton.innerText = isLightMode ? "dark_mode" : "light_mode";
    });

    // Delete all chats from local storage
    deleteChatButton.addEventListener("click", () => {
        // no operation
    });

    // Handle suggestion clicks
    suggestions.forEach(suggestion => {
        suggestion.addEventListener("click", () => {
            userMessage = suggestion.querySelector(".text").innerText;
            handleOutgoingChat();
        });
    });

    // Handle form submission
    typingForm.addEventListener("submit", (e) => {
        e.preventDefault();
        handleOutgoingChat();
    });
});