import { useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Bot, ArrowLeft } from 'lucide-react'
import api from '../api/client'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post('/users/forgot-password', { email })
      toast.success(data.detail || 'Check your email for reset instructions.')
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
          <h1 className="text-2xl font-bold text-white">Forgot password</h1>
          <p className="text-gray-500 text-sm mt-1 text-center">
            Enter your account email. We'll send a reset link if the account exists.
          </p>
        </div>

        <form onSubmit={handle} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input
              className="input"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? 'Please wait…' : 'Send reset link'}
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
