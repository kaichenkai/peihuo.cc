import Axios from 'axios'
import common from './modules/common'
console.log(common)
const modules = [common]
console.log(modules)
class Fetch {
    getData(config) {
        const instance = Axios.create(config)

        // 添加单次请求的拦截器
        instance.interceptors.request.use(...config.reqInterceptor)
        instance.interceptors.response.use(...config.repInterceptor)

        return instance().finally(e => {

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
