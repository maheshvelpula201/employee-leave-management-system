
import { useState, type FormEvent } from 'react'
import { Link2, ShieldCheck } from 'lucide-react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { apiRequest } from './lib/api'
import './InvitationRegistrationPage.css'

type InvitationAcceptanceResponse = {
  message: string
  user_id: number
  name: string
  email: string
  role: string
  company_id: number
  is_active: boolean
}

export default function InvitationRegistrationPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') ?? ''

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (!token) {
      setError('This invitation link is missing its token.')
      return
    }

    if (password.length < 8) {
      setError('Your password must contain at least 8 characters.')
      return
    }

    if (password !== confirmPassword) {
      setError('Your passwords do not match.')
      return
    }

    setLoading(true)

    try {
      const response =
        await apiRequest<InvitationAcceptanceResponse>(
          '/invitations/accept',
          {
            method: 'POST',
            body: {
              token,
              name: name.trim(),
              email: email.trim().toLowerCase(),
              password,
            },
          },
        )

      setSuccess(
        `Welcome, ${response.name}! Your ${response.role} account has been created. You can now sign in.`,
      )

      // Give the user time to read the success message before navigating.
      window.setTimeout(() => {
        navigate('/', { replace: true })
      }, 1800)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Registration failed. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="invitation-registration-page">
      <section className="invitation-registration-card">
        <div className="registration-brand">
          <div className="registration-brand-icon">
            <Link2 size={23} />
          </div>
          <div>
            <h1>Northstar</h1>
            <p>HR Management Platform</p>
          </div>
        </div>

        <div className="registration-heading">
          <div className="registration-shield">
            <ShieldCheck size={25} />
          </div>
          <p className="registration-eyebrow">TEAM INVITATION</p>
          <h2>Join your workspace</h2>
          <p>
            Create your account using the invitation link you received.
          </p>
        </div>

        <form className="invitation-registration-form" onSubmit={handleSubmit}>
          <label htmlFor="registration-name">Full name</label>
          <input
            id="registration-name"
            type="text"
            autoComplete="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Enter your full name"
            maxLength={150}
            required
          />

          <label htmlFor="registration-email">Email address</label>
          <input
            id="registration-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@company.com"
            required
          />

          <label htmlFor="registration-password">Password</label>
          <input
            id="registration-password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="At least 8 characters"
            minLength={8}
            maxLength={128}
            required
          />

          <label htmlFor="registration-confirm-password">
            Confirm password
          </label>
          <input
            id="registration-confirm-password"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Enter your password again"
            minLength={8}
            maxLength={128}
            required
          />

          {error && (
            <p className="registration-message error" role="alert">
              {error}
            </p>
          )}

          {success && (
            <p className="registration-message success" role="status">
              {success}
            </p>
          )}

          <button type="submit" disabled={loading || !token}>
            {loading ? 'Creating account...' : 'Create my account'}
          </button>
        </form>

        <p className="registration-login-link">
          Already have an account? <a href="/">Sign in</a>
        </p>

        <p className="registration-footer">
          Your role and company membership are determined by your invitation.
        </p>
      </section>
    </main>
  )
}
