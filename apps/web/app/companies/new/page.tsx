'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const TEMPLATES = [
  {
    id: 'content-agency',
    name: 'AI Content Agency',
    description: 'Create viral TikTok and Instagram content on autopilot',
    icon: '📱',
    color: 'from-pink-500 to-purple-600',
    agents: 5,
    setupFee: 199,
    credits: 5000,
    features: ['Trend research', 'Content creation', 'Post scheduling', 'Analytics']
  },
  {
    id: 'dropshipping',
    name: 'Dropshipping Store',
    description: 'Automated product hunting, ads, and order fulfillment',
    icon: '🛒',
    color: 'from-blue-500 to-cyan-500',
    agents: 6,
    setupFee: 299,
    credits: 10000,
    features: ['Product research', 'Ad management', 'Store automation', 'Customer support']
  },
  {
    id: 'saas-micro',
    name: 'Micro-SaaS Builder',
    description: 'Build and launch micro-SaaS products from scratch',
    icon: '🚀',
    color: 'from-green-500 to-emerald-600',
    agents: 5,
    setupFee: 499,
    credits: 8000,
    features: ['Full-stack dev', 'UI/UX design', 'Growth marketing', 'DevOps']
  },
  {
    id: 'custom',
    name: 'Custom Company',
    description: 'Build your own autonomous company from scratch',
    icon: '⚙️',
    color: 'from-gray-500 to-gray-600',
    agents: 1,
    setupFee: 0,
    credits: 1000,
    features: ['Custom configuration', 'Manual setup', 'Flexible structure']
  }
]

export default function NewCompany() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    niche: '',
    description: ''
  })
  const [loading, setLoading] = useState(false)

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId)
    setStep(2)
  }

  const handleSubmit = async () => {
    setLoading(true)
    
    try {
      // TODO: Replace with actual API call
      // await fetch('/api/companies', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     ...formData,
      //     useTemplate: selectedTemplate !== 'custom' ? selectedTemplate : undefined
      //   })
      // })
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      router.push('/dashboard')
    } catch (error) {
      console.error('Failed to create company:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectedTemplateData = TEMPLATES.find(t => t.id === selectedTemplate)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
              A
            </div>
            <span className="text-xl font-bold">New Company</span>
          </Link>
          <div className="text-sm text-gray-500">
            Step {step} of 2
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        {step === 1 ? (
          <div>
            <div className="text-center mb-12">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Choose a Template
              </h1>
              <p className="text-gray-600">
                Start with a proven business model or build your own
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {TEMPLATES.map((template) => (
                <button
                  key={template.id}
                  onClick={() => handleTemplateSelect(template.id)}
                  className="text-left card hover:shadow-lg hover:border-blue-300 transition-all group"
                >
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${template.color} flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform`}>
                    {template.icon}
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {template.name}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {template.description}
                  </p>

                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                    <span>🤖 {template.agents} agents</span>
                    <span>💳 {template.credits.toLocaleString()} credits</span>
                  </div>

                  <div className="space-y-2">
                    {template.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                        <span className="text-green-500">✓</span>
                        {feature}
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 pt-4 border-t flex items-center justify-between">
                    <span className="text-2xl font-bold text-gray-900">
                      ${template.setupFee}
                    </span>
                    <span className="text-blue-600 font-medium group-hover:underline">
                      Select →
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <button
              onClick={() => setStep(1)}
              className="text-gray-600 hover:text-gray-900 mb-6 flex items-center gap-2"
            >
              ← Back to templates
            </button>

            <div className="text-center mb-12">
              <div className={`inline-flex w-16 h-16 rounded-xl bg-gradient-to-br ${selectedTemplateData?.color} items-center justify-center text-4xl mb-4`}>
                {selectedTemplateData?.icon}
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {selectedTemplateData?.name}
              </h1>
              <p className="text-gray-600">
                {selectedTemplateData?.description}
              </p>
            </div>

            <div className="card max-w-xl mx-auto">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Viral Content Co"
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company URL
                  </label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                      arli.ai/c/
                    </span>
                    <input
                      type="text"
                      value={formData.slug}
                      onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                      placeholder="viral-content"
                      className="input rounded-l-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Niche/Industry
                  </label>
                  <select
                    value={formData.niche}
                    onChange={(e) => setFormData({ ...formData, niche: e.target.value })}
                    className="input"
                  >
                    <option value="">Select a niche</option>
                    <option value="fitness">Fitness</option>
                    <option value="crypto">Crypto/Finance</option>
                    <option value="beauty">Beauty</option>
                    <option value="tech">Technology</option>
                    <option value="food">Food</option>
                    <option value="travel">Travel</option>
                    <option value="education">Education</option>
                    <option value="gaming">Gaming</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="What does your company do?"
                    rows={3}
                    className="input"
                  />
                </div>

                <div className="border-t pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-gray-600">Setup Fee</span>
                    <span className="font-semibold">${selectedTemplateData?.setupFee}</span>
                  </div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="text-gray-600">Initial Credits</span>
                    <span className="font-semibold">{selectedTemplateData?.credits.toLocaleString()}</span>
                  </div>
                  
                  <button
                    onClick={handleSubmit}
                    disabled={!formData.name || !formData.slug || loading}
                    className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <span className="animate-spin">⏳</span>
                        Creating...
                      </span>
                    ) : (
                      `Create Company - $${selectedTemplateData?.setupFee}`
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}