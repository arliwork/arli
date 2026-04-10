'use client'

import { useEffect, useState } from 'react'
import { useAuth, UserButton } from '@clerk/nextjs'
import Link from 'next/link'
import toast from 'react-hot-toast'
// import { CREDIT_PACKAGES } from '@arli/types'
const CREDIT_PACKAGES = [
  { id: 'starter', name: 'Starter', credits: 1000, price: 10 },
  { id: 'growth', name: 'Growth', credits: 5000, price: 45 },
  { id: 'enterprise', name: 'Enterprise', credits: 20000, price: 150 }
]

interface Company {
  id: string
  name: string
  credits: number
}

export default function BillingPage() {
  const { getToken, userId } = useAuth()
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [purchasing, setPurchasing] = useState<string | null>(null)

  useEffect(() => {
    if (userId) {
      fetchCompanies()
    }
  }, [userId])

  const fetchCompanies = async () => {
    try {
      const token = await getToken()
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/companies`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch')
      
      const data = await response.json()
      setCompanies(data.companies || [])
    } catch (error) {
      toast.error('Failed to load companies')
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = async (packageId: string) => {
    if (companies.length === 0) {
      toast.error('Create a company first')
      return
    }
    
    setPurchasing(packageId)
    try {
      const token = await getToken()
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/billing/checkout`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            packageId,
            companyId: companies[0].id
          })
        }
      )

      if (!response.ok) throw new Error('Failed to create checkout')

      const { url } = await response.json()
      window.location.href = url
    } catch (error) {
      toast.error('Failed to start checkout')
      setPurchasing(null)
    }
  }

  const handlePortal = async () => {
    try {
      const token = await getToken()
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/billing/portal`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )

      if (!response.ok) throw new Error('Failed to create portal session')

      const { url } = await response.json()
      window.location.href = url
    } catch (error) {
      toast.error('Failed to open billing portal')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                A
              </div>
              <span className="text-xl font-bold">Billing</span>
            </Link>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/companies" as="/companies" className="text-gray-600 hover:text-gray-900">
              Companies
            </Link>
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Credits Overview */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white mb-8">
          <h1 className="text-2xl font-bold mb-2">Credits Balance</h1>
          <p className="text-blue-100 mb-6">
            Credits are used to power your AI agents. Purchase more to keep your companies running.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {companies.map(company => (
              <div key={company.id} className="bg-white/10 backdrop-blur rounded-lg p-4">
                <p className="text-sm text-blue-200">{company.name}</p>
                <p className="text-3xl font-bold">{company.credits.toLocaleString()}</p>
                <p className="text-sm text-blue-200">credits</p>
              </div>
            ))}
            {companies.length === 0 && (
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <p className="text-sm text-blue-200">No companies yet</p>
                <p className="text-3xl font-bold">0</p>
                <p className="text-sm text-blue-200">credits</p>
              </div>
            )}
          </div>
        </div>

        {/* Credit Packages */}
        <h2 className="text-xl font-bold text-gray-900 mb-6">Purchase Credits</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {CREDIT_PACKAGES.map((pkg) => (
            <div
              key={pkg.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <h3 className="text-lg font-bold text-gray-900">{pkg.name}</h3>
              <div className="mt-4 mb-6">
                <span className="text-4xl font-bold text-gray-900">${pkg.priceUsd}</span>
              </div>
              <div className="space-y-2 mb-6">
                <p className="text-2xl font-semibold text-blue-600">
                  {pkg.credits.toLocaleString()} credits
                </p>
                {pkg.bonusCredits > 0 && (
                  <p className="text-sm text-green-600 font-medium">
                    + {pkg.bonusCredits.toLocaleString()} bonus
                  </p>
                )}
                <p className="text-sm text-gray-500">
                  ${(pkg.priceUsd / pkg.credits).toFixed(4)} per credit
                </p>
              </div>
              <button
                onClick={() => handlePurchase(pkg.id)}
                disabled={!!purchasing}
                className="w-full btn-primary py-3 disabled:opacity-50"
              >
                {purchasing === pkg.id ? 'Processing...' : 'Purchase'}
              </button>
            </div>
          ))}
        </div>

        {/* Billing Portal */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-2">Billing History</h3>
          <p className="text-gray-600 mb-4">
            View your past invoices, update payment methods, and manage subscriptions.
          </p>
          <button
            onClick={handlePortal}
            className="btn-secondary"
          >
            Open Billing Portal
          </button>
        </div>
      </main>
    </div>
  )
}
