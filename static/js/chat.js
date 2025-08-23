/**
 * AI Chat Assistant - Frontend JavaScript
 * Handles chat interface interactions and API communication
 */

class ChatApp {
    constructor() {
        this.messageInput = null;
        this.sendBtn = null;
        this.chatMessages = null;
        this.typingIndicator = null;
        this.clearChatBtn = null;
        this.toggleThemeBtn = null;
        this.aiRoleSelect = null;
        this.charCount = null;
        this.isLoading = false;
        this.isLoadingHistory = false;
        this.currentTheme = localStorage.getItem('theme') || 'light';
        
        // Initialize
        this.init();
    }
    
    init() {
        this.initElements();
        this.initEventListeners();
        this.initTheme();
        this.autoResizeTextarea();
        
        // Load chat history after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.loadChatHistory();
        }, 100);
    }
    
    initElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.toggleThemeBtn = document.getElementById('toggleThemeBtn');
        this.aiRoleSelect = document.getElementById('aiRoleSelect');
        this.charCount = document.getElementById('charCount');
    }
    
    initEventListeners() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        
        // UI control events
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        this.toggleThemeBtn.addEventListener('click', () => this.toggleTheme());
        this.aiRoleSelect.addEventListener('change', () => this.onRoleChange());
        
        // Focus input on page load
        this.messageInput.focus();
    }
    
    initTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateThemeIcon();
    }
    
    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    handleInputChange() {
        this.autoResizeTextarea();
        this.updateCharacterCount();
        this.updateSendButton();
    }
    
    autoResizeTextarea() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    updateCharacterCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;
        
        if (count > 1800) {
            this.charCount.style.color = 'var(--error-color)';
        } else if (count > 1500) {
            this.charCount.style.color = 'var(--warning-color)';
        } else {
            this.charCount.style.color = 'var(--text-muted)';
        }
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText || this.isLoading;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        console.log('Sending message:', message);
        
        // Clear input and update UI
        this.messageInput.value = '';
        this.handleInputChange();
        this.setLoading(true);
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            console.log('Calling chat API...');
            const response = await this.callChatAPI(message);
            console.log('API response received:', response);
            
            if (!response.streamed) { // Non-stream fallback
                if (response.response) {
                    this.addMessage('ai', response.response, response.role_name || 'AI Assistant');
                    console.log('AI message added to chat (non-stream)');
                } else {
                    throw new Error('Empty response from server');
                }
            } else {
                console.log('Streaming already rendered message');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage('ai', 'I apologize, but I encountered an error. Please try again.', 'AI Assistant');
            this.showError(`Failed to send message: ${error.message}`);
        } finally {
            this.hideTypingIndicator();
            this.setLoading(false);
            this.messageInput.focus();
        }
    }
    
    async callChatAPI(message) {
        const aiRole = this.aiRoleSelect.value;
        console.log('Calling API with role:', aiRole);

        // If streaming supported use SSE endpoint
        if (window.EventSource && !this.disableStreaming) {
            return await this.streamChat(message, aiRole);
        }

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    ai_role: aiRole
                })
            });

            console.log('Fetch response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('API error response:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data = await response.json();
            console.log('Parsed JSON data:', data);
            return data;

        } catch (error) {
            console.error('Network or parsing error:', error);
            throw error;
        }
    }

    async streamChat(message, aiRole) {
        return new Promise(async (resolve, reject) => {
            try {
                const response = await fetch('/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, ai_role: aiRole })
                });

                if (!response.ok || !response.body) {
                    reject(new Error('Streaming not supported'));
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';
                let aiDiv = null;
                let full = '';

                // Create placeholder message immediately (hide typing indicator)
                this.hideTypingIndicator();
                aiDiv = document.createElement('div');
                aiDiv.className = 'message-wrapper ai-message';
                aiDiv.innerHTML = `<div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="message-header"><span class="message-sender">AI Assistant</span><span class="message-time">${formatTime(new Date())}</span></div><div class="message-text" id="streamingText"><i class='fas fa-spinner fa-spin'></i> <span style='opacity:.6;'>Thinking...</span></div></div>`;
                this.chatMessages.appendChild(aiDiv);
                const streamingText = aiDiv.querySelector('#streamingText');
                this.scrollToBottom();

                const processLine = (line) => {
                    if (!line.startsWith('data:')) return;
                    const jsonStr = line.replace(/^data:\s*/, '');
                    if (!jsonStr) return;
                    try {
                        const payload = JSON.parse(jsonStr);
                        if (payload.error) {
                            streamingText.textContent = 'Error: ' + payload.error;
                            return;
                        }
                        if (payload.delta) {
                            full += payload.delta;
                            streamingText.innerHTML = this.formatMessage(full);
                            this.scrollToBottom();
                        }
                        if (payload.done) {
                            // Save final streamed message to localStorage
                            this.updateLocalStorage({ role: 'ai', content: payload.response || full, timestamp: new Date().toISOString() });
                            resolve({ response: payload.response || full, ai_role: payload.ai_role, role_name: payload.role_name, streamed: true });
                        }
                    } catch (e) {
                        console.warn('Bad JSON line', e, line);
                    }
                };

                const read = () => {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            processLine('data: {"done": true, "response": "' + full.replace(/"/g, '\\"') + '"}');
                            return;
                        }
                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split(/\n\n/);
                        buffer = lines.pop();
                        lines.forEach(processLine);
                        read();
                    }).catch(reject);
                };
                read();
            } catch (err) {
                reject(err);
            }
        });
    }
    
    addMessage(role, content, senderName = null) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message-wrapper ${role}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';
        
        const messageSender = document.createElement('span');
        messageSender.className = 'message-sender';
        messageSender.textContent = senderName || (role === 'user' ? 'You' : 'AI Assistant');
        
        const messageTime = document.createElement('span');
        messageTime.className = 'message-time';
        messageTime.textContent = formatTime(new Date());
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        
        // Process content for better formatting
        const formattedContent = this.formatMessage(content);
        messageText.innerHTML = formattedContent;
        
        messageHeader.appendChild(messageSender);
        messageHeader.appendChild(messageTime);
        
        messageContent.appendChild(messageHeader);
        messageContent.appendChild(messageText);
        
        messageWrapper.appendChild(avatar);
        messageWrapper.appendChild(messageContent);
        
        // Insert before typing indicator or at the end
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator && typingIndicator.style.display !== 'none') {
            this.chatMessages.insertBefore(messageWrapper, typingIndicator);
        } else {
            this.chatMessages.appendChild(messageWrapper);
        }
        
        console.log(`Message added: ${role} - ${content.substring(0, 50)}...`);
        
        // Save to localStorage (but only during normal chat, not during history loading)
        if (!this.isLoadingHistory) {
            const messageData = {
                role: role,
                content: content,
                timestamp: new Date().toISOString()
            };
            this.updateLocalStorage(messageData);
        }
        
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        let formatted = content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Handle code blocks
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        return formatted;
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.updateSendButton();
        
        if (loading) {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }
        
        try {
            const response = await fetch('/clear_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Remove all messages except welcome message
                const messages = this.chatMessages.querySelectorAll('.message-wrapper');
                messages.forEach((msg, index) => {
                    if (index > 0) { // Keep the welcome message
                        msg.remove();
                    }
                });
                
                // Clear localStorage
                localStorage.removeItem('chatHistory');
                console.log('Chat history cleared from localStorage');
            } else {
                throw new Error('Failed to clear chat');
            }
        } catch (error) {
            console.error('Clear chat error:', error);
            this.showError('Failed to clear chat. Please try again.');
        }
    }
    
    async loadChatHistory() {
        try {
            console.log('Loading chat history...');
            
            // First try to load from localStorage
            const localHistory = this.loadFromLocalStorage();
            if (localHistory && localHistory.length > 0) {
                console.log(`Loading ${localHistory.length} messages from localStorage`);
                this.displayMessages(localHistory);
                return;
            }
            
            // Fallback to server session if localStorage is empty
            const response = await fetch('/get_history');
            if (response.ok) {
                const data = await response.json();
                console.log('Chat history data from server:', data);
                
                // Set AI role
                if (data.ai_role) {
                    this.aiRoleSelect.value = data.ai_role;
                    console.log('Set AI role to:', data.ai_role);
                }
                
                // Load message history
                if (data.history && data.history.length > 0) {
                    console.log(`Loading ${data.history.length} messages from server`);
                    this.displayMessages(data.history);
                    // Save to localStorage for future refreshes
                    this.saveToLocalStorage(data.history);
                } else {
                    console.log('No chat history found on server');
                }
            } else {
                console.error('Failed to load chat history:', response.status);
            }
        } catch (error) {
            console.error('Load history error:', error);
        }
    }
    
    displayMessages(messages) {
        // Clear existing messages except welcome message
        const existingMessages = this.chatMessages.querySelectorAll('.message-wrapper');
        console.log(`Found ${existingMessages.length} existing messages`);
        existingMessages.forEach((msg, index) => {
            if (index > 0) { // Keep the welcome message (first message)
                msg.remove();
            }
        });
        
        // Set loading flag to prevent saving to localStorage during history restoration
        this.isLoadingHistory = true;
        
        // Add historical messages
        messages.forEach((msg, index) => {
            console.log(`Adding message ${index + 1}: ${msg.role} - ${msg.content.substring(0, 50)}...`);
            if (msg.role === 'user') {
                this.addMessage('user', msg.content);
            } else {
                this.addMessage('ai', msg.content);
            }
        });
        
        // Reset loading flag
        this.isLoadingHistory = false;
        
        // Scroll to bottom after loading history
        this.scrollToBottom();
        console.log('Messages displayed successfully');
    }
    
    saveToLocalStorage(messages) {
        try {
            const chatData = {
                messages: messages,
                timestamp: Date.now(),
                aiRole: this.aiRoleSelect.value
            };
            localStorage.setItem('chatHistory', JSON.stringify(chatData));
            console.log('Chat history saved to localStorage');
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    }
    
    loadFromLocalStorage() {
        try {
            const chatData = localStorage.getItem('chatHistory');
            if (chatData) {
                const parsed = JSON.parse(chatData);
                // Check if data is not too old (24 hours)
                const dayInMs = 24 * 60 * 60 * 1000;
                if (Date.now() - parsed.timestamp < dayInMs) {
                    if (parsed.aiRole) {
                        this.aiRoleSelect.value = parsed.aiRole;
                    }
                    return parsed.messages || [];
                } else {
                    // Remove old data
                    localStorage.removeItem('chatHistory');
                    console.log('Removed old chat history from localStorage');
                }
            }
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
            localStorage.removeItem('chatHistory');
        }
        return null;
    }
    
    updateLocalStorage(newMessage) {
        try {
            const existingData = this.loadFromLocalStorage() || [];
            existingData.push(newMessage);
            this.saveToLocalStorage(existingData);
        } catch (error) {
            console.error('Failed to update localStorage:', error);
        }
    }
    
    onRoleChange() {
        const selectedRole = this.aiRoleSelect.value;
        const selectedOption = this.aiRoleSelect.options[this.aiRoleSelect.selectedIndex];
        
        // Add a system message about role change
        this.addMessage('ai', `I've switched to ${selectedOption.text} mode. How can I help you in this capacity?`);
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.updateThemeIcon();
    }
    
    updateThemeIcon() {
        const icon = this.toggleThemeBtn.querySelector('i');
        if (this.currentTheme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
    
    showError(message) {
        const errorModal = document.getElementById('errorModal');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorModal.style.display = 'flex';
    }
}

// Utility functions
function formatTime(date) {
    return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function closeErrorModal() {
    document.getElementById('errorModal').style.display = 'none';
}

// Initialize app when DOM is loaded
let ChatAppInstance;

document.addEventListener('DOMContentLoaded', function() {
    ChatAppInstance = new ChatApp();
});

// Global app reference for external access
window.ChatApp = {
    init: function() {
        if (!ChatAppInstance) {
            ChatAppInstance = new ChatApp();
        }
        return ChatAppInstance;
    },
    getInstance: function() {
        return ChatAppInstance;
    }
};

// Handle page visibility change to refocus input
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && ChatAppInstance) {
        setTimeout(() => {
            ChatAppInstance.messageInput.focus();
        }, 100);
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    if (ChatAppInstance) {
        ChatAppInstance.scrollToBottom();
    }
});
