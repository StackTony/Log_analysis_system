import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import LogAnalysis from '../views/LogAnalysis.vue'
import CaseLibrary from '../views/CaseLibrary.vue'
import CheckItemManagement from '../views/CheckItemManagement.vue'
import ReportManagement from '../views/ReportManagement.vue'
import UserManagement from '../views/UserManagement.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/log-analysis',
    name: 'LogAnalysis',
    component: LogAnalysis,
    meta: { requiresAuth: true }
  },
  {
    path: '/case-library',
    name: 'CaseLibrary',
    component: CaseLibrary,
    meta: { requiresAuth: true }
  },
  {
    path: '/check-items',
    name: 'CheckItemManagement',
    component: CheckItemManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/reports',
    name: 'ReportManagement',
    component: ReportManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user'))
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else if (to.matched.some(record => record.meta.requiresAdmin)) {
      if (user && user.role === 'admin') {
        next()
      } else {
        next({
          path: '/',
          query: { redirect: to.fullPath }
        })
      }
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router