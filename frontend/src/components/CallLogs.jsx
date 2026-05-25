import React, { useEffect, useState } from 'react'
import { RefreshCw, PhoneCall } from 'lucide-react'
import api from '../api/client'

const ENDED_REASON_BADGE = {
  customer_ended_call: 'badge-dark-blue',
  assistant_ended_call: 'badge-dark-blue',
  voicemail: 'badge-dark-yellow',
  no_answer: 'badge-dark-red',
  failed: 'badge-dark-red',
  busy: 'badge-dark-red',
  transferred: 'badge-dark-yellow',
  abandoned: 'badge-dark-red',
  booked: 'badge-dark-green',
  success: 'badge-dark-green',
}

const EVAL_BADGE = {
  success: 'badge-dark-green',
  failure: 'badge-dark-red',
  unknown: 'badge-dark-yellow',
}

const COLUMNS = [
  '#',
  'VAPI Call ID',
  'Assistant',
  'Assistant Phone',
  'Customer Phone',
  'Type',
  'Start Time',
  'Duration',
  'Ended Reason',
  'Evaluation',
  'Score',
  'Cost',
  'Transcript',
]

const Badge = ({ value, map, fallback = 'badge-dark-blue' }) => {
  if (!value) return <span className="text-gray-600">—</span>
  const cls = map[value.toLowerCase()] || fallback
  const label = value.replace(/[_\.]/g, ' ')
  return (
    <span className={`${cls} max-w-[160px] truncate block`} title={label}>
      {label}
    </span>
  )
}

export default function CallLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/call-logs', { params: { limit: 100 } })
      setLogs(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const formatDuration = (s) => {
    if (!s) return '—'
    const m = Math.floor(s / 60)
    const sec = Math.round(s % 60)
    return m > 0 ? `${m}m ${sec}s` : `${sec}s`
  }

  const formatDt = (dt) => {
    if (!dt) return '—'
    return new Date(dt).toLocaleString()
  }

  const formatCost = (c) => {
    if (c == null) return '—'
    return `$${c.toFixed(4)}`
  }

  const formatCallType = (t) => {
    if (!t) return '—'
    return t.replace(/([A-Z])/g, ' $1').trim()
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Call Logs</h1>
          <p className="text-gray-500 text-sm mt-1">
            {logs.length} {logs.length === 1 ? 'call' : 'calls'} recorded
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white hover:border-gray-500 transition-all duration-150 text-sm font-medium"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {/* Table card */}
      <div className="rounded-xl border border-gray-800 bg-gray-950 overflow-hidden">
        {loading ? (
          <div className="text-center text-gray-600 py-16 text-sm">Loading…</div>
        ) : logs.length === 0 ? (
          <div className="text-center text-gray-600 py-16 flex flex-col items-center gap-3">
            <PhoneCall size={36} className="text-gray-700" />
            <p className="text-sm">No calls yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  {COLUMNS.map((h) => (
                    <th
                      key={h}
                      className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-widest whitespace-nowrap bg-gray-900"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <React.Fragment key={log.id}>
                    <tr
                      className={`border-b border-gray-800/60 transition-colors duration-100 hover:bg-gray-900 ${
                        i % 2 === 0 ? 'bg-gray-950' : 'bg-[#0d0d0d]'
                      }`}
                    >
                      {/* # */}
                      <td className="px-4 py-3.5 text-gray-600 font-mono text-xs">{log.id}</td>

                      {/* VAPI Call ID */}
                      <td className="px-4 py-3.5 font-mono text-xs text-gray-500 max-w-[120px] truncate" title={log.vapi_call_id || ''}>
                        {log.vapi_call_id || <span className="text-gray-700">—</span>}
                      </td>

                      {/* Assistant */}
                      <td className="px-4 py-3.5 text-white font-medium whitespace-nowrap">
                        {log.assistant_name || <span className="text-gray-600">—</span>}
                      </td>

                      {/* Assistant Phone */}
                      <td className="px-4 py-3.5 text-gray-400 whitespace-nowrap">
                        {log.assistant_phone_number || <span className="text-gray-700">—</span>}
                      </td>

                      {/* Customer Phone */}
                      <td className="px-4 py-3.5 text-white font-medium whitespace-nowrap">
                        {log.customer_phone_number || <span className="text-gray-600">—</span>}
                      </td>

                      {/* Type */}
                      <td className="px-4 py-3.5 text-gray-400 whitespace-nowrap capitalize text-xs">
                        {formatCallType(log.call_type)}
                      </td>

                      {/* Start Time */}
                      <td className="px-4 py-3.5 text-gray-300 whitespace-nowrap text-xs">
                        {formatDt(log.start_time)}
                      </td>

                      {/* Duration */}
                      <td className="px-4 py-3.5 text-gray-300 whitespace-nowrap">
                        {formatDuration(log.duration_seconds)}
                      </td>

                      {/* Ended Reason */}
                      <td className="px-4 py-3.5 max-w-[180px]">
                        <Badge value={log.ended_reason} map={ENDED_REASON_BADGE} />
                      </td>

                      {/* Evaluation */}
                      <td className="px-4 py-3.5 max-w-[130px]">
                        <Badge value={log.success_evaluation} map={EVAL_BADGE} />
                      </td>

                      {/* Score */}
                      <td className="px-4 py-3.5 text-gray-300">
                        {log.score != null ? (
                          <span className="font-mono text-xs">{log.score}</span>
                        ) : (
                          <span className="text-gray-700">—</span>
                        )}
                      </td>

                      {/* Cost */}
                      <td className="px-4 py-3.5 text-gray-300 font-mono text-xs">
                        {log.cost != null ? formatCost(log.cost) : <span className="text-gray-700">—</span>}
                      </td>

                      {/* Transcript */}
                      <td className="px-4 py-3.5">
                        {log.transcript ? (
                          <button
                            onClick={() => setExpanded(expanded === log.id ? null : log.id)}
                            className="px-3 py-1 rounded-md text-xs font-medium bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white border border-gray-700 hover:border-gray-500 transition-all duration-150 whitespace-nowrap"
                          >
                            {expanded === log.id ? 'Hide' : 'View'}
                          </button>
                        ) : (
                          <span className="text-gray-700">—</span>
                        )}
                      </td>
                    </tr>

                    {/* Expanded transcript row */}
                    {expanded === log.id && log.transcript && (
                      <tr className="bg-gray-900 border-b border-gray-800">
                        <td colSpan={COLUMNS.length} className="px-6 py-4">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Transcript</span>
                            <div className="flex-1 h-px bg-gray-800" />
                          </div>
                          <div className="bg-black rounded-lg border border-gray-800 p-4 text-xs text-gray-300 whitespace-pre-wrap font-mono max-h-64 overflow-auto leading-relaxed">
                            {log.transcript}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
