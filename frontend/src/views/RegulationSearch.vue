<template>
  <div>
    <el-card>
      <template #header>
        <span>法规智能检索</span>
      </template>

      <el-input
        v-model="query"
        placeholder="请输入查询内容，如'烟酰胺使用限量要求'"
        size="large"
      >
        <template #append>
          <el-button :icon="Search" @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </el-card>

    <el-card v-if="result" style="margin-top: 16px;">
      <template #header>
        <span>AI 智能摘要</span>
      </template>
      <div v-html="result" class="result-content" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const query = ref('')
const result = ref('')

function handleSearch() {
  if (!query.value.trim()) return
  // Placeholder：后续接入真实检索 API
  result.value = '检索功能开发中...'
}
</script>

<style scoped>
.result-content {
  line-height: 1.8;
  color: #333;
}
</style>
