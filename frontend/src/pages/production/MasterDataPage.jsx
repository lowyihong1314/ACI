import { useEffect, useState } from 'react'

import { deleteProduct, getPlants, getProducts, saveProduct } from '../../api/production'

const defaultProductForm = {
  id: null,
  plant_id: '',
  part_code: '',
  description: '',
  product_class: '',
  warehouse_code: '',
  is_active: true,
}

const PAGE_SIZE = 25

export default function MasterDataPage() {
  const [plants, setPlants] = useState([])
  const [products, setProducts] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [productForm, setProductForm] = useState(defaultProductForm)

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [productsResponse, plantsResponse] = await Promise.all([
        getProducts(),
        getPlants(),
      ])
      setProducts(productsResponse.items || [])
      setPlants(plantsResponse.items || [])
      setCurrentPage(1)
    } catch (requestError) {
      setError(requestError.message || 'Unable to load products.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const submitProduct = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    try {
      const response = await saveProduct(productForm, productForm.id)
      setMessage(response.message)
      setProductForm(defaultProductForm)
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to save product.')
    }
  }

  const handleDelete = async (productId) => {
    setMessage('')
    setError('')
    try {
      const response = await deleteProduct(productId)
      setMessage(response.message || 'Product deleted')
      if (productForm.id === productId) {
        setProductForm(defaultProductForm)
      }
      await loadData()
    } catch (requestError) {
      setError(requestError.message || 'Unable to delete product.')
    }
  }

  const normalizedSearch = searchTerm.trim().toLowerCase()
  const filteredProducts = products.filter((item) => {
    if (!normalizedSearch) {
      return true
    }
    return [
      item.plant?.code,
      item.warehouse_code,
      item.part_code,
      item.description,
      item.product_class,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(normalizedSearch)
  })
  const totalPages = Math.max(1, Math.ceil(filteredProducts.length / PAGE_SIZE))
  const safeCurrentPage = Math.min(currentPage, totalPages)
  const pageStart = (safeCurrentPage - 1) * PAGE_SIZE
  const visibleProducts = filteredProducts.slice(pageStart, pageStart + PAGE_SIZE)

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Master Data</p>
          <h2>Products</h2>
          <p className="card-description">
            Product master records are maintained in the frontend form and are unique by part code plus warehouse.
          </p>
        </div>
      </div>

      {message ? <p className="success-message">{message}</p> : null}
      {error ? <p className="error-message">{error}</p> : null}
      {loading ? <p className="loading-text">Loading products...</p> : null}

      {!loading ? (
        <div className="dual-grid">
          <section className="module-card">
            <h3 className="section-title">Product Form</h3>
            <form className="profile-form" onSubmit={submitProduct}>
              <label className="field">
                <span>Plant</span>
                <select
                  className="table-input"
                  value={productForm.plant_id}
                  onChange={(event) => setProductForm((current) => ({ ...current, plant_id: event.target.value }))}
                >
                  <option value="">No plant</option>
                  {plants.map((plant) => (
                    <option key={plant.id} value={plant.id}>
                      {plant.code} - {plant.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Part Code</span>
                <input value={productForm.part_code} onChange={(event) => setProductForm((current) => ({ ...current, part_code: event.target.value }))} />
              </label>
              <label className="field">
                <span>Description</span>
                <input value={productForm.description} onChange={(event) => setProductForm((current) => ({ ...current, description: event.target.value }))} />
              </label>
              <label className="field">
                <span>Product Class</span>
                <input value={productForm.product_class} onChange={(event) => setProductForm((current) => ({ ...current, product_class: event.target.value }))} />
              </label>
              <label className="field">
                <span>Warehouse Code</span>
                <input value={productForm.warehouse_code} onChange={(event) => setProductForm((current) => ({ ...current, warehouse_code: event.target.value }))} />
              </label>
              <div className="module-actions">
                <button className="submit-button" type="submit">
                  {productForm.id ? 'Update Product' : 'Create Product'}
                </button>
                <button
                  className="mini-button ghost-button"
                  type="button"
                  onClick={() => setProductForm(defaultProductForm)}
                >
                  Reset
                </button>
              </div>
            </form>
          </section>

          <section className="module-card">
            <h3 className="section-title">Product List</h3>
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
                Showing {visibleProducts.length ? pageStart + 1 : 0}-{pageStart + visibleProducts.length} of {filteredProducts.length} products
              </p>
            </div>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Plant</th>
                    <th>WH</th>
                    <th>Part Code</th>
                    <th>Description</th>
                    <th>Class</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleProducts.map((item) => (
                    <tr key={item.id}>
                      <td>{item.plant?.code || '-'}</td>
                      <td>{item.warehouse_code || '-'}</td>
                      <td>{item.part_code}</td>
                      <td>{item.description}</td>
                      <td>{item.product_class || '-'}</td>
                      <td className="action-cell">
                        <button
                          className="mini-button"
                          type="button"
                          onClick={() =>
                            setProductForm({
                              id: item.id,
                              plant_id: item.plant_id || '',
                              part_code: item.part_code,
                              description: item.description,
                              product_class: item.product_class || '',
                              warehouse_code: item.warehouse_code || '',
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
                  {!visibleProducts.length ? (
                    <tr>
                      <td colSpan="6" className="empty-cell">
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
          </section>
        </div>
      ) : null}
    </section>
  )
}
