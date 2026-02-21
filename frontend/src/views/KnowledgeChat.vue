<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <template #header>
        <span>知识问答</span>
      </template>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-item"
          :class="msg.role"
        >
          <div class="message-bubble">
            <div class="message-role">{{ msg.role === 'user' ? '我' : 'AI助手' }}</div>
            <div class="message-content">{{ msg.content }}</div>
          </div>
        </div>

        <div v-if="messages.length === 0" class="empty-hint">
          <el-empty description="暂无对话，请在下方输入问题开始问答" />
        </div>
      </div>

      <!-- 底部输入栏 -->
      <div class="input-bar">
        <el-input
          v-model="inputText"
          placeholder="请输入您的问题..."
          @keyup.enter="handleSend"
        />
        <el-button type="primary" @click="handleSend" :icon="Promotion">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputText = ref('')
const messageListRef = ref<HTMLElement>()

async function handleSend() {
  const text = inputText.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''

  // Placeholder：后续接入真实知识问答 API
  await nextTick()
  messages.value.push({ role: 'assistant', content: '知识问答功能开发中，敬请期待...' })

  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  height: 100%;
}

.chat-card {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  margin-bottom: 12px;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.message-item.user {
  justify-content: flex-end;
}

.message-item.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
}

.message-role {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.message-item.user .message-role {
  text-align: right;
}

.message-content {
  background: #f0f2f5;
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.message-item.user .message-content {
  background: #409eff;
  color: #fff;
}

.empty-hint {
  padding: 40px 0;
}

.input-bar {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
