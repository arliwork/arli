'use client'

import { useState } from 'react'

interface PaymentModalProps {
  itemType: 'agent' | 'skill'
  itemId: string
  itemName: string
  price: number
  sellerId: string
  onClose: () => void
  onSuccess: () => void
}

export default function PaymentModal({ 
  itemType, 
  itemId, 
  itemName, 
  price, 
  sellerId,
  onClose, 
  onSuccess 
}: PaymentModalProps) {
  const [step, setStep] = useState<'confirm' | 'processing' | 'success' | 'error'>('confirm')
  const [error, setError] = useState<string | null>(null)
  const [txId, setTxId] = useState<string | null>(null)

  // Calculate fees
  const platformFee = price * 0.10
  const creatorRoyalty = price * 0.05
  const sellerReceives = price - platformFee - creatorRoyalty
  const total = price

  const handlePurchase = async () => {
    setStep('processing')

    try {
      // In real implementation:
      // 1. Call ICP ledger to transfer ICP
      // 2. Call experience_registry canister to transfer ownership
      // 3. Call agent_nft canister to transfer NFT
      
      // Mock processing
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Generate mock tx ID
      setTxId(`tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
      setStep('success')
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Purchase failed')
      setStep('error')
    }
  }

  if (step === 'processing') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
          <h3 className="text-lg font-semibold">Processing Payment...</h3>
          <p className="text-gray-500 mt-2">Please wait while we confirm the transaction</p>
        </div>
      </div>
    )
  }

  if (step === 'success') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✓</span>
          </div>
          <h3 className="text-xl font-bold text-green-800 mb-2">Purchase Complete!</h3>
          <p className="text-gray-600 mb-4">
            You now own <strong>{itemName}</strong>
          </p>
          {txId && (
            <div className="bg-gray-100 rounded p-3 mb-4">
              <div className="text-sm text-gray-600">Transaction ID</div>
              <div className="font-mono text-sm">{txId}</div>
            </div>
          )}
          <button 
            onClick={onClose}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700"
          >
            Done
          </button>
        </div>
      </div>
    )
  }

  if (step === 'error') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✕</span>
          </div>
          <h3 className="text-xl font-bold text-red-800 mb-2">Purchase Failed</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="flex gap-3 justify-center">
            <button 
              onClick={() => setStep('confirm')}
              className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg font-medium hover:bg-gray-300"
            >
              Try Again
            </button>
            <button 
              onClick={onClose}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Complete Purchase</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600">{itemType === 'agent' ? 'Agent' : 'Skill'}</span>
            <span className="font-medium">{itemName}</span>
          </div>
          <div className="flex items-center justify-between text-lg font-bold">
            <span>Price</span>
            <span>${price.toFixed(2)}</span>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Platform Fee (10%)</span>
            <span>${platformFee.toFixed(2)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Creator Royalty (5%)</span>
            <span>${creatorRoyalty.toFixed(2)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Seller Receives</span>
            <span className="text-green-600">${sellerReceives.toFixed(2)}</span>
          </div>
          <div className="border-t pt-3 flex items-center justify-between font-bold">
            <span>Total</span>
            <span>${total.toFixed(2)}</span>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-3 mb-6">
          <div className="text-sm text-blue-800">
            <span className="font-semibold">Payment Method:</span> ICP
          </div>
          <div className="text-xs text-blue-600 mt-1">
            ~{(total / 5).toFixed(2)} ICP at current rate
          </div>
        </div>

        <button 
          onClick={handlePurchase}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Confirm Purchase
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          By confirming, you agree to transfer the specified amount from your wallet.
        </p>
      </div>
    </div>
  )
}
