<template>
    <el-dialog
    title="设置采购员"
    :visible.sync="dialogVisible"
    width="300">
    <p style="color: #999">设置完成后，该商品以后会默认分配到该采购员</p>
    <span class="name">商品名称：{{goodsData.goods_name}}</span>
    <!-- <p><my-radio v-model="choosedPurchaser" :label="0">无</my-radio></p> -->
    <p v-for="(item,index) in purchasers" :key="index"><my-radio v-model="choosedPurchaser" :label="item.staff_id">{{item.name}}</my-radio>({{item.remarks}})<span></span></p>
    <span slot="footer" class="dialog-footer">
        <button class="btn confirm" @click="confirm">确认</button>
        <button class="btn cancel" @click="dialogVisible = false">取消</button>
    </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            purchasers: [{
                staff_id: 0,
                name: '无',
                remarks: '-'
            }],
            choosedPurchaser: 0,
            goodsData: {}
        }
    },

    created() {
        this.getPurchasers()
    },

    methods: {
        open(obj) {
            this.dialogVisible = true
            this.goodsData = obj.data
            this.wishOrderData = obj.wishOrderData
            this.callback = obj.callback || function() {}
            this.choosedPurchaser = obj.data.purchaser_id
        },

        getPurchasers() {
            this.$fetch.get({
                url: '/stafflist',
                params: {
                    "role": 'purchaser',
                    "page": 0,
                    "limit": 10000
                }
            }).then(data => {
                this.purchasers = this.purchasers.concat(data.staff_list)
            }).catch(e => {
                this.openMessage(0, '获取采购员数据失败,' + e)
            })
        },

        confirm() {
            let choosedPurchaserData = this.purchasers.filter(value => {
                return this.choosedPurchaser === value.staff_id
            })[0]
            this.$fetch.put({
                url: '/purchase/order/goods/purchaser',
                params: {
                    wish_order_id: this.wishOrderData,
                    goods_id: this.goodsData.goods_id,
                    purchaser_id: this.choosedPurchaser
                }
            }).then(() => {
                this.dialogVisible = false
                this.callback(this.choosedPurchaser, choosedPurchaserData.remarks)
            }).catch(e => {
                console.log(e)
                this.openMessage(0, e || '设置默认采购员失败')
            })
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
