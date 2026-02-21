<template>
  <div class="regulation-search-page">
    <div class="search-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h2 class="page-title">法规智能检索</h2>
        <p class="page-subtitle">基于AI的化妆品法规智能问答，快速获取准确的法规信息</p>
      </div>

      <!-- 搜索区域 -->
      <el-card class="search-card" shadow="never">
        <el-input
          v-model="query"
          placeholder="请输入法规问题，如：烟酰胺使用限量要求"
          size="large"
          clearable
          @keyup.enter="handleSearch"
          class="search-input"
        >
          <template #append>
            <el-button
              :icon="Search"
              :loading="loading"
              @click="handleSearch"
              class="search-btn"
            >
              搜索
            </el-button>
          </template>
        </el-input>

        <!-- 快捷标签 -->
        <div class="quick-tags">
          <span class="quick-tags-label">常用查询：</span>
          <el-tag
            v-for="tag in quickTags"
            :key="tag"
            class="quick-tag"
            type="info"
            effect="plain"
            size="default"
            @click="handleTagClick(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
      </el-card>

      <!-- 主体内容区 -->
      <div class="main-content">
        <!-- 左侧搜索历史 -->
        <div v-if="searchHistory.length > 0" class="sidebar">
          <el-card shadow="never" class="history-card">
            <template #header>
              <div class="history-header">
                <span>搜索历史</span>
                <el-button link type="danger" size="small" @click="clearHistory">清空</el-button>
              </div>
            </template>
            <ul class="history-list">
              <li
                v-for="(item, index) in searchHistory"
                :key="index"
                class="history-item"
                @click="handleHistoryClick(item)"
                :title="item"
              >
                <el-icon class="history-icon"><Clock /></el-icon>
                <span class="history-text">{{ item }}</span>
              </li>
            </ul>
          </el-card>
        </div>

        <!-- 右侧结果区 -->
        <div class="result-area" :class="{ 'full-width': searchHistory.length === 0 }">
          <!-- 加载状态 -->
          <el-card v-if="loading" shadow="never" class="result-card">
            <template #header>
              <span>AI 正在检索中...</span>
            </template>
            <el-skeleton :rows="8" animated />
          </el-card>

          <!-- 结果展示 -->
          <el-card v-else-if="result" shadow="never" class="result-card">
            <template #header>
              <div class="result-header">
                <el-icon class="result-icon"><ChatDotRound /></el-icon>
                <span>AI 智能摘要</span>
                <el-tag type="success" size="small" effect="light" style="margin-left: auto;">已完成</el-tag>
              </div>
            </template>

            <!-- Markdown 渲染区域 -->
            <div
              class="result-content markdown-body"
              v-html="renderedResult"
            />

            <!-- 参考来源（可折叠） -->
            <template v-if="sources.length > 0">
              <el-divider />
              <el-collapse class="sources-collapse">
                <el-collapse-item name="sources">
                  <template #title>
                    <el-icon><DocumentCopy /></el-icon>
                    <span style="margin-left: 6px;">参考来源（{{ sources.length }} 条）</span>
                  </template>
                  <ul class="sources-list">
                    <li v-for="(src, idx) in sources" :key="idx" class="source-item">
                      <span class="source-index">{{ idx + 1 }}</span>
                      <span class="source-text">{{ src }}</span>
                    </li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </template>
          </el-card>

          <!-- 空状态 -->
          <el-card v-else shadow="never" class="empty-card">
            <el-empty
              description="输入问题后点击搜索，AI将为您解答化妆品相关法规问题"
              :image-size="120"
            >
              <template #image>
                <el-icon style="font-size: 80px; color: #c0c4cc;"><Search /></el-icon>
              </template>
            </el-empty>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Clock, ChatDotRound, DocumentCopy } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import { runWorkflow } from '@/api/workflow'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: true,
})

// 响应式状态
const query = ref('')
const loading = ref(false)
const result = ref('')
const sources = ref<string[]>([])
const searchHistory = ref<string[]>([])

// 快捷标签
const quickTags = [
  '烟酰胺使用限量',
  '化妆品备案流程',
  '防腐剂添加标准',
  '功效宣称要求',
  '标签标识规范',
]

// 渲染后的 Markdown
const renderedResult = computed(() => {
  if (!result.value) return ''
  return md.render(result.value)
})

// 点击快捷标签
function handleTagClick(tag: string) {
  query.value = tag
  handleSearch()
}

// 点击历史记录
function handleHistoryClick(item: string) {
  query.value = item
  handleSearch()
}

// 清空历史
function clearHistory() {
  searchHistory.value = []
}

// 添加到搜索历史（去重，最多保留10条）
function addToHistory(q: string) {
  const trimmed = q.trim()
  if (!trimmed) return
  const idx = searchHistory.value.indexOf(trimmed)
  if (idx !== -1) {
    searchHistory.value.splice(idx, 1)
  }
  searchHistory.value.unshift(trimmed)
  if (searchHistory.value.length > 10) {
    searchHistory.value = searchHistory.value.slice(0, 10)
  }
}

// 从响应中提取来源
function extractSources(outputs: Record<string, any>): string[] {
  const candidates = [
    outputs?.sources,
    outputs?.references,
    outputs?.citations,
    outputs?.source_documents,
  ]
  for (const candidate of candidates) {
    if (Array.isArray(candidate) && candidate.length > 0) {
      return candidate.map((s: any) => (typeof s === 'string' ? s : JSON.stringify(s)))
    }
  }
  return []
}

// 从响应中提取答案文本
function extractAnswer(outputs: Record<string, any>): string {
  const candidates = [
    outputs?.answer,
    outputs?.output,
    outputs?.result,
    outputs?.text,
    outputs?.content,
    outputs?.response,
  ]
  for (const candidate of candidates) {
    if (typeof candidate === 'string' && candidate.trim()) {
      return candidate.trim()
    }
  }
  // 兜底：将整个 outputs 序列化
  return JSON.stringify(outputs, null, 2)
}

// 执行搜索
async function handleSearch() {
  const q = query.value.trim()
  if (!q) {
    ElMessage.warning('请输入查询内容')
    return
  }

  loading.value = true
  result.value = ''
  sources.value = []

  try {
    const response = await runWorkflow({
      workflow_key: 'regulation_search',
      inputs: { question: q },
    })

    const outputs = response?.data?.outputs ?? response?.outputs ?? response?.data ?? {}
    result.value = extractAnswer(outputs)
    sources.value = extractSources(outputs)

    addToHistory(q)
  } catch (err: any) {
    const msg =
      err?.response?.data?.message ||
      err?.response?.data?.detail ||
      err?.message ||
      '搜索失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.regulation-search-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px 16px 48px;
}

.search-container {
  max-width: 960px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 搜索卡片 */
.search-card {
  border-radius: 12px;
  margin-bottom: 24px;
}

.search-input :deep(.el-input__wrapper) {
  font-size: 15px;
}

.search-btn {
  padding: 0 20px;
}

/* 快捷标签 */
.quick-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
}

.quick-tags-label {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}

.quick-tag {
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.quick-tag:hover {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

/* 主体内容 */
.main-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* 左侧历史 */
.sidebar {
  width: 220px;
  flex-shrink: 0;
}

.history-card {
  border-radius: 12px;
  position: sticky;
  top: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 4px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
  overflow: hidden;
}

.history-item:hover {
  background: #f5f7fa;
}

.history-icon {
  color: #c0c4cc;
  flex-shrink: 0;
  font-size: 13px;
}

.history-text {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 右侧结果区 */
.result-area {
  flex: 1;
  min-width: 0;
}

.result-area.full-width {
  width: 100%;
}

.result-card,
.empty-card {
  border-radius: 12px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-icon {
  color: #409eff;
  font-size: 16px;
}

/* Markdown 渲染样式 */
.result-content {
  line-height: 1.85;
  color: #303133;
  font-size: 15px;
}

.result-content :deep(h1),
.result-content :deep(h2),
.result-content :deep(h3),
.result-content :deep(h4) {
  color: #1a1a2e;
  margin: 1.2em 0 0.6em;
  font-weight: 600;
  line-height: 1.4;
}

.result-content :deep(h2) {
  font-size: 18px;
  border-bottom: 2px solid #ebeef5;
  padding-bottom: 8px;
}

.result-content :deep(h3) {
  font-size: 16px;
}

.result-content :deep(p) {
  margin: 0.75em 0;
}

.result-content :deep(ul),
.result-content :deep(ol) {
  padding-left: 1.6em;
  margin: 0.75em 0;
}

.result-content :deep(li) {
  margin: 0.4em 0;
}

.result-content :deep(strong) {
  color: #1a1a2e;
  font-weight: 600;
}

.result-content :deep(code) {
  background: #f4f4f5;
  color: #e6a23c;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.result-content :deep(pre) {
  background: #f4f4f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
}

.result-content :deep(pre code) {
  background: none;
  padding: 0;
  color: #303133;
}

.result-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  margin: 1em 0;
  padding: 8px 16px;
  background: #ecf5ff;
  border-radius: 0 8px 8px 0;
  color: #606266;
}

.result-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.result-content :deep(th),
.result-content :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.result-content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}

.result-content :deep(tr:hover td) {
  background: #fafafa;
}

/* 参考来源 */
.sources-collapse {
  margin-top: 4px;
}

.sources-collapse :deep(.el-collapse-item__header) {
  font-size: 14px;
  color: #606266;
}

.sources-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.source-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f2f3f5;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.source-item:last-child {
  border-bottom: none;
}

.source-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 2px;
}

.source-text {
  flex: 1;
}

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }

  .history-card {
    position: static;
  }

  .page-title {
    font-size: 22px;
  }
}
</style>
