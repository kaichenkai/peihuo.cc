import Vue from 'vue'
import Router from 'vue-router'
import HomePage from '@/views/home_page/home_page.vue'
import CaigouBill from '@/views/caigou_bill/caigou_bill.vue'
import PersonInfo from '@/views/user_info/person_info.vue'
import Login from '@/views/login/login.vue'
Vue.use(Router)

export default new Router({
    routes: [{
        path: '/',
        redirect: '/login'
    }, {
        path: '/login',
        name: 'login',
        component: Login
    }, {
        path: '/home',
        name: 'home',
        component: HomePage
    }, {
        path: '/caigou',
        name: 'caigou',
        component: CaigouBill
    }, {
        path: '/person',
        name: 'person',
        component: PersonInfo
    }]
})
