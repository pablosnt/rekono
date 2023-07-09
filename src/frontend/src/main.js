import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import Icon from 'vue-awesome/components/Icon'
import Clipboard from "v-clipboard";

import 'vue-awesome/icons/brands/telegram'
import 'vue-awesome/icons/brands/linux'
import 'vue-awesome/icons/brands/windows'
import 'vue-awesome/icons/brands/apple'
import 'vue-awesome/icons/brands/android'
import 'vue-awesome/icons/brands/freebsd'
import 'vue-awesome/icons/sun'
import 'vue-awesome/icons/desktop'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import '@/assets/style.scss'

Vue.config.productionTip = false

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.use(Clipboard)
Vue.component('v-icon', Icon)

new Vue({
  el: '#app',
  router: router,
  store: store,
  render: h => h(App),
}).$mount('#app')
