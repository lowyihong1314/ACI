import { useEffect, useState } from 'react'

import {
  deleteDailyProduction,
  getDailyProduction,
  getDailyProductionByMonth,
  getProducts,
  saveDailyProduction,
} from '../../api/production'

const PAGE_SIZE = 25

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

function buildSearchText(product) {
  return [
    product?.plant?.code,
    product?.warehouse_code,
    product?.part_code,
    product?.description,
    product?.product_class,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
}

export default function DailyProductionPage() {
  const [selectedDate, setSelectedDate] = useState(todayString())
  const [historyMonth, setHistoryMonth] = useState(todayString().slice(0, 7))
  const [products, setProducts] = useState([])
  const [rows, setRows] = useState([])
  const [historyRows, setHistoryRows] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [historyCurrentPage, setHistoryCurrentPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [savingId, setSavingId] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [historyError, setHistoryError] = useState('')

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
        setCurrentPage(1)
      } catch (requestError) {
        setError(requestError.message || 'Unable to load daily product tonnage.')
      } finally {
        setLoading(false)
      }
    }

    loadInitial()
  }, [selectedDate])

  useEffect(() => {
    const loadHistory = async () => {
      setHistoryLoading(true)
      setHistoryError('')
      try {
        const response = await getDailyProductionByMonth(historyMonth)
        setHistoryRows(response.items || [])
        setHistoryCurrentPage(1)
      } catch (requestError) {
        setHistoryError(requestError.message || 'Unable to load monthly tonnage history.')
      } finally {
        setHistoryLoading(false)
      }
    }

    loadHistory()
  }, [historyMonth])

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

  const productMap = new Map(products.map((product) => [product.id, product]))
  const normalizedSearch = searchTerm.trim().toLowerCase()
  const filteredRows = rows.filter((row) => {
    if (!normalizedSearch) {
      return true
    }
    return buildSearchText(productMap.get(row.product_id)).includes(normalizedSearch)
  })
  const totalPages = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE))
  const safeCurrentPage = Math.min(currentPage, totalPages)
  const pageStart = (safeCurrentPage - 1) * PAGE_SIZE
  const visibleRows = filteredRows.slice(pageStart, pageStart + PAGE_SIZE)
  const filteredHistoryRows = historyRows.filter((row) => {
    if (!normalizedSearch) {
      return true
    }
    return [row.record_date, buildSearchText(row.product || productMap.get(row.product_id))]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(normalizedSearch)
  })
  const historyTotalPages = Math.max(1, Math.ceil(filteredHistoryRows.length / PAGE_SIZE))
  const safeHistoryCurrentPage = Math.min(historyCurrentPage, historyTotalPages)
  const historyPageStart = (safeHistoryCurrentPage - 1) * PAGE_SIZE
  const visibleHistoryRows = filteredHistoryRows.slice(historyPageStart, historyPageStart + PAGE_SIZE)

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

      <div className="module-actions">
        <label className="field search-field">
          <span>Search</span>
          <input
            type="search"
            placeholder="Plant, WH, part code, description, class"
            value={searchTerm}
            onChange={(event) => {
              setSearchTerm(event.target.value)
              setCurrentPage(1)
            }}
          />
        </label>
        <p className="subtext pagination-summary">
          Showing {visibleRows.length ? pageStart + 1 : 0}-{pageStart + visibleRows.length} of {filteredRows.length} products
        </p>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}

      {loading ? (
        <p className="loading-text">Loading daily product tonnage...</p>
      ) : (
        <>
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
                {visibleRows.map((row) => {
                  const product = productMap.get(row.product_id)
                  return (
                    <tr key={row.product_id}>
                      <td>{product?.plant?.code || '-'}</td>
                      <td>{product?.warehouse_code || '-'}</td>
                      <td>{product?.part_code || row.product_id}</td>
                      <td>{product?.description || '-'}</td>
                      <td>{product?.product_class || '-'}</td>
                      <td>
                        <input
                          className="table-input"
                          value={row.output_mt}
                          onChange={(event) => handleRowChange(row.product_id, event.target.value)}
                        />
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
                {!visibleRows.length ? (
                  <tr>
                    <td colSpan="7" className="empty-cell">
                      No products match the current search.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>

          <div className="pagination-bar">
            <button
              className="mini-button ghost-button"
              type="button"
              disabled={safeCurrentPage <= 1}
              onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
            >
              Previous
            </button>
            <span className="pagination-status">
              Page {safeCurrentPage} of {totalPages}
            </span>
            <button
              className="mini-button ghost-button"
              type="button"
              disabled={safeCurrentPage >= totalPages}
              onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
            >
              Next
            </button>
          </div>
        </>
      )}

      <section className="module-card">
        <div className="module-header">
          <div>
            <p className="content-label">History</p>
            <h3 className="section-title">Daily Tonnage By Date</h3>
          </div>
          <label className="field compact-field">
            <span>Month</span>
            <input type="month" value={historyMonth} onChange={(event) => setHistoryMonth(event.target.value)} />
          </label>
        </div>

        {historyError ? <p className="error-message">{historyError}</p> : null}

        <p className="subtext pagination-summary">
          Showing {visibleHistoryRows.length ? historyPageStart + 1 : 0}-{historyPageStart + visibleHistoryRows.length} of {filteredHistoryRows.length} records
        </p>

        {historyLoading ? (
          <p className="loading-text">Loading monthly tonnage history...</p>
        ) : (
          <>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Plant</th>
                    <th>WH</th>
                    <th>Part Code</th>
                    <th>Description</th>
                    <th>Class</th>
                    <th>Output MT</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleHistoryRows.map((row) => {
                    const product = row.product || productMap.get(row.product_id)
                    return (
                      <tr key={row.id}>
                        <td>{row.record_date || '-'}</td>
                        <td>{product?.plant?.code || '-'}</td>
                        <td>{product?.warehouse_code || '-'}</td>
                        <td>{product?.part_code || row.product_id}</td>
                        <td>{product?.description || '-'}</td>
                        <td>{product?.product_class || '-'}</td>
                        <td>{row.output_mt ?? 0}</td>
                      </tr>
                    )
                  })}
                  {!visibleHistoryRows.length ? (
                    <tr>
                      <td colSpan="7" className="empty-cell">
                        No tonnage records found for the selected month.
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>

            <div className="pagination-bar">
              <button
                className="mini-button ghost-button"
                type="button"
                disabled={safeHistoryCurrentPage <= 1}
                onClick={() => setHistoryCurrentPage((page) => Math.max(1, page - 1))}
              >
                Previous
              </button>
              <span className="pagination-status">
                Page {safeHistoryCurrentPage} of {historyTotalPages}
              </span>
              <button
                className="mini-button ghost-button"
                type="button"
                disabled={safeHistoryCurrentPage >= historyTotalPages}
                onClick={() => setHistoryCurrentPage((page) => Math.min(historyTotalPages, page + 1))}
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </section>
  )
}
