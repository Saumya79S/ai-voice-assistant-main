import { useEffect, useState } from 'react'
import { PhoneCall, CalendarCheck, Clock, TrendingUp } from 'lucide-react'
import api from '../api/client'
import { format } from 'date-fns'

export default function Dashboard() {
  const [stats, setStats] = useState({ calls: 0, booked: 0, transferred: 0, today: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [logsRes, apptsRes] = await Promise.all([
          api.get('/call-logs?limit=200'),
          api.get('/appointments'),
        ])
        const logs = logsRes.data
        const appts = apptsRes.data
        const today = format(new Date(), 'yyyy-MM-dd')
        setStats({
          calls: logs.length,
          booked: logs.filter((l) => l.ended_reason === 'booked').length,
          transferred: logs.filter((l) => l.ended_reason === 'transferred').length,
          today: appts.filter((a) => a.date === today).length,
        })
      } catch {
        // ignore
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  const cards = [
    { label: 'Total Calls', value: stats.calls, icon: PhoneCall, accent: 'text-blue-400', bg: 'bg-blue-950/50 border-blue-900' },
    { label: 'Appointments Booked', value: stats.booked, icon: CalendarCheck, accent: 'text-emerald-400', bg: 'bg-emerald-950/50 border-emerald-900' },
    { label: 'Transferred to Human', value: stats.transferred, icon: TrendingUp, accent: 'text-yellow-400', bg: 'bg-yellow-950/50 border-yellow-900' },
    { label: "Today's Appointments", value: stats.today, icon: Clock, accent: 'text-purple-400', bg: 'bg-purple-950/50 border-purple-900' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Overview of your AI receptionist</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card animate-pulse h-32 bg-gray-900" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {cards.map(({ label, value, icon: Icon, accent, bg }) => (
            <div key={label} className={`card border flex items-center gap-4 ${bg}`}>
              <div className={`p-3 rounded-xl bg-black/40`}>
                <Icon size={22} className={accent} />
              </div>
              <div>
                <p className="text-sm text-gray-500">{label}</p>
                <p className={`text-3xl font-bold ${accent}`}>{value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 card">
        <h2 className="font-semibold text-white mb-3">Quick Start</h2>
        <ol className="text-sm text-gray-400 space-y-2 list-decimal list-inside leading-relaxed">
          <li>Go to <span className="text-white font-medium">Agent Settings</span> to configure your AI prompt and voice</li>
          <li>Set your working hours in <span className="text-white font-medium">Availability</span></li>
          <li>Copy your Vapi webhook URL and paste it into your Vapi dashboard</li>
          <li>Test by calling your Vapi phone number</li>
          <li>Bookings will appear in <span className="text-white font-medium">Appointments</span> and <span className="text-white font-medium">Calendar</span></li>
        </ol>
      </div>
    </div>
  )
}
