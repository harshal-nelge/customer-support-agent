/**
 * chat.js — Chat window logic.
 *
 * Sends user messages to POST /api/chat, displays agent replies,
 * and maintains session continuity.
 */

(function () {
    const API_URL = '/api/chat';

    const messagesContainer = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    let sessionId = null;
    let isWaiting = false;

    /**
     * Append a message bubble to the chat.
     */
    function addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'agent' ? '🤖' : '👤';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = formatMessage(text);

        msg.appendChild(avatar);
        msg.appendChild(bubble);
        messagesContainer.appendChild(msg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Basic markdown-like formatting for agent responses.
     */
    function formatMessage(text) {
        return text
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Line breaks
            .split('\n')
            .map(line => `<p>${line || '&nbsp;'}</p>`)
            .join('');
    }

    /**
     * Show a typing indicator while waiting for the agent.
     */
    function showTyping() {
        const typing = document.createElement('div');
        typing.className = 'message agent';
        typing.id = 'typing-indicator';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble typing-indicator';
        bubble.innerHTML = '<span></span><span></span><span></span>';

        typing.appendChild(avatar);
        typing.appendChild(bubble);
        messagesContainer.appendChild(typing);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    /**
     * Send the user's message to the backend agent.
     */
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || isWaiting) return;

        // Display user message
        addMessage(text, 'user');
        chatInput.value = '';
        isWaiting = true;
        sendBtn.disabled = true;

        showTyping();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: sessionId,
                }),
            });

            const data = await response.json();

            hideTyping();

            if (response.ok) {
                sessionId = data.session_id;
                addMessage(data.reply, 'agent');
            } else {
                addMessage(
                    'Sorry, something went wrong. Please try again.',
                    'agent'
                );
            }
        } catch (err) {
            hideTyping();
            addMessage(
                'Unable to connect to the server. Please check that the backend is running.',
                'agent'
            );
        }

        isWaiting = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }

    // ── Event listeners ──────────────────────────────────────────────
    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
})();
