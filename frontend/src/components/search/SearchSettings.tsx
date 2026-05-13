import { useEffect, useState } from 'react'
import { useSearchStore } from '../../stores/searchStore'
import { searchAPI } from '../../services/api'

const SearchSettings = () => {
  const { settings, setSettings, searchMode } = useSearchStore()
  const [classes, setClasses] = useState<string[]>(['plane'])
  const [classesLoading, setClassesLoading] = useState(false)

  // Fetch YOLO classes on mount
  useEffect(() => {
    setClassesLoading(true)
    searchAPI
      .getClasses()
      .then((data) => setClasses(data.classes))
      .catch(() => {
        // Fallback: common DOTA classes if API not reachable yet
        setClasses([
          'plane', 'ship', 'storage-tank', 'baseball-diamond',
          'tennis-court', 'basketball-court', 'ground-track-field',
          'harbor', 'bridge', 'large-vehicle', 'small-vehicle',
          'helicopter', 'roundabout', 'soccer-ball-field', 'swimming-pool',
        ])
      })
      .finally(() => setClassesLoading(false))
  }, [])

  // ── AI Detection settings ──────────────────────────────────────────────
  if (searchMode === 'ai_detection') {
    return (
      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-xs font-medium">Object Class</label>
          <select
            value={settings.targetClass}
            onChange={(e) => setSettings({ targetClass: e.target.value })}
            disabled={classesLoading}
            className="w-full bg-secondary border border-border rounded-md px-2 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none"
          >
            {classes.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <label className="text-xs font-medium">Confidence Threshold</label>
            <span className="text-xs text-primary font-mono">
              {settings.confidenceThreshold.toFixed(2)}
            </span>
          </div>
          <input
            type="range"
            min="0.25"
            max="0.95"
            step="0.05"
            value={settings.confidenceThreshold}
            onChange={(e) =>
              setSettings({ confidenceThreshold: parseFloat(e.target.value) })
            }
            className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium">Max Results (Top K)</label>
          <input
            type="number"
            min="10"
            max="200"
            value={settings.topK}
            onChange={(e) => setSettings({ topK: parseInt(e.target.value) || 50 })}
            className="w-full bg-secondary border border-border rounded-md px-2 py-1.5 text-xs"
          />
        </div>
      </div>
    )
  }

  // ── RemoteCLIP settings (Visual Similarity + Text Search) ──────────────
  const minThreshold = searchMode === 'text_search' ? 0.10 : 0.30
  const maxThreshold = searchMode === 'text_search' ? 0.50 : 0.95

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex justify-between">
          <label className="text-xs font-medium">Similarity Threshold</label>
          <span className="text-xs text-primary font-mono">
            {settings.threshold.toFixed(2)}
          </span>
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
          {[60, 80, 100, 120, 160, 180].map((size) => (
            <option key={size} value={size}>
              {size}x{size}
            </option>
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
          {[14, 15, 16, 17, 18].map((zoom) => (
            <option key={zoom} value={zoom}>
              Zoom {zoom}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}

export default SearchSettings
