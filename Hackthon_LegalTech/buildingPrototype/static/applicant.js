document.addEventListener('DOMContentLoaded', () => {
    const dialogueBox = document.getElementById('dialogue-box');
    const userInput = document.getElementById('user-input');
    const submitButton = document.getElementById('submit-button');

    function appendMessage(message, sender) {
        const messageElement = document.createElement('p');
        messageElement.classList.add(`${sender}-message`);
        messageElement.textContent = message;
        dialogueBox.appendChild(messageElement);
        dialogueBox.scrollTop = dialogueBox.scrollHeight;
    }

    async function sendMessageToAI(question) {
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // Replace "Your predefined context" with actual context data
                body: JSON.stringify({ 
                    question: question, 
                    context: "Your predefined context" 
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            appendMessage(data.answer || "No answer found.", 'ai');
        } catch (error) {
            appendMessage("Error: Unable to reach AI server.", 'ai');
            console.error(error);
        }
    }

    submitButton.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (message) {
            appendMessage(message, 'user');
            userInput.value = '';
            sendMessageToAI(message);
        }
    });

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            submitButton.click();
        }
    });
});
