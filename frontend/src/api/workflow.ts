import request from './request'

interface WorkflowResponse {
  workflow_run_id: string
  status: string
  outputs?: Record<string, any>
  error?: string
}

interface ChatResponse {
  answer: string
  conversation_id: string
  sources: Record<string, any>[]
}

export function runWorkflow(data: { workflow_key: string; inputs: Record<string, any> }) {
  return request.post<WorkflowResponse>('/workflow/run', data)
}

export function chatWithKB(data: { query: string; conversation_id?: string }) {
  return request.post<ChatResponse>('/workflow/chat', data)
}
