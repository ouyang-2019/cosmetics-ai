<template>
  <div class="page-container">
    <!-- 左侧会话历史 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <el-button type="primary" :icon="Plus" class="new-chat-btn" @click="createNewConversation">
          新建对话
        </el-button>
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ active: conv.id === activeConversationId }"
          @click="switchConversation(conv.id)"
        >
          <div class="conv-title">{{ conv.title }}</div>
          <div class="conv-time">{{ formatTime(conv.updatedAt) }}</div>
        </div>
        <div v-if="conversations.length === 0" class="no-conv-hint">暂无历史对话</div>
      </div>
    </aside>

    <!-- 右���聊天区域 -->
    <main class="chat-main">
      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <!-- 欢迎页 -->
        <div v-if="currentMessages.length === 0" class="welcome-area">
          <div class="welcome-icon">🤖</div>
          <p class="welcome-text">你好！我是化妆品知识问答助手，可以回答关于化妆品法规、成分、工艺等方面的问题。</p>
          <div class="suggested-questions">
            <span
              v-for="q in suggestedQuestions"
              :key="q"
              class="question-tag"
              @click="sendSuggestedQuestion(q)"
            >{{ q }}</span>
          </div>
        </div>

        <!-- 消息列表 -->
        <template v-else>
          <div
            v-for="(msg, index) in currentMessages"
            :key="index"
            class="message-item"
            :class="msg.role"
          >
            <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
            <div class="bubble-wrapper">
              <div
                class="message-bubble"
                :class="msg.role"
              >
                <div
                  v-if="msg.role === 'assistant'"
                  class="markdown-content"
                  v-html="renderMarkdown(msg.content)"
                />
                <div v-else class="plain-content">{{ msg.content }}</div>
              </div>

              <!-- 参考来源 -->
              <div v-if="msg.sources && msg.sources.length > 0" class="sources-section">
                <div class="sources-toggle" @click="toggleSources(index)">
                  <el-icon><DocumentCopy /></el-icon>
                  参考来源（{{ msg.sources.length }}）
                  <el-icon class="toggle-icon" :class="{ rotated: expandedSources.has(index) }">
                    <ArrowDown />
                  </el-icon>
                </div>
                <transition name="sources-slide">
                  <div v-if="expandedSources.has(index)" class="sources-list">
                    <div
                      v-for="(src, si) in msg.sources"
                      :key="si"
                      class="source-item"
                    >
                      <div class="source-name">
                        <el-icon><Document /></el-icon>
                        {{ src.document_name }}
                      </div>
                      <div class="source-content">{{ src.content }}</div>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
          </div>

          <!-- 加载指示器 -->
          <div v-if="loading" class="message-item assistant">
            <div class="avatar">AI</div>
            <div class="bubble-wrapper">
              <div class="message-bubble assistant loading-bubble">
                <span class="dot" /><span class="dot" /><span class="dot" />
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 底部输入区 -->
      <div class="input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="请输入您的问题..."
          resize="none"
          :disabled="loading"
          @keydown="handleKeydown"
          class="chat-input"
        />
        <el-button
          type="primary"
          :icon="Promotion"
          :disabled="loading || !inputText.trim()"
          @click="handleSend"
          class="send-btn"
        >
          发送
        </el-button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { Plus, Promotion, DocumentCopy, Document, ArrowDown } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import { chatWithKB } from '@/api/workflow'
import { ElMessage } from 'element-plus'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

interface Source {
  document_name: string
  content: string
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: number
}

interface Conversation {
  id: string
  title: string
  messages: Message[]
  conversationId: string
  updatedAt: number
}

// ---- 状态 ----
const conversations = ref<Conversation[]>([])
const activeConversationId = ref<string>('')
const inputText = ref('')
const loading = ref(false)
const messageListRef = ref<HTMLElement>()
const expandedSources = ref<Set<number>>(new Set())

const suggestedQuestions = [
  '化妆品GMP要求有哪些？',
  '烟酰胺的安全使用浓度？',
  '特殊化妆品备案流程？',
]

// ---- 计算属性 ----
const activeConversation = computed(() =>
  conversations.value.find(c => c.id === activeConversationId.value)
)

const currentMessages = computed<Message[]>(() => activeConversation.value?.messages ?? [])

// ---- 工具函数 ----
function generateId() {
  return `conv_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

function renderMarkdown(content: string) {
  return md.render(content)
}

function formatTime(ts: number) {
  const d = new Date(ts)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

function toggleSources(index: number) {
  if (expandedSources.value.has(index)) {
    expandedSources.value.delete(index)
  } else {
    expandedSources.value.add(index)
  }
  // 触发响应式更新
  expandedSources.value = new Set(expandedSources.value)
}

async function scrollToBottom() {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTo({ top: messageListRef.value.scrollHeight, behavior: 'smooth' })
  }
}

// ---- 持久化 ----
const STORAGE_KEY = 'kb_conversations'

function saveToStorage() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations.value))
}

function loadFromStorage() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (raw) {
    try {
      conversations.value = JSON.parse(raw)
      if (conversations.value.length > 0) {
        activeConversationId.value = conversations.value[0].id
      }
    } catch {
      conversations.value = []
    }
  }
}

// ---- 会话操作 ----
function createNewConversation() {
  const conv: Conversation = {
    id: generateId(),
    title: '新对话',
    messages: [],
    conversationId: '',
    updatedAt: Date.now(),
  }
  conversations.value.unshift(conv)
  activeConversationId.value = conv.id
  expandedSources.value = new Set()
  saveToStorage()
}

function switchConversation(id: string) {
  activeConversationId.value = id
  expandedSources.value = new Set()
  scrollToBottom()
}

// ---- 发送消息 ----
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function sendSuggestedQuestion(q: string) {
  inputText.value = q
  handleSend()
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 确保有激活的会话
  if (!activeConversationId.value) {
    createNewConversation()
  }

  const conv = activeConversation.value!
  const userMsg: Message = { role: 'user', content: text, timestamp: Date.now() }
  conv.messages.push(userMsg)

  // 更新会话标题（使用第一条用户消息前20字）
  if (conv.messages.filter(m => m.role === 'user').length === 1) {
    conv.title = text.length > 20 ? text.slice(0, 20) + '...' : text
  }

  inputText.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const payload: { query: string; conversation_id?: string } = {
      query: text,
    }
    if (conv.conversationId) {
      payload.conversation_id = conv.conversationId
    }

    const res = await chatWithKB(payload)
    const data = res.data as { answer: string; conversation_id: string; sources?: Source[] }

    // 更新 conversationId
    if (data.conversation_id) {
      conv.conversationId = data.conversation_id
    }

    const assistantMsg: Message = {
      role: 'assistant',
      content: data.answer || '',
      sources: data.sources || [],
      timestamp: Date.now(),
    }
    conv.messages.push(assistantMsg)
    conv.updatedAt = Date.now()

    // 将当前会话置顶
    const idx = conversations.value.findIndex(c => c.id === conv.id)
    if (idx > 0) {
      conversations.value.splice(idx, 1)
      conversations.value.unshift(conv)
    }
  } catch (err: any) {
    const errMsg = err?.response?.data?.detail || err?.message || '请求失败，请稍后重试'
    ElMessage.error(errMsg)
    conv.messages.push({
      role: 'assistant',
      content: `抱歉，出现了错误：${errMsg}`,
      timestamp: Date.now(),
    })
    conv.updatedAt = Date.now()
  } finally {
    loading.value = false
    saveToStorage()
    await scrollToBottom()
  }
}

// ---- 初始化 ----
onMounted(() => {
  loadFromStorage()
  if (conversations.value.length === 0) {
    createNewConversation()
  }
})
</script>

<style scoped>
.page-container {
  display: flex;
  height: calc(100vh - 120px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 左侧边栏 */
.sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e8eaed;
  background: #f7f8fa;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e8eaed;
}

.new-chat-btn {
  width: 100%;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 4px;
}

.conversation-item:hover {
  background: #eef0f4;
}

.conversation-item.active {
  background: #e6f0ff;
}

.conv-title {
  font-size: 13px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
  font-weight: 500;
}

.conversation-item.active .conv-title {
  color: #409eff;
}

.conv-time {
  font-size: 11px;
  color: #aaa;
}

.no-conv-hint {
  text-align: center;
  color: #bbb;
  font-size: 13px;
  padding: 24px 0;
}

/* 右侧主区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 消息列表 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px 24px 16px;
  scroll-behavior: smooth;
}

/* 欢迎区 */
.welcome-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  text-align: center;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-text {
  font-size: 15px;
  color: #555;
  line-height: 1.7;
  max-width: 500px;
  margin-bottom: 24px;
}

.suggested-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.question-tag {
  display: inline-block;
  padding: 6px 14px;
  background: #f0f4ff;
  border: 1px solid #c0d4ff;
  border-radius: 20px;
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
  transition: all 0.15s;
}

.question-tag:hover {
  background: #409eff;
  color: #fff;
  border-color: #409eff;
}

/* 消息条目 */
.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #555;
  flex-shrink: 0;
}

.message-item.user .avatar {
  background: #409eff;
  color: #fff;
}

.message-item.assistant .avatar {
  background: #67c23a;
  color: #fff;
}

.bubble-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-item.user .bubble-wrapper {
  align-items: flex-end;
}

.message-bubble {
  padding: 10px 16px;
  border-radius: 12px;
  line-height: 1.65;
  font-size: 14px;
  word-break: break-word;
}

.message-bubble.user {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 4px;
}

.message-bubble.assistant {
  background: #f0f2f5;
  color: #333;
  border-top-left-radius: 4px;
}

.plain-content {
  white-space: pre-wrap;
}

/* markdown 样式 */
.markdown-content {
  font-size: 14px;
  line-height: 1.7;
}

.markdown-content :deep(p) {
  margin: 0 0 8px;
}

.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

.markdown-content :deep(li) {
  margin-bottom: 4px;
}

.markdown-content :deep(code) {
  background: #e8eaed;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.markdown-content :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid #409eff;
  margin: 8px 0;
  padding: 4px 12px;
  color: #666;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin: 10px 0 6px;
  font-weight: 600;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #f5f5f5;
}

/* 加载指示器 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 18px;
  min-width: 60px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  display: inline-block;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* 参考来源 */
.sources-section {
  margin-top: 8px;
}

.sources-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #888;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s;
  user-select: none;
}

.sources-toggle:hover {
  background: #e8eaed;
  color: #555;
}

.toggle-icon {
  transition: transform 0.2s;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.sources-slide-enter-active,
.sources-slide-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.sources-slide-enter-from,
.sources-slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.sources-slide-enter-to,
.sources-slide-leave-from {
  opacity: 1;
  max-height: 600px;
}

.sources-list {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-item {
  background: #fafafa;
  border-left: 3px solid #409eff;
  padding: 8px 12px;
  border-radius: 0 6px 6px 0;
}

.source-name {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.source-content {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 底部输入区 */
.input-area {
  border-top: 1px solid #e8eaed;
  padding: 16px 24px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #fff;
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}

.send-btn {
  height: 60px;
  padding: 0 20px;
  flex-shrink: 0;
}
</style>
