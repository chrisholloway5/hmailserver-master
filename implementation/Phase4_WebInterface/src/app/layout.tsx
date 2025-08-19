import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ClientProviders } from '@/components/client-providers'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    template: '%s | hMailServer',
    default: 'hMailServer - Next-Generation Email Platform',
  },
  description: 'Enterprise-grade email server with AI-powered features and modern web interface',
  keywords: ['email', 'server', 'enterprise', 'AI', 'machine learning', 'security'],
  authors: [{ name: 'hMailServer Development Team' }],
  creator: 'hMailServer Development Team',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://hmailserver.com',
    title: 'hMailServer - Next-Generation Email Platform',
    description: 'Enterprise-grade email server with AI-powered features',
    siteName: 'hMailServer',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'hMailServer - Next-Generation Email Platform',
    description: 'Enterprise-grade email server with AI-powered features',
  },
  robots: {
    index: false, // Admin interface should not be indexed
    follow: false,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  )
}