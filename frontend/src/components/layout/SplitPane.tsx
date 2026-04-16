import { useState, useCallback, useRef, useEffect } from 'react';
import { GripVertical } from 'lucide-react';

interface SplitPaneProps {
  left: React.ReactNode;
  right: React.ReactNode;
  initialPosition?: number;
  minLeft?: number;
  minRight?: number;
  onPositionChange?: (position: number) => void;
}

export function SplitPane({
  left,
  right,
  initialPosition = 60,
  minLeft = 20,
  minRight = 20,
  onPositionChange,
}: SplitPaneProps) {
  const [position, setPosition] = useState(initialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const newPosition = ((e.clientX - rect.left) / rect.width) * 100;

      if (newPosition >= minLeft && newPosition <= 100 - minRight) {
        setPosition(newPosition);
        onPositionChange?.(newPosition);
      }
    },
    [isDragging, minLeft, minRight, onPositionChange]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div ref={containerRef} className="flex h-full w-full overflow-hidden">
      <div
        className="h-full overflow-auto border-r border-border"
        style={{ width: `${position}%` }}
      >
        {left}
      </div>

      <div
        className={`group relative flex w-2 cursor-col-resize items-center justify-center transition-colors ${
          isDragging ? 'bg-primary/20' : 'hover:bg-primary/10'
        }`}
        onMouseDown={handleMouseDown}
      >
        <div className="absolute inset-y-0 -left-1 -right-1 z-10" />
        <GripVertical
          className={`h-6 w-4 text-muted-foreground transition-colors ${
            isDragging ? 'text-primary' : 'group-hover:text-primary'
          }`}
        />
      </div>

      <div
        className="h-full overflow-auto"
        style={{ width: `${100 - position}%` }}
      >
        {right}
      </div>
    </div>
  );
}
