import { useEffect, useState } from 'react'

import { getProducts, saveProduct } from '../../api/production'

const defaultProductForm = {
  id: null,
  plant_id: '',
  part_code: '',
  description: '',
  product_class: '',
  warehouse_code: '',
  is_active: true,
}

export default function MasterDataPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [productForm, setProductForm] = useState(defaultProductForm)

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const productsResponse = await getProducts()
      setProducts(productsResponse.items || [])
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

  return (
    <section className="module-card">
      <div className="module-header">
        <div>
          <p className="content-label">Master Data</p>
          <h2>Products</h2>
          <p className="card-description">
            Product master records come from the raw workbook and are unique by part code plus warehouse.
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
                <span>Plant ID</span>
                <input value={productForm.plant_id} onChange={(event) => setProductForm((current) => ({ ...current, plant_id: event.target.value }))} />
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
              <button className="submit-button" type="submit">
                {productForm.id ? 'Update Product' : 'Create Product'}
              </button>
            </form>
          </section>

          <section className="module-card">
            <h3 className="section-title">Product List</h3>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Plant</th>
                    <th>WH</th>
                    <th>Part Code</th>
                    <th>Description</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((item) => (
                    <tr key={item.id}>
                      <td>{item.plant?.code || '-'}</td>
                      <td>{item.warehouse_code || '-'}</td>
                      <td>{item.part_code}</td>
                      <td>{item.description}</td>
                      <td>
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
