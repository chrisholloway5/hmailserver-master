'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user'
  permissions: string[]
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  refreshUser: () => Promise<void>
  hasPermission: (permission: string) => boolean
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = React.useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = React.useState<User | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)
  const router = useRouter()

  const login = React.useCallback(async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData.user)
        localStorage.setItem('auth_token', userData.token)
        return true
      }
      
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = React.useCallback(() => {
    setUser(null)
    localStorage.removeItem('auth_token')
    router.push('/login')
  }, [router])

  const refreshUser = React.useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData.user)
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('auth_token')
        setUser(null)
      }
    } catch (error) {
      console.error('Refresh user error:', error)
      localStorage.removeItem('auth_token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const hasPermission = React.useCallback((permission: string): boolean => {
    if (!user) return false
    if (user.role === 'admin') return true
    return user.permissions.includes(permission)
  }, [user])

  // Check authentication on mount
  React.useEffect(() => {
    refreshUser()
  }, [refreshUser])

  // Set up token refresh interval
  React.useEffect(() => {
    if (!user) return

    const refreshInterval = setInterval(() => {
      refreshUser()
    }, 15 * 60 * 1000) // Refresh every 15 minutes

    return () => clearInterval(refreshInterval)
  }, [user, refreshUser])

  const value = React.useMemo(
    () => ({
      user,
      isLoading,
      login,
      logout,
      refreshUser,
      hasPermission,
    }),
    [user, isLoading, login, logout, refreshUser, hasPermission]
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}