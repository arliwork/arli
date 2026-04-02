import { SignIn } from '@clerk/nextjs'
import { dark } from '@clerk/themes'

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-slate-400">Sign in to your ARLI account</p>
        </div>
        <SignIn
          appearance={{
            baseTheme: dark,
            elements: {
              card: 'bg-slate-800/50 border border-slate-700',
              headerTitle: 'text-white',
              headerSubtitle: 'text-slate-400',
              socialButtonsBlockButton: 'bg-slate-700 hover:bg-slate-600 border-slate-600',
              formButtonPrimary: 'bg-blue-600 hover:bg-blue-500',
              footerActionLink: 'text-blue-400 hover:text-blue-300',
            },
          }}
        />
      </div>
    </div>
  )
}
