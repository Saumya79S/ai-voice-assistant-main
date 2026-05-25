import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { format, addDays, subDays } from 'date-fns'
import api from '../api/client'

export default function CalendarView() {
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(false)
  const [booking, setBooking] = useState(null)
  const [form, setForm] = useState({ name: '', phone: '', notes: '' })
  const [submitting, setSubmitting] = useState(false)

  const fetchSlots = async (d) => {
    setLoading(true)
    try {
      const { data } = await api.get(`/availability/slots?target_date=${d}`)
      setSlots(data)
    } catch {
      setSlots([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchSlots(selectedDate) }, [selectedDate])

  const navigate = (direction) => {
    const date = direction === 'prev'
      ? subDays(new Date(selectedDate), 1)
      : addDays(new Date(selectedDate), 1)
    setSelectedDate(format(date, 'yyyy-MM-dd'))
  }

  const bookManually = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/appointments', {
        ...form,
        date: selectedDate,
        start_time: booking.start_time,
      })
      toast.success('Appointment booked!')
      setBooking(null)
      setForm({ name: '', phone: '', notes: '' })
      fetchSlots(selectedDate)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Booking failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white tracking-tight">Calendar</h1>
        <p className="text-gray-500 text-sm mt-1">View slots and book appointments manually</p>
      </div>

      {/* Date nav */}
      <div className="card mb-6 flex items-center justify-between gap-4">
        <button onClick={() => navigate('prev')} className="btn-secondary p-2">
          <ChevronLeft size={18} />
        </button>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="input text-center font-semibold text-base border-none bg-transparent focus:ring-0 w-auto text-white"
        />
        <button onClick={() => navigate('next')} className="btn-secondary p-2">
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Slots grid */}
      {loading ? (
        <div className="card text-center text-gray-600 py-12 text-sm">Loading slots…</div>
      ) : slots.length === 0 ? (
        <div className="card text-center text-gray-600 py-12 text-sm">
          No availability configured for this day
        </div>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
          {slots.map((slot) => (
            <button
              key={slot.start_time}
              disabled={!slot.available}
              onClick={() => slot.available && setBooking(slot)}
              className={`rounded-xl p-3 text-sm font-medium text-center transition-all border ${
                slot.available
                  ? 'border-emerald-800 bg-emerald-950/50 text-emerald-400 hover:bg-emerald-900/60 hover:border-emerald-600 cursor-pointer'
                  : 'border-red-900 bg-red-950/50 text-red-500 cursor-not-allowed'
              }`}
            >
              <div>{slot.start_time}</div>
              <div className="text-xs opacity-60 mt-0.5">{slot.available ? 'Free' : 'Booked'}</div>
            </button>
          ))}
        </div>
      )}

      {/* Manual booking modal */}
      {booking && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="font-bold text-lg text-white mb-1">Book Appointment</h2>
            <p className="text-sm text-gray-500 mb-5">
              {selectedDate} at {booking.start_time} – {booking.end_time}
            </p>

            <form onSubmit={bookManually} className="space-y-4">
              <div>
                <label className="label">Full Name</label>
                <input
                  className="input"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="label">Phone Number</label>
                <input
                  className="input"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="label">Notes (optional)</label>
                <input
                  className="input"
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                />
              </div>
              <div className="flex gap-3 pt-1">
                <button
                  type="button"
                  onClick={() => setBooking(null)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn-primary flex-1">
                  {submitting ? 'Booking…' : 'Confirm Booking'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
