import Vue from 'vue'
import Router from 'vue-router'
// import store from '../store'

import Login from '@/components/Login'
import Main from '@/components/Main'

Vue.use(Router)

var router = new Router({
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/(dashboard|projects|tools|processes|resources|users|)',
      name: 'main',
      component: Main
    }
  ]
})
/*
const publicRoutes = ['login']

router.beforeEach((to, from, next) => {
  if (to.name === 'login)' && store.state.user != null) {
    next({ name: 'main' })
  } else if (!publicRoutes.includes(to.name) && store.state.user == null) {
    next({ name: 'login' })
  } else {
    next()
  }
})
*/
export default router
