import { useEffect, useState } from 'react'

import {
  deleteDailyMachinePlan,
  getDailyMachinePlans,
  getMachines,
  saveDailyMachinePlan,
} from '../../api/production'

function todayString() {
  return new Date().toISOString().slice(0, 10)
}

function emptyRow(selectedDate) {
  return {
    localId: `${Date.now()}-${Math.random()}`,
    id: null,
    plan_date: selectedDate,
    machine_id: '',
    standard_output_mt: '',
    planned_output_mt: '',
  }
}

export default function DailyBreakdownPage() {
  const [selectedDate, setSelectedDate] = useState(todayString())
  const [machines, setMachines] = useState([])
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [savingId, setSavingId] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError('')
      try {
        const [machineResponse, planResponse] = await Promise.all([
          getMachines(),
          getDailyMachinePlans(selectedDate),
        ])
        setMachines(machineResponse.items || [])
        const items = (planResponse.items || []).map((item) => ({
          localId: item.id,
          ...item,
          machine_id: String(item.machine_id),
          planned_output_mt: String(item.planned_output_mt ?? ''),
          standard_output_mt: String(item.standard_output_mt ?? ''),
        }))
        setRows(items.length ? items : [emptyRow(selectedDate)])
      } catch (requestError) {
        setError(requestError.message || 'Unable to load daily machine plans.')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [selectedDate])

  const updateRow = (localId, field, value) => {
    setRows((current) =>
      current.map((row) => (row.localId === localId ? { ...row, [field]: value } : row)),
    )
  }

  const addRow = () => {
    setRows((current) => [...current, emptyRow(selectedDate)])
  }

  const removeRow = async (row) => {
    setMessage('')
    setError('')
    if (!row.id) {
      setRows((current) => current.filter((item) => item.localId !== row.localId))
      return
    }
    setSavingId(row.localId)
    try {
      await deleteDailyMachinePlan(row.id)
      setRows((current) => current.filter((item) => item.localId !== row.localId))
      setMessage('Machine plan row deleted')
    } catch (requestError) {
      setError(requestError.message || 'Unable to delete machine plan row.')
    } finally {
      setSavingId(null)
    }
  }

  const saveRow = async (row) => {
    setMessage('')
    setError('')
    setSavingId(row.localId)
    try {
      const response = await saveDailyMachinePlan(
        {
          plan_date: selectedDate,
          machine_id: Number(row.machine_id),
          planned_output_mt: Number(row.planned_output_mt || 0),
          standard_output_mt: row.standard_output_mt === '' ? null : Number(row.standard_output_mt),
        },
        row.id,
      )
      const item = response.item
      setRows((current) =>
        current.map((currentRow) =>
          currentRow.localId === row.localId
            ? {
                localId: item.id,
                ...item,
                machine_id: String(item.machine_id),
                planned_output_mt: String(item.planned_output_mt ?? ''),
                standard_output_mt: String(item.standard_output_mt ?? ''),
              }
            : currentRow,
        ),
      )
      setMessage(response.message || 'Machine plan row saved')
    } catch (requestError) {
      setError(requestError.message || 'Unable to save machine plan row.')
    } finally {
      setSavingId(null)
    }
  }

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Daily Machine Plan</p>
          <h2>Daily Machine Plan</h2>
        </div>
        <div className="module-actions">
          <label className="field compact-field">
            <span>Date</span>
            <input type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
          </label>
          <button className="mini-button" type="button" onClick={addRow}>
            Add Row
          </button>
        </div>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}

      {loading ? (
        <p className="loading-text">Loading daily machine plans...</p>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Machine</th>
                <th>Standard MT</th>
                <th>Planned MT</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.localId}>
                  <td>
                    <select className="table-input" value={row.machine_id} onChange={(event) => updateRow(row.localId, 'machine_id', event.target.value)}>
                      <option value="">Select machine</option>
                      {machines.map((machine) => (
                        <option key={machine.id} value={machine.id}>
                          {machine.plant?.code} - {machine.name}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input className="table-input" value={row.standard_output_mt} onChange={(event) => updateRow(row.localId, 'standard_output_mt', event.target.value)} />
                  </td>
                  <td>
                    <input className="table-input" value={row.planned_output_mt} onChange={(event) => updateRow(row.localId, 'planned_output_mt', event.target.value)} />
                  </td>
                  <td className="action-cell">
                    <button className="mini-button" type="button" disabled={savingId === row.localId} onClick={() => saveRow(row)}>
                      Save
                    </button>
                    <button className="mini-button ghost-button" type="button" disabled={savingId === row.localId} onClick={() => removeRow(row)}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
