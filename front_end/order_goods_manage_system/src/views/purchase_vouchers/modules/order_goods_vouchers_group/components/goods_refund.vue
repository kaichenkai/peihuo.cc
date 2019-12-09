<template>
    <el-dialog
    title="退货"
    :visible.sync="dialogVisible"
    width="300">
    <p style="color: #999">退货后将清除采购端该货品的采购数据</p>
    <span class="name">商品名称：{{goodsData.goods_name}}</span>
    <p v-for="(item,index) in refundList" :key="index"><my-radio v-model="choosedFirm" :label="item.id">{{item.firm_name}} 实采:{{item.actual_amount}}</my-radio></p>
    <span slot="footer" class="dialog-footer">
        <button class="btn confirm" @click="confirm">确认退货</button>
        <button class="btn cancel" @click="dialogVisible = false">取消</button>
        <!-- <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button> -->
    </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            refundList: [],
            choosedFirm: 0,
            goodsData: {}
        }
    },

    created() {
    },

    methods: {
        open(obj) {
            this.dialogVisible = true
            this.goodsData = obj.data
            this.wishOrderId = obj.wishOrderId
            this.callback = obj.callback || function() {}
            this.getRefundData(this.goodsData)
        },

        getRefundData(data) {
            this.$fetch.get({
                url: '/purchase/order/goods/return',
                params: {
                    wish_order_id: this.wishOrderId,
                    goods_id: data.goods_id
                }
            }).then(data => {
                this.refundList = data.goods_list
            }).catch(e => {
                this.openMessage(0, e || '获取退货信息失败')
            })
        },

        confirm() {
            if (!this.choosedFirm) return this.openMessage(2, '请先选择供货商')
            let choosedFirmData = this.refundList.filter(value => value.id === this.choosedFirm)[0]
            this.$fetch.put({
                url: '/purchase/order/goods/return',
                params: {
                    wish_order_id: this.wishOrderId,
                    goods_id: choosedFirmData.id,
                    firm_id: choosedFirmData.firm_id
                }
            }).then(data => {
                this.openMessage(1, '退货成功')
                this.callback()
                this.choosedFirm = 0
                this.dialogVisible = false
            }).catch(e => {
                this.openMessage(0, e || '退货失败')
            })

            // this.callback(this.choosedPurchaser)
        }
    }
}
</script>

<style lang="scss" scoped>
.name {
    // position: absolute;
    // top: 20px;
    // left: 160px;
    // max-width: 200px;
    // overflow: hidden;
    // text-overflow: ellipsis;
    // white-space: nowrap;
    color: #333;
    font-weight: bold;
}

p {
    margin: 10px 0;
}
</style>
