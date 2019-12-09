import Vue from 'vue'
import App from './App.vue'
import router from './router/router'
import store from './store/index'

// ---------------- lib -------------------
import ElementUI from 'element-ui'
// import Rx from 'rxjs'

// ----------------  ----------------------
import Api from './api'
import MyComponents from '@/components/common'
import MyMobileComponents from '@/components/mobile/common'
import MainMixins from '@/mixins'
import Validator from '@/assets/js/validator'
// import TableScrollLoad from '@/directives/table_scroll_load'
import MainDirective from '@/directives'

// ---------------- css --------------------
// import 'element-ui/lib/theme-chalk/index.css'
import '@/assets/style/reset.scss'
import '@/assets/style/override_element_ui.scss'
import '@/assets/style/common.scss'

// window.Rx = Rx
Vue.use(ElementUI)
Vue.use(Api)
Vue.use(MyComponents)
Vue.use(MyMobileComponents)
Vue.use(MainMixins)
Vue.use(Validator)
// Vue.use(TableScrollLoad)
Vue.use(MainDirective)

Vue.config.productionTip = false

new Vue({
    router,
    store,
    render: h => h(App)
}).$mount('#app')
