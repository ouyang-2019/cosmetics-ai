<template>
  <div class="copy-workbench">
    <!-- 顶部操作栏 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-radio-group v-model="mode" size="large">
            <el-radio-button value="review">合规审核</el-radio-button>
            <el-radio-button value="generate">文案生成</el-radio-button>
          </el-radio-group>
          <el-select v-model="productType" placeholder="产品类型" style="width: 150px; margin-left: 12px;">
            <el-option label="护肤品" value="护肤品" />
            <el-option label="彩妆" value="彩妆" />
            <el-option label="洗护用品" value="洗护用品" />
            <el-option label="香水" value="香水" />
            <el-option label="特殊化妆品" value="特殊化妆品" />
          </el-select>
        </div>
        <el-button type="primary" size="large" :loading="loading" @click="handleProcess">
          {{ mode === 'review' ? '开始审核' : '生成文案' }}
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="16" class="main-row">
      <!-- 左侧：输入区 -->
      <el-col :span="14">
        <el-card class="panel-card">
          <template #header>
            <span>{{ mode === 'review' ? '文案内容' : '产品信���' }}</span>
          </template>

          <!-- 审核模式：文案输入 -->
          <div v-if="mode === 'review'">
            <el-input
              v-model="copyText"
              type="textarea"
              :rows="22"
              placeholder="请粘贴或输入需要审核的文案内容...&#10;&#10;例如：本产品富含高浓度玻尿酸精华，7天见效美白淡斑，彻底消除皱纹，医学级别护肤体验。"
            />
          </div>

          <!-- 生成模式：产品信息表单 -->
          <el-form v-else label-position="top" :model="genForm" class="gen-form">
            <el-form-item label="产品名称">
              <el-input v-model="genForm.product_name" placeholder="例如：焕白精华液" />
            </el-form-item>
            <el-form-item label="核心成分">
              <el-input v-model="genForm.ingredients" placeholder="例如：烟酰胺5%、透明质酸钠、维生素C衍生物" />
            </el-form-item>
            <el-form-item label="目标人群">
              <el-input v-model="genForm.target_audience" placeholder="例如：25-35岁女性，关注美白抗初老" />
            </el-form-item>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="目标平台">
                  <el-select v-model="genForm.platform" style="width: 100%">
                    <el-option label="电商详情页" value="电商详情页" />
                    <el-option label="小红书" value="小红书" />
                    <el-option label="微信朋友圈" value="微信朋友圈" />
                    <el-option label="短视频脚本" value="短视频脚本" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="文案风格">
                  <el-select v-model="genForm.style" style="width: 100%">
                    <el-option label="专业科学" value="专业科学" />
                    <el-option label="温柔亲和" value="温柔亲和" />
                    <el-option label="活力时尚" value="活力时尚" />
                    <el-option label="高端奢华" value="高端奢华" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：结果区 -->
      <el-col :span="10">
        <el-card class="panel-card result-card">
          <template #header>
            <div class="result-header">
              <span>处理结果</span>
              <div v-if="resultText" class="result-actions">
                <el-button size="small" @click="handleCopy">复制结果</el-button>
                <el-button size="small" @click="handleExport">导出报告</el-button>
              </div>
            </div>
          </template>

          <!-- 加载状态 -->
          <div v-if="loading" class="loading-area">
            <el-skeleton :rows="10" animated />
          </div>

          <!-- 结果展示 -->
          <div v-else-if="resultText" class="result-content">
            <!-- 审核模式：风险等级 -->
            <div v-if="mode === 'review' && riskLevel" class="risk-badge">
              <el-tag :type="riskTagType" size="large" effect="dark">
                {{ riskLevel }}
              </el-tag>
            </div>
            <div v-html="renderedResult" class="markdown-body" />
            <div v-if="mode === 'review'" class="apply-section">
              <el-button type="success" @click="handleApplySuggestions">
                一键应用修改建议
              </el-button>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-area">
            <el-empty :description="mode === 'review' ? '请输入文案后点击「开始审核」' : '请填写产品信息后点击「生成文案」'" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import { runWorkflow } from '@/api/workflow'

const md = new MarkdownIt()

const mode = ref<'review' | 'generate'>('review')
const productType = ref('护肤品')
const loading = ref(false)
const copyText = ref('')
const resultText = ref('')
const riskLevel = ref('')

const genForm = reactive({
  product_name: '',
  ingredients: '',
  target_audience: '',
  platform: '电商详情页',
  style: '专业科学',
})

const renderedResult = computed(() => md.render(resultText.value))

const riskTagType = computed(() => {
  if (riskLevel.value.includes('高风险')) return 'danger'
  if (riskLevel.value.includes('中风险')) return 'warning'
  return 'success'
})

async function handleProcess() {
  if (mode.value === 'review') {
    if (!copyText.value.trim()) {
      ElMessage.warning('请先输入需要审核的文案内容')
      return
    }
    loading.value = true
    try {
      const res: any = await runWorkflow({
        workflow_key: 'copy_review',
        inputs: { text: copyText.value, copy_type: productType.value },
      })
      const outputs = res.outputs || {}
      resultText.value = outputs.result || outputs.answer || outputs.output || JSON.stringify(outputs)
      // 尝试从结果中提取风险等级
      if (resultText.value.includes('高风险')) riskLevel.value = '高风险'
      else if (resultText.value.includes('中风险')) riskLevel.value = '中风险'
      else if (resultText.value.includes('低风险')) riskLevel.value = '低风险'
      else riskLevel.value = '合规通过'
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '审核请求失败')
    } finally {
      loading.value = false
    }
  } else {
    if (!genForm.product_name.trim()) {
      ElMessage.warning('请填写产品名称')
      return
    }
    loading.value = true
    try {
      const res: any = await runWorkflow({
        workflow_key: 'copy_generate',
        inputs: {
          product_name: genForm.product_name,
          product_type: productType.value,
          ingredients: genForm.ingredients,
          target_audience: genForm.target_audience,
          platform: genForm.platform,
          style: genForm.style,
        },
      })
      const outputs = res.outputs || {}
      resultText.value = outputs.result || outputs.answer || outputs.output || JSON.stringify(outputs)
      riskLevel.value = ''
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '生成请求失败')
    } finally {
      loading.value = false
    }
  }
}

function handleCopy() {
  navigator.clipboard.writeText(resultText.value).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

function handleExport() {
  const header = mode.value === 'review' ? '文案合规审核报告' : '文案生成结果'
  const content = `${header}\n${'='.repeat(40)}\n\n产品类型：${productType.value}\n生成时间：${new Date().toLocaleString()}\n\n${resultText.value}`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${header}_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('报告已下载')
}

function handleApplySuggestions() {
  // 简单实现：将结果中的修改建议应用到文案
  ElMessage.info('修改建议已应用（需配合实际工作流返回结构化数据）')
}
</script>

<style scoped>
.copy-workbench {
  height: 100%;
}

.toolbar-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.main-row {
  height: calc(100vh - 220px);
}

.panel-card {
  height: 100%;
}

.panel-card :deep(.el-card__body) {
  height: calc(100% - 56px);
  overflow-y: auto;
}

.gen-form {
  padding-top: 4px;
}

.result-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
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

.result-content {
  flex: 1;
  overflow-y: auto;
}

.risk-badge {
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

.apply-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.empty-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
