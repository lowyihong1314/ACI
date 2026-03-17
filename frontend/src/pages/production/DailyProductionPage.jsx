import { useEffect, useState } from 'react'

import {
  deleteDailyProduction,
  getDailyProduction,
  getProducts,
  saveDailyProduction,
} from '../../api/production'

function todayString() {
  return new Date().toISOString().slice(0, 10)
}

function createDraft(product) {
  return {
    id: null,
    record_date: todayString(),
    product_id: product.id,
    output_mt: '',
  }
}

function toInputValue(value) {
  return value === null || value === undefined ? '' : String(value)
}

export default function DailyProductionPage() {
  const [selectedDate, setSelectedDate] = useState(todayString())
  const [products, setProducts] = useState([])
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [savingId, setSavingId] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const loadInitial = async () => {
      setLoading(true)
      setError('')
      try {
        const [productResponse, productionResponse] = await Promise.all([
          getProducts(),
          getDailyProduction(selectedDate),
        ])
        const productItems = productResponse.items || []
        const productionMap = new Map(
          (productionResponse.items || []).map((item) => [item.product_id, item]),
        )
        setProducts(productItems)
        setRows(
          productItems.map((product) => {
            const existing = productionMap.get(product.id)
            return existing
              ? {
                  ...existing,
                  record_date: selectedDate,
                  output_mt: toInputValue(existing.output_mt),
                }
              : createDraft(product)
          }),
        )
      } catch (requestError) {
        setError(requestError.message || 'Unable to load daily product tonnage.')
      } finally {
        setLoading(false)
      }
    }

    loadInitial()
  }, [selectedDate])

  const handleRowChange = (productId, value) => {
    setMessage('')
    setError('')
    setRows((current) =>
      current.map((row) =>
        row.product_id === productId ? { ...row, output_mt: value, record_date: selectedDate } : row,
      ),
    )
  }

  const handleSave = async (row) => {
    setSavingId(row.product_id)
    setMessage('')
    setError('')
    try {
      const response = await saveDailyProduction(
        {
          record_date: selectedDate,
          product_id: row.product_id,
          output_mt: Number(row.output_mt || 0),
        },
        row.id,
      )
      const item = response.item
      setRows((current) =>
        current.map((currentRow) =>
          currentRow.product_id === row.product_id
            ? {
                ...item,
                output_mt: toInputValue(item.output_mt),
              }
            : currentRow,
        ),
      )
      setMessage(response.message || 'Saved')
    } catch (requestError) {
      setError(requestError.message || 'Unable to save daily product tonnage.')
    } finally {
      setSavingId(null)
    }
  }

  const handleDelete = async (row) => {
    if (!row.id) {
      setRows((current) =>
        current.map((currentRow) =>
          currentRow.product_id === row.product_id ? createDraft({ id: row.product_id }) : currentRow,
        ),
      )
      return
    }

    setSavingId(row.product_id)
    setMessage('')
    setError('')
    try {
      await deleteDailyProduction(row.id)
      setRows((current) =>
        current.map((currentRow) =>
          currentRow.product_id === row.product_id
            ? {
                ...createDraft({ id: row.product_id }),
                product_id: row.product_id,
                record_date: selectedDate,
              }
            : currentRow,
        ),
      )
      setMessage('Daily product tonnage deleted')
    } catch (requestError) {
      setError(requestError.message || 'Unable to delete daily product tonnage.')
    } finally {
      setSavingId(null)
    }
  }

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Daily Product Output</p>
          <h2>Daily Product Tonnage</h2>
        </div>
        <label className="field compact-field">
          <span>Date</span>
          <input type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
        </label>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}

      {loading ? (
        <p className="loading-text">Loading daily product tonnage...</p>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Plant</th>
                <th>WH</th>
                <th>Part Code</th>
                <th>Description</th>
                <th>Class</th>
                <th>Output MT</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const product = products.find((item) => item.id === row.product_id)
                return (
                  <tr key={row.product_id}>
                    <td>{product?.plant?.code || '-'}</td>
                    <td>{product?.warehouse_code || '-'}</td>
                    <td>{product?.part_code || row.product_id}</td>
                    <td>{product?.description || '-'}</td>
                    <td>{product?.product_class || '-'}</td>
                    <td>
                      <input className="table-input" value={row.output_mt} onChange={(event) => handleRowChange(row.product_id, event.target.value)} />
                    </td>
                    <td className="action-cell">
                      <button className="mini-button" type="button" disabled={savingId === row.product_id} onClick={() => handleSave(row)}>
                        Save
                      </button>
                      <button className="mini-button ghost-button" type="button" disabled={savingId === row.product_id} onClick={() => handleDelete(row)}>
                        Clear
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
