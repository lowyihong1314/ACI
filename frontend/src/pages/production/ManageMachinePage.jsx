import { useEffect, useState } from 'react'

import { deleteMachine, getManageMachines, getPlants, saveManageMachine } from '../../api/production'

const defaultForm = {
  id: null,
  plant_id: '',
  code: '',
  name: '',
  machine_group: '',
  display_order: 0,
  is_active: true,
  supports_output: true,
  supports_reject: true,
  supports_breakdown: true,
  supports_efficiency: true,
}

const checkboxFields = [
  { key: 'is_active', label: 'Active' },
  { key: 'supports_output', label: 'Supports Output' },
  { key: 'supports_reject', label: 'Supports Reject' },
  { key: 'supports_breakdown', label: 'Supports Breakdown' },
  { key: 'supports_efficiency', label: 'Supports Efficiency' },
]

export default function ManageMachinePage() {
  const [plants, setPlants] = useState([])
  const [items, setItems] = useState([])
  const [form, setForm] = useState(defaultForm)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [plantsResponse, machinesResponse] = await Promise.all([
        getPlants(),
        getManageMachines(),
      ])
      setPlants(plantsResponse.items || [])
      setItems(machinesResponse.items || [])
    } catch (requestError) {
      setError(requestError.message || 'Unable to load machine management data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const submitForm = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    try {
      const payload = {
        ...form,
        plant_id: Number(form.plant_id),
        display_order: Number(form.display_order || 0),
      }
      const response = await saveManageMachine(payload, form.id)
      setMessage(response.message)
      setForm(defaultForm)
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to save machine.')
    }
  }

  const removeMachine = async (machineId) => {
    setMessage('')
    setError('')
    try {
      const response = await deleteMachine(machineId)
      setMessage(response.message || 'Machine deleted')
      if (form.id === machineId) {
        setForm(defaultForm)
      }
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to delete machine.')
    }
  }

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Manage Machine</p>
          <h2>Machine Administration</h2>
          <p className="card-description">
            Dedicated backend and frontend screen for machine setup and capability flags.
          </p>
        </div>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading machines...</p> : null}

      {!loading ? (
        <div className="dual-grid">
          <section className="module-card">
            <h3 className="section-title">Machine Form</h3>
            <form className="profile-form" onSubmit={submitForm}>
              <label className="field">
                <span>Plant</span>
                <select className="table-input" value={form.plant_id} onChange={(event) => setForm((current) => ({ ...current, plant_id: event.target.value }))}>
                  <option value="">Select plant</option>
                  {plants.map((plant) => (
                    <option key={plant.id} value={plant.id}>
                      {plant.code} - {plant.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Code</span>
                <input value={form.code} onChange={(event) => setForm((current) => ({ ...current, code: event.target.value }))} />
              </label>
              <label className="field">
                <span>Name</span>
                <input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} />
              </label>
              <label className="field">
                <span>Machine Group</span>
                <input value={form.machine_group} onChange={(event) => setForm((current) => ({ ...current, machine_group: event.target.value }))} />
              </label>
              <label className="field">
                <span>Display Order</span>
                <input type="number" value={form.display_order} onChange={(event) => setForm((current) => ({ ...current, display_order: event.target.value }))} />
              </label>

              <div className="checkbox-grid">
                {checkboxFields.map((item) => (
                  <label className="toggle-row" key={item.key}>
                    <input
                      type="checkbox"
                      checked={Boolean(form[item.key])}
                      onChange={(event) => setForm((current) => ({ ...current, [item.key]: event.target.checked }))}
                    />
                    <span>{item.label}</span>
                  </label>
                ))}
              </div>

              <button className="submit-button" type="submit">
                {form.id ? 'Update Machine' : 'Create Machine'}
              </button>
              <button className="mini-button ghost-button" type="button" onClick={() => setForm(defaultForm)}>
                Reset
              </button>
            </form>
          </section>

          <section className="module-card">
            <h3 className="section-title">Machine List</h3>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Plant</th>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Group</th>
                    <th>Order</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.id}>
                      <td>{item.plant?.code}</td>
                      <td>{item.code}</td>
                      <td>{item.name}</td>
                      <td>{item.machine_group || '-'}</td>
                      <td>{item.display_order}</td>
                      <td>{item.is_active ? 'Active' : 'Inactive'}</td>
                      <td className="action-cell">
                        <button
                          className="mini-button"
                          type="button"
                          onClick={() =>
                            setForm({
                              id: item.id,
                              plant_id: item.plant_id,
                              code: item.code,
                              name: item.name,
                              machine_group: item.machine_group || '',
                              display_order: item.display_order,
                              is_active: item.is_active,
                              supports_output: item.supports_output,
                              supports_reject: item.supports_reject,
                              supports_breakdown: item.supports_breakdown,
                              supports_efficiency: item.supports_efficiency,
                            })
                          }
                        >
                          Edit
                        </button>
                        <button
                          className="mini-button ghost-button"
                          type="button"
                          onClick={() => removeMachine(item.id)}
                        >
                          Delete
                        </button>
                      </td>
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
