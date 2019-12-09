<template>
    <div>
        <el-dialog
            title="供货商支付账号"
            :visible.sync="dialogVisible"
            width="685px">
            <p>供货商：{{firm.name}}<span>(最多支持添加四个支付帐号)</span></p>
            <el-table
                :data="accounts"
                border
                style="width: 100%">
                <el-table-column
                    width="80">
                    <template slot-scope="scope">
                        {{scope.row.account_type | accountType}}
                    </template>
                </el-table-column>
                <el-table-column>
                    <template slot-scope="scope">
                        <span class="span">{{scope.row | showInfo}}</span>
                        <el-button @click="edit(scope.row)" type="text">编辑</el-button>
                        <el-button @click="deletePament(scope.row,$event)" type="text" style="color:#ff6666;">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <p class="add_payment"><i @click="addPayment">+添加新账号</i></p>
        </el-dialog>
        <supplier-payment-account ref="supplierPaymentAccount"></supplier-payment-account>
    </div>
</template>
<script>
import supplierPaymentAccount from './add_payment_account.vue'
export default {
    data() {
        return {
            dialogVisible: false,
            accounts: [],
            firm: {}
        }
    },

    filters: {
        accountType(type) {
            switch (type) {
                case 0:
                    return '未知'
                case 1:
                    return '支付宝'
                case 2:
                    return '对公转账'
                case 3:
                    return '对私转账'
            }
        },
        showInfo(item) {
            switch (item.account_type) {
                case 0:
                    return ''
                case 1:
                    return `${item.account_name} (${item.account_num})`
                case 2:
                case 3:
                    return `${item.bank_name}${item.account_num}(${item.account_name})${item.branch_bank_name}`
            }
        }
    },

    methods: {
        deletePament(payment, e) {
            this.$myWarning({
                message: '确定要删除吗？'
            }).then(() => {
                this.$fetch.delete({
                    url: `/firm/${this.firm.id}/paymentaccount/${payment.id}`
                }).then(data => {
                    this.openMessage(1, '删除成功')
                    this.open(this.firm)
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(e => {})
        },

        edit(payment) {
            this.cancel()
            this.$refs.supplierPaymentAccount.open(this.firm, payment)
        },

        addPayment() {
            this.cancel()
            this.$refs.supplierPaymentAccount.open(this.firm)
        },

        open(obj) {
            this.firm = JSON.parse(JSON.stringify(obj))
            this.$fetch.get({
                url: `/firm/paymentaccounts`,
                params: {
                    firm_ids: obj.id
                }
            }).then(data => {
                this.accounts = data.accounts
            }).catch(e => {
                this.openMessage(0, e)
            })
            this.dialogVisible = true
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
        font-size: 14px;
        color: #333333;
        &.add_payment{
            padding-left: 8px;
            color: rgba(107,164,239,0.95);
            line-height: 36px;
            border: 1px solid #DDDDDD;
            border-top: none;
            i{
                font-style: normal;
                cursor: pointer;
            }
        }
        span{
            margin-left: 10px;
            color: #999999;
        }
    }
    .span{
        position: relative;
        top:3px;
        display:inline-block;
        width:480px;
        white-space:nowrap;
        overflow: hidden;
        text-overflow:ellipsis;
    }
    /deep/ .el-table__header-wrapper{
        display: none;
    }
    /deep/ .el-dialog{
        height: 430px;
    }
    /deep/ .el-table .el-button--text{
        position: relative;
        top:-3px;
    }
</style>
