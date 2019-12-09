import { mapState } from 'vuex'
import userInputCache from '../js/user_input_cache_manage'
import _ from 'lodash'
export default {
    data() {
        return {
            tableData: [],
            orderStoreList: [],
            wishOrderData: {},
            demandOrderData: {},
            status: 0,
            ismodify: false
        }
    },

    computed: {
        ...mapState(['currentShop', 'userInfo']),
        status0DemandTotal() {
            return this.getDemandAmount(0)
        },

        status1DemandTotal() {
            return this.getDemandAmount(1)
        },

        status2DemandTotal() {
            return this.getDemandAmount(2)
        },

        demandTotal() {
            return +(this.status0DemandTotal + this.status1DemandTotal + this.status2DemandTotal).toFixed(2)
        },

        volumeTotal() {
            return +(this.getTotal(0, 'goods_volume') + this.getTotal(1, 'goods_volume') + this.getTotal(2, 'goods_volume')).toFixed(2)
        },

        weightTotal() {
            return +(this.getTotal(0, 'goods_weight') + this.getTotal(1, 'goods_weight') + this.getTotal(2, 'goods_weight')).toFixed(2)
        }
    },

    created() {
        this.stationId = this.$route.query.stationId
        this.cacheUserInput = _.debounce(this.debounceCacheUserInput.bind(this), 300)
    },

    methods: {
        async init() {
            await this.getWishOrderData()
            this.getOrderStores()
            this.demandOrderId = await this.demandordersync()
            await this.getDemandorder(this.demandOrderId)

            this.mergeOrderData()
        },

        getOrderStores() {
            this.$fetch.get({
                url: '/wishorder/demand/' + this.wishOrderData.id
            }).then(data => {
                this.orderStoreList = data.demand_order_data
            }).catch(e => {
                this.openMessage(0, e || '获取订货门店列表失败')
            })
        },

        getWishOrderData() {
            return this.$fetch.get({
                url: '/demandwishorder/current'
            }).then(data => {
                // return data.order_data
                this.wishOrderData = data.order_data
            }).catch(e => {
                this.openMessage(0, e || '获取当前意向单失败')
            })
            // return this.$fetch.get({
            //     url: '/demandwishorder/' + this.stationId
            // }).then(data => {
            //     console.log(data)
            //     this.wishOrderData = data.order_data || {}
            // })
        },

        demandordersync() {
            return this.$fetch.put({
                url: '/demandordersync',
                params: {
                    wish_order_id: this.wishOrderData.id,
                    shop_id: this.currentShop.id
                }
            }).then(data => {
                // console.log(data)
                return data.demand_order_id
            })
        },

        getDemandorder(id) {
            return this.$fetch.get({
                url: '/shop/demandorder/' + id
            }).then(data => {
                console.log(data)
                this.demandOrderData = data.order_data || {}
            })
        },

        mergeOrderData() {
            // debugger
            // 获取用户上一次输入缓存的信息
            let lastUserInputCacheData = userInputCache.getData(this.demandOrderId, this.demandOrderData.update_time.replace(/-/g, '/'))
            // 合并意向单以及订货单数据

            this.tableData = Object.values(this.wishOrderData.goods_data)
                .reduce((last, next) => [...last, ...next.map(value => { // 将意向单以及订货单同名字段进行修改备份
                    value._remarks = value.remarks
                    value._status = value.status
                    return value
                })], [])
                .map(goods => { // goods为意向单的商品
                    let cachedGoodsData = {}
                    let demandGoods = this.demandOrderData.goods_data.find(item => item.wish_order_goods_id === goods.id) || {}

                    if (lastUserInputCacheData) { // 如果用户之前输入了数据但是没提交订货单，那么就从之前缓存的数据中读取数据
                        cachedGoodsData = lastUserInputCacheData.find(item => item.wish_order_goods_id === goods.id) || {}
                        return Object.assign({}, goods, demandGoods, cachedGoodsData)
                    } else {
                        return Object.assign({}, goods, demandGoods)
                    }
                })
            // console.log(this.tableData)
        },

        debounceCacheUserInput() {
            userInputCache.setData(this.demandOrderId, this.tableData.map(value => {
                let obj = {}
                obj.remarks = value.remarks
                obj.current_storage = value.current_storage
                obj.demand_amount = value.demand_amount
                obj.wish_order_goods_id = value.wish_order_goods_id

                return obj
            }))
        },

        getDemandAmount(goodsStatus) {
            return this.tableData.filter(value => value._status === goodsStatus).reduce((last, next) => {
                return +last + (+next.demand_amount || 0)
            }, 0)
        },

        getTotal(goodsStatus, totalType) {
            return this.tableData.filter(value => value._status === goodsStatus).reduce((last, next) => {
                return +last + (+next.demand_amount || 0) * next[totalType]
            }, 0)
        }
    }
}
