<template>
  <div class="doc-review">
    <!-- 上传区域 -->
    <el-card v-if="!reportData" class="upload-card">
      <template #header>
        <span>体系文件审核</span>
      </template>

      <el-row :gutter="16">
        <el-col :span="16">
          <el-upload
            ref="uploadRef"
            drag
            action="#"
            accept=".pdf,.doc,.docx"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="1"
            :on-exceed="handleExceed"
            class="upload-area"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word 格式，文件��小不超过 50MB</div>
            </template>
          </el-upload>
        </el-col>
        <el-col :span="8">
          <el-form label-position="top">
            <el-form-item label="文件类型">
              <el-select v-model="docType" style="width: 100%">
                <el-option label="GMP体系文件" value="GMP体系文件" />
                <el-option label="质量手册" value="质量手册" />
                <el-option label="SOP标准操作规程" value="SOP标准操作规程" />
                <el-option label="验证方案" value="验证方案" />
                <el-option label="检验规程" value="检验规程" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item label="审核重点（选填）">
              <el-input
                v-model="reviewFocus"
                type="textarea"
                :rows="3"
                placeholder="可指定审核重点，如：重点检查物料管理章节"
              />
            </el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :disabled="!selectedFile"
              :loading="loading"
              @click="handleStartReview"
            >
              开始审核
            </el-button>
          </el-form>
        </el-col>
      </el-row>
    </el-card>

    <!-- 审核进度 -->
    <el-card v-if="loading" class="progress-card">
      <template #header>
        <span>审核进行中...</span>
      </template>
      <el-steps :active="activeStep" align-center>
        <el-step title="文档解析" description="解析文档内容与结构" />
        <el-step title="标准对比" description="与标准模板对比" />
        <el-step title="法规检查" description="检查法规合规性" />
        <el-step title="生成报告" description="汇总审核结论" />
      </el-steps>
      <div class="progress-hint">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>{{ stepDescriptions[activeStep] || '处理中...' }}</span>
      </div>
    </el-card>

    <!-- 审核报告 -->
    <div v-if="reportData && !loading">
      <!-- 总结卡片 -->
      <el-card class="summary-card">
        <template #header>
          <div class="report-header">
            <span>审核报告 - {{ selectedFileName }}</span>
            <div class="report-actions">
              <el-button @click="handleDownloadReport">下载审核报告</el-button>
              <el-button type="primary" @click="handleReset">重新审核</el-button>
            </div>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="审核结论">
              <template #default>
                <el-tag :type="overallResultType" size="large" effect="dark">
                  {{ overallResult }}
                </el-tag>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="高风险问题" :value="issueCountByLevel('high')" class="stat-danger" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="中风险问题" :value="issueCountByLevel('medium')" class="stat-warning" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="优化建议" :value="issueCountByLevel('low')" class="stat-info" />
          </el-col>
        </el-row>
      </el-card>

      <!-- 详细结果 -->
      <el-card class="detail-card">
        <template #header>
          <span>详细审核结果</span>
        </template>
        <div v-html="renderedReport" class="markdown-body" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Loading } from '@element-plus/icons-vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import MarkdownIt from 'markdown-it'
import { runWorkflow } from '@/api/workflow'

const md = new MarkdownIt()

const uploadRef = ref<UploadInstance>()
const docType = ref('GMP体系文件')
const reviewFocus = ref('')
const selectedFile = ref<File | null>(null)
const selectedFileName = ref('')
const loading = ref(false)
const activeStep = ref(0)
const reportData = ref('')

const stepDescriptions = [
  '正在解析文档内容与结构...',
  '正在与标准模板进行对比分析...',
  '正在检查法规合规性...',
  '正在生成审核报告...',
]

const renderedReport = computed(() => md.render(reportData.value))

const overallResult = computed(() => {
  if (reportData.value.includes('高风险') || reportData.value.includes('严重')) return '需要修改'
  if (reportData.value.includes('中风险') || reportData.value.includes('建议')) return '基本合规'
  return '审核通过'
})

const overallResultType = computed(() => {
  if (overallResult.value === '需要修改') return 'danger'
  if (overallResult.value === '基本合规') return 'warning'
  return 'success'
})

function issueCountByLevel(level: string): number {
  const text = reportData.value
  if (level === 'high') return (text.match(/高风险|🔴|严重/g) || []).length
  if (level === 'medium') return (text.match(/中风险|🟡|注意/g) || []).length
  return (text.match(/建议优化|🟢|优化/g) || []).length
}

function handleFileChange(file: UploadFile) {
  selectedFile.value = file.raw || null
  selectedFileName.value = file.name
}

function handleFileRemove() {
  selectedFile.value = null
  selectedFileName.value = ''
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件，请先移除已选文件')
}

async function handleStartReview() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要审核的文件')
    return
  }

  loading.value = true
  reportData.value = ''
  activeStep.value = 0

  // 模拟进度步骤
  const stepTimer = setInterval(() => {
    if (activeStep.value < 3) {
      activeStep.value++
    }
  }, 2000)

  try {
    // 读取文件内容（对于文本文件）
    let fileContent = `[文件名: ${selectedFileName.value}]`
    if (selectedFile.value.type === 'text/plain' || selectedFileName.value.endsWith('.txt')) {
      fileContent = await selectedFile.value.text()
    }

    const res: any = await runWorkflow({
      workflow_key: 'doc_review',
      inputs: {
        document_content: fileContent,
        document_type: docType.value,
        file_name: selectedFileName.value,
        review_focus: reviewFocus.value,
      },
    })

    activeStep.value = 3
    const outputs = res.outputs || {}
    reportData.value = outputs.result || outputs.answer || outputs.output || JSON.stringify(outputs)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '审核请求失败')
    reportData.value = ''
  } finally {
    clearInterval(stepTimer)
    loading.value = false
  }
}

function handleDownloadReport() {
  const content = [
    '化妆品体系文件审核报告',
    '='.repeat(40),
    '',
    `文件名称：${selectedFileName.value}`,
    `文件类型：${docType.value}`,
    `审核时间：${new Date().toLocaleString()}`,
    `审核结论：${overallResult.value}`,
    '',
    '详细审核结果',
    '-'.repeat(40),
    '',
    reportData.value,
  ].join('\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `审核报告_${selectedFileName.value}_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('报告已下载')
}

function handleReset() {
  reportData.value = ''
  selectedFile.value = null
  selectedFileName.value = ''
  reviewFocus.value = ''
  activeStep.value = 0
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.doc-review {
  max-width: 1100px;
  margin: 0 auto;
}

.upload-card {
  margin-bottom: 16px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.progress-card {
  margin-bottom: 16px;
}

.progress-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  color: #409eff;
  font-size: 14px;
}

.summary-card {
  margin-bottom: 16px;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.report-actions {
  display: flex;
  gap: 8px;
}

.stat-danger :deep(.el-statistic__number) {
  color: #f56c6c;
}

.stat-warning :deep(.el-statistic__number) {
  color: #e6a23c;
}

.stat-info :deep(.el-statistic__number) {
  color: #67c23a;
}

.detail-card {
  margin-bottom: 16px;
}

.markdown-body {
  line-height: 1.8;
  color: #333;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 16px 0 8px;
  color: #1a1a1a;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding: 8px 16px;
  margin: 12px 0;
  background: #f8f9fa;
  color: #666;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}
</style>
