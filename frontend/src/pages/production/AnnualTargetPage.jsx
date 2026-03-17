import { useEffect, useState } from 'react'

import { getRawDataSummary, triggerRawDataImport } from '../../api/production'

export default function AnnualTargetPage() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [importing, setImporting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await getRawDataSummary()
      setSummary(response)
    } catch (requestError) {
      setError(requestError.message || 'Unable to load raw data summary.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleImport = async () => {
    setImporting(true)
    setMessage('')
    setError('')
    try {
      const response = await triggerRawDataImport()
      setMessage(response.message || 'Raw data import completed.')
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to import raw data.')
    } finally {
      setImporting(false)
    }
  }

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Raw Data Import</p>
          <h2>Workbook Rebuild</h2>
        </div>
        <button className="submit-button" type="button" disabled={importing} onClick={handleImport}>
          {importing ? 'Importing...' : 'Reimport 3 XLSX Files'}
        </button>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading raw data summary...</p> : null}

      {!loading && summary ? (
        <div className="dual-grid">
          <section className="module-card">
            <h3 className="section-title">Workbook Sources</h3>
            <div className="profile-form">
              {Object.entries(summary.files || {}).map(([key, value]) => (
                <label className="field" key={key}>
                  <span>{key}</span>
                  <input value={value} readOnly />
                </label>
              ))}
            </div>
          </section>

          <section className="module-card">
            <h3 className="section-title">Current Row Counts</h3>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Dataset</th>
                    <th>Rows</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(summary.counts || {}).map(([key, value]) => (
                    <tr key={key}>
                      <td>{key}</td>
                      <td>{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      ) : null}
    </section>
  )
}
