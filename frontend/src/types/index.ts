export interface Detection {
  id: string;
  class_name: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  confidence: number;
  latitude?: number;
  longitude?: number;
  status: string;
  created_at: string;
}

export interface Inspection {
  id: string;
  inspection_id: string;
  title: string;
  site_name: string;
  status: string;
  total_defects: number;
  critical_count: number;
  created_at: string;
}

export interface DashboardStats {
  total_inspections: number;
  total_assets: number;
  total_defects: number;
  critical_issues: number;
  high_issues: number;
  inspections_this_month: number;
  avg_defects_per_inspection: number;
  health_score_avg: number;
}

export interface SeverityDistribution {
  critical: number;
  high: number;
  medium: number;
  low: number;
}
