import { useState, useEffect } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Bot, ArrowLeft } from 'lucide-react'
import api from '../api/client'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) {
      toast.error('Missing reset token. Use the link from your email.')
    }
  }, [token])

  const handle = async (e) => {
    e.preventDefault()
    if (password !== confirm) {
      toast.error('Passwords do not match')
      return
    }
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/users/reset-password', {
        token,
        new_password: password,
      })
      toast.success(data.detail || 'Password updated.')
      navigate('/login', { replace: true })
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
          <h1 className="text-2xl font-bold text-white">Set new password</h1>
          <p className="text-gray-500 text-sm mt-1">Choose a strong password for your account.</p>
        </div>

        <form onSubmit={handle} className="space-y-4">
          <div>
            <label className="label">New password</label>
            <input
              className="input"
              type="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>
          <div>
            <label className="label">Confirm password</label>
            <input
              className="input"
              type="password"
              placeholder="Repeat password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={8}
            />
          </div>
          <button type="submit" disabled={loading || !token} className="btn-primary w-full mt-2">
            {loading ? 'Please wait…' : 'Update password'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600 mt-6">
          <Link
            to="/login"
            className="inline-flex items-center gap-1 text-gray-400 hover:text-white transition-colors font-medium"
          >
            <ArrowLeft size={14} />
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
