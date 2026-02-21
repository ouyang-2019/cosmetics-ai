<template>
  <div>
    <el-card>
      <template #header>
        <span>文案工作台</span>
      </template>

      <el-row :gutter="16">
        <!-- 左侧：编辑区 -->
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>
              <span>文案编辑</span>
            </template>
            <el-input
              v-model="copyText"
              type="textarea"
              :rows="15"
              placeholder="请输入需要审核或优化的文案内容..."
            />
          </el-card>
        </el-col>

        <!-- 右侧：模式与结果 -->
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>处理结果</span>
                <el-button-group>
                  <el-button
                    :type="mode === 'review' ? 'primary' : 'default'"
                    @click="mode = 'review'"
                  >
                    审核
                  </el-button>
                  <el-button
                    :type="mode === 'generate' ? 'primary' : 'default'"
                    @click="mode = 'generate'"
                  >
                    生成
                  </el-button>
                </el-button-group>
              </div>
            </template>

            <div class="result-area">
              <div v-if="result" class="result-text">{{ result }}</div>
              <el-empty v-else description="暂无结果，请输入文案后点击处理" />
            </div>

            <div style="margin-top: 12px;">
              <el-button type="primary" @click="handleProcess">
                {{ mode === 'review' ? '开始审核' : '生成文案' }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const copyText = ref('')
const mode = ref<'review' | 'generate'>('review')
const result = ref('')

function handleProcess() {
  // Placeholder：后续接入真实 API
  if (mode.value === 'review') {
    result.value = '文案审核功能开发中...'
  } else {
    result.value = '文案生成功能开发中...'
  }
}
</script>

<style scoped>
.result-area {
  min-height: 280px;
  display: flex;
  align-items: flex-start;
}

.result-text {
  width: 100%;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
}
</style>
