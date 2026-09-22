import { create } from 'zustand'

interface DashboardState {
  stats: any | null;
  recentInspections: any[];
  severityDistribution: any | null;
  assetHealth: any | null;
  setStats: (stats: any) => void;
  setRecentInspections: (inspections: any[]) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  recentInspections: [],
  severityDistribution: null,
  assetHealth: null,
  setStats: (stats) => set({ stats }),
  setRecentInspections: (recentInspections) => set({ recentInspections }),
}))
