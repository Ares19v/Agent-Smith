import React from 'react';
import {
  Plus,
  Info,
  Trash2,
  Code2,
  Layout,
  Database,
  Server,
  ShieldCheck,
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
    case 'Coder':
      return { tag: 'DEV', role: 'Algorithms & Code Logic', icon: <Code2 size={15} /> };
    case 'Frontend Dev':
      return { tag: 'UI', role: 'React 18, CSS & Client Arch', icon: <Layout size={15} /> };
    case 'Backend Dev':
      return { tag: 'API', role: 'FastAPI, SQL & Auth Services', icon: <Database size={15} /> };
    case 'DevOps Engineer':
      return { tag: 'OPS', role: 'Docker, CI/CD & Deployments', icon: <Server size={15} /> };
    case 'Security Analyst':
      return { tag: 'SEC', role: 'Vulnerability Audits & Defense', icon: <ShieldCheck size={15} /> };
    default:
      return { tag: 'CUSTOM', role: 'Custom Neural Routine', icon: <Cpu size={15} /> };
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
            alt="Agent Smith Matrix Avatar"
            className="smith-avatar-img"
            onError={(e) => {
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
          <span className="smith-avatar-tag">ORCHESTRATION SENTINEL // v2.0</span>
        </div>

        <div className="logo-block">
          <div>
            <h1 className="logo-title">AGENT SMITH</h1>
            <p className="logo-sub">[ AI DEVELOPER PLATFORM ]</p>
          </div>
          <Activity size={18} color="#00ff41" />
        </div>
      </div>

      <div className="agent-list-section">
        <div className="section-label">
          <span>// SPECIALIZED DEV CORES</span>
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
                  <div style={{ fontSize: '0.66rem', color: isActive ? '#a3e635' : '#007711' }}>
                    [{meta.tag}] {meta.role}
                  </div>
                </div>
              </div>

              <div className="agent-actions" onClick={(e) => e.stopPropagation()}>
                <button
                  className="icon-btn-mini"
                  title="Inspect Core Intent Architecture"
                  onClick={() => onOpenInspectModal(agent)}
                >
                  <Info size={13} />
                </button>
                {agent !== 'Coder' && agent !== 'Frontend Dev' && agent !== 'Backend Dev' && agent !== 'DevOps Engineer' && agent !== 'Security Analyst' && (
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

      {/* Telemetry Summary */}
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
          <span>// ENGINE TELEMETRY</span>
          <span>4.80 THz</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>MEMORY BUFFER:</span>
          <span style={{ color: '#00ff41' }}>512 MB / 8 GB</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>STATUS:</span>
          <span style={{ color: '#00ff41' }}>5 CORES ACTIVE</span>
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="btn-matrix" onClick={onOpenCreateModal}>
          <Plus size={15} /> [ Deploy Custom Core ]
        </button>
      </div>
    </aside>
  );
};
