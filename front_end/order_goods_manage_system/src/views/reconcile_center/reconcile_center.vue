<template>
    <div>
        <template v-if="show_1">
            <title-and-tools :config="{title: '对账中心'}"></title-and-tools>
            <el-tabs v-model="activeName" @tab-click="handleClick">
                <el-tab-pane label="费用对账" name="first">
                    <expenses-reconcile :activeName="activeName" style="margin-top: 13px"></expenses-reconcile>
                </el-tab-pane>
                <!-- <el-tab-pane label="资金对账" name="second">
                    <funds-reconcile style="margin-top: 13px"></funds-reconcile>
                </el-tab-pane> -->
                <el-tab-pane label="供货商结款" name="third">
                    <suppliers-settle-accounts style="margin-top: 13px" ref="SuppliersSettleAccounts" :activeName='activeName'></suppliers-settle-accounts>
                </el-tab-pane>
                <el-tab-pane label="分店对账" name="fourth">
                    <branch-reconciliation style="margin-top: 13px" ref="branchReconciliation" :activeName='activeName'></branch-reconciliation>
                </el-tab-pane>
            </el-tabs>
        </template>
    </div>
</template>

<script>
import titleAndTools from '@/components/modules_top_tools/title_&_tools'
import ExpensesReconcile from './modules/expenses_reconcile/expenses_reconcile'
import branchReconciliation from './modules/branch_reconciliation/branch_reconciliation'
import FundsReconcile from './modules/funds_reconcile'
import SuppliersSettleAccounts from './modules/suppliers_settle_accounts/suppliers_settle_accounts'
export default {
    data() {
        return {
            activeName: '',
            show_1: true,
            show_2: false
        }
    },
    watch: {
        activeName(val) {
            this.$router.replace({
                path: '/main/reconcileCenter/main',
                query: {
                    active: val
                }
            })
        }
    },

    created() {
        this.activeName = this.$route.query.active || 'first'
    },

    methods: {
        handleClick() {

        }

    },
    components: {
        titleAndTools,
        ExpensesReconcile,
        FundsReconcile,
        SuppliersSettleAccounts,
        branchReconciliation
    }
}
</script>

<style lang="scss" scoped>
    .layout-main{
        background-color: #f8f8f8!important;
    }
    /deep/ .layout-main{
        background-color: #f8f8f8!important;
    }
    /deep/ .el-tabs__content{
        overflow: inherit;
    }
</style>
