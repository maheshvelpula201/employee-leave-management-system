// frontend/src/ProfilePage.tsx

import { useEffect, useState, type FormEvent } from 'react'
import { User, LoaderCircle, ShieldCheck, CheckCircle2 } from 'lucide-react'
import { apiRequest } from './lib/api'
import { getAccessToken } from './lib/auth'
import './ProfilePage.css'

type UserProfile = {
  id: number
  name: string
  email: string
  role: string
  company_id: number
  phone: string | null
  department: string | null
  designation: string | null
  employment_status: string | null
  joining_date: string | null
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [department, setDepartment] = useState('')
  const [designation, setDesignation] = useState('')
  
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const token = getAccessToken()

  useEffect(() => {
    async function loadProfile() {
      if (!token) {
        setError('Session missing. Please sign in again.')
        setLoading(false)
        return
      }

      try {
        const data = await apiRequest<UserProfile>('/staff/profile', { token })
        setProfile(data)
        setName(data.name || '')
        setPhone(data.phone || '')
        setDepartment(data.department || '')
        setDesignation(data.designation || '')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not load profile.')
      } finally {
        setLoading(false)
      }
    }

    void loadProfile()
  }, [token])

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError('')
    setSuccess('')
    if (!token) return

    setSaving(true)
    try {
      const updated = await apiRequest<UserProfile>('/staff/profile', {
        method: 'PUT',
        token,
        body: {
          name: name.trim(),
          phone: phone.trim() ? phone.trim() : null,
          department: department.trim() ? department.trim() : null,
          designation: designation.trim() ? designation.trim() : null,
        },
      })
      setProfile(updated)
      setSuccess('Profile updated successfully and synchronized to the staff directory.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
        <LoaderCircle className="profile-spinner" size={28} />
      </div>
    )
  }

  return (
    <div className="profile-page-container">
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-header-icon">
            <User size={24} />
          </div>
          <div>
            <h2>My Professional Profile</h2>
            <p>Update your professional details visible in the company staff directory.</p>
          </div>
        </div>

        {error && <p className="profile-message error" role="alert">{error}</p>}
        {success && <p className="profile-message success" role="status"><CheckCircle2 size={16}/>{success}</p>}

        <form onSubmit={handleSave} className="profile-form">
          <div className="profile-field">
            <label htmlFor="profile-name">Full Name</label>
            <input
              id="profile-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={150}
            />
          </div>

          <div className="profile-field">
            <label htmlFor="profile-email">Work Email (Managed)</label>
            <input
              id="profile-email"
              type="email"
              value={profile?.email || ''}
              disabled
            />
          </div>

          <div className="profile-field">
            <label htmlFor="profile-phone">Phone Number</label>
            <input
              id="profile-phone"
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (555) 000-0000"
            />
          </div>

          <div className="profile-grid-row">
            <div className="profile-field">
              <label htmlFor="profile-dept">Department</label>
              <input
                id="profile-dept"
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
              />
            </div>
            <div className="profile-field">
              <label htmlFor="profile-desig">Job Title / Designation</label>
              <input
                id="profile-desig"
                type="text"
                value={designation}
                onChange={(e) => setDesignation(e.target.value)}
              />
            </div>
          </div>

          <div className="profile-meta-note">
            <strong>Role & Tenant:</strong> {profile?.role} · Company ID: {profile?.company_id} (Admin-controlled fields cannot be edited here).
          </div>

          <button
            type="submit"
            className="profile-submit-btn"
            disabled={saving}
          >
            {saving ? <LoaderCircle className="profile-spinner" size={16} /> : <ShieldCheck size={16} />}
            {saving ? 'Saving Profile...' : 'Save Profile'}
          </button>
        </form>
      </div>
    </div>
  )
}