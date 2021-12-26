import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import Login from '@/views/Login'
import Main from '@/views/Main'
import Project from '@/views/Project'
import Signup from '@/views/Signup'

Vue.use(Router)

const publicRoutes = ['login', 'signup']
const routes = [
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/(dashboard|projects|tools|processes|wordlists|users|)',
    name: 'main',
    component: Main
  },
  {
    path: '/projects/:id',
    name: 'project',
    component: Project,
    props: true
  },
  {
    path: '/signup',
    name: 'signup',
    component: Signup,
    props: route => ({ otp: route.query.token })
  }
]

const router = new Router({ routes: routes })

router.beforeEach((to, from, next) => {
  store.dispatch('checkState')
  if (publicRoutes.includes(to.name) && store.state.user !== null) {
    next({ name: 'main' })
  } else if (!publicRoutes.includes(to.name) && store.state.user === null) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
