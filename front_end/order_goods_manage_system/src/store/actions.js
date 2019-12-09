import Api from '@/api'
const fetch = Api.fetch

export default {
    init({ commit }) {
        this.dispatch('getStationConfig')
        commit('SET_TABLE_HEADER', { table: '1', columnsSetting: [] })
        // this.dispatch('getUserPrivileges')
    },

    getStationConfig({ commit }) {
        fetch.get({
            url: '/config'
        }).then(data => {
            commit('SET_STATION_CONFIG', data.config)
        }).catch(e => {

        })
    },

    getUserPrivileges({ commit }) {
        return fetch.get({
            url: '/station/currentstaff'
        }).then(data => {
            // console.log('getUserPrivileges', data)
            commit('SET_USER_PRIVILEGES_INFO', data.data)
            return data.data
        }).catch(e => {

        })
    }
}
