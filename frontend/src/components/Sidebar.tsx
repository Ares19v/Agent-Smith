import React from 'react';
import {
  Plus,
  Info,
  Trash2,
  ShieldAlert,
  Terminal,
  BookOpen,
  Brain,
  Server,
  Activity,
  Cpu,
} from 'lucide-react';

interface SidebarProps {
  agents: string[];
  currentAgent: string;
  onSelectAgent: (agent: string) => void;
  onOpenCreateModal: () => void;
  onOpenInspectModal: (agentName: string) => void;
  onDeleteAgent: (agentName: string) => void;
}

const getCoreMeta = (name: string) => {
  switch (name) {
    case 'Agent Smith':
      return { tag: 'PRIME', role: 'Matrix Sentinel & Orchestrator', icon: <ShieldAlert size={14} /> };
    case 'Trinity':
      return { tag: 'DEV', role: 'Code Execution & Exploit Debugger', icon: <Terminal size={14} /> };
    case 'Morpheus':
      return { tag: 'RAG', role: 'Document Intelligence & Knowledge', icon: <BookOpen size={14} /> };
    case 'Oracle':
      return { tag: 'ARCH', role: 'System Architecture & Predictor', icon: <Brain size={14} /> };
    case 'Cypher':
      return { tag: 'OPS', role: 'DevOps, Docker & Infrastructure', icon: <Server size={14} /> };
    default:
      return { tag: 'CUSTOM', role: 'Neural Sub-Routine', icon: <Cpu size={14} /> };
  }
};

export const Sidebar: React.FC<SidebarProps> = ({
  agents,
  currentAgent,
  onSelectAgent,
  onOpenCreateModal,
  onOpenInspectModal,
  onDeleteAgent,
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="smith-avatar-box">
          <img
            src="/smith_matrix.jpg"
            alt="Agent Smith Matrix Portrait"
            className="smith-avatar-img"
            onError={(e) => {
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
          <span className="smith-avatar-tag">PRIME MATRIX SENTINEL // v2.0</span>
        </div>

        <div className="logo-block">
          <div>
            <h1 className="logo-title">AGENT SMITH</h1>
            <p className="logo-sub">[ NEURAL COMMAND MATRIX ]</p>
          </div>
          <Activity size={18} color="#00ff41" />
        </div>
      </div>

      <div className="agent-list-section">
        <div className="section-label">
          <span>// SYNCHRONIZED CORES</span>
          <span>[{agents.length}]</span>
        </div>

        {agents.map((agent) => {
          const isActive = agent === currentAgent;
          const meta = getCoreMeta(agent);

          return (
            <div
              key={agent}
              className={`agent-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectAgent(agent)}
            >
              <div className="agent-item-content">
                <span className="agent-prefix">{isActive ? '►' : '▫'}</span>
                <span style={{ color: isActive ? '#00ff41' : '#00aa2a' }}>{meta.icon}</span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{agent}</div>
                  <div style={{ fontSize: '0.65rem', color: isActive ? '#a3e635' : '#007711' }}>
                    [{meta.tag}] {meta.role}
                  </div>
                </div>
              </div>

              <div className="agent-actions" onClick={(e) => e.stopPropagation()}>
                <button
                  className="icon-btn-mini"
                  title="Inspect Neural Intent Map"
                  onClick={() => onOpenInspectModal(agent)}
                >
                  <Info size={13} />
                </button>
                {agent !== 'Agent Smith' && agent !== 'Trinity' && agent !== 'Morpheus' && agent !== 'Oracle' && agent !== 'Cypher' && (
                  <button
                    className="icon-btn-mini danger"
                    title="Purge Core from Registry"
                    onClick={() => onDeleteAgent(agent)}
                  >
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Live System Telemetry Box */}
      <div
        style={{
          margin: '0 10px 10px 10px',
          border: '1px solid var(--matrix-border-dim)',
          background: 'rgba(0, 15, 5, 0.9)',
          padding: '8px 10px',
          fontSize: '0.68rem',
          color: '#00aa2a',
          fontFamily: 'VT323, monospace',
          letterSpacing: '1px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#00ff41', marginBottom: '2px' }}>
          <span>// MATRIX TELEMETRY</span>
          <span>4.80 THz</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>MEMORY BUFFER:</span>
          <span style={{ color: '#00ff41' }}>512 MB / 8 GB</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>ANOMALY DETECTOR:</span>
          <span style={{ color: '#00ff41' }}>0 THREATS</span>
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="btn-matrix" onClick={onOpenCreateModal}>
          <Plus size={15} /> [ Deploy Neural Core ]
        </button>
      </div>
    </aside>
  );
};
