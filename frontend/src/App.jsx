import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Dashboard from './pages/Dashboard'
import Layout from './components/Layout'
import AgentSettings from './components/AgentSettings'
import AvailabilitySetup from './components/AvailabilitySetup'
import CalendarView from './components/CalendarView'
import AppointmentsTable from './components/AppointmentsTable'
import CallLogs from './components/CallLogs'

function RequireAuth({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="agent" element={<AgentSettings />} />
        <Route path="availability" element={<AvailabilitySetup />} />
        <Route path="calendar" element={<CalendarView />} />
        <Route path="appointments" element={<AppointmentsTable />} />
        <Route path="call-logs" element={<CallLogs />} />
      </Route>
    </Routes>
  )
}
