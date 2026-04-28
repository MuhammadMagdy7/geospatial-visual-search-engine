import { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useMapStore } from '../../stores/mapStore'
import { useSearchStore } from '../../stores/searchStore'
import { getScoreBg } from '../../lib/utils'
import { BoxSelect, RefreshCw, ZoomIn, ZoomOut } from 'lucide-react'

const MapView = () => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const startPoint = useRef<[number, number] | null>(null)
  
  const { center, zoom, mode, setMode, setSelectedBBox, setCenter, setZoom } = useMapStore()
  const { results, resetSearch } = useSearchStore()
  const markers = useRef<maplibregl.Marker[]>([])

  useEffect(() => {
    console.log('MapView: useEffect running');
    if (map.current || !mapContainer.current) {
      return
    }

    console.log('MapView: container dimensions =', 
      mapContainer.current?.clientWidth, 
      mapContainer.current?.clientHeight
    );

    try {
      // Switch to OpenStreetMap tiles to guarantee loading
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {
            'satellite': {
              type: 'raster',
              tiles: [
                'https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}',
                'https://mt1.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}',
                'https://mt2.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}',
                'https://mt3.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}'
              ],
              tileSize: 256,
              maxzoom: 20
            }
          },
          layers: [
            {
              id: 'satellite-layer',
              type: 'raster',
              source: 'satellite',
              minzoom: 0,
              maxzoom: 20
            }
          ]
        },
        center: center,
        zoom: zoom
      })

      console.log('MapView: map instance created');

      map.current.on('load', () => {
        console.log('MapView: map loaded successfully');
        if (!map.current) return
        
        // Add selection source and layers only after load
        map.current.addSource('selection', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        })

        map.current.addLayer({
          id: 'selection-fill',
          type: 'fill',
          source: 'selection',
          paint: {
            'fill-color': '#3b82f6',
            'fill-opacity': 0.2
          }
        })

        map.current.addLayer({
          id: 'selection-outline',
          type: 'line',
          source: 'selection',
          paint: {
            'line-color': '#3b82f6',
            'line-width': 2
          }
        })
      });

      map.current.on('error', (e) => {
        console.error('MapView: map error', e);
      });

      // Use moveend to reduce re-renders and potential loops
      map.current.on('moveend', () => {
        if (map.current) {
          const { lng, lat } = map.current.getCenter()
          setCenter([lng, lat])
          setZoom(map.current.getZoom())
        }
      });

    } catch (err) {
      console.error('MapView: Failed to initialize map', err);
    }

    return () => {
      console.log('MapView: Cleaning up map');
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [])

  // Update center/zoom if changed from store (e.g. from ResultCard)
  useEffect(() => {
    if (map.current && map.current.loaded()) {
      const currentCenter = map.current.getCenter()
      const lonDiff = Math.abs(currentCenter.lng - center[0])
      const latDiff = Math.abs(currentCenter.lat - center[1])
      
      if (lonDiff > 0.0001 || latDiff > 0.0001) {
        map.current.flyTo({ center, zoom, speed: 1.5 })
      }
    }
  }, [center, zoom])

  // Drawing logic
  useEffect(() => {
    if (!map.current) return

    const handleMouseDown = (e: maplibregl.MapMouseEvent) => {
      if (mode !== 'draw') return
      setIsDrawing(true)
      startPoint.current = [e.lngLat.lng, e.lngLat.lat]
      map.current?.dragPan.disable()
    }

    const handleMouseMove = (e: maplibregl.MapMouseEvent) => {
      if (!isDrawing || !startPoint.current || !map.current) return
      
      const p1 = startPoint.current
      const p2 = [e.lngLat.lng, e.lngLat.lat]
      
      const feature: GeoJSON.Feature = {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [[
            [p1[0], p1[1]],
            [p2[0], p1[1]],
            [p2[0], p2[1]],
            [p1[0], p2[1]],
            [p1[0], p1[1]]
          ]]
        },
        properties: {}
      }

      try {
        const source = map.current.getSource('selection') as maplibregl.GeoJSONSource
        if (source) {
          source.setData(feature)
        }
      } catch (err) {
        console.warn('MapView: Selection source not yet available', err)
      }
    }

    const handleMouseUp = (e: maplibregl.MapMouseEvent) => {
      if (!isDrawing || !startPoint.current) return
      setIsDrawing(false)
      map.current?.dragPan.enable()
      
      const p1 = startPoint.current
      const p2 = [e.lngLat.lng, e.lngLat.lat]
      
      const bbox = [
        [p1[1], p1[0]],
        [p1[1], p2[0]],
        [p2[1], p2[0]],
        [p2[1], p1[0]],
        [p1[1], p1[0]]
      ]
      
      setSelectedBBox(bbox)
      setMode('view')
    }

    map.current.on('mousedown', handleMouseDown)
    map.current.on('mousemove', handleMouseMove)
    map.current.on('mouseup', handleMouseUp)

    return () => {
      map.current?.off('mousedown', handleMouseDown)
      map.current?.off('mousemove', handleMouseMove)
      map.current?.off('mouseup', handleMouseUp)
    }
  }, [mode, isDrawing])

  // Display markers
  useEffect(() => {
    if (!map.current) return

    markers.current.forEach(m => m.remove())
    markers.current = []

    results.forEach(result => {
      const el = document.createElement('div')
      el.className = `w-6 h-6 rounded-full border-2 border-white shadow-lg cursor-pointer ${getScoreBg(result.similarity)} transition-transform hover:scale-125`
      
      const marker = new maplibregl.Marker(el)
        .setLngLat([result.longitude, result.latitude])
        .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(`
          <div class="p-2 text-background">
            <h3 class="font-bold border-b mb-1 pb-1">Result Details</h3>
            <p class="text-xs mb-1">Score: ${(result.similarity * 100).toFixed(1)}%</p>
            <p class="text-[10px] font-mono mb-2">${result.latitude.toFixed(5)}, ${result.longitude.toFixed(5)}</p>
            <a href="${result.google_maps_link}" target="_blank" class="text-[10px] bg-primary text-white px-2 py-1 rounded block text-center no-underline">Open in Google Maps</a>
          </div>
        `))
        .addTo(map.current!)
      
      markers.current.push(marker)
    })
  }, [results])

  const handleReset = () => {
    resetSearch()
    setSelectedBBox(null)
    if (map.current) {
      try {
        const source = map.current.getSource('selection') as maplibregl.GeoJSONSource
        if (source) {
          source.setData({ type: 'FeatureCollection', features: [] })
        }
      } catch (err) {
        console.warn('MapView: Could not reset selection source:', err)
      }
    }
  }

  return (
    <div className="w-full h-full relative bg-slate-900">
      <div ref={mapContainer} className="w-full h-full" />
      
      <div className="absolute top-4 left-4 flex flex-col gap-2 z-10">
        <div className="flex flex-col bg-card border rounded-md shadow-md overflow-hidden">
          <button 
            onClick={() => map.current?.zoomIn()}
            className="p-2 hover:bg-secondary transition-colors border-b"
            title="Zoom In"
          >
            <ZoomIn size={18} />
          </button>
          <button 
            onClick={() => map.current?.zoomOut()}
            className="p-2 hover:bg-secondary transition-colors"
            title="Zoom Out"
          >
            <ZoomOut size={18} />
          </button>
        </div>

        <div className="flex flex-col bg-card border rounded-md shadow-md overflow-hidden">
          <button 
            onClick={() => setMode(mode === 'draw' ? 'view' : 'draw')}
            className={`p-2 transition-colors border-b ${mode === 'draw' ? 'bg-primary text-white' : 'hover:bg-secondary'}`}
            title="Select Region"
          >
            <BoxSelect size={18} />
          </button>
          <button 
            onClick={handleReset}
            className="p-2 hover:bg-secondary transition-colors"
            title="Reset Map"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {mode === 'draw' && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-primary text-white px-4 py-1 rounded-full text-xs font-medium shadow-lg animate-bounce z-10">
          Click and drag to select a region
        </div>
      )}
    </div>
  )
}

export default MapView
