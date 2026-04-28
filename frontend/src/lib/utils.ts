import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCoordinate(coord: number) {
  return coord.toFixed(6)
}

export function getScoreColor(score: number) {
  if (score > 0.75) return "text-[#1D9E75]"
  if (score > 0.60) return "text-[#BA7517]"
  return "text-[#E24B4A]"
}

export function getScoreBg(score: number) {
  if (score > 0.75) return "bg-[#1D9E75]"
  if (score > 0.60) return "bg-[#BA7517]"
  return "bg-[#E24B4A]"
}
