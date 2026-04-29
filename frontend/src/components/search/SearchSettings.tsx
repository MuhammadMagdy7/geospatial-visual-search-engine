import { useSearchStore } from '../../stores/searchStore'

const SearchSettings = () => {
  const { settings, setSettings, searchMode } = useSearchStore()

  const minThreshold = searchMode === 'text' ? 0.10 : 0.30;
  const maxThreshold = searchMode === 'text' ? 0.50 : 0.95;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex justify-between">
          <label className="text-xs font-medium">Similarity Threshold</label>
          <span className="text-xs text-primary font-mono">{settings.threshold.toFixed(2)}</span>
        </div>
        <input 
          type="range" 
          min={minThreshold} 
          max={maxThreshold} 
          step="0.01"
          value={settings.threshold}
          onChange={(e) => setSettings({ threshold: parseFloat(e.target.value) })}
          className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
        />
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium">Tile Size (px)</label>
        <select 
          value={settings.tileSize}
          onChange={(e) => setSettings({ tileSize: parseInt(e.target.value) })}
          className="w-full bg-secondary border border-border rounded-md px-2 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none"
        >
          {[60, 80, 100, 120, 160, 180].map(size => (
            <option key={size} value={size}>{size}x{size}</option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium">Zoom Level</label>
        <select 
          value={settings.zoomLevel}
          onChange={(e) => setSettings({ zoomLevel: parseInt(e.target.value) })}
          className="w-full bg-secondary border border-border rounded-md px-2 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none"
        >
          {[14, 15, 16, 17, 18].map(zoom => (
            <option key={zoom} value={zoom}>Zoom {zoom}</option>
          ))}
        </select>
      </div>
    </div>
  )
}

export default SearchSettings
