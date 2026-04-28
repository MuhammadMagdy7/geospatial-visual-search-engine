import { create } from 'zustand';
import { MapMode } from '../types/map';

interface MapState {
  mode: MapMode;
  selectedBBox: number[][] | null; // [[lat, lon], ...]
  center: [number, number];
  zoom: number;
  
  setMode: (mode: MapMode) => void;
  setSelectedBBox: (bbox: number[][] | null) => void;
  setCenter: (center: [number, number]) => void;
  setZoom: (zoom: number) => void;
}

export const useMapStore = create<MapState>((set) => ({
  mode: 'view',
  selectedBBox: null,
  center: [31.4056, 30.1219], // Cairo Airport [lon, lat] for MapLibre
  zoom: 15,

  setMode: (mode) => set({ mode }),
  setSelectedBBox: (bbox) => set({ selectedBBox: bbox }),
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
}));
