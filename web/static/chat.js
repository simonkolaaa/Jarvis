const chatWindow = document.getElementById('chatWindow');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const btnLearn = document.getElementById('btnLearn');

// Auto-resize
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

if (btnLearn) {
    btnLearn.addEventListener('click', async function() {
        if(confirm("Indicizzare di nuovo i file?")) {
            try {
                const res = await fetch(`/api/learn/${BOT_ID}`, {method: 'POST'});
                const data = await res.json();
                alert(data.message || data.error);
            } catch(e) {
                alert("Errore di Sync con il server RAG.");
            }
        }
    });
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
        }[tag] || tag)
    );
}

function appendMessage(sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
    let avatarHtml = '';
    if (sender === 'user') {
        avatarHtml = `<i class="fa-solid fa-user"></i>`;
    } else {
        if (BOT_ID === 'linda') {
            avatarHtml = `<img src="/static/linda_avatar.jpg" alt="Linda">`;
        } else {
            avatarHtml = `<i class="fa-solid fa-robot"></i>`;
        }
    }
    
    msgDiv.innerHTML = `
        <div class="avatar">${avatarHtml}</div>
        <div class="bubble"><span class="content"></span></div>
    `;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    return msgDiv.querySelector('.content');
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Aggiungi utente
    const userSpan = appendMessage('user');
    userSpan.innerHTML = escapeHTML(text);
    
    userInput.value = '';
    userInput.style.height = 'auto';
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Crea placeholder bot animato
    const botSpan = appendMessage('system');
    botSpan.classList.add('typing-cursor');
    
    let markdownBuffer = "";

    try {
        const response = await fetch(`/api/chat/${BOT_ID}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunkText = decoder.decode(value, {stream: true});
            // Il formato SSE usa `data: {...}\n\n`
            const events = chunkText.split('\n\n');
            
            for (let ev of events) {
                if (ev.startsWith('data: ')) {
                    const dataStr = ev.replace('data: ', '').trim();
                    if (!dataStr) continue;
                    
                    if (dataStr === "{}") continue; // end signal

                    try {
                        const parsed = JSON.parse(dataStr);
                        if (parsed.error) {
                            markdownBuffer += `\n**Errore**: ${parsed.error}`;
                        } else if (parsed.chunk) {
                            markdownBuffer += parsed.chunk;
                        }
                    } catch (err) {
                        console.error("JSON parse fallito per payload: ", dataStr);
                    }
                    
                    // Render in tempo reale del Markdown usando Marked
                    botSpan.innerHTML = marked.parse(markdownBuffer);
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                }
            }
        }
    } catch (e) {
        botSpan.innerHTML = "❌ Connessione con il server smarrita.";
    } finally {
        botSpan.classList.remove('typing-cursor');
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}
