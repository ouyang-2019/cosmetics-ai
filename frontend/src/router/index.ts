import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    name: 'Main',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/regulation',
    children: [
      {
        path: '/regulation',
        name: 'RegulationSearch',
        component: () => import('../views/RegulationSearch.vue'),
        meta: { title: '法规检索', icon: 'Search' },
      },
      {
        path: '/doc-review',
        name: 'DocReview',
        component: () => import('../views/DocReview.vue'),
        meta: { title: '文档审核', icon: 'Document' },
      },
      {
        path: '/copy-workbench',
        name: 'CopyWorkbench',
        component: () => import('../views/CopyWorkbench.vue'),
        meta: { title: '文案工作台', icon: 'Edit' },
      },
      {
        path: '/knowledge',
        name: 'KnowledgeChat',
        component: () => import('../views/KnowledgeChat.vue'),
        meta: { title: '知识问答', icon: 'ChatDotRound' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/login') {
    next('/login')
  } else {
    next()
  }
})

export default router
