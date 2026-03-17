const jsonHeaders = {
  'Content-Type': 'application/json',
}

function getToken() {
  return window.localStorage.getItem('aci-access-token')
}

async function requestJson(path, options = {}) {
  const token = getToken()
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? jsonHeaders : {}),
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.message || 'Request failed')
  }
  return data
}

export function getPlants() {
  return requestJson('/api/plants')
}

export function savePlant(payload, plantId) {
  return requestJson(plantId ? `/api/plants/${plantId}` : '/api/plants', {
    method: plantId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function deletePlant(plantId) {
  return requestJson(`/api/plants/${plantId}`, {
    method: 'DELETE',
  })
}

export function getMachines() {
  return requestJson('/api/machines')
}

export function getManageMachines() {
  return requestJson('/api/manage-machine')
}

export function getProducts() {
  return requestJson('/api/products')
}

export function saveProduct(payload, productId) {
  return requestJson(productId ? `/api/products/${productId}` : '/api/products', {
    method: productId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteProduct(productId) {
  return requestJson(`/api/products/${productId}`, {
    method: 'DELETE',
  })
}

export function saveMachine(payload, machineId) {
  return requestJson(machineId ? `/api/machines/${machineId}` : '/api/machines', {
    method: machineId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteMachine(machineId) {
  return requestJson(`/api/machines/${machineId}`, {
    method: 'DELETE',
  })
}

export function saveManageMachine(payload, machineId) {
  return requestJson(machineId ? `/api/manage-machine/${machineId}` : '/api/manage-machine', {
    method: machineId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function getBreakdownReasons() {
  return requestJson('/api/breakdown-reasons')
}

export function saveBreakdownReason(payload, reasonId) {
  return requestJson(reasonId ? `/api/breakdown-reasons/${reasonId}` : '/api/breakdown-reasons', {
    method: reasonId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function getDailyProduction(date) {
  return requestJson(`/api/daily-production?date=${date}`)
}

export function getDailyProductionByMonth(month) {
  return requestJson(`/api/daily-production?month=${month}`)
}

export function saveDailyProduction(payload, recordId) {
  return requestJson(recordId ? `/api/daily-production/${recordId}` : '/api/daily-production', {
    method: recordId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteDailyProduction(recordId) {
  return requestJson(`/api/daily-production/${recordId}`, {
    method: 'DELETE',
  })
}

export function getDailyMachinePlans(date) {
  return requestJson(`/api/daily-machine-plans?date=${date}`)
}

export function saveDailyMachinePlan(payload, recordId) {
  return requestJson(recordId ? `/api/daily-machine-plans/${recordId}` : '/api/daily-machine-plans', {
    method: recordId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteDailyMachinePlan(recordId) {
  return requestJson(`/api/daily-machine-plans/${recordId}`, {
    method: 'DELETE',
  })
}

export function getDailyBreakdowns(date) {
  return requestJson(`/api/daily-breakdowns?date=${date}`)
}

export function saveDailyBreakdown(payload, recordId) {
  return requestJson(recordId ? `/api/daily-breakdowns/${recordId}` : '/api/daily-breakdowns', {
    method: recordId ? 'PUT' : 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteDailyBreakdown(recordId) {
  return requestJson(`/api/daily-breakdowns/${recordId}`, {
    method: 'DELETE',
  })
}

export function getMonthlyMachineSummary(month) {
  return requestJson(`/api/reports/monthly-machine-summary?month=${month}`)
}

export function getMonthlyPlantSummary(month) {
  return requestJson(`/api/reports/monthly-plant-summary?month=${month}`)
}

export function getBreakdownAnalysis(month) {
  return requestJson(`/api/reports/breakdown-analysis?month=${month}`)
}

export function getYtdSummary(year, month) {
  return requestJson(`/api/reports/ytd-summary?year=${year}&month=${month}`)
}

export function getDailyPlanVsActual(endDate, days = 7, machineId = '') {
  const machineQuery = machineId ? `&machine_id=${machineId}` : ''
  return requestJson(`/api/reports/daily-plan-vs-actual?end_date=${endDate}&days=${days}${machineQuery}`)
}
