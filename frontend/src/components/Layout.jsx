import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Bot, Clock, Calendar, CalendarCheck, PhoneCall, LogOut,
} from 'lucide-react'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/agent', label: 'Agent Settings', icon: Bot },
  { to: '/availability', label: 'Availability', icon: Clock },
  { to: '/calendar', label: 'Calendar', icon: Calendar },
  { to: '/appointments', label: 'Appointments', icon: CalendarCheck },
  { to: '/call-logs', label: 'Call Logs', icon: PhoneCall },
]

export default function Layout() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-black">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Bot className="text-white" size={22} />
            <span className="font-bold text-white text-lg tracking-tight">AI Receptionist</span>
          </div>
          <p className="text-xs text-gray-600 mt-1">Voice Booking System</p>
        </div>

        <nav className="flex-1 p-3 space-y-0.5">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-white text-black'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-800">
          <button
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2.5 w-full text-sm font-medium text-gray-600 hover:text-red-400 hover:bg-red-950/40 rounded-lg transition-colors"
          >
            <LogOut size={17} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto bg-black">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
