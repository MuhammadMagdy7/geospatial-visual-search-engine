import React from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { SearchMode } from '../../types/search';

const SearchModeToggle: React.FC = () => {
  const { searchMode, setSearchMode, settings, setSettings } = useSearchStore();

  const handleModeSwitch = (mode: SearchMode) => {
    setSearchMode(mode);
    // Adjust threshold defaults when switching modes
    if (mode === 'text_search' && settings.threshold > 0.5) {
      setSettings({ threshold: 0.20 });
    }
    if (mode === 'visual_similarity' && settings.threshold < 0.3) {
      setSettings({ threshold: 0.55 });
    }
  };

  const modes: { value: SearchMode; label: string; icon: string; desc: string }[] = [
    { value: 'ai_detection', label: 'AI Detection', icon: '🎯', desc: 'YOLOv8 object detection' },
    { value: 'visual_similarity', label: 'Image Search', icon: '🖼️', desc: 'RemoteCLIP similarity' },
    { value: 'text_search', label: 'Text Search', icon: '🔤', desc: 'RemoteCLIP text query' },
  ];

  return (
    <div className="space-y-1 mb-4">
      <div className="flex gap-1 p-1 bg-secondary/50 rounded-lg">
        {modes.map((mode) => (
          <button
            key={mode.value}
            onClick={() => handleModeSwitch(mode.value)}
            title={mode.desc}
            className={`
              flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-md 
              text-xs font-medium transition-all duration-200
              ${
                searchMode === mode.value
                  ? 'bg-card text-primary shadow-sm border border-border'
                  : 'text-muted-foreground hover:text-foreground'
              }
            `}
          >
            <span>{mode.icon}</span>
            <span className="hidden sm:inline">{mode.label}</span>
          </button>
        ))}
      </div>
      <p className="text-[10px] text-muted-foreground text-center">
        {modes.find((m) => m.value === searchMode)?.desc}
      </p>
    </div>
  );
};

export default SearchModeToggle;
