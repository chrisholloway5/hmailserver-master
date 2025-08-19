'use client'

import * as React from 'react'
import { useAuth } from '@/components/auth-provider'
import { useSocket } from '@/components/socket-provider'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Mail, Users, Shield, Activity, TrendingUp, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

interface DashboardStats {
  totalEmails: number
  queuedEmails: number
  activeUsers: number
  blockedIPs: number
  cpuUsage: number
  memoryUsage: number
  diskUsage: number
  uptime: string
}

interface RecentActivity {
  id: string
  type: 'email' | 'security' | 'system'
  message: string
  timestamp: Date
  severity: 'info' | 'warning' | 'error'
}

export function Dashboard() {
  const { user, isLoading: authLoading } = useAuth()
  const { socket, isConnected } = useSocket()
  const [stats, setStats] = React.useState<DashboardStats | null>(null)
  const [recentActivity, setRecentActivity] = React.useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = React.useState(true)

  // Fetch initial dashboard data
  React.useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsResponse, activityResponse] = await Promise.all([
          fetch('/api/dashboard/stats'),
          fetch('/api/dashboard/activity')
        ])

        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setStats(statsData)
        }

        if (activityResponse.ok) {
          const activityData = await activityResponse.json()
          setRecentActivity(activityData)
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    if (user && !authLoading) {
      fetchDashboardData()
    }
  }, [user, authLoading])

  // Listen for real-time updates
  React.useEffect(() => {
    if (!socket || !isConnected) return

    const handleStatsUpdate = (newStats: DashboardStats) => {
      setStats(newStats)
    }

    const handleActivityUpdate = (activity: RecentActivity) => {
      setRecentActivity(prev => [activity, ...prev.slice(0, 9)])
    }

    socket.on('dashboard:stats', handleStatsUpdate)
    socket.on('dashboard:activity', handleActivityUpdate)

    return () => {
      socket.off('dashboard:stats', handleStatsUpdate)
      socket.off('dashboard:activity', handleActivityUpdate)
    }
  }, [socket, isConnected])

  if (authLoading || isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Access Denied
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Please log in to access the dashboard.
          </p>
        </div>
      </div>
    )
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'email':
        return <Mail className="h-4 w-4" />
      case 'security':
        return <Shield className="h-4 w-4" />
      case 'system':
        return <Activity className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'info':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      default:
        return <CheckCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const formatUptime = (uptime: string) => {
    // Assuming uptime is in seconds
    const seconds = parseInt(uptime)
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                hMailServer Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-300">
                Welcome, {user.name}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <div className="flex items-center">
              <Mail className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Emails</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.totalEmails?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Queue</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.queuedEmails?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Users</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.activeUsers?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-red-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Blocked IPs</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats?.blockedIPs?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* System Resources and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* System Resources */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              System Resources
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">CPU Usage</span>
                  <span className="font-medium">{stats?.cpuUsage || 0}%</span>
                </div>
                <div className="mt-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div 
                    className="h-2 bg-blue-500 rounded-full transition-all duration-300"
                    style={{ width: `${stats?.cpuUsage || 0}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Memory Usage</span>
                  <span className="font-medium">{stats?.memoryUsage || 0}%</span>
                </div>
                <div className="mt-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div 
                    className="h-2 bg-green-500 rounded-full transition-all duration-300"
                    style={{ width: `${stats?.memoryUsage || 0}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Disk Usage</span>
                  <span className="font-medium">{stats?.diskUsage || 0}%</span>
                </div>
                <div className="mt-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div 
                    className="h-2 bg-yellow-500 rounded-full transition-all duration-300"
                    style={{ width: `${stats?.diskUsage || 0}%` }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Uptime</span>
                  <span className="font-medium">{stats?.uptime ? formatUptime(stats.uptime) : '0m'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Activity
            </h2>
            <div className="space-y-4 max-h-80 overflow-y-auto custom-scrollbar">
              {recentActivity.length > 0 ? (
                recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 dark:text-white">
                        {activity.message}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      {getSeverityIcon(activity.severity)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No recent activity
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}