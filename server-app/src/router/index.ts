import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'layout',
      redirect: '/dashboard',
      component: () => import('@/views/Layout.vue'),
      children: [
        {
          path: '/dashboard',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '数据概览' }
        },
        {
          path: '/users',
          name: 'users',
          component: () => import('@/views/Users.vue'),
          meta: { title: '人员管理' }
        },
        {
          path: '/events',
          name: 'events',
          component: () => import('@/views/Events.vue'),
          meta: { title: '拷入记录' }
        },
        {
          path: '/devices',
          name: 'devices',
          component: () => import('@/views/Devices.vue'),
          meta: { title: 'USB设备' }
        }
      ]
    }
  ]
})

export default router
