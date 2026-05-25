import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Plus, Trash2, Clock } from 'lucide-react'
import api from '../api/client'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const DURATIONS = [15, 20, 30, 45, 60, 90, 120]

export default function AvailabilitySetup() {
  const [rules, setRules] = useState([])
  const [form, setForm] = useState({
    day_of_week: 0,
    start_time: '09:00',
    end_time: '17:00',
    slot_duration: 30,
    is_active: true,
  })
  const [saving, setSaving] = useState(false)

  const load = () =>
    api.get('/availability').then(({ data }) => setRules(data))

  useEffect(() => { load() }, [])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/availability', form)
      toast.success(`${DAYS[form.day_of_week]} availability saved!`)
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  const toggle = async (rule) => {
    try {
      await api.patch(`/availability/${rule.id}`, { is_active: !rule.is_active })
      load()
    } catch {
      toast.error('Failed to update')
    }
  }

  const remove = async (id) => {
    if (!confirm('Delete this availability rule?')) return
    try {
      await api.delete(`/availability/${id}`)
      toast.success('Rule deleted')
      load()
    } catch {
      toast.error('Failed to delete')
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white tracking-tight">Availability Setup</h1>
        <p className="text-gray-500 text-sm mt-1">Define your working hours and appointment slot duration</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Add rule form */}
        <form onSubmit={save} className="card space-y-4">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <Plus size={17} className="text-gray-500" /> Add / Update Rule
          </h2>

          <div>
            <label className="label">Day of Week</label>
            <select
              className="input"
              value={form.day_of_week}
              onChange={(e) => setForm({ ...form, day_of_week: parseInt(e.target.value) })}
            >
              {DAYS.map((d, i) => (
                <option key={d} value={i}>{d}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Start Time</label>
              <input
                className="input"
                type="time"
                value={form.start_time}
                onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">End Time</label>
              <input
                className="input"
                type="time"
                value={form.end_time}
                onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                required
              />
            </div>
          </div>

          <div>
            <label className="label">Slot Duration</label>
            <select
              className="input"
              value={form.slot_duration}
              onChange={(e) => setForm({ ...form, slot_duration: parseInt(e.target.value) })}
            >
              {DURATIONS.map((d) => (
                <option key={d} value={d}>{d} minutes</option>
              ))}
            </select>
          </div>

          <button type="submit" disabled={saving} className="btn-primary w-full">
            {saving ? 'Saving…' : 'Save Rule'}
          </button>
        </form>

        {/* Current rules */}
        <div className="card">
          <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Clock size={17} className="text-gray-500" /> Current Rules
          </h2>

          {rules.length === 0 ? (
            <p className="text-sm text-gray-600 text-center py-8">No rules set yet</p>
          ) : (
            <div className="space-y-2">
              {rules.map((r) => (
                <div
                  key={r.id}
                  className="flex items-center justify-between p-3 bg-gray-900 border border-gray-800 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm text-white">{DAYS[r.day_of_week]}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {r.start_time} – {r.end_time} · {r.slot_duration}min slots
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggle(r)}
                      className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors ${
                        r.is_active
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800 hover:bg-emerald-900'
                          : 'bg-gray-800 text-gray-500 border border-gray-700 hover:bg-gray-700'
                      }`}
                    >
                      {r.is_active ? 'Active' : 'Off'}
                    </button>
                    <button
                      onClick={() => remove(r.id)}
                      className="text-gray-600 hover:text-red-400 transition-colors"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
