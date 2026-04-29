import React from 'react';
import { useSearchStore } from '../../stores/searchStore';
import { SearchMode } from '../../types/search';

const SearchModeToggle: React.FC = () => {
  const { searchMode, setSearchMode, settings, setSettings } = useSearchStore();

  const handleModeSwitch = (mode: SearchMode) => {
    setSearchMode(mode);
    // When switching to text mode, lower the threshold
    if (mode === 'text' && settings.threshold > 0.5) {
      setSettings({ threshold: 0.20 });
    }
    // When switching to image mode, raise the threshold
    if (mode === 'image' && settings.threshold < 0.3) {
      setSettings({ threshold: 0.55 });
    }
  };

  const modes: { value: SearchMode; label: string; icon: string }[] = [
    { value: 'image', label: 'Image Search', icon: '🖼️' },
    { value: 'text', label: 'Text Search', icon: '🔤' },
  ];

  return (
    <div className="flex gap-1 p-1 bg-gray-100 rounded-lg mb-4">
      {modes.map((mode) => (
        <button
          key={mode.value}
          onClick={() => handleModeSwitch(mode.value)}
          className={`
            flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md 
            text-sm font-medium transition-all duration-200
            ${
              searchMode === mode.value
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }
          `}
        >
          <span>{mode.icon}</span>
          <span>{mode.label}</span>
        </button>
      ))}
    </div>
  );
};

export default SearchModeToggle;
