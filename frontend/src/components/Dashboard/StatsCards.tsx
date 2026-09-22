import { useEffect } from 'react'
import { useQuery } from 'react-query'
import { AlertTriangle, CheckCircle, Box, ClipboardCheck } from 'lucide-react'
import { dashboardApi } from '../../services/api'
import { useDashboardStore } from '../../store/dashboardStore'

export default function StatsCards() {
  const { data } = useQuery('dashboardStats', () => dashboardApi.getStats())
  const { setStats, setRecentInspections } = useDashboardStore()

  useEffect(() => {
    if (data?.data) {
      setStats(data.data.stats)
      setRecentInspections(data.data.recent_inspections)
    }
  }, [data, setStats, setRecentInspections])

  const stats = data?.data?.stats
  if (!stats) return <div className="grid grid-cols-4 gap-6">Loading...</div>

  const cards = [
    { label: 'Total Assets', value: stats.total_assets, icon: Box, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Total Defects', value: stats.total_defects, icon: ClipboardCheck, color: 'text-orange-600', bg: 'bg-orange-50' },
    { label: 'Critical Issues', value: stats.critical_issues, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' },
    { label: 'Health Score Avg', value: `${stats.health_score_avg}%`, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <div key={card.label} className="card flex items-center gap-4">
            <div className={`p-3 rounded-lg ${card.bg}`}><Icon size={24} className={card.color} /></div>
            <div>
              <p className="text-sm text-gray-500 font-medium">{card.label}</p>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}