import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Bot, LogIn } from 'lucide-react'
import api from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', phone_number: '' })
  const [loading, setLoading] = useState(false)

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'register') {
        await api.post('/users/register', {
          email: form.email,
          password: form.password,
          phone_number: form.phone_number?.trim() || '',
        })
        toast.success('Account created! Please log in.')
        setMode('login')
      } else {
        const { data } = await api.post('/users/login', {
          email: form.email,
          password: form.password,
        })
        localStorage.setItem('token', data.access_token)
        navigate('/dashboard')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-black">
      <div className="bg-gray-950 border border-gray-800 rounded-2xl p-8 w-full max-w-md shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-white rounded-full p-3 mb-4">
            <Bot className="text-black" size={28} />
          </div>
          <h1 className="text-2xl font-bold text-white">AI Receptionist</h1>
          <p className="text-gray-500 text-sm mt-1">Dashboard Login</p>
        </div>

        <form onSubmit={handle} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input
              className="input"
              type="email"
              placeholder="admin@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>

          {mode === 'register' && (
            <div>
              <label className="label">Phone (optional)</label>
              <input
                className="input"
                type="tel"
                placeholder="+1 555 123 4567"
                value={form.phone_number}
                onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
              />
            </div>
          )}

          <div>
            <div className="flex items-center justify-between gap-2">
              <label className="label mb-0">Password</label>
              {mode === 'login' && (
                <Link to="/forgot-password" className="text-xs text-gray-400 hover:text-white transition-colors">
                  Forgot password?
                </Link>
              )}
            </div>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
          >
            <LogIn size={16} />
            {loading ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600 mt-6">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => {
              const nextMode = mode === 'login' ? 'register' : 'login'
              setMode(nextMode)
              setForm((prev) => ({
                ...prev,
                password: '',
                ...(nextMode === 'login' ? { phone_number: '' } : {}),
              }))
            }}
            className="text-white font-medium hover:underline"
          >
            {mode === 'login' ? 'Register' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  )
}
