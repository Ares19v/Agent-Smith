import React, { useEffect, useRef } from 'react';

interface TelemetryWaveformProps {
  isThinking: boolean;
}

export const TelemetryWaveform: React.FC<TelemetryWaveformProps> = ({ isThinking }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let step = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Grid lines
      ctx.strokeStyle = 'rgba(0, 255, 65, 0.08)';
      ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 15) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 10) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      // Signal wave
      ctx.beginPath();
      ctx.strokeStyle = isThinking ? '#39ff14' : '#00ff41';
      ctx.lineWidth = isThinking ? 2 : 1.2;
      ctx.shadowColor = '#00ff41';
      ctx.shadowBlur = isThinking ? 8 : 4;

      const midY = canvas.height / 2;
      const speed = isThinking ? 0.08 : 0.03;
      const amplitude = isThinking ? 14 : 7;

      for (let x = 0; x < canvas.width; x++) {
        const freq1 = Math.sin((x * 0.05) + (step * speed * 2));
        const freq2 = Math.cos((x * 0.02) + (step * speed));
        const noise = (Math.random() - 0.5) * (isThinking ? 4 : 1.5);
        const y = midY + (freq1 * freq2 * amplitude) + noise;

        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      step++;
      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [isThinking]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <canvas
        ref={canvasRef}
        width={140}
        height={32}
        style={{
          border: '1px solid rgba(0, 255, 65, 0.3)',
          background: 'rgba(0, 10, 3, 0.8)',
        }}
      />
    </div>
  );
};
