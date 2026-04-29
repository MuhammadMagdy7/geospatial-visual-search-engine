import React from 'react';
import { useSearchStore } from '../../stores/searchStore';

const TextSearch: React.FC = () => {
  const { queryText, setQueryText } = useSearchStore();

  const exampleQueries = [
    'airplane on runway',
    'parking lot with cars',
    'swimming pool',
    'buildings and roads',
    'green vegetation area',
  ];

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Describe what you're looking for
      </label>
      <textarea
        value={queryText}
        onChange={(e) => setQueryText(e.target.value)}
        placeholder="e.g., airplane on runway"
        rows={3}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg 
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                   resize-none text-sm"
      />
      <div className="space-y-1">
        <p className="text-xs text-gray-500">Try an example:</p>
        <div className="flex flex-wrap gap-1">
          {exampleQueries.map((q) => (
            <button
              key={q}
              onClick={() => setQueryText(q)}
              className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 
                         rounded-full text-gray-600 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TextSearch;
