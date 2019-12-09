export default {

    methods: {
        getUserInfo() {
            return this.$fetch.get({
                url: '/login'
            }).then(data => {
                this.userData = data.user
                this.$store.commit('SET_USER_INFO', this.userData)
            }).catch(e => {
                this.openMessage(0, e || '获取用户信息失败')
            })
        },

        getCurrentShop() {
            return this.$fetch.get({
                url: '/currentshop'
            }).then(data => {
                this.$store.commit('SET_CURRENT_SHOP', data.data)
            }).catch(e => {
                this.openMessage(0, e || '获取当前店铺失败')
            })
        },

        getShopList() {
            return this.$fetch.get({
                url: '/demandorder/shop/list'
            }).then(data => {
                // this.shopList = data.shop_list
                this.$store.commit('SET_SHOP_LIST', data.shop_list)
            }).catch(e => {
                this.openMessage(0, e || '获取中转站列表失败')
            })
        }
    }
}
