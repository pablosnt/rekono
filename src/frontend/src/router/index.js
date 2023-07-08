import NotFound from '@/errors/NotFound'
import store from '@/store'
import Login from '@/views/Login'
import Main from '@/views/Main'
import Profile from '@/views/Profile'
import Project from '@/views/Project'
import ResetPassword from '@/views/ResetPassword'
import Settings from '@/views/Settings'
import Signup from '@/views/Signup'
import Task from '@/views/Task'
import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

const publicRoutes = ['login', 'signup', 'resetPassword']
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
    path: '/projects/:id/(details|targets|tasks|findings|members)?',
    name: 'project',
    component: Project,
    props: true
  },
  {
    path: '/signup',
    name: 'signup',
    component: Signup,
    props: route => ({ otp: route.query.token })
  },
  {
    path: '/reset-password',
    name: 'resetPassword',
    component: ResetPassword,
    props: route => ({ otp: route.query.token })
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings
  },
  {
    path: '/tasks/:id',
    name: 'task',
    component: Task,
    props: true
  },
  {
    path: '*',
    name: 'notFound',
    component: NotFound
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
