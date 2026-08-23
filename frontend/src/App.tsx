import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Paperclip,
  Mic,
  MicOff,
  Activity,
  Trash2,
  Download,
  Terminal,
} from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { ChatFeed } from './components/ChatFeed';
import { CreateAgentModal } from './components/CreateAgentModal';
import { AgentInspectorModal } from './components/AgentInspectorModal';
import { DocumentContextBadge } from './components/DocumentContextBadge';
import { MatrixRain } from './components/MatrixRain';
import { TelemetryWaveform } from './components/TelemetryWaveform';
import { Message, DocumentContextInfo } from './types';

export const App: React.FC = () => {
  const [agents, setAgents] = useState<string[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>('Agent Smith');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isBotThinking, setIsBotThinking] = useState(false);
  const [docContext, setDocContext] = useState<DocumentContextInfo>({
    filename: null,
    loaded: false,
  });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [inspectAgentName, setInspectAgentName] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);

  // Audio / Mic State
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Initial Load & Health Check
  useEffect(() => {
    fetchAgents();
    fetchHealth();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch('/api/agents');
      if (res.ok) {
        const data = await res.json();
        setAgents(data.agents || []);
        if (data.agents && data.agents.length > 0) {
          if (!data.agents.includes(currentAgent)) {
            setCurrentAgent(data.agents[0]);
          }
        }
      }
    } catch (err) {
      console.error('Failed to fetch agents:', err);
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        if (data.document_loaded && data.document_filename) {
          setDocContext({
            filename: data.document_filename,
            loaded: true,
          });
        }
      }
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const addMessage = (
    text: string,
    sender: 'user' | 'bot' | 'system',
    agentName?: string,
    isError?: boolean
  ) => {
    const newMsg: Message = {
      id: Math.random().toString(36).substring(2, 9),
      sender,
      text,
      agentName,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      isError,
    };
    setMessages((prev) => [...prev, newMsg]);
  };

  const sendMessageText = async (text: string) => {
    const query = text.trim();
    if (!query || isBotThinking) return;

    setInputMessage('');
    addMessage(query, 'user');
    setIsBotThinking(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: currentAgent,
          message: query,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Neural inference failed');
      }

      const data = await res.json();
      addMessage(data.response, 'bot', currentAgent);
    } catch (err: any) {
      addMessage(`Neural Link Error: ${err.message}`, 'system', undefined, true);
    } finally {
      setIsBotThinking(false);
    }
  };

  const handleSendMessage = () => {
    sendMessageText(inputMessage);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadProgress(35);
    addMessage(`[STREAMING DOCUMENT: ${file.name}]`, 'system');
    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadProgress(70);
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Document extraction failed');
      }

      setUploadProgress(100);
      const data = await res.json();
      setDocContext({
        filename: data.filename,
        loaded: true,
        size_kb: data.size_kb,
        preview: data.preview,
      });
      addMessage(
        `✓ [${data.filename}] indexed into matrix tensor (${data.size_kb} KB, ${data.chars_extracted} chars).`,
        'system'
      );
    } catch (err: any) {
      addMessage(`Upload Error: ${err.message}`, 'system', undefined, true);
    } finally {
      setTimeout(() => setUploadProgress(null), 500);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleClearContext = async () => {
    try {
      const res = await fetch('/api/context', { method: 'DELETE' });
      if (res.ok) {
        setDocContext({ filename: null, loaded: false });
        addMessage('Document matrix buffer purged from neural memory.', 'system');
      }
    } catch (err) {
      console.error('Failed to clear context:', err);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleExportChat = () => {
    if (messages.length === 0) return;
    const content = messages
      .map((m) => `[${m.timestamp}] ${m.sender.toUpperCase()} (${m.agentName || 'Agent Smith'}):\n${m.text}\n`)
      .join('\n---\n\n');
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `matrix-transcript-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleToggleVoice = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          stream.getTracks().forEach((track) => track.stop());

          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');
          addMessage('Audio received — streaming to voice engine...', 'system');

          try {
            const res = await fetch('/api/voice', {
              method: 'POST',
              body: formData,
            });
            const data = await res.json();
            if (data.text) {
              setInputMessage((prev) => (prev ? `${prev} ${data.text}` : data.text));
            }
          } catch (err: any) {
            addMessage(`Voice Pipeline Error: ${err.message}`, 'system', undefined, true);
          }
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        alert('Microphone access denied or unavailable.');
      }
    }
  };

  const handleCreateAgent = async (data: {
    name: string;
    patterns: string;
    responses: string;
  }) => {
    const res = await fetch('/api/agents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Creation failed');
    }
    await fetchAgents();
    setCurrentAgent(data.name);
    addMessage(`Agent core '${data.name}' deployed & neural weights loaded.`, 'system');
  };

  const handleCreateAgentRaw = async (data: { name: string; json_data: any }) => {
    const res = await fetch('/api/agents/raw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Raw deployment failed');
    }
    await fetchAgents();
    setCurrentAgent(data.name);
    addMessage(`Agent core '${data.name}' deployed from raw JSON structure.`, 'system');
  };

  const handleDeleteAgent = async (agentName: string) => {
    if (!confirm(`Permanently purge agent core '${agentName}'?`)) return;

    try {
      const res = await fetch(`/api/agents/${encodeURIComponent(agentName)}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        addMessage(`Agent core '${agentName}' purged from registry.`, 'system');
        await fetchAgents();
      }
    } catch (err) {
      console.error('Failed to delete agent:', err);
    }
  };

  return (
    <div className="app-container">
      {/* Matrix Rain Canvas */}
      <MatrixRain />

      <Sidebar
        agents={agents}
        currentAgent={currentAgent}
        onSelectAgent={(agent) => setCurrentAgent(agent)}
        onOpenCreateModal={() => setIsCreateModalOpen(true)}
        onOpenInspectModal={(name) => setInspectAgentName(name)}
        onDeleteAgent={handleDeleteAgent}
      />

      <main className="main-area">
        <header className="main-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div className="terminal-badge">
              <Terminal size={14} />
              <span>CORE: {currentAgent.toUpperCase()}</span>
            </div>

            <DocumentContextBadge
              context={docContext}
              onClearContext={handleClearContext}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Live Oscilloscope Waveform Telemetry */}
            <TelemetryWaveform isThinking={isBotThinking} />

            {messages.length > 0 && (
              <>
                <button
                  className="icon-btn-mini"
                  title="Export Transcript (.md)"
                  onClick={handleExportChat}
                >
                  <Download size={14} />
                </button>
                <button
                  className="icon-btn-mini danger"
                  title="Purge Terminal Log"
                  onClick={handleClearChat}
                >
                  <Trash2 size={14} />
                </button>
              </>
            )}

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.72rem',
                color: '#00ff41',
                border: '1px solid rgba(0,255,65,0.4)',
                padding: '2px 8px',
                background: 'rgba(0,255,65,0.06)',
                letterSpacing: '1px',
              }}
            >
              <Activity size={13} color="#00ff41" />
              <span>LINK: SECURE</span>
            </div>
          </div>
        </header>

        {/* Retro Downloading / Ingesting Progress Bar if uploading */}
        {uploadProgress !== null && (
          <div
            style={{
              background: 'rgba(0, 15, 5, 0.95)',
              borderBottom: '1px solid var(--matrix-green)',
              padding: '6px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontFamily: 'VT323, monospace',
              fontSize: '1rem',
              color: '#00ff41',
              zIndex: 20,
            }}
          >
            <span>INGESTING DOCUMENT STREAM...</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div className="retro-progress">
                {Array.from({ length: 20 }).map((_, i) => (
                  <div
                    key={i}
                    className="retro-progress-seg"
                    style={{
                      opacity: i < (uploadProgress / 100) * 20 ? 1 : 0.15,
                    }}
                  />
                ))}
              </div>
              <span>{uploadProgress}%</span>
            </div>
          </div>
        )}

        <ChatFeed
          messages={messages}
          currentAgent={currentAgent}
          isBotThinking={isBotThinking}
          onSuggestionClick={(prompt) => sendMessageText(prompt)}
        />

        <section className="input-section">
          <div className="input-box">
            <div className="input-line">
              <span className="prompt-symbol">&gt;</span>
              <textarea
                className="chat-textarea"
                placeholder={`Transmit command to [${currentAgent}] (Shift+Enter for newline)...`}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
              />
            </div>

            <div className="input-toolbar">
              <div className="toolbar-left">
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={handleFileUpload}
                  accept=".pdf,.txt,.docx"
                />
                <button
                  type="button"
                  className="btn-matrix-secondary"
                  onClick={() => fileInputRef.current?.click()}
                  title="Upload PDF/TXT/DOCX for Neural RAG Injection"
                >
                  <Paperclip size={13} /> [ Inject Doc ]
                </button>

                <button
                  type="button"
                  className={`btn-matrix-secondary ${isRecording ? 'recording' : ''}`}
                  onClick={handleToggleVoice}
                  title="Voice Input (STT)"
                  style={isRecording ? { color: '#ff3344', borderColor: '#ff3344' } : {}}
                >
                  {isRecording ? <MicOff size={13} /> : <Mic size={13} />}
                  {isRecording ? '[ Recording... ]' : '[ Voice ]'}
                </button>
              </div>

              <div className="toolbar-right">
                <button
                  className="send-btn"
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isBotThinking}
                  title="Transmit Command (Enter)"
                >
                  <Send size={14} /> TRANSMIT
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <CreateAgentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreateAgent={handleCreateAgent}
        onCreateAgentRaw={handleCreateAgentRaw}
      />

      <AgentInspectorModal
        agentName={inspectAgentName}
        onClose={() => setInspectAgentName(null)}
        onTestPrompt={(prompt) => sendMessageText(prompt)}
      />
    </div>
  );
};

export default App;
