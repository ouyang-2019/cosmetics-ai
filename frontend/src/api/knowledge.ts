import request from './request'

export function searchKnowledge(data: { question: string; dataset_ids: string[]; top_k?: number }) {
  return request.post('/knowledge/search', data)
}

export function listDatasets() {
  return request.get('/knowledge/datasets')
}
