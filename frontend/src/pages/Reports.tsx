import { useQuery } from 'react-query'
import { FileText, Download, Clock } from 'lucide-react'
import { api } from '../services/api'
import { format } from 'date-fns'

export default function Reports() {
  const { data } = useQuery('reports', () => api.get('/reports'))
  const reports = data?.data?.items || []

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Inspection Reports</h2>
      <div className="card">
        <div className="space-y-4">
          {reports.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <FileText size={48} className="mx-auto mb-4 opacity-50" />
              <p>No reports generated yet.</p>
              <p className="text-sm mt-1">Create an inspection and generate a report to see it here.</p>
            </div>
          )}
          {reports.map((report: any) => (
            <div key={report.id} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:border-primary-200 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-primary-50 rounded-lg"><FileText size={20} className="text-primary-600" /></div>
                <div>
                  <h3 className="font-medium text-gray-900">{report.title}</h3>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                    <span>{report.report_id}</span><span>•</span><span className="capitalize">{report.report_type}</span><span>•</span>
                    <span className="flex items-center gap-1"><Clock size={14} />{format(new Date(report.created_at), 'MMM d, yyyy')}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 text-xs rounded-full font-medium ${report.status === 'ready' ? 'bg-green-100 text-green-700' : report.status === 'generating' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>{report.status}</span>
                {report.status === 'ready' && (
                  <a href={`http://localhost:8000/api/v1/reports/${report.report_id}/download`} className="p-2 hover:bg-gray-100 rounded-lg transition-colors" download>
                    <Download size={18} className="text-gray-600" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}