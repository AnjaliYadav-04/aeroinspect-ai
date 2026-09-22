import StatsCards from '../components/Dashboard/StatsCards'
import InspectionMap from '../components/Map/InspectionMap'
import { useDashboardStore } from '../store/dashboardStore'
import { format } from 'date-fns'

export default function Dashboard() {
  const { recentInspections, stats } = useDashboardStore()
  return (
    <div className="space-y-8">
      <StatsCards />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Inspection Map</h3>
            <InspectionMap height="450px" />
          </div>
        </div>
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Recent Inspections</h3>
            <div className="space-y-3">
              {recentInspections.length === 0 && <p className="text-gray-500 text-sm">No recent inspections</p>}
              {recentInspections.map((inp: any) => (
                <div key={inp.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{inp.title}</p>
                    <p className="text-sm text-gray-500">{inp.site_name}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-block px-2 py-1 text-xs rounded-full font-medium ${inp.defect_count > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                      {inp.defect_count} issues
                    </span>
                    <p className="text-xs text-gray-400 mt-1">{format(new Date(inp.created_at), 'MMM d')}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
            <div className="space-y-3">
              {['critical', 'high', 'medium', 'low'].map((sev) => (
                <div key={sev} className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full bg-severity-${sev}`} />
                  <span className="flex-1 text-sm capitalize text-gray-700">{sev}</span>
                  <span className="text-sm font-medium text-gray-900">{stats?.[`${sev}_issues`] || 0}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}