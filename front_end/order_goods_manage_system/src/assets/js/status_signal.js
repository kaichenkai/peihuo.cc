import api from '@/api'
import Vue from 'vue'
import store from '@/store'

const vue = new Vue()
const getData = api.fetch

class StatusSignal {
    getStatus() {
        this.getPurchaseStatusSignal()
    }

    startCheck() {
        this.getStatus()
        this.timer = setInterval(() => {
            this.getStatus()
        }, 60000)
    }

    clearCheck() {
        clearInterval(this.timer)
    }

    getPurchaseStatusSignal() {
        getData.get({
            url: '/summarynotifications'
        }).then(data => {
            console.log(data)
            store.commit('SET_DEMAND_ORDER_UPDATE_STATUS', data.data.demand_order_update)
        }).catch(e => {
            vue.$message.error(e || '获取数据更新失败')
        })
    }

    setPurchaseSignalStatus(wishOrderId) {
        getData.delete({
            url: '/summarynotifications',
            params: {
                notification_type: 'demand_order_update',
                wish_order_id: wishOrderId
            }
        }).then(data => {
            this.getStatus()
        }).catch(e => {
            vue.$message.error(e)
        })
    }
}

export default new StatusSignal()
