import _ from 'lodash'
class DistributionManager {
    constructor() {
        let storage = sessionStorage.getItem('DistributionStaff')

        if (!storage) {
            sessionStorage.setItem('DistributionStaff', JSON.stringify({}))
        }

        // let dataExample = {
        //     12: { // 意向单Id
        //         24: [{ // 商品id
        //             shop_id: 0,
        //             allocating_amount: 12
        //         }]
        //     }
        // }
        this.storage = null
    }

    set(wishOrderId, goodsId, data) {
        this.storage = JSON.parse(sessionStorage.getItem('DistributionStaff'))
        _.setWith(this.storage, `[${wishOrderId}][${goodsId}]`, data, Object)
        sessionStorage.setItem('DistributionStaff', JSON.stringify(this.storage))
    }

    get(wishOrderId, goodsId) {
        let storage = this.storage || JSON.parse(sessionStorage.getItem('DistributionStaff'))
        return _.get(storage, `${wishOrderId}.${goodsId}`, [])
    }
}

export default new DistributionManager()
