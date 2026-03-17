import { useEffect, useState } from 'react'

import { deletePlant, getPlants, savePlant } from '../../api/production'

const defaultPlantForm = {
  id: null,
  name: '',
  code: '',
  is_active: true,
}

export default function PlantManagementPage() {
  const [plants, setPlants] = useState([])
  const [plantForm, setPlantForm] = useState(defaultPlantForm)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await getPlants()
      setPlants(response.items || [])
    } catch (requestError) {
      setError(requestError.message || 'Unable to load plants.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const submitPlant = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    try {
      const response = await savePlant(plantForm, plantForm.id)
      setMessage(response.message || 'Plant saved')
      setPlantForm(defaultPlantForm)
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to save plant.')
    }
  }

  const handleDelete = async (plantId) => {
    setMessage('')
    setError('')
    try {
      const response = await deletePlant(plantId)
      setMessage(response.message || 'Plant deleted')
      if (plantForm.id === plantId) {
        setPlantForm(defaultPlantForm)
      }
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to delete plant.')
    }
  }

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Plant Management</p>
          <h2>Plants</h2>
          <p className="card-description">
            Maintain plant master records used by machine and product setup.
          </p>
        </div>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading plants...</p> : null}

      {!loading ? (
        <div className="dual-grid">
          <section className="module-card">
            <h3 className="section-title">Plant Form</h3>
            <form className="profile-form" onSubmit={submitPlant}>
              <label className="field">
                <span>Code</span>
                <input
                  value={plantForm.code}
                  onChange={(event) => setPlantForm((current) => ({ ...current, code: event.target.value }))}
                />
              </label>
              <label className="field">
                <span>Name</span>
                <input
                  value={plantForm.name}
                  onChange={(event) => setPlantForm((current) => ({ ...current, name: event.target.value }))}
                />
              </label>
              <label className="toggle-row">
                <input
                  type="checkbox"
                  checked={Boolean(plantForm.is_active)}
                  onChange={(event) => setPlantForm((current) => ({ ...current, is_active: event.target.checked }))}
                />
                <span>Active</span>
              </label>
              <div className="module-actions">
                <button className="submit-button" type="submit">
                  {plantForm.id ? 'Update Plant' : 'Create Plant'}
                </button>
                <button
                  className="mini-button ghost-button"
                  type="button"
                  onClick={() => setPlantForm(defaultPlantForm)}
                >
                  Reset
                </button>
              </div>
            </form>
          </section>

          <section className="module-card">
            <h3 className="section-title">Plant List</h3>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {plants.map((item) => (
                    <tr key={item.id}>
                      <td>{item.code}</td>
                      <td>{item.name}</td>
                      <td>{item.is_active ? 'Active' : 'Inactive'}</td>
                      <td className="action-cell">
                        <button
                          className="mini-button"
                          type="button"
                          onClick={() =>
                            setPlantForm({
                              id: item.id,
                              name: item.name,
                              code: item.code,
                              is_active: item.is_active,
                            })
                          }
                        >
                          Edit
                        </button>
                        <button
                          className="mini-button ghost-button"
                          type="button"
                          onClick={() => handleDelete(item.id)}
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
