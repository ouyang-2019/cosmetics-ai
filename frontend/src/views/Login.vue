<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="logo-section">
        <h1>化妆品AI智能平台</h1>
        <p>法规检索 · 文档审核 · 文案合规 · 知识问答</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-position="top"
            @submit.prevent="handleLogin"
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                :loading="loginLoading"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            @submit.prevent="handleRegister"
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                :prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                :prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item label="姓名" prop="full_name">
              <el-input
                v-model="registerForm.full_name"
                placeholder="请输入姓名（选填）"
                size="large"
              />
            </el-form-item>

            <el-form-item label="部门" prop="department">
              <el-select
                v-model="registerForm.department"
                placeholder="请选择部门（选填）"
                size="large"
                style="width: 100%"
                clearable
              >
                <el-option label="法规事务部" value="法规事务部" />
                <el-option label="质量管理部" value="质量管理部" />
                <el-option label="研发部" value="研发部" />
                <el-option label="市场部" value="市场部" />
                <el-option label="生产部" value="生产部" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                :loading="registerLoading"
                @click="handleRegister"
              >
                注 册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '../stores/user'
import { register as registerApi } from '../api/auth'

const userStore = useUserStore()
const activeTab = ref('login')

// === Login ===
const loginFormRef = ref<FormInstance>()
const loginLoading = ref(false)
const loginForm = reactive({ username: '', password: '' })

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!loginFormRef.value) return
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loginLoading.value = true
  try {
    await userStore.login(loginForm.username, loginForm.password)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loginLoading.value = false
  }
}

// === Register ===
const registerFormRef = ref<FormInstance>()
const registerLoading = ref(false)
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  full_name: '',
  department: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度 3-50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

async function handleRegister() {
  if (!registerFormRef.value) return
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  registerLoading.value = true
  try {
    await registerApi({
      username: registerForm.username,
      password: registerForm.password,
      full_name: registerForm.full_name || undefined,
      department: registerForm.department || undefined,
    })
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    loginForm.password = ''
    registerFormRef.value.resetFields()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '注册失败，请稍后重试')
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 440px;
  border-radius: 12px;
  padding: 10px 20px;
}

.logo-section {
  text-align: center;
  margin-bottom: 8px;
}

.logo-section h1 {
  font-size: 22px;
  color: #333;
  margin: 0 0 6px;
}

.logo-section p {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}
</style>
