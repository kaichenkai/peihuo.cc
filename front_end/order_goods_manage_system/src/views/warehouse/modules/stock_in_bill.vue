<template>
    <el-dialog
        title="分车入库"
        :visible.sync="dialogVisible"
        width="600px">
        <p>分车单号：{{stock_in_detail.order_no}}</p>
        <p>货品名：{{stock_in_detail.goods_name}}</p>
        <p>入库数量：{{stock_in_detail.stock_in_amount}}</p>
        <p>修改入库数量：<input type="number" v-selectTextOnFocus v-removeMouseWheelEvent v-model="modifyAmount"></p>
        <span slot="footer" class="dialog-footer">
            <el-button class="btn confirm" @click="confirm">确认入库</el-button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            modifyAmount: 0
        }
    },

    props: {
        stock_in_detail: {
            default() {
                return {}
            },
            type: Object
        }
    },

    watch: {
        stock_in_detail: {
            handler: function(newVal) {
                this.modifyAmount = newVal.stock_in_amount
            },
            deep: true
        }
    },

    methods: {
        open(obj) {
            this.callback = obj.callback || function() {}
            this.dialogVisible = true
        },

        confirm() {
            this.$fetch.post({
                url: `/warehouse/stockin`,
                params: {
                    allocation_order_id: this.stock_in_detail.allocation_order_id,
                    stock_in_amount: this.modifyAmount
                }
            }).then(() => {
                this.openMessage(1, '入库成功')
                this.$emit('stockinSuccess')
                this.callback()
                this.dialogVisible = false
            }).catch(erro => {
                this.openMessage(0, erro)
            })
        },

        cancel() {
            this.dialogVisible = false
        }
    },
    components: {
    }
}
</script>

<style lang="scss" scoped>
p{
    line-height: 32px;
    color:#000;
}
.inline {
    .el-form-item{
        margin-bottom: 20px;
    }
}

input {
    height: 40px;
    padding-left: 10px;
    font-size: 18px;
}
</style>
