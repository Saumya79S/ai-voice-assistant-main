import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Save, Bot, Power } from 'lucide-react'
import api from '../api/client'

const VOICES = [
  { value: 'jennifer-playht', label: 'Jennifer (PlayHT) — Warm Female' },
  { value: 'matt-playht', label: 'Matt (PlayHT) — Professional Male' },
  { value: 'alloy', label: 'Alloy (OpenAI) — Neutral' },
  { value: 'nova', label: 'Nova (OpenAI) — Friendly Female' },
  { value: 'echo', label: 'Echo (OpenAI) — Deep Male' },
]

export default function AgentSettings() {
  const [agent, setAgent] = useState(null)
  const [form, setForm] = useState({ name: '', prompt: '', voice: '', is_active: true, vapi_assistant_id: '' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/agents').then(({ data }) => {
      if (data.length > 0) {
        const a = data[0]
        setAgent(a)
        setForm({ name: a.name, prompt: a.prompt, voice: a.voice, is_active: a.is_active, vapi_assistant_id: a.vapi_assistant_id || '' })
      }
    })
  }, [])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    const payload = { ...form, vapi_assistant_id: form.vapi_assistant_id.trim() || null }
    try {
      if (agent) {
        const { data } = await api.patch(`/agents/${agent.id}`, payload)
        setAgent(data)
        if (data.vapi_sync_error) {
          toast.error(data.vapi_sync_error)
        } else {
          toast.success('Agent saved and synced to Vapi.')
        }
      } else {
        const { data } = await api.post('/agents', payload)
        setAgent(data)
        if (data.vapi_sync_error) {
          toast.error(data.vapi_sync_error)
        } else {
          toast.success('Agent created and synced to Vapi.')
        }
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Agent Settings</h1>
          <p className="text-gray-500 text-sm mt-1">Configure your AI receptionist</p>
        </div>
        {agent && (
          <span className={agent.is_active ? 'badge-green' : 'badge-red'}>
            <Power size={11} className="mr-1" />
            {agent.is_active ? 'Active' : 'Inactive'}
          </span>
        )}
      </div>

      <form onSubmit={save} className="card space-y-6 max-w-3xl">
        <div>
          <label className="label">Agent Name</label>
          <input
            className="input"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="AI Receptionist"
            required
          />
        </div>

        <div>
          <label className="label">Voice</label>
          <select
            className="input"
            value={form.voice}
            onChange={(e) => setForm({ ...form, voice: e.target.value })}
          >
            {VOICES.map((v) => (
              <option key={v.value} value={v.value}>{v.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">Vapi Assistant ID</label>
          <input
            className="input font-mono text-xs"
            value={form.vapi_assistant_id}
            onChange={(e) => setForm({ ...form, vapi_assistant_id: e.target.value })}
            placeholder="e.g. 82a3aefc-1e6b-4b42-9834-888aa6722d54"
          />
          <p className="text-xs text-gray-600 mt-1">Paste an existing Vapi assistant ID to link it, or leave blank to auto-create.</p>
        </div>

        <div>
          <label className="label">System Prompt
            <span className="text-gray-600 font-normal ml-2 text-xs">(Instructions for the AI — be specific)</span>
          </label>
          <textarea
            className="input font-mono text-xs"
            rows={16}
            value={form.prompt}
            onChange={(e) => setForm({ ...form, prompt: e.target.value })}
            placeholder="You are a professional AI receptionist..."
            required
          />
          <p className="text-xs text-gray-600 mt-1">{form.prompt.length} characters</p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="is_active"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
            className="w-4 h-4 accent-white"
          />
          <label htmlFor="is_active" className="text-sm font-medium text-gray-400">
            Agent is active (answering calls)
          </label>
        </div>

        <div className="flex gap-3">
          <button type="submit" disabled={saving} className="btn-primary flex items-center gap-2">
            <Save size={16} />
            {saving ? 'Saving…' : 'Save & Sync to Vapi'}
          </button>
        </div>

        {agent?.vapi_sync_error && (
          <div className="bg-red-950/50 border border-red-900 rounded-lg p-3">
            <p className="text-xs text-red-400 font-medium">Vapi sync failed</p>
            <p className="text-xs text-red-500 mt-1 break-words">{agent.vapi_sync_error}</p>
          </div>
        )}

        {agent?.vapi_assistant_id && (
          <div className="bg-emerald-950/50 border border-emerald-900 rounded-lg p-3">
            <p className="text-xs text-emerald-400">
              <span className="font-semibold">Vapi Assistant ID:</span>{' '}
              <code className="font-mono">{agent.vapi_assistant_id}</code>
            </p>
          </div>
        )}

        {agent && !agent.vapi_assistant_id && !agent.vapi_sync_error && (
          <p className="text-xs text-yellow-400 bg-yellow-950/50 border border-yellow-900 rounded-lg p-3">
            No Vapi assistant ID yet. Click <strong>Save &amp; Sync to Vapi</strong> and ensure{' '}
            <code className="bg-yellow-950 px-1 rounded">VAPI_API_KEY</code> is set in{' '}
            <code className="bg-yellow-950 px-1 rounded">.env</code> (restart the server after editing).
          </p>
        )}
      </form>
    </div>
  )
}
