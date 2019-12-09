<template>
    <div>
        <el-table
            :data="firm_list"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
                prop="name"
                label="姓名"
                width="120">
            </el-table-column>
            <el-table-column
                prop="phone"
                label="联系电话"
                width="200">
            </el-table-column>
            <el-table-column
                prop="remarks"
                label="备注"
                width="">
            </el-table-column>
            <el-table-column
                label="供应货品"
                width="150">
                <template slot-scope="scope">
                    <span style="display:inline-block;color:#009688;padding:0 8px;cursor:pointer" @click="$emit('openGoodsList',scope.row)">{{scope.row.goods_ids.length}}</span>
                    <el-button @click="$emit('chooseGoods',scope.row)" type="text">+添加</el-button>
                </template>
            </el-table-column>
            <el-table-column
                label="操作"
                width="190">
                <template slot-scope="scope">
                    <el-button @click="$emit('editSupplier',scope.row)" type="text" >编辑</el-button>
                    <el-button @click="paymentAccount(scope.row)" type="text" >支付账号</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <search-box :styleData='styleData' @searchData='searchData'></search-box>
        <edit-payment-account ref="editPaymentAccount"></edit-payment-account>
    </div>
</template>
<script>
import searchBox from '@/components/common/search.vue'
import editPaymentAccount from './edit_payment_account.vue'
export default {
    data() {
        return {
            firm_list: [
            ],
            styleData: {
                top: -64,
                placeholder: '请输入供货商姓名/手机号'
            },
            search_str: ''
        }
    },
    created() {
        this.queryData()
    },

    methods: {
        paymentAccount(firm) {
            this.$refs.editPaymentAccount.open(firm)
        },
        searchData(str) {
            this.search_str = str
            this.queryData(str)
        },
        getTableList(page) {
            return this.queryData(this.search_str, page)
        },
        queryData(str = '', page = 0) {
            return this.$fetch.get({
                url: '/station/firm/list',
                params: {
                    search: str,
                    page: page
                }
            }).then(data => {
                if (page === 0) {
                    this.firm_list = data.firm_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.firm_list = this.firm_list.concat(data.firm_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取供货商失败')
            })
        }
    },

    components: {
        searchBox,
        editPaymentAccount
    }
}
</script>
