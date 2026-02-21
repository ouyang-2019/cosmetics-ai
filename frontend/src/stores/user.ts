import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi } from '../api/auth'
import router from '../router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')

  async function login(name: string, password: string) {
    const res: any = await loginApi({ username: name, password })
    token.value = res.access_token
    username.value = name
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('username', name)
    router.push('/')
  }

  function logout() {
    token.value = ''
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  }

  return { token, username, login, logout }
})
