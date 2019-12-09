import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/store'
import ajax from './api'
import loading from '@/components/base/loading'
import toast from '@/components/base/toast'
import './assets/style/reset.css'
import Alert from '@/components/base/alert'
import fastclick from 'fastclick'

require('viewport-units-buggyfill').init()
fastclick.attach(document.body)

Vue.prototype.$alert = Alert.install
Vue.config.productionTip = false
Vue.use(ajax)
Vue.use(loading)
Vue.use(toast)

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#app')
