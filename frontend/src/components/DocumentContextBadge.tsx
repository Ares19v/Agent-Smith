import React from 'react';
import { FileText, X } from 'lucide-react';
import { DocumentContextInfo } from '../types';

interface DocumentContextBadgeProps {
  context: DocumentContextInfo;
  onClearContext: () => void;
}

export const DocumentContextBadge: React.FC<DocumentContextBadgeProps> = ({
  context,
  onClearContext,
}) => {
  if (!context.loaded || !context.filename) return null;

  return (
    <div className="context-pill" title={context.preview || 'Active Document RAG Context'}>
      <FileText size={13} />
      <span>DOC: {context.filename}</span>
      <button className="context-close" onClick={onClearContext} title="Unload Document Context">
        <X size={13} />
      </button>
    </div>
  );
};
