import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
}

export const inspectionsApi = {
  list: (params?: any) => api.get('/inspections', { params }),
  create: (data: any) => api.post('/inspections', data),
  get: (id: string) => api.get(`/inspections/${id}`),
}

export const detectionsApi = {
  list: (params?: any) => api.get('/detections', { params }),
}

export const mapsApi = {
  getDetections: (params?: any) => api.get('/maps/detections', { params }),
  getAssets: (params?: any) => api.get('/maps/assets', { params }),
  getClusters: () => api.get('/maps/clusters'),
}

export const uploadApi = {
  uploadImage: (file: File, inspectionId?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/upload/image?inspection_id=${inspectionId || ''}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
