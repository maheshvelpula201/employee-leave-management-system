
import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Copy, Link2, LoaderCircle, RefreshCw, ShieldCheck, XCircle } from 'lucide-react'
import { apiRequest } from './lib/api'
import { getAccessToken } from './lib/auth'
import './InvitationsPage.css'

type Invitation = {
  id: number
  company_id: number
  role: string
  status: string
  max_uses: number | null
  uses_count: number
  created_by: number | null
  revoked_at: string | null
  expires_at: string
  created_at: string
}

type CreatedInvitation = {
  invitation_id: number
  company_id: number
  role: string
  status: string
  max_uses: number | null
  uses_count: number
  expires_at: string
  invitation_token: string
}

export default function InvitationsPage() {
  const [invitations, setInvitations] = useState<Invitation[]>([])
  const [role, setRole] = useState('EMPLOYEE')
  const [unlimited, setUnlimited] = useState(false)
  const [maxUses, setMaxUses] = useState('3')
  const [expiryDays, setExpiryDays] = useState('3')
  const [created, setCreated] = useState<CreatedInvitation | null>(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [revokingId, setRevokingId] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [copied, setCopied] = useState(false)

  const token = getAccessToken()

  const loadInvitations = useCallback(async () => {
    if (!token) {
      setError('Your session is missing. Please sign in again.')
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const data = await apiRequest<Invitation[]>('/invitations/', {
        token,
      })
      setInvitations(data)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not load invitations.',
      )
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    void loadInvitations()
  }, [loadInvitations])

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setNotice('')
    setCreated(null)

    const uses = Number(maxUses)
    const days = Number(expiryDays)

    if (!unlimited && (!Number.isInteger(uses) || uses < 1)) {
      setError('Enter a valid usage limit of at least 1.')
      return
    }

    if (!Number.isInteger(days) || days < 1 || days > 90) {
      setError('Expiration must be between 1 and 90 days.')
      return
    }

    if (!token) {
      setError('Your session is missing. Please sign in again.')
      return
    }

    setCreating(true)

    try {
      const result = await apiRequest<CreatedInvitation>('/invitations/', {
        method: 'POST',
        token,
        body: {
          role,
          max_uses: unlimited ? null : uses,
          expires_in_days: days,
        },
      })

      setCreated(result)
      setNotice('Invitation created. Copy the link below to share it.')
      await loadInvitations()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not create invitation.',
      )
    } finally {
      setCreating(false)
    }
  }

  async function handleCopy() {
    if (!created) return

    const url = new URL('/invite', window.location.origin)
    url.searchParams.set('token', created.invitation_token)

    try {
      await navigator.clipboard.writeText(url.toString())
      setCopied(true)
      setNotice('Invitation link copied.')
    } catch {
      setError('Could not copy automatically. Copy the link from the field.')
    }
  }

  async function handleRevoke(invitationId: number) {
    if (!token) {
      setError('Your session is missing. Please sign in again.')
      return
    }

    setError('')
    setNotice('')
    setRevokingId(invitationId)

    try {
      await apiRequest(`/invitations/${invitationId}/revoke`, {
        method: 'POST',
        token,
      })

      setNotice('Invitation revoked.')
      await loadInvitations()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not revoke invitation.',
      )
    } finally {
      setRevokingId(null)
    }
  }

  function invitationUrl(invitation: Invitation) {
    return invitation.status === 'PENDING' ? 'Active link' : 'Unavailable'
  }

  return (
    <div className="invitations-page">
      <section className="invitation-intro">
        <div className="invitation-intro-icon">
          <Link2 size={22} />
        </div>
        <div>
          <h2>Invite people to your workspace</h2>
          <p>
            Create secure invitation links with a fixed role, usage limit,
            and expiration date.
          </p>
        </div>
      </section>

      {error && <p className="invitation-message error" role="alert">{error}</p>}
      {notice && <p className="invitation-message success" role="status">{notice}</p>}

      <section className="invitation-panel">
        <div className="invitation-panel-heading">
          <div>
            <h2>Create an invitation</h2>
            <p>The assigned role cannot be changed during registration.</p>
          </div>
          <ShieldCheck size={22} />
        </div>

        <form className="invitation-form" onSubmit={handleCreate}>
          <div className="invitation-field">
            <label htmlFor="invite-role">Role</label>
            <select
              id="invite-role"
              value={role}
              onChange={(event) => setRole(event.target.value)}
            >
              <option value="EMPLOYEE">Employee</option>
              <option value="MANAGER">Manager</option>
              <option value="HR">HR</option>
            </select>
          </div>

          <div className="invitation-field">
            <label htmlFor="invite-expiry">Expires in</label>
            <select
              id="invite-expiry"
              value={expiryDays}
              onChange={(event) => setExpiryDays(event.target.value)}
            >
              <option value="1">1 day</option>
              <option value="3">3 days</option>
              <option value="7">7 days</option>
              <option value="14">14 days</option>
              <option value="30">30 days</option>
              <option value="90">90 days</option>
            </select>
          </div>

          <div className="invitation-field">
            <label htmlFor="invite-uses">Maximum registrations</label>
            <input
              id="invite-uses"
              type="number"
              min="1"
              value={maxUses}
              disabled={unlimited}
              onChange={(event) => setMaxUses(event.target.value)}
              required={!unlimited}
            />
          </div>

          <label className="invitation-checkbox">
            <input
              type="checkbox"
              checked={unlimited}
              onChange={(event) => setUnlimited(event.target.checked)}
            />
            Allow unlimited registrations
          </label>

          <button className="invitation-primary-button" type="submit" disabled={creating}>
            {creating ? <LoaderCircle className="invitation-spinner" size={17} /> : <Link2 size={17} />}
            {creating ? 'Creating...' : 'Create invitation link'}
          </button>
        </form>

        {created && (
          <div className="created-invitation">
            <h3>Invitation ready</h3>
            <p>
              Role: <strong>{created.role}</strong> · Expires:{' '}
              {new Date(created.expires_at).toLocaleString()}
            </p>
            <div className="invitation-link-row">
              <input
                aria-label="Generated invitation link"
                readOnly
                value={(() => {
                  const url = new URL('/invite', window.location.origin)
                  url.searchParams.set('token', created.invitation_token)
                  return url.toString()
                })()}
                onFocus={(event) => event.currentTarget.select()}
              />
              <button type="button" onClick={handleCopy}>
                <Copy size={16} />
                {copied ? 'Copied' : 'Copy link'}
              </button>
            </div>
            <p className="invitation-security-note">
              Anyone with this link can register until it expires, is revoked,
              or reaches its usage limit. Share it only with the intended people.
            </p>
          </div>
        )}
      </section>

      <section className="invitation-panel">
        <div className="invitation-panel-heading">
          <div>
            <h2>Invitation links</h2>
            <p>Review usage, expiration, and current status.</p>
          </div>
          <button
            className="invitation-refresh-button"
            type="button"
            onClick={() => void loadInvitations()}
            disabled={loading}
            aria-label="Refresh invitations"
          >
            <RefreshCw size={17} />
          </button>
        </div>

        {loading ? (
          <div className="invitation-empty">
            <LoaderCircle className="invitation-spinner" size={22} />
            <p>Loading invitations...</p>
          </div>
        ) : invitations.length === 0 ? (
          <div className="invitation-empty">
            <Link2 size={25} />
            <h3>No invitations yet</h3>
            <p>Create your first invitation link above.</p>
          </div>
        ) : (
          <div className="invitation-table-wrap">
            <table className="invitation-table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Usage</th>
                  <th>Expires</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {invitations.map((invitation) => (
                  <tr key={invitation.id}>
                    <td>
                      <strong>{invitation.role}</strong>
                    </td>
                    <td>
                      {invitation.uses_count} / {invitation.max_uses ?? 'Unlimited'}
                    </td>
                    <td>{new Date(invitation.expires_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`invitation-status ${invitation.status.toLowerCase()}`}>
                        {invitation.status}
                      </span>
                    </td>
                    <td>
                      {invitation.status === 'PENDING' ? (
                        <button
                          className="invitation-revoke-button"
                          type="button"
                          disabled={revokingId === invitation.id}
                          onClick={() => void handleRevoke(invitation.id)}
                        >
                          <XCircle size={15} />
                          {revokingId === invitation.id ? 'Revoking...' : 'Revoke'}
                        </button>
                      ) : (
                        <span className="invitation-unavailable">{invitationUrl(invitation)}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
