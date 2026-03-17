import { useEffect, useState } from 'react'
import DailyBreakdownPage from './pages/production/DailyBreakdownPage'
import DailyProductionPage from './pages/production/DailyProductionPage'
import AnnualTargetPage from './pages/production/AnnualTargetPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import ManageMachinePage from './pages/production/ManageMachinePage'
import MasterDataPage from './pages/production/MasterDataPage'
import MonthlySummaryPage from './pages/production/MonthlySummaryPage'
import './App.css'

const TOKEN_STORAGE_KEY = 'aci-access-token'
const USER_STORAGE_KEY = 'aci-user'

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'fa-solid fa-house' },
  { id: 'production-admin', label: 'Raw Data Admin', icon: 'fa-solid fa-industry' },
  { id: 'profile', label: 'Profile', icon: 'fa-solid fa-id-card' },
]

const productionTabs = [
  { id: 'daily-production', label: 'Daily Product Output' },
  { id: 'daily-breakdown', label: 'Daily Machine Plan' },
  { id: 'monthly-summary', label: 'Monthly Summary' },
  { id: 'manage-machine', label: 'Manage Machine' },
  { id: 'master-data', label: 'Products' },
  { id: 'annual-targets', label: 'Raw Data Import' },
]

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isBootstrapping, setIsBootstrapping] = useState(true)
  const [isProfileSaving, setIsProfileSaving] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [activeItem, setActiveItem] = useState(navItems[0].id)
  const [activeProductionTab, setActiveProductionTab] = useState(productionTabs[0].id)
  const [currentUser, setCurrentUser] = useState(null)
  const [profileMessage, setProfileMessage] = useState('')
  const [profileError, setProfileError] = useState('')
  const [profileForm, setProfileForm] = useState({
    username: '',
    full_name: '',
    email: '',
    current_password: '',
    new_password: '',
  })

  const syncUserState = (user) => {
    setCurrentUser(user)
    setUsername(user.username)
    setProfileForm({
      username: user.username || '',
      full_name: user.full_name || '',
      email: user.email || '',
      current_password: '',
      new_password: '',
    })
    window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  }

  useEffect(() => {
    const bootstrapSession = async () => {
      const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)

      if (!token) {
        setIsBootstrapping(false)
        return
      }

      try {
        const response = await fetch('/api/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error('Session expired')
        }

        const data = await response.json()
        syncUserState(data.user)
        setIsLoggedIn(true)
      } catch (_error) {
        window.localStorage.removeItem(TOKEN_STORAGE_KEY)
        window.localStorage.removeItem(USER_STORAGE_KEY)
        setIsLoggedIn(false)
        setCurrentUser(null)
      } finally {
        setIsBootstrapping(false)
      }
    }

    bootstrapSession()
  }, [])

  const handleLogin = async (event) => {
    event.preventDefault()

    const nextUsername = username.trim()
    if (!nextUsername || !password.trim()) {
      setError('Please enter username and password.')
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: nextUsername,
          password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Login failed')
      }

      window.localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token)
      syncUserState(data.user)
      setPassword('')
      setIsLoggedIn(true)
    } catch (requestError) {
      setError(requestError.message || 'Unable to login.')
      setIsLoggedIn(false)
      setCurrentUser(null)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleLogout = () => {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY)
    window.localStorage.removeItem(USER_STORAGE_KEY)
    setCurrentUser(null)
    setUsername('')
    setPassword('')
    setError('')
    setIsLoggedIn(false)
    setActiveItem(navItems[0].id)
    setActiveProductionTab(productionTabs[0].id)
    setProfileMessage('')
    setProfileError('')
    setProfileForm({
      username: '',
      full_name: '',
      email: '',
      current_password: '',
      new_password: '',
    })
  }

  const handleProfileFieldChange = (event) => {
    const { name, value } = event.target
    setProfileMessage('')
    setProfileError('')
    setProfileForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  const handleProfileSubmit = async (event) => {
    event.preventDefault()

    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      setProfileError('Please login again.')
      setIsLoggedIn(false)
      return
    }

    setIsProfileSaving(true)
    setProfileMessage('')
    setProfileError('')

    try {
      const response = await fetch('/api/auth/profile', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(profileForm),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Unable to update profile.')
      }

      syncUserState(data.user)
      setProfileForm((current) => ({
        ...current,
        current_password: '',
        new_password: '',
      }))
      setProfileMessage(data.message)
    } catch (requestError) {
      setProfileError(requestError.message || 'Unable to update profile.')
    } finally {
      setIsProfileSaving(false)
    }
  }

  if (isBootstrapping) {
    return (
      <main className="auth-shell">
        <section className="login-card loading-card">
          <div className="login-icon">
            <i className="fa-solid fa-spinner fa-spin" aria-hidden="true" />
          </div>
          <p className="loading-text">Checking login session...</p>
        </section>
      </main>
    )
  }

  if (!isLoggedIn) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <div className="auth-copy">
            <p className="eyebrow">ACI Control Center</p>
            <h1>Sign in to enter the workspace.</h1>
            <p className="description">
              Sign in with the Flask backend account running on port `5011`.
            </p>
          </div>

          <form className="login-card" onSubmit={handleLogin}>
            <div className="login-icon">
              <i className="fa-solid fa-user-lock" aria-hidden="true" />
            </div>

            <label className="field">
              <span>Username</span>
              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Enter username"
              />
            </label>

            <label className="field">
              <span>Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter password"
              />
            </label>

            {error ? <p className="error-message">{error}</p> : null}

            <button className="submit-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Login'}
            </button>
          </form>
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <p className="eyebrow">ACI Dashboard</p>
          <h1>Operations Home</h1>
        </div>

        <nav className="navbar" aria-label="Primary">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${activeItem === item.id ? 'active' : ''}`}
              onClick={() => {
                setActiveItem(item.id)
                setProfileMessage('')
                setProfileError('')
              }}
            >
              <i className={item.icon} aria-hidden="true" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <button className="logout-button" type="button" onClick={handleLogout}>
          <i className="fa-solid fa-right-from-bracket" aria-hidden="true" />
          <span>Logout</span>
        </button>
      </header>

      <section className="workspace-grid">
        <aside className="profile-summary-card">
          <div className="profile-summary-head">
            <div className="profile-avatar">
              <i className="fa-solid fa-user" aria-hidden="true" />
            </div>
            <div>
              <p className="content-label">Signed in user</p>
              <h2 className="profile-name">
                {currentUser?.full_name || currentUser?.username || username}
              </h2>
            </div>
          </div>

          <dl className="profile-meta">
            <div>
              <dt>Username</dt>
              <dd>{currentUser?.username || '-'}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{currentUser?.email || '-'}</dd>
            </div>
            <div>
              <dt>Admin</dt>
              <dd>{currentUser?.is_admin ? 'Yes' : 'No'}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{currentUser?.is_active ? 'Active' : 'Inactive'}</dd>
            </div>
          </dl>

          <div className="quick-links">
            <button
              className={`profile-launch-button ${activeItem === 'profile' ? 'active' : ''}`}
              type="button"
              onClick={() => setActiveItem('profile')}
            >
              <i className="fa-solid fa-id-card" aria-hidden="true" />
              <span>Profile</span>
            </button>
            <button
              className={`profile-launch-button ${activeItem === 'production-admin' ? 'active' : ''}`}
              type="button"
              onClick={() => setActiveItem('production-admin')}
            >
              <i className="fa-solid fa-industry" aria-hidden="true" />
              <span>Raw Data Admin</span>
            </button>
          </div>
        </aside>

        {activeItem === 'profile' ? (
          <section className="content-card profile-card">
            <div className="card-heading">
              <p className="content-label">Profile</p>
              <h2>Edit user_data</h2>
              <p className="card-description">
                Update your username, full name, email and password.
              </p>
            </div>

            <form className="profile-form" onSubmit={handleProfileSubmit}>
              <label className="field">
                <span>Username</span>
                <input
                  name="username"
                  type="text"
                  value={profileForm.username}
                  onChange={handleProfileFieldChange}
                  placeholder="Username"
                />
              </label>

              <label className="field">
                <span>Full Name</span>
                <input
                  name="full_name"
                  type="text"
                  value={profileForm.full_name}
                  onChange={handleProfileFieldChange}
                  placeholder="Full name"
                />
              </label>

              <label className="field">
                <span>Email</span>
                <input
                  name="email"
                  type="email"
                  value={profileForm.email}
                  onChange={handleProfileFieldChange}
                  placeholder="Email"
                />
              </label>

              <label className="field">
                <span>Current Password</span>
                <input
                  name="current_password"
                  type="password"
                  value={profileForm.current_password}
                  onChange={handleProfileFieldChange}
                  placeholder="Current password"
                />
              </label>

              <label className="field">
                <span>New Password</span>
                <input
                  name="new_password"
                  type="password"
                  value={profileForm.new_password}
                  onChange={handleProfileFieldChange}
                  placeholder="Leave blank if not changing"
                />
              </label>

              {profileError ? <p className="error-message">{profileError}</p> : null}
              {profileMessage ? <p className="success-message">{profileMessage}</p> : null}

              <button
                className="submit-button"
                type="submit"
                disabled={isProfileSaving}
              >
                {isProfileSaving ? 'Saving...' : 'Save Profile'}
              </button>
            </form>
          </section>
        ) : activeItem === 'production-admin' ? (
          <section className="content-card production-module-shell">
            <div className="card-heading">
              <p className="content-label">Raw Data Workflow</p>
              <h2>Workbook-Driven Production Module</h2>
              <p className="card-description">
                The 3 Excel workbooks are the source of truth for products, machine plans, monthly output and efficiency reporting.
              </p>
            </div>

            <div className="subnav">
              {productionTabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  className={`subnav-item ${activeProductionTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveProductionTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeProductionTab === 'daily-production' ? <DailyProductionPage /> : null}
            {activeProductionTab === 'daily-breakdown' ? <DailyBreakdownPage /> : null}
            {activeProductionTab === 'monthly-summary' ? <MonthlySummaryPage /> : null}
            {activeProductionTab === 'manage-machine' ? <ManageMachinePage /> : null}
            {activeProductionTab === 'master-data' ? <MasterDataPage /> : null}
            {activeProductionTab === 'annual-targets' ? <AnnualTargetPage /> : null}
          </section>
        ) : (
          <DashboardPage />
        )}
      </section>
    </main>
  )
}

export default App
