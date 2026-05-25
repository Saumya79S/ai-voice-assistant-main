import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Trash2, RefreshCw } from 'lucide-react'
import api from '../api/client'

const STATUS_BADGE = {
  confirmed: 'badge-green',
  pending: 'badge-yellow',
  cancelled: 'badge-red',
  completed: 'badge-blue',
}

export default function AppointmentsTable() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ date: '', status: '' })

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filter.date) params.appt_date = filter.date
      if (filter.status) params.status = filter.status
      const { data } = await api.get('/appointments', { params })
      setAppointments(data)
    } catch {
      toast.error('Failed to load appointments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filter])

  const cancel = async (id) => {
    if (!confirm('Cancel this appointment?')) return
    try {
      await api.delete(`/appointments/${id}`)
      toast.success('Appointment cancelled')
      load()
    } catch {
      toast.error('Failed to cancel')
    }
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Appointments</h1>
          <p className="text-gray-500 text-sm mt-1">{appointments.length} total</p>
        </div>
        <button onClick={load} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-6 flex gap-4 items-end">
        <div>
          <label className="label">Filter by Date</label>
          <input
            type="date"
            className="input"
            value={filter.date}
            onChange={(e) => setFilter({ ...filter, date: e.target.value })}
          />
        </div>
        <div>
          <label className="label">Filter by Status</label>
          <select
            className="input"
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          >
            <option value="">All</option>
            <option value="confirmed">Confirmed</option>
            <option value="pending">Pending</option>
            <option value="cancelled">Cancelled</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <button onClick={() => setFilter({ date: '', status: '' })} className="btn-secondary">
          Clear
        </button>
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-950 overflow-hidden">
        {loading ? (
          <div className="text-center text-gray-600 py-12 text-sm">Loading…</div>
        ) : appointments.length === 0 ? (
          <div className="text-center text-gray-600 py-12 text-sm">No appointments found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  {['#', 'Name', 'Phone', 'Date', 'Time', 'Status', 'Notes', ''].map((h) => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-widest bg-gray-900 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {appointments.map((a, i) => (
                  <tr
                    key={a.id}
                    className={`border-b border-gray-800/60 hover:bg-gray-900 transition-colors ${
                      i % 2 === 0 ? 'bg-gray-950' : 'bg-[#0d0d0d]'
                    }`}
                  >
                    <td className="px-4 py-3.5 text-gray-600 font-mono text-xs">{a.id}</td>
                    <td className="px-4 py-3.5 font-medium text-white">{a.name}</td>
                    <td className="px-4 py-3.5 text-gray-400">{a.phone}</td>
                    <td className="px-4 py-3.5 text-gray-400">{a.date}</td>
                    <td className="px-4 py-3.5 text-gray-400 whitespace-nowrap">
                      {a.start_time.slice(0, 5)} – {a.end_time.slice(0, 5)}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={STATUS_BADGE[a.status] || 'badge-blue'}>{a.status}</span>
                    </td>
                    <td className="px-4 py-3.5 text-gray-600 max-w-xs truncate">{a.notes || '—'}</td>
                    <td className="px-4 py-3.5">
                      {a.status !== 'cancelled' && (
                        <button
                          onClick={() => cancel(a.id)}
                          className="text-gray-600 hover:text-red-400 transition-colors"
                          title="Cancel"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
