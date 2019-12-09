import mainConfig from '../server_config/main'
import qs from 'qs'

export default {
    getHomePageData(params) {
        let serverConfig = {
            url: '/staff',
            params: qs.stringify(params),
            method: 'get'
        }
        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    getOrderList(params) {
        let serverConfig = {
            url: '/staff/order',
            params: qs.stringify(params),
            method: 'get'
        }

        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    orderPostAction(params) {
        let serverConfig = {
            url: '/staff/order',
            params: qs.stringify(params),
            method: 'post'
        }

        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    staffPostAction(params) {
        let serverConfig = {
            url: '/staff',
            params: qs.stringify(params),
            method: 'post'
        }

        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    get(data) {
        let serverConfig = {
            url: data.url,
            method: 'get',
            params: qs.stringify(data.params)
        }

        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    post(data) {
        let serverConfig = {
            url: data.url,
            method: 'post',
            data: data.params // qs.stringify(data.params)
        }

        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    put(data) {
        let serverConfig = {
            url: data.url,
            method: 'put',
            data: data.params // qs.stringify(data.params)
        }

        return this.getData(Object.assign(mainConfig, serverConfig))
    },

    delete(data) {
        let serverConfig = {
            url: data.url,
            method: 'delete',
            data: qs.stringify(data.params)
        }
        return this.getData(Object.assign(mainConfig, serverConfig))
    }

}
