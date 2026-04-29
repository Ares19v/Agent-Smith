const uiAgentList = document.getElementById('uiAgentList');
const chatHistory = document.getElementById('chatHistory');
const promptInput = document.getElementById('promptInput');
const mainWorkspace = document.querySelector('.main');

// --- CUSTOM DROPDOWN LOGIC ---
const dropdownSelected = document.getElementById('dropdownSelected');
const dropdownOptions = document.getElementById('agentDropdownOptions');
let currentAgent = "Coder"; // State variable for the selected agent

dropdownSelected.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdownOptions.classList.toggle('show');
    dropdownSelected.classList.toggle('open');
});

// Close dropdown if clicking anywhere else
window.addEventListener('click', () => {
    dropdownOptions.classList.remove('show');
    dropdownSelected.classList.remove('open');
});

promptInput.addEventListener('focus', () => mainWorkspace.classList.add('chat-active'));

// Modals
const createModal = document.getElementById('createModal');
const toggleMode = document.getElementById('toggleMode');
const standardInputs = document.getElementById('standardInputs');
const jsonEditorArea = document.getElementById('jsonEditorArea');
let isJsonMode = false;

document.getElementById('openModalBtn').onclick = () => createModal.style.display = 'flex';
document.getElementById('closeModalBtn').onclick = () => createModal.style.display = 'none';

toggleMode.onclick = (e) => {
    e.preventDefault();
    isJsonMode = !isJsonMode;
    if (isJsonMode) {
        standardInputs.style.display = 'none';
        jsonEditorArea.style.display = 'block';
        toggleMode.textContent = "Switch to Standard Mode";
        if (!document.getElementById('rawJsonInput').value) {
            document.getElementById('rawJsonInput').value = JSON.stringify({"intents": [{"tag": "greet", "patterns": ["hi", "hello"], "responses": ["Greetings."]}]}, null, 4);
        }
    } else {
        standardInputs.style.display = 'block';
        jsonEditorArea.style.display = 'none';
        toggleMode.textContent = "Switch to JSON Mode";
    }
};

document.getElementById('saveAgentBtn').onclick = async () => {
    let name, patterns, responses, payload;
    if (isJsonMode) {
        name = document.getElementById('agentNameJson').value;
        const rawJson = document.getElementById('rawJsonInput').value;
        if (!name || !rawJson) return alert("Designation and JSON required.");
        try {
            const parsed = JSON.parse(rawJson);
            payload = { name: name, json_data: parsed };
            await fetch('/api/agents/raw', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        } catch (err) { return alert("Invalid JSON syntax."); }
    } else {
        name = document.getElementById('agentName').value;
        patterns = document.getElementById('agentPatterns').value;
        responses = document.getElementById('agentResponses').value;
        if (!name || !patterns || !responses) return alert("Fields missing.");
        await fetch('/api/agents', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, patterns, responses }) });
    }
    createModal.style.display = 'none';
    fetchAgents(); 
};

// Auth
const signupBtn = document.getElementById('signupBtn');
const authModal = document.getElementById('authModal');
signupBtn.onclick = (e) => { e.preventDefault(); authModal.style.display = 'flex'; };
document.getElementById('closeAuthBtn').onclick = () => authModal.style.display = 'none';
document.getElementById('authToggle').onclick = (e) => {
    e.preventDefault();
    const isLogin = document.getElementById('authTitle').textContent === 'Sign Up';
    document.getElementById('authTitle').textContent = isLogin ? 'Log In' : 'Sign Up';
    document.getElementById('submitAuthBtn').textContent = isLogin ? 'Log In' : 'Sign Up';
    document.getElementById('authToggle').textContent = isLogin ? 'Sign up instead' : 'Log in instead';
};
document.getElementById('submitAuthBtn').onclick = () => {
    const email = document.getElementById('authEmail').value;
    if(!email) return alert("Enter email.");
    document.getElementById('submitAuthBtn').textContent = "Authenticating...";
    setTimeout(() => {
        authModal.style.display = 'none';
        const isLogin = document.getElementById('authTitle').textContent === 'Log In';
        document.getElementById('submitAuthBtn').textContent = isLogin ? 'Log In' : 'Sign Up';
        signupBtn.textContent = email;
        addMessage(`System: Authenticated as ${email}.`, 'system');
    }, 800);
};

// Data Fetching
async function fetchAgents() {
    const response = await fetch('/api/agents');
    const data = await response.json();
    uiAgentList.innerHTML = '';
    dropdownOptions.innerHTML = ''; // Clear custom options
    
    data.agents.forEach(agent => {
        // Sidebar list
        uiAgentList.innerHTML += `<div class="agent-item">${agent}</div>`;
        
        // Custom Dropdown list
        const opt = document.createElement('div');
        opt.className = 'dropdown-option';
        opt.textContent = agent;
        opt.onclick = () => {
            currentAgent = agent;
            dropdownSelected.innerHTML = `${agent} <span class="chevron">▼</span>`;
        };
        dropdownOptions.appendChild(opt);
    });

    // Ensure the UI matches the first available agent if our current is deleted/missing
    if(data.agents.length > 0 && !data.agents.includes(currentAgent)){
        currentAgent = data.agents[0];
        dropdownSelected.innerHTML = `${currentAgent} <span class="chevron">▼</span>`;
    }
}

function addMessage(text, sender) {
    mainWorkspace.classList.add('chat-active'); 
    const msg = document.createElement('div');
    msg.className = `msg ${sender}`;
    msg.textContent = text;
    chatHistory.appendChild(msg);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Upload
const uploadBtn = document.getElementById('uploadBtn');
const fileUpload = document.getElementById('fileUpload');
uploadBtn.onclick = () => fileUpload.click(); 
fileUpload.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    addMessage(`Uploading document: ${file.name}...`, 'user');
    const formData = new FormData();
    formData.append('file', file);
    try {
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();
        addMessage(`System: [${data.filename}] successfully parsed to context (${data.size} KB).`, 'system');
    } catch (err) { addMessage("System Error.", 'system'); }
    fileUpload.value = ''; 
};

// Voice
const micBtn = document.getElementById('micBtn');
let mediaRecorder; let audioChunks = []; let isRecording = false;
micBtn.onclick = async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = e => { audioChunks.push(e.data); };
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = []; 
                const formData = new FormData(); formData.append('audio', audioBlob, 'recording.webm');
                addMessage("Transcribing audio...", 'system');
                try {
                    const response = await fetch('/api/voice', { method: 'POST', body: formData });
                    const data = await response.json();
                    promptInput.value = data.text; 
                } catch (err) { addMessage("System Error.", 'system'); }
            };
            mediaRecorder.start(); isRecording = true; micBtn.classList.add('recording');
        } catch (err) { alert("Microphone access denied."); }
    } else {
        mediaRecorder.stop(); isRecording = false; micBtn.classList.remove('recording');
        mediaRecorder.stream.getTracks().forEach(track => track.stop()); 
    }
};

// Chat 
promptInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const text = promptInput.value.trim();
        if (!text) return;
        addMessage(text, 'user');
        promptInput.value = '';
        try {
            // Using the custom currentAgent state variable instead of the native select value
            const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ agent_name: currentAgent, message: text }) });
            const data = await response.json();
            addMessage(data.response, 'bot');
        } catch (err) { addMessage("System Error.", 'bot'); }
    }
});

fetchAgents();
