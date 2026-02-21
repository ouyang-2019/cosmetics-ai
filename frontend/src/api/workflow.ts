import request from './request'

export function runWorkflow(data: { workflow_key: string; inputs: Record<string, any> }) {
  return request.post('/workflow/run', data)
}

export function chatWithKB(data: { query: string; conversation_id?: string }) {
  return request.post('/workflow/chat', data)
}
