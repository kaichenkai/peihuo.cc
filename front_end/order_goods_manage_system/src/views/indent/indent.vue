<template>
    <div style="height: 100%;background: #fff">
        <pc-indent v-if="isPC"></pc-indent>
        <mobile-indent v-else></mobile-indent>
    </div>
</template>

<script>
import MobileIndent from './modules/mobile/mobile_indent'
import PcIndent from './modules/pc/order_goods_voucher'
import MIXIN_GET_INFO from './mixin/get_info'
import { isPC } from '@/utils'
export default {
    data() {
        return {
            isPC: isPC()
        }
    },

    mixins: [MIXIN_GET_INFO],

    async created() {
        this.stationId = this.$route.query.stationId
        await this.setServerStatus()
        this.getUserInfo()
        this.getCurrentShop()
        this.getShopList()
    },

    methods: {
        setServerStatus() {
            return this.$fetch.get({
                url: '/demandorder/station',
                params: {
                    'station_id': this.stationId
                }
            })
        }
    },

    components: {
        MobileIndent,
        PcIndent
    }
}
</script>

<style>

</style>
