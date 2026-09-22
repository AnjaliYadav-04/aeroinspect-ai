import { useQuery } from 'react-query'
import { Box, AlertTriangle } from 'lucide-react'
import { api } from '../services/api'

export default function Assets() {
  const { data } = useQuery('assets', () => api.get('/assets?page_size=50'))
  const assets = data?.data?.items || []

  const statusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-700'
      case 'degraded': return 'bg-yellow-100 text-yellow-700'
      case 'critical': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Assets</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {assets.map((asset: any) => (
          <div key={asset.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg"><Box size={20} className="text-blue-600" /></div>
                <div><h3 className="font-semibold text-gray-900">{asset.name}</h3><p className="text-sm text-gray-500 capitalize">{asset.asset_type.replace('_', ' ')}</p></div>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full font-medium ${statusColor(asset.status)}`}>{asset.status}</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Health Score</span><span className={`font-medium ${asset.health_score < 50 ? 'text-red-600' : 'text-gray-900'}`}>{asset.health_score}%</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Location</span><span className="text-gray-700 font-mono text-xs">{asset.latitude?.toFixed(4)}, {asset.longitude?.toFixed(4)}</span></div>
              {asset.capacity_kw && <div className="flex justify-between"><span className="text-gray-500">Capacity</span><span className="text-gray-700">{asset.capacity_kw} kW</span></div>}
            </div>
            {asset.status === 'critical' && (
              <div className="mt-4 p-3 bg-red-50 rounded-lg flex items-center gap-2 text-sm text-red-700"><AlertTriangle size={16} /> Maintenance required immediately</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}