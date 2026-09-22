import { useState } from 'react'
import { useQuery } from 'react-query'
import { Plus, Upload, FileImage } from 'lucide-react'
import { inspectionsApi } from '../services/api'
import { format } from 'date-fns'

export default function Inspections() {
  const [page] = useState(1)
  const { data, isLoading } = useQuery(['inspections', page], () => inspectionsApi.list({ page, page_size: 10 }))
  const inspections = data?.data?.items || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Inspections</h2>
        <button className="btn-primary flex items-center gap-2"><Plus size={18} /> New Inspection</button>
      </div>
      <div className="card overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">ID</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Title</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Site</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Status</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Defects</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Date</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading && <tr><td colSpan={7} className="px-6 py-8 text-center text-gray-500">Loading...</td></tr>}
            {inspections.map((inp: any) => (
              <tr key={inp.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-mono text-gray-600">{inp.inspection_id}</td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{inp.title}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{inp.site_name || '-'}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex px-2 py-1 text-xs rounded-full font-medium ${inp.status === 'completed' ? 'bg-green-100 text-green-700' : inp.status === 'processing' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}>{inp.status}</span>
                </td>
                <td className="px-6 py-4 text-sm"><span className={inp.stats.total_defects > 0 ? 'text-red-600 font-medium' : 'text-gray-500'}>{inp.stats.total_defects}</span>{inp.stats.critical > 0 && <span className="ml-2 text-xs text-red-500">({inp.stats.critical} critical)</span>}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{format(new Date(inp.created_at), 'MMM d, yyyy')}</td>
                <td className="px-6 py-4"><div className="flex gap-2"><button className="p-1 hover:bg-gray-100 rounded" title="Upload images"><Upload size={16} className="text-gray-500" /></button><button className="p-1 hover:bg-gray-100 rounded" title="View report"><FileImage size={16} className="text-gray-500" /></button></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}