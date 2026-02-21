<template>
  <div>
    <el-card>
      <template #header>
        <span>文档审核</span>
      </template>

      <el-upload
        drag
        action="#"
        accept=".pdf,.doc,.docx"
        :auto-upload="false"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 .pdf、.doc、.docx 格式</div>
        </template>
      </el-upload>
    </el-card>

    <el-card v-if="reportVisible" style="margin-top: 16px;">
      <template #header>
        <span>审核报告</span>
      </template>
      <div class="report-placeholder">
        <el-empty description="审核功能开发中..." />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'

const reportVisible = ref(false)

function handleFileChange(_file: UploadFile) {
  // Placeholder：后续接入真实审核 API
  reportVisible.value = true
}
</script>

<style scoped>
.report-placeholder {
  padding: 24px 0;
}
</style>
