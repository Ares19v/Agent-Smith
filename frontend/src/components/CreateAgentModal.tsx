import React, { useState } from 'react';
import { X, Code, Sliders, Terminal } from 'lucide-react';

interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateAgent: (data: { name: string; patterns: string; responses: string }) => Promise<void>;
  onCreateAgentRaw: (data: { name: string; json_data: any }) => Promise<void>;
}

export const CreateAgentModal: React.FC<CreateAgentModalProps> = ({
  isOpen,
  onClose,
  onCreateAgent,
  onCreateAgentRaw,
}) => {
  const [isJsonMode, setIsJsonMode] = useState(false);
  const [name, setName] = useState('');
  const [patterns, setPatterns] = useState('');
  const [responses, setResponses] = useState('');
  const [rawJson, setRawJson] = useState(
    JSON.stringify(
      {
        intents: [
          {
            tag: 'debug',
            patterns: ['debug my app', 'find bugs', 'check runtime errors'],
            responses: ['Analyzing neural stack trace and memory matrix...'],
          },
        ],
      },
      null,
      2
    )
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    if (!name.trim()) {
      setErrorMsg('Core designation is required.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (isJsonMode) {
        let parsed;
        try {
          parsed = JSON.parse(rawJson);
        } catch (err) {
          throw new Error('Invalid JSON format. Check syntax.');
        }
        await onCreateAgentRaw({ name: name.trim(), json_data: parsed });
      } else {
        if (!patterns.trim() || !responses.trim()) {
          throw new Error('Trigger patterns and responses are required.');
        }
        await onCreateAgent({
          name: name.trim(),
          patterns: patterns.trim(),
          responses: responses.trim(),
        });
      }
      onClose();
      setName('');
      setPatterns('');
      setResponses('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to compile neural agent weights.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Terminal size={16} color="#00ff41" />
            <h2 style={{ fontSize: '1rem', fontFamily: 'VT323', letterSpacing: '1.5px', color: '#00ff41' }}>
              [ DEPLOY NEW NEURAL CORE ]
            </h2>
          </div>
          <button className="icon-btn-mini" onClick={onClose}>
            <X size={15} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '2px' }}>
              <button
                type="button"
                className="btn-matrix-secondary"
                style={{ fontSize: '0.75rem', padding: '3px 8px' }}
                onClick={() => setIsJsonMode(!isJsonMode)}
              >
                {isJsonMode ? (
                  <>
                    <Sliders size={12} /> [ Switch to Standard Form ]
                  </>
                ) : (
                  <>
                    <Code size={12} /> [ Switch to Raw JSON ]
                  </>
                )}
              </button>
            </div>

            {errorMsg && (
              <div style={{ background: 'rgba(255, 51, 68, 0.15)', border: '1px solid #ff3344', color: '#ff6677', padding: '6px 10px', fontSize: '0.8rem' }}>
                ! ERROR: {errorMsg}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">// CORE DESIGNATION (NAME)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. SentryBot"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            {!isJsonMode ? (
              <>
                <div className="form-group">
                  <label className="form-label">// TRIGGER PATTERNS (COMMA SEPARATED)</label>
                  <textarea
                    className="form-textarea"
                    rows={2}
                    placeholder="e.g. review code, check errors, fix bug"
                    value={patterns}
                    onChange={(e) => setPatterns(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">// CORE RESPONSES (COMMA SEPARATED)</label>
                  <textarea
                    className="form-textarea"
                    rows={2}
                    placeholder="e.g. Diagnostics initialized..., Memory nominal."
                    value={responses}
                    onChange={(e) => setResponses(e.target.value)}
                    required
                  />
                </div>
              </>
            ) : (
              <div className="form-group">
                <label className="form-label">// RAW INTENT JSON DEFINITION</label>
                <textarea
                  className="form-textarea"
                  style={{ fontFamily: 'VT323, monospace', fontSize: '0.95rem', color: '#00ff41', background: '#010502' }}
                  rows={8}
                  value={rawJson}
                  onChange={(e) => setRawJson(e.target.value)}
                  required
                />
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-matrix-secondary" onClick={onClose}>
              [ CANCEL ]
            </button>
            <button type="submit" className="btn-matrix" disabled={isSubmitting}>
              {isSubmitting ? '[ TRAINING CORE... ]' : '[ COMPILE & DEPLOY ]'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
