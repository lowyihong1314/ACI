import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getMonthlyMachineSummary,
  getMonthlyPlantSummary,
  getYtdSummary,
} from '../../api/production'

function currentMonth() {
  return new Date().toISOString().slice(0, 7)
}

function previousMonths(count = 6) {
  const items = []
  const current = new Date()
  current.setDate(1)

  for (let index = count - 1; index >= 0; index -= 1) {
    const value = new Date(current.getFullYear(), current.getMonth() - index, 1)
    const year = value.getFullYear()
    const month = String(value.getMonth() + 1).padStart(2, '0')
    items.push(`${year}-${month}`)
  }
  return items
}

function formatNumber(value) {
  if (value === null || value === undefined) {
    return '-'
  }
  return Number(value).toFixed(2)
}

export default function DashboardPage() {
  const [selectedMonth, setSelectedMonth] = useState(currentMonth())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [machineSummary, setMachineSummary] = useState([])
  const [plantSummary, setPlantSummary] = useState([])
  const [ytdSummary, setYtdSummary] = useState(null)
  const [trendData, setTrendData] = useState([])

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true)
      setError('')
      try {
        const [year, month] = selectedMonth.split('-')
        const [machineResponse, plantResponse, ytdResponse] = await Promise.all([
          getMonthlyMachineSummary(selectedMonth),
          getMonthlyPlantSummary(selectedMonth),
          getYtdSummary(year, month),
        ])

        setMachineSummary(machineResponse.items || [])
        setPlantSummary(plantResponse.items || [])
        setYtdSummary(ytdResponse.item || null)

        const months = previousMonths(6)
        const trendResponses = await Promise.all(
          months.map(async (monthKey) => {
            const response = await getMonthlyPlantSummary(monthKey)
            const totals = (response.items || []).reduce(
              (accumulator, item) => {
                accumulator.actual += Number(item.actual_output_mt || 0)
                accumulator.planned += Number(item.planned_output_mt || 0)
                return accumulator
              },
              { actual: 0, planned: 0 },
            )
            return {
              month: monthKey,
              actual: totals.actual,
              planned: totals.planned,
            }
          }),
        )
        setTrendData(trendResponses)
      } catch (requestError) {
        setError(requestError.message || 'Unable to load dashboard.')
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [selectedMonth])

  const topMachines = [...machineSummary]
    .sort((left, right) => Number(right.actual_output_mt || 0) - Number(left.actual_output_mt || 0))
    .slice(0, 6)

  return (
    <section className="module-card dashboard-shell">
      <div className="module-header">
        <div>
          <p className="content-label">Dashboard</p>
          <h2>Raw Data Performance Overview</h2>
          <p className="card-description">
            Month-by-month view of actual output, planned output and current YTD attainment from the imported workbooks.
          </p>
        </div>
        <label className="field compact-field">
          <span>Month</span>
          <input type="month" value={selectedMonth} onChange={(event) => setSelectedMonth(event.target.value)} />
        </label>
      </div>

      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading dashboard...</p> : null}

      {!loading ? (
        <>
          <div className="dashboard-kpi-grid">
            <article className="kpi-card accent-card">
              <span className="content-label">YTD Actual</span>
              <strong>{formatNumber(ytdSummary?.actual_output_mt)} MT</strong>
            </article>
            <article className="kpi-card dark-card">
              <span className="content-label">YTD Planned</span>
              <strong>{formatNumber(ytdSummary?.planned_output_mt)} MT</strong>
            </article>
            <article className="kpi-card light-card">
              <span className="content-label">YTD Reject</span>
              <strong>{formatNumber(ytdSummary?.rejected_output_mt)} MT</strong>
            </article>
            <article className="kpi-card light-card">
              <span className="content-label">YTD Efficiency</span>
              <strong>{formatNumber(ytdSummary?.output_efficiency_pct)}%</strong>
            </article>
          </div>

          <div className="chart-grid chart-grid-wide">
            <article className="chart-card">
              <div className="chart-card-head">
                <p className="content-label">6-Month Trend</p>
                <h3 className="section-title">Actual vs Planned Output</h3>
              </div>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="month" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Line type="monotone" dataKey="actual" stroke="#f05d3d" strokeWidth={3} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="planned" stroke="#14202b" strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </article>

            <article className="chart-card">
              <div className="chart-card-head">
                <p className="content-label">Plant Performance</p>
                <h3 className="section-title">Actual Output by Plant</h3>
              </div>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={plantSummary}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="plant_code" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Bar dataKey="actual_output_mt" fill="#f29d35" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="planned_output_mt" fill="#14202b" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </article>
          </div>

          <div className="chart-grid">
            <article className="chart-card">
              <div className="chart-card-head">
                <p className="content-label">Top Machines</p>
                <h3 className="section-title">Monthly Actual Output</h3>
              </div>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={topMachines} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" stroke="#6b7280" />
                    <YAxis type="category" dataKey="machine_name" stroke="#6b7280" width={90} />
                    <Tooltip />
                    <Bar dataKey="actual_output_mt" fill="#f05d3d" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </article>

            <article className="chart-card">
              <div className="chart-card-head">
                <p className="content-label">Plant Attainment</p>
                <h3 className="section-title">Plan Attainment by Plant</h3>
              </div>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={plantSummary}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="plant_code" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Bar dataKey="plan_attainment_pct" fill="#22c55e" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </article>
          </div>
        </>
      ) : null}
    </section>
  )
}
