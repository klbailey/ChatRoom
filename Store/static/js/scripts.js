// Store>static>js>scripts.js
document.addEventListener('DOMContentLoaded', function () {
    const chatLog = document.getElementById('chat-log');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Function to add a message to the chat log
    function appendMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = message;
        chatLog.appendChild(messageDiv);
    }

    // Function to send user input to the server and display the response
    async function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;
    
        // Add user message to chat log
        appendMessage(userMessage, 'user');
    
        // Send user input to server
        const response = await fetch('/chatbox/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken'), // Get CSRF token from cookie
            },
            body: `user_input=${encodeURIComponent(userMessage)}&prompt=Hello, GPT! ${userMessage}`,
        });
    
        if (response.ok) {
            const data = await response.json();
            const botResponse = data.response;
            appendMessage(botResponse, 'bot');
        } else {
            appendMessage('Error communicating with server', 'bot');
        }
    
        // Clear user input field
        userInput.value = '';
    }
    

    // Function to handle send button click
    sendBtn.addEventListener('click', sendMessage);

    // Function to handle enter key press in input field
    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Function to get CSRF token from cookie
    function getCookie(name) {
        const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
    }
});