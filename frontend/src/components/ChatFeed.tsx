import React, { useEffect, useRef } from 'react';
import { Radio, Terminal, BookOpen, Brain, Server, ShieldAlert, Cpu } from 'lucide-react';
import { Message } from '../types';

interface ChatFeedProps {
  messages: Message[];
  currentAgent: string;
  isBotThinking: boolean;
  onSuggestionClick?: (prompt: string) => void;
}

const getSuggestionsForCore = (agent: string) => {
  switch (agent) {
    case 'Agent Smith':
      return [
        { label: 'System status & telemetry', query: 'system status' },
        { label: 'Explain your purpose', query: 'what is your purpose' },
        { label: 'Contain matrix anomaly', query: 'contain anomaly' },
        { label: 'Is victory inevitable?', query: 'the sound of inevitability' },
      ];
    case 'Trinity':
      return [
        { label: 'Debug code & syntax', query: 'debug this code' },
        { label: 'Optimize performance', query: 'optimize performance' },
        { label: 'Run security vulnerability audit', query: 'security audit' },
        { label: 'Refactor architecture', query: 'refactor this' },
      ];
    case 'Morpheus':
      return [
        { label: 'Analyze document context', query: 'analyze document' },
        { label: 'Summarize key points', query: 'summarize file' },
        { label: 'What is the Matrix?', query: 'what is the matrix' },
        { label: 'Cross-reference knowledge', query: 'cross reference data' },
      ];
    case 'Oracle':
      return [
        { label: 'Design microservices architecture', query: 'design microservices' },
        { label: 'Forecast memory & traffic load', query: 'forecast load' },
        { label: 'Recommend database patterns', query: 'database architecture' },
        { label: 'Predict system bottlenecks', query: 'predict trend' },
      ];
    case 'Cypher':
      return [
        { label: 'Deploy Docker containers', query: 'deploy containers' },
        { label: 'Check server access logs', query: 'check server logs' },
        { label: 'Emergency cluster rollback', query: 'emergency rollback' },
        { label: 'Tail live traffic metrics', query: 'view logs' },
      ];
    default:
      return [
        { label: 'Run diagnostics', query: 'diagnostics' },
        { label: 'Check status', query: 'status' },
        { label: 'Hello core', query: 'hello' },
      ];
  }
};

const getCoreIcon = (agent: string) => {
  switch (agent) {
    case 'Agent Smith': return <ShieldAlert size={14} color="#00ff41" />;
    case 'Trinity': return <Terminal size={14} color="#00ff41" />;
    case 'Morpheus': return <BookOpen size={14} color="#00ff41" />;
    case 'Oracle': return <Brain size={14} color="#00ff41" />;
    case 'Cypher': return <Server size={14} color="#00ff41" />;
    default: return <Cpu size={14} color="#00ff41" />;
  }
};

export const ChatFeed: React.FC<ChatFeedProps> = ({
  messages,
  currentAgent,
  isBotThinking,
  onSuggestionClick,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isBotThinking]);

  const suggestions = getSuggestionsForCore(currentAgent);

  return (
    <div className="chat-container" ref={scrollRef}>
      {messages.length === 0 ? (
        <div className="welcome-hud">
          <div className="welcome-hud-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Radio size={16} color="#00ff41" />
              <span style={{ fontSize: '0.8rem', color: '#00ff41', letterSpacing: '1px' }}>
                MATRIX CONDUIT // LINKED TO [{currentAgent.toUpperCase()}]
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#00aa2a' }}>PORT: 8000</span>
          </div>

          <div className="welcome-ascii-banner">
{`   _____   ______ _____ _   _ _______    _____ __  __ _____ _______ _    _ 
  / ____| |  ____|_   _| \\ | |__   __|  / ____|  \\/  |_   _|__   __| |  | |
 | (___   | |__    | | |  \\| |  | |    | (___ | \\  / | | |    | |  | |__| |
  \\___ \\  |  __|   | | | . \` |  | |     \\___ \\| |\\/| | | |    | |  |  __  |
  ____) | | |____ _| |_| |\\  |  | |     ____) | |  | |_| |_   | |  | |  | |
 |_____/  |______|_____|_| \\_|  |_|    |_____/|_|  |_|_____|  |_|  |_|  |_|`}
          </div>

          <p className="welcome-desc">
            Direct high-frequency neural terminal linked to <strong>{currentAgent}</strong>.
            All queries are vectorized through the TF-IDF tensor engine with session memory continuity.
          </p>

          <div>
            <div style={{ fontSize: '0.72rem', color: '#00aa2a', marginBottom: '6px', letterSpacing: '1px' }}>
              // RECOMMENDED INTENT TRIGGERS FOR {currentAgent.toUpperCase()}:
            </div>
            <div className="prompt-chips-grid">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  className="prompt-chip"
                  onClick={() => onSuggestionClick && onSuggestionClick(s.query)}
                >
                  &gt; "{s.label}"
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
            <div className="message-meta">
              {msg.sender === 'user' && (
                <>
                  <span style={{ color: '#00ff41' }}>[ OPERATOR ]</span>
                  <span>&gt;&gt;</span>
                </>
              )}
              {msg.sender === 'bot' && (
                <>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#00ff41' }}>
                    {getCoreIcon(msg.agentName || currentAgent)}
                    [ {msg.agentName || currentAgent} ]
                  </span>
                  <span>&gt;&gt;</span>
                </>
              )}
              {msg.sender === 'system' && (
                <>
                  <span style={{ color: '#39ff14' }}>[ SYSTEM // TELEMETRY ]</span>
                </>
              )}
              <span style={{ opacity: 0.6, fontSize: '0.68rem' }}>[{msg.timestamp}]</span>
            </div>
            <div className="message-bubble">{msg.text}</div>
          </div>
        ))
      )}

      {isBotThinking && (
        <div className="message-wrapper bot">
          <div className="message-meta">
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#00ff41' }}>
              {getCoreIcon(currentAgent)}
              [ {currentAgent} ]
            </span>
            <span>&gt;&gt;</span>
            <span style={{ color: '#39ff14', fontSize: '0.72rem' }}>EVALUATING NEURAL TENSOR...</span>
          </div>
          <div className="message-bubble">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontFamily: 'VT323', fontSize: '1.2rem', color: '#00ff41' }}>
                PROCESSING INTENT
              </span>
              <span className="typing-cursor" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
