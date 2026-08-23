import React, { useEffect, useState } from 'react';
import { X, Cpu, Layers, Brain, CheckCircle2, AlertCircle, Play } from 'lucide-react';
import { AgentDetails } from '../types';

interface AgentInspectorModalProps {
  agentName: string | null;
  onClose: () => void;
  onTestPrompt?: (prompt: string) => void;
}

export const AgentInspectorModal: React.FC<AgentInspectorModalProps> = ({
  agentName,
  onClose,
  onTestPrompt,
}) => {
  const [details, setDetails] = useState<AgentDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!agentName) return;

    setLoading(true);
    setError('');
    fetch(`/api/agents/${encodeURIComponent(agentName)}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setDetails(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [agentName]);

  if (!agentName) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '640px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={18} color="#00ff88" />
            <h2 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff' }}>
              Inspect Agent Architecture: {agentName}
            </h2>
          </div>
          <button className="icon-btn-mini" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#7e8b9b' }}>
              Extracting neural graph & intent vectors...
            </div>
          ) : error ? (
            <div style={{ background: 'rgba(255,71,87,0.15)', padding: '12px', borderRadius: '8px', color: '#ff6b81' }}>
              Error inspecting agent: {error}
            </div>
          ) : details ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', gap: '12px' }}>
                <div style={{ flex: 1, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', padding: '12px' }}>
                  <div style={{ fontSize: '0.72rem', color: '#7e8b9b', marginBottom: '4px' }}>TRAINING STATUS</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.9rem', fontWeight: 600, color: details.is_trained ? '#00ff88' : '#ffaa00' }}>
                    {details.is_trained ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                    {details.is_trained ? 'Trained (Online)' : 'Untrained'}
                  </div>
                </div>

                <div style={{ flex: 1, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', padding: '12px' }}>
                  <div style={{ fontSize: '0.72rem', color: '#7e8b9b', marginBottom: '4px' }}>INTENTS & PATTERNS</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.9rem', fontWeight: 600, color: '#00d9ff' }}>
                    <Layers size={16} />
                    {details.intent_count} Intents ({details.total_patterns ?? details.intents.length} Patterns)
                  </div>
                </div>
              </div>

              {/* Intents & Registered Triggers */}
              <div>
                <div className="form-label" style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Layers size={14} color="#00d9ff" /> INTENT BLOCKS & TRIGGER PHRASES
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {details.intents.map((tag) => {
                    const patterns = details.patterns_map?.[tag] || [];
                    const responses = details.responses_map?.[tag] || [];
                    return (
                      <div
                        key={tag}
                        style={{
                          background: 'rgba(0, 217, 255, 0.05)',
                          border: '1px solid rgba(0, 217, 255, 0.2)',
                          borderRadius: '8px',
                          padding: '10px 12px',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                          <span style={{ color: '#00d9ff', fontWeight: 600, fontSize: '0.82rem', fontFamily: 'Fira Code, monospace' }}>
                            #{tag}
                          </span>
                          <span style={{ fontSize: '0.72rem', color: '#7e8b9b' }}>
                            {patterns.length} pattern(s)
                          </span>
                        </div>

                        {patterns.length > 0 && (
                          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginBottom: '6px' }}>
                            {patterns.map((pat, idx) => (
                              <button
                                key={idx}
                                style={{
                                  background: 'rgba(0, 255, 136, 0.1)',
                                  border: '1px solid rgba(0, 255, 136, 0.3)',
                                  color: '#00ff88',
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  cursor: 'pointer',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                }}
                                title="Click to test this prompt"
                                onClick={() => {
                                  if (onTestPrompt) {
                                    onTestPrompt(pat);
                                    onClose();
                                  }
                                }}
                              >
                                <Play size={10} /> {pat}
                              </button>
                            ))}
                          </div>
                        )}

                        {responses.length > 0 && (
                          <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontStyle: 'italic' }}>
                            Replies: "{responses.join('", "')}"
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Working Memory */}
              <div>
                <div className="form-label" style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Brain size={14} color="#9d4edd" /> SESSION MEMORY BUFFER ({details.memory.length} turns)
                </div>
                {details.memory.length === 0 ? (
                  <div style={{ fontSize: '0.8rem', color: '#7e8b9b', fontStyle: 'italic', padding: '4px 0' }}>
                    No interaction history cached in active memory yet.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '160px', overflowY: 'auto' }}>
                    {details.memory.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'rgba(255,255,255,0.02)',
                          border: '1px solid rgba(255,255,255,0.06)',
                          borderRadius: '6px',
                          padding: '8px',
                          fontSize: '0.78rem',
                        }}
                      >
                        <div style={{ color: '#00d9ff' }}>User: {item.user}</div>
                        <div style={{ color: '#00ff88', marginTop: '2px' }}>Bot: {item.bot}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
