import React, { useEffect, useRef } from 'react';
import { Radio, Code2, Layout, Database, Server, ShieldCheck, Cpu } from 'lucide-react';
import { Message } from '../types';

interface ChatFeedProps {
  messages: Message[];
  currentAgent: string;
  isBotThinking: boolean;
  onSuggestionClick?: (prompt: string) => void;
}

const getSuggestionsForCore = (agent: string) => {
  switch (agent) {
    case 'Coder':
      return [
        { label: 'Write an algorithm function', query: 'write a function' },
        { label: 'Fix bugs & syntax errors', query: 'fix my code' },
        { label: 'Optimize runtime complexity', query: 'optimize performance' },
        { label: 'Explain code architecture', query: 'explain how this works' },
      ];
    case 'Frontend Dev':
      return [
        { label: 'Build React functional component', query: 'react component' },
        { label: 'Fix responsive CSS layout', query: 'fix css layout' },
        { label: 'Manage state with Hooks', query: 'state management' },
        { label: 'Optimize Vite bundle size', query: 'reduce bundle size' },
      ];
    case 'Backend Dev':
      return [
        { label: 'Create FastAPI REST endpoint', query: 'fastapi router' },
        { label: 'Optimize SQL database query', query: 'database query' },
        { label: 'Implement JWT authentication', query: 'jwt authentication' },
        { label: 'Setup Redis cache layer', query: 'redis caching' },
      ];
    case 'DevOps Engineer':
      return [
        { label: 'Write multi-stage Dockerfile', query: 'dockerfile' },
        { label: 'Configure GitHub Actions CI/CD', query: 'github actions' },
        { label: 'Check server access logs', query: 'check server logs' },
        { label: 'Deploy Kubernetes pods', query: 'kubernetes pod' },
      ];
    case 'Security Analyst':
      return [
        { label: 'Run security vulnerability audit', query: 'security audit' },
        { label: 'Prevent SQL injection & XSS', query: 'sql injection' },
        { label: 'Configure CORS & rate limiting', query: 'cors policy' },
        { label: 'Check OWASP Top 10 defenses', query: 'owasp top 10' },
      ];
    default:
      return [
        { label: 'Check core status', query: 'ready' },
        { label: 'Run diagnostics', query: 'diagnostics' },
        { label: 'Hello core', query: 'hello' },
      ];
  }
};

const getCoreIcon = (agent: string) => {
  switch (agent) {
    case 'Coder': return <Code2 size={14} color="#00ff41" />;
    case 'Frontend Dev': return <Layout size={14} color="#00ff41" />;
    case 'Backend Dev': return <Database size={14} color="#00ff41" />;
    case 'DevOps Engineer': return <Server size={14} color="#00ff41" />;
    case 'Security Analyst': return <ShieldCheck size={14} color="#00ff41" />;
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
                DEVELOPER CONDUIT // ACTIVE [{currentAgent.toUpperCase()}]
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
            Directly connected to <strong>{currentAgent}</strong>. Real-time NLP intent matching,
            session memory buffers, and RAG document grounding active.
          </p>

          <div>
            <div style={{ fontSize: '0.72rem', color: '#00aa2a', marginBottom: '6px', letterSpacing: '1px' }}>
              // QUICK INTENT PROMPTS FOR {currentAgent.toUpperCase()}:
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
            <span style={{ color: '#39ff14', fontSize: '0.72rem' }}>COMPUTING INFERENCE...</span>
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
