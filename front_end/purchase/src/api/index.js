import Axios from 'axios'
import Vue from 'vue'
import common from './modules/common'

const modules = [common]

class Fetch {
    getData(config) {
        Vue.myLoading.show('正在请求数据')
        const instance = Axios.create(config)

        // 添加单次请求的拦截器
        instance.interceptors.request.use(...config.reqInterceptor)
        instance.interceptors.response.use(...config.repInterceptor)

        return instance().finally(e => {
            Vue.myLoading.close()
        })
    }
}

modules.forEach(_module => {
    for (let [fnName, fn] of Object.entries(_module)) {
        Fetch.prototype[fnName] = fn
    }
})

export default {
    fetch: new Fetch(),
    install: (Vue) => {
        Vue.prototype.$fetch = new Fetch()
    }
}
