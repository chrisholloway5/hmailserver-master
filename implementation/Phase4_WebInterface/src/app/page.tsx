import { Metadata } from 'next'
import { Dashboard } from '@/components/dashboard'

export const metadata: Metadata = {
  title: 'Dashboard',
  description: 'hMailServer administration dashboard',
}

export default function HomePage() {
  return <Dashboard />
}