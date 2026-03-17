import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { getDailyPlanVsActual, getMachines } from '../../api/production'

function currentDate() {
  return new Date().toISOString().slice(0, 10)
}

function formatNumber(value) {
  if (value === null || value === undefined) {
    return '-'
  }
  return Number(value).toFixed(2)
}

function formatLabel(value) {
  return value.slice(5)
}

export default function DailyTrendPage() {
  const [endDate, setEndDate] = useState(currentDate())
  const [machineId, setMachineId] = useState('')
  const [machines, setMachines] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [items, setItems] = useState([])

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError('')

      try {
        const [trendResponse, machineResponse] = await Promise.all([
          getDailyPlanVsActual(endDate, 7, machineId),
          getMachines(),
        ])
        setItems(trendResponse.items || [])
        setMachines(machineResponse.items || [])
      } catch (requestError) {
        setError(requestError.message || 'Unable to load daily trend.')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [endDate, machineId])

  const selectedMachine = machines.find((item) => String(item.id) === String(machineId))

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">7-Day Daily Trend</p>
          <h2>Actual Output vs Machine Plan</h2>
          <p className="card-description">
            Sum of daily product output against summed machine plan for the last 7 days ending on the selected date.
          </p>
        </div>
        <div className="dual-grid">
          <label className="field compact-field">
            <span>End Date</span>
            <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
          </label>
          <label className="field compact-field">
            <span>Machine</span>
            <select className="table-input" value={machineId} onChange={(event) => setMachineId(event.target.value)}>
              <option value="">All Machines</option>
              {machines.map((machine) => (
                <option key={machine.id} value={machine.id}>
                  {machine.code} - {machine.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading 7-day trend...</p> : null}
      {selectedMachine ? (
        <p className="card-description">
          Machine filter is applied to plan only: showing plan for {selectedMachine.code}, while actual output remains plant total because the raw workbook has no daily machine-level actual output.
        </p>
      ) : null}

      {!loading ? (
        <>
          <div className="chart-card">
            <div className="chart-card-head">
              <p className="content-label">Daily Comparison</p>
              <h3 className="section-title">7-Day Output vs Plan</h3>
            </div>
            <div className="chart-box">
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={items}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="date" tickFormatter={formatLabel} stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    formatter={(value) => `${formatNumber(value)} MT`}
                    labelFormatter={(value) => `Date ${value}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="actual_output_mt"
                    name={selectedMachine ? 'Plant Actual Output' : 'Actual Output'}
                    stroke="#f05d3d"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="planned_output_mt"
                    name={selectedMachine ? `${selectedMachine.code} Plan` : 'Machine Plan'}
                    stroke="#14202b"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>{selectedMachine ? 'Plant Actual Output' : 'Actual Output'}</th>
                  <th>{selectedMachine ? `${selectedMachine.code} Plan` : 'Machine Plan'}</th>
                  <th>Plan Attainment%</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.date}>
                    <td>{item.date}</td>
                    <td>{formatNumber(item.actual_output_mt)}</td>
                    <td>{formatNumber(item.planned_output_mt)}</td>
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
