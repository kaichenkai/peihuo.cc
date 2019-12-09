<template>
    <el-dialog
    title="修改品名"
    :visible.sync="dialogVisible"
    width="300"
    >
    <!-- <span class="name">{{goodsData.goods_name}}</span> -->
    <el-input class="input" v-model="orderGoodsName"></el-input>
    <span slot="footer" class="dialog-footer">
        <button class="btn confirm" @click="confirm">确认</button>
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
            goodsData: {},
            orderGoodsName: ''
        }
    },

    methods: {
        open(obj) {
            console.log(obj)
            // this.orderGoodsName = obj.goodsData.goods_name
            this.dialogVisible = true
            this.callback = obj.callback || function() {}
            this.goodsData = obj.data
            this.orderGoodsName = obj.data.order_goods_name || obj.data.goods_name || obj.data.name
        },

        confirm() {
            if (!this.orderGoodsName) {
                return this.openMessage(2, '请填写品名')
            }
            this.dialogVisible = false
            this.callback(this.orderGoodsName)
        }
    }
}
</script>

<style lang="scss" scoped>
/deep/ .input {
    margin-top: 10px;
    .el-input__inner {
        border-radius: 0px;
    }
}
</style>
