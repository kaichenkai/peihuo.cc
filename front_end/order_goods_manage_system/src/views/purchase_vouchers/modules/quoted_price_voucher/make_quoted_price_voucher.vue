<template>
    <div>
        <bread-crumb :titles="['采购单', '订货汇总单']"></bread-crumb>
        <i class="one-px-line"></i>
        <quoted-price-voucher mode="edit"></quoted-price-voucher>
    </div>
</template>

<script>
import BreadCrumb from '@/components/modules_top_tools/bread_crumb'
import QuotedPriceVoucher from './components/quoted_price_voucher'
export default {
    data() {
        return {

        }
    },

    components: {
        BreadCrumb,
        QuotedPriceVoucher
    }
}
</script>

<style lang="scss" scoped>

</style>
