<template>
  <div class="doc-review">
    <!-- 模式切换 -->
    <el-card class="mode-card">
      <div class="mode-bar">
        <el-radio-group v-model="mode" size="large">
          <el-radio-button value="review">
            <el-icon><EditPen /></el-icon>
            体系文件审核
          </el-radio-button>
          <el-radio-button value="generate">
            <el-icon><DocumentAdd /></el-icon>
            体系文件编制
          </el-radio-button>
        </el-radio-group>
        <el-tag type="info" effect="plain" size="default" class="mode-hint">
          {{ mode === 'review' ? '上传已有文件，AI检查合规性' : '输入需求，AI自动生成体系文件' }}
        </el-tag>
      </div>
    </el-card>

    <!-- ============ 审核模式 ============ -->
    <template v-if="mode === 'review'">
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
                <div class="el-upload__tip">支持 PDF、Word 格式，文件大小不超过 50MB</div>
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
      <el-card v-if="loading && mode === 'review'" class="progress-card">
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
    </template>

    <!-- ============ 编制模式 ============ -->
    <template v-else>
      <el-row :gutter="16">
        <!-- 左侧：编制表单 -->
        <el-col :span="10">
          <el-card class="gen-card">
            <template #header>
              <span>文件编制需求</span>
            </template>

            <el-form label-position="top" :model="genForm" class="gen-form">
              <el-form-item label="文件类型" required>
                <el-select v-model="genForm.doc_type" style="width: 100%">
                  <el-option label="GMP体系文件" value="GMP体系文件" />
                  <el-option label="质量手册" value="质量手册" />
                  <el-option label="SOP标准操作规程" value="SOP标准操作规程" />
                  <el-option label="验证方案" value="验证方案" />
                  <el-option label="检验规程" value="检验规程" />
                  <el-option label="管理规程" value="管理规程" />
                  <el-option label="批生产记录" value="批生产记录" />
                </el-select>
              </el-form-item>

              <el-form-item label="文件主题" required>
                <el-input
                  v-model="genForm.topic"
                  placeholder="例如：原料验收SOP、成品微生物检验规程、清洁验证方案"
                />
              </el-form-item>

              <el-form-item label="适用范围">
                <el-input
                  v-model="genForm.scope"
                  type="textarea"
                  :rows="2"
                  placeholder="例如：适用于公司所有车间的原料验收作业"
                />
              </el-form-item>

              <el-row :gutter="12">
                <el-col :span="12">
                  <el-form-item label="产品类型">
                    <el-select v-model="genForm.product_type" style="width: 100%">
                      <el-option label="护肤品" value="护肤品" />
                      <el-option label="彩妆" value="彩妆" />
                      <el-option label="洗护用品" value="洗护用品" />
                      <el-option label="特殊化妆品" value="特殊化妆品" />
                      <el-option label="通用" value="通用" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="详细程度">
                    <el-select v-model="genForm.detail_level" style="width: 100%">
                      <el-option label="框架版（章节大纲）" value="框架版" />
                      <el-option label="标准版（完整内容）" value="标准版" />
                      <el-option label="详细版（含附录表单）" value="详细版" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="特殊要求（选填）">
                <el-input
                  v-model="genForm.requirements"
                  type="textarea"
                  :rows="3"
                  placeholder="例如：需符合ISO 22716要求、需包含风险评估章节、公司名称为XX化妆品有限公司"
                />
              </el-form-item>

              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                :disabled="!genForm.topic.trim()"
                :loading="loading"
                @click="handleGenerate"
              >
                开始编制
              </el-button>
            </el-form>

            <!-- 快捷模板 -->
            <div class="quick-templates">
              <div class="quick-label">快捷模板：</div>
              <el-tag
                v-for="tmpl in quickTemplates"
                :key="tmpl.topic"
                class="quick-tmpl-tag"
                effect="plain"
                @click="applyTemplate(tmpl)"
              >
                {{ tmpl.label }}
              </el-tag>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：生成结果 -->
        <el-col :span="14">
          <el-card class="result-card">
            <template #header>
              <div class="result-header">
                <span>生成结果</span>
                <div v-if="genResult" class="result-actions">
                  <el-button size="small" @click="handleCopyGenResult">复制内容</el-button>
                  <el-button size="small" @click="handleDownloadGenResult">下载文件</el-button>
                  <el-button size="small" type="primary" @click="handleSendToReview">发送至审核</el-button>
                </div>
              </div>
            </template>

            <!-- 加载状态 -->
            <div v-if="loading && mode === 'generate'" class="loading-area">
              <el-skeleton :rows="15" animated />
              <div class="gen-progress-hint">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>AI 正在编制体系文件，请稍候...</span>
              </div>
            </div>

            <!-- 结果展示 -->
            <div v-else-if="genResult" class="gen-result-content">
              <div v-html="renderedGenResult" class="markdown-body" />
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-area">
              <el-empty description="填写编制需求后点击「开始编制」，AI将自动生成体系文件">
                <template #image>
                  <el-icon style="font-size: 60px; color: #c0c4cc;"><DocumentAdd /></el-icon>
                </template>
              </el-empty>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Loading, EditPen, DocumentAdd } from '@element-plus/icons-vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import MarkdownIt from 'markdown-it'
import { runWorkflow } from '@/api/workflow'

const md = new MarkdownIt({ html: false })

// ---- 公共状态 ----
const mode = ref<'review' | 'generate'>('review')
const loading = ref(false)

// ---- 审核模式状态 ----
const uploadRef = ref<UploadInstance>()
const docType = ref('GMP体系文件')
const reviewFocus = ref('')
const selectedFile = ref<File | null>(null)
const selectedFileName = ref('')
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

  const stepTimer = setInterval(() => {
    if (activeStep.value < 3) {
      activeStep.value++
    }
  }, 2000)

  try {
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

// ---- 编制模式状态 ----
const genResult = ref('')
const renderedGenResult = computed(() => md.render(genResult.value))

const genForm = reactive({
  doc_type: 'SOP标准操作规程',
  topic: '',
  scope: '',
  product_type: '通用',
  detail_level: '标准版',
  requirements: '',
})

const quickTemplates = [
  { label: '原料验收SOP', topic: '原料验收标准操作规程', doc_type: 'SOP标准操作规程', scope: '适用于所有原料的验收、取样、检验和入库' },
  { label: '清洁验证方案', topic: '生产设备清洁验证方案', doc_type: '验证方案', scope: '适用于生产车间所有直接接触产品的设备' },
  { label: '成品检验规程', topic: '化妆品成品检验规程', doc_type: '检验规程', scope: '适用于所有成品的出厂检验' },
  { label: '质量手册', topic: '化妆品生产质量管理手册', doc_type: '质量手册', scope: '适用于公司化妆品生产全过程的质量管理' },
  { label: '偏差处理SOP', topic: '偏差调查与处理标准操作规程', doc_type: 'SOP标准操作规程', scope: '适用于生产和质量控制过程中发现的偏差' },
]

function applyTemplate(tmpl: typeof quickTemplates[0]) {
  genForm.doc_type = tmpl.doc_type
  genForm.topic = tmpl.topic
  genForm.scope = tmpl.scope
  ElMessage.success('已填入模板信息')
}

async function handleGenerate() {
  if (!genForm.topic.trim()) {
    ElMessage.warning('请填写文件主题')
    return
  }

  loading.value = true
  genResult.value = ''

  try {
    const res: any = await runWorkflow({
      workflow_key: 'doc_generate',
      inputs: {
        doc_type: genForm.doc_type,
        topic: genForm.topic,
        scope: genForm.scope,
        product_type: genForm.product_type,
        detail_level: genForm.detail_level,
        requirements: genForm.requirements,
      },
    })

    const outputs = res.outputs || {}
    genResult.value = outputs.result || outputs.answer || outputs.output || JSON.stringify(outputs)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '文件编制请求失败')
  } finally {
    loading.value = false
  }
}

function handleCopyGenResult() {
  navigator.clipboard.writeText(genResult.value).then(
    () => ElMessage.success('已复制到剪贴板'),
    () => ElMessage.warning('复制失败，请手动复制'),
  )
}

function handleDownloadGenResult() {
  const blob = new Blob([genResult.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${genForm.topic}_${new Date().toISOString().slice(0, 10)}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('文件已下载')
}

function handleSendToReview() {
  // 将生成结果发送到审核模式
  mode.value = 'review'
  reportData.value = ''
  docType.value = genForm.doc_type
  reviewFocus.value = `由AI编制的${genForm.topic}，请重点审核内容完整性和法规合规性`
  ElMessage.info('已切换至审核模式，请上传生成的文件进行审核')
}
</script>

<style scoped>
.doc-review {
  max-width: 1200px;
  margin: 0 auto;
}

/* 模式切换栏 */
.mode-card {
  margin-bottom: 16px;
}

.mode-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mode-hint {
  font-size: 13px;
}

/* 审核模式 */
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

/* 编制模式 */
.gen-card {
  height: calc(100vh - 220px);
  overflow-y: auto;
}

.gen-form {
  padding-top: 4px;
}

.quick-templates {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.quick-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
}

.quick-tmpl-tag {
  margin: 0 8px 8px 0;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tmpl-tag:hover {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.result-card {
  height: calc(100vh - 220px);
  display: flex;
  flex-direction: column;
}

.result-card :deep(.el-card__body) {
  flex: 1;
  overflow-y: auto;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.loading-area {
  padding: 20px 0;
}

.gen-progress-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  color: #409eff;
  font-size: 14px;
}

.gen-result-content {
  overflow-y: auto;
}

.empty-area {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

/* Markdown 样式 */
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

.markdown-body :deep(code) {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: #f4f4f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}
</style>
