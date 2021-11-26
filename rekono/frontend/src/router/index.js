import Vue from 'vue'
import Router from 'vue-router'
import store from '../store'

import Dashboard from '@/components/Dashboard'
import Login from '@/components/Login'

Vue.use(Router)

var router = new Router({
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard
    }
  ]
})

const publicRoutes = ['login']

router.beforeEach((to, from, next) => {
  if (!publicRoutes.includes(to.name) && store.state.user == null) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
