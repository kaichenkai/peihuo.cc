<template>
    <div>
        <el-dialog
            title="新建供货商"
            :visible.sync="dialogVisible"
            width="445px">
            <p class="success">供货商新建成功</p>
            <p class="info">添加供货商转账信息，方便财务结算</p>
            <span slot="footer" class="dialog-footer">
                <button class="btn confirm" @click="confirm" style="padding: 7px 16px;">补充转账信息</button>
                <button class="btn cancel" @click="cancel">暂不想填</button>
            </span>
        </el-dialog>
        <supplier-payment-account ref="supplierPaymentAccount"></supplier-payment-account>
    </div>
</template>

<script>
import supplierPaymentAccount from './add_payment_account.vue'
export default {
    data() {
        return {
            dialogVisible: false
        }
    },
    methods: {
        open(obj) {
            this.dialogVisible = true
            this.firm_dict = obj
        },

        confirm() {
            this.cancel()
            this.$refs.supplierPaymentAccount.open(this.firm_dict)
        },

        cancel() {
            this.dialogVisible = false
        }

    },
    components: {
        supplierPaymentAccount
    }
}
</script>

<style lang="scss" scoped>
    p{
        text-align: center;
        &.success{
            color: #333333;
            font-size: 16px;
            font-weight: bold;
            padding-top: 56px;
            background: url('~@/assets/images/finish.png') no-repeat center -50px;
        }
        &.info{
            padding-top: 20px;
        }
    }
</style>
