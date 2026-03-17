import { useEffect, useState } from 'react'

import {
  getMonthlyMachineSummary,
  getMonthlyPlantSummary,
  getYtdSummary,
} from '../../api/production'

function currentMonth() {
  return new Date().toISOString().slice(0, 7)
}

function formatNumber(value) {
  if (value === null || value === undefined) {
    return '-'
  }
  return Number(value).toFixed(2)
}

export default function MonthlySummaryPage() {
  const [selectedMonth, setSelectedMonth] = useState(currentMonth())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [machineSummary, setMachineSummary] = useState([])
  const [plantSummary, setPlantSummary] = useState([])
  const [ytdSummary, setYtdSummary] = useState(null)

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError('')
      const [year, month] = selectedMonth.split('-')
      try {
        const [machineResponse, plantResponse, ytdResponse] = await Promise.all([
          getMonthlyMachineSummary(selectedMonth),
          getMonthlyPlantSummary(selectedMonth),
          getYtdSummary(year, month),
        ])
        setMachineSummary(machineResponse.items || [])
        setPlantSummary(plantResponse.items || [])
        setYtdSummary(ytdResponse.item || null)
      } catch (requestError) {
        setError(requestError.message || 'Unable to load monthly summary.')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [selectedMonth])

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Monthly Summary</p>
          <h2>Plan vs Actual Reporting</h2>
        </div>
        <label className="field compact-field">
          <span>Month</span>
          <input type="month" value={selectedMonth} onChange={(event) => setSelectedMonth(event.target.value)} />
        </label>
      </div>

      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading monthly summary...</p> : null}

      {!loading && ytdSummary ? (
        <div className="summary-card-grid">
          <div className="summary-card">
            <p className="content-label">YTD Actual</p>
            <strong>{formatNumber(ytdSummary.actual_output_mt)} MT</strong>
          </div>
          <div className="summary-card">
            <p className="content-label">YTD Planned</p>
            <strong>{formatNumber(ytdSummary.planned_output_mt)} MT</strong>
          </div>
          <div className="summary-card">
            <p className="content-label">YTD Reject</p>
            <strong>{formatNumber(ytdSummary.rejected_output_mt)} MT</strong>
          </div>
          <div className="summary-card">
            <p className="content-label">YTD Efficiency</p>
            <strong>{formatNumber(ytdSummary.output_efficiency_pct)}%</strong>
          </div>
        </div>
      ) : null}

      {!loading ? (
        <>
          <div className="summary-card-grid">
            {plantSummary.map((item) => (
              <div className="summary-card" key={item.plant_id}>
                <p className="content-label">{item.plant_name}</p>
                <strong>{formatNumber(item.actual_output_mt)} MT</strong>
                <span>Planned {formatNumber(item.planned_output_mt)} MT</span>
                <span>Reject {formatNumber(item.rejected_output_mt)} MT</span>
                <span>Plan Attainment {formatNumber(item.plan_attainment_pct)}%</span>
              </div>
            ))}
          </div>

          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Plant</th>
                  <th>Machine</th>
                  <th>Actual</th>
                  <th>Planned</th>
                  <th>Reject</th>
                  <th>Plan Attainment%</th>
                </tr>
              </thead>
              <tbody>
                {machineSummary.map((item) => (
                  <tr key={item.machine_id}>
                    <td>{item.plant_code}</td>
                    <td>{item.machine_name}</td>
                    <td>{formatNumber(item.actual_output_mt)}</td>
                    <td>{formatNumber(item.planned_output_mt)}</td>
                    <td>{formatNumber(item.rejected_output_mt)}</td>
                    <td>{formatNumber(item.plan_attainment_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  )
}
