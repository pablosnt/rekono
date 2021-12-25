import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import Login from '@/views/Login'
import Main from '@/views/Main'
import Project from '@/views/Project'

Vue.use(Router)

const publicRoutes = ['login']
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
  }
]

const router = new Router({ routes: routes })

router.beforeEach((to, from, next) => {
  store.dispatch('checkState')
  if (to.name === 'login' && store.state.user !== null) {
    next({ name: 'main' })
  } else if (!publicRoutes.includes(to.name) && store.state.user === null) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
