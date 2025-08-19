import { NextRequest, NextResponse } from 'next/server'

// Mock recent activity data
const MOCK_ACTIVITIES = [
  {
    id: '1',
    type: 'email',
    message: 'Email from john@example.com processed successfully',
    timestamp: new Date(Date.now() - 300000), // 5 minutes ago
    severity: 'info'
  },
  {
    id: '2',
    type: 'security',
    message: 'Failed login attempt from IP 192.168.1.100',
    timestamp: new Date(Date.now() - 600000), // 10 minutes ago
    severity: 'warning'
  },
  {
    id: '3',
    type: 'system',
    message: 'Mail queue processed: 25 emails delivered',
    timestamp: new Date(Date.now() - 900000), // 15 minutes ago
    severity: 'info'
  },
  {
    id: '4',
    type: 'email',
    message: 'Spam message blocked from suspicious sender',
    timestamp: new Date(Date.now() - 1200000), // 20 minutes ago
    severity: 'warning'
  },
  {
    id: '5',
    type: 'system',
    message: 'Backup completed successfully',
    timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
    severity: 'info'
  },
  {
    id: '6',
    type: 'security',
    message: 'IP 10.0.0.50 added to blocklist',
    timestamp: new Date(Date.now() - 2400000), // 40 minutes ago
    severity: 'error'
  },
  {
    id: '7',
    type: 'email',
    message: 'Large attachment (15MB) processed for admin@company.com',
    timestamp: new Date(Date.now() - 3000000), // 50 minutes ago
    severity: 'info'
  },
  {
    id: '8',
    type: 'system',
    message: 'SSL certificate renewal reminder: expires in 30 days',
    timestamp: new Date(Date.now() - 3600000), // 1 hour ago
    severity: 'warning'
  }
]

export async function GET(request: NextRequest) {
  try {
    // In a real implementation, this would come from:
    // - Application logs
    // - Database activity logs
    // - System event logs
    // - Security monitoring
    
    // Return recent activities sorted by timestamp (newest first)
    const activities = MOCK_ACTIVITIES
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 10) // Return last 10 activities

    return NextResponse.json(activities)
  } catch (error) {
    console.error('Dashboard activity error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch dashboard activity' },
      { status: 500 }
    )
  }
}