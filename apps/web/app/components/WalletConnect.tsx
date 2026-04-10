'use client'

import { useState, useEffect } from 'react'

interface Wallet {
  id: string
  name: string
  icon: string
  description: string
}

const WALLETS: Wallet[] = [
  {
    id: 'ii',
    name: 'Internet Identity',
    icon: '🔐',
    description: 'Passkey authentication'
  },
  {
    id: 'plug',
    name: 'Plug Wallet',
    icon: '⚡',
    description: 'Browser extension'
  },
  {
    id: 'stoic',
    name: 'Stoic Wallet',
    icon: '🔷',
    description: 'Web wallet'
  },
  {
    id: 'oisy',
    name: 'OISY Wallet',
    icon: '💎',
    description: 'Smart wallet'
  }
]

export default function WalletConnect() {
  const [isConnected, setIsConnected] = useState(false)
  const [principal, setPrincipal] = useState<string | null>(null)
  const [balance, setBalance] = useState<number>(0)
  const [showWalletModal, setShowWalletModal] = useState(false)
  const [selectedWallet, setSelectedWallet] = useState<string | null>(null)

  useEffect(() => {
    // Check if already connected
    const savedPrincipal = localStorage.getItem('arli_principal')
    if (savedPrincipal) {
      setPrincipal(savedPrincipal)
      setIsConnected(true)
      fetchBalance(savedPrincipal)
    }
  }, [])

  const fetchBalance = async (principalId: string) => {
    // In real implementation: call ICP ledger canister
    // For demo: mock balance
    setBalance(125.50)
  }

  const connectWallet = async (walletId: string) => {
    setSelectedWallet(walletId)
    
    try {
      let principal = ''
      
      switch (walletId) {
        case 'ii':
          // Internet Identity
          principal = await connectInternetIdentity()
          break
        case 'plug':
          principal = await connectPlug()
          break
        case 'stoic':
          principal = await connectStoic()
          break
        case 'oisy':
          principal = await connectOisy()
          break
      }
      
      if (principal) {
        setPrincipal(principal)
        setIsConnected(true)
        localStorage.setItem('arli_principal', principal)
        localStorage.setItem('arli_wallet', walletId)
        setShowWalletModal(false)
        fetchBalance(principal)
      }
    } catch (error) {
      console.error('Connection failed:', error)
      alert('Failed to connect wallet')
    }
    
    setSelectedWallet(null)
  }

  const connectInternetIdentity = async (): Promise<string> => {
    // In real implementation:
    // const authClient = await AuthClient.create()
    // await authClient.login({
    //   identityProvider: 'https://identity.ic0.app',
    // })
    // return authClient.getIdentity().getPrincipal().toText()
    
    // Mock for demo
    return 'rdmx6-jaaaa-aaaaa-aaadq-cai'
  }

  const connectPlug = async (): Promise<string> => {
    // @ts-ignore
    if (window.ic?.plug) {
      // @ts-ignore
      const connected = await window.ic.plug.requestConnect()
      if (connected) {
        // @ts-ignore
        return await window.ic.plug.getPrincipal()
      }
    }
    throw new Error('Plug not installed')
  }

  const connectStoic = async (): Promise<string> => {
    // Stoic connection logic
    return '2vxsx-fae'
  }

  const connectOisy = async (): Promise<string> => {
    // OISY connection logic
    return 'yhabg-5l6'
  }

  const disconnect = () => {
    setIsConnected(false)
    setPrincipal(null)
    setBalance(0)
    localStorage.removeItem('arli_principal')
    localStorage.removeItem('arli_wallet')
  }

  const buyAgent = async (agentId: string, price: number) => {
    if (!isConnected) {
      alert('Please connect wallet first')
      return
    }
    
    if (balance < price) {
      alert('Insufficient balance')
      return
    }
    
    // In real implementation: call canister to transfer ICP
    // const result = await agentCanister.buy_agent(agentId, price)
    
    alert(`Buying agent ${agentId} for $${price}...`)
    // Mock success
    setBalance(prev => prev - price)
  }

  if (isConnected && principal) {
    return (
      <div className="flex items-center gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-green-800">
              {principal.slice(0, 8)}...{principal.slice(-4)}
            </span>
          </div>
          <div className="text-xs text-green-600 mt-1">
            Balance: {balance.toFixed(2)} ICP
          </div>
        </div>
        <button 
          onClick={disconnect}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Disconnect
        </button>
      </div>
    )
  }

  return (
    <>
      <button 
        onClick={() => setShowWalletModal(true)}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        Connect Wallet
      </button>

      {showWalletModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Connect Wallet</h2>
              <button 
                onClick={() => setShowWalletModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              {WALLETS.map((wallet) => (
                <button
                  key={wallet.id}
                  onClick={() => connectWallet(wallet.id)}
                  disabled={selectedWallet === wallet.id}
                  className="w-full flex items-center gap-4 p-4 border rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
                >
                  <span className="text-3xl">{wallet.icon}</span>
                  <div className="text-left flex-1">
                    <div className="font-medium">{wallet.name}</div>
                    <div className="text-sm text-gray-500">{wallet.description}</div>
                  </div>
                  {selectedWallet === wallet.id && (
                    <div className="animate-spin w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full" />
                  )}
                </button>
              ))}
            </div>

            <div className="mt-6 text-center text-sm text-gray-500">
              New to ICP?{' '}
              <a href="https://internetcomputer.org" target="_blank" className="text-blue-600 hover:underline">
                Learn more
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
