<template>
    <div>
        <bread-crumb :titles="['对账中心 / 费用对账', '货品采购详情']"></bread-crumb>
        <i class="one-px-line"></i>
        <p style="margin: 10px 0; font-wight: bold; font-size: 14px;">{{date}}货品采购详情&nbsp;&nbsp;还剩{{unSettlement.count}}个货品未结算，应付款{{unSettlement.price.toFixed(2)}}元</p>
        <el-table
            :data="tableData"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
            type='index'
            width="50">
            <template slot-scope="scope">
                <span>{{scope.row._columnName || scope.$index}}</span>
                <!-- <span>{{JSON.stringify(scope)}}</span> -->
            </template>
            </el-table-column>
            <el-table-column
            prop="goods_name"
            label="商品名"
            min-width="200">
            </el-table-column>
            <el-table-column
            prop="purchaser_name"
            label="采购员"
            width="100">
            </el-table-column>
            <el-table-column
            prop="amount"
            label="件数">
            </el-table-column>
            <el-table-column
            prop="price"
            label="采购价">
            </el-table-column>
            <el-table-column
            prop="total_money"
            label="小计">
            </el-table-column>
            <el-table-column
            prop="firm_name"
            label="供货商">
            </el-table-column>
            <el-table-column
            prop="address"
            label="结款状态">
            <template slot-scope="scope">
                <span v-if="scope.row.status == 1">已结算</span>
                <el-button v-else-if="scope.row.status == 0" type="text" @click="clearingOrder(scope.row)">去结算</el-button>
            </template>
            </el-table-column>
            <el-table-column
            prop="settled_time"
            width="160"
            label="结算时间">
            <template slot-scope="scope">
                <span v-if="scope.row.settled_time">{{scope.row.settled_time}}</span>
                <span v-else>-</span>
            </template>
            </el-table-column>
            <el-table-column
            prop="creator_name"
            width="120"
            label="操作人">
            </el-table-column>
            <el-table-column
            prop="remarks"
            label="结款备注">
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
    </div>
</template>

<script>
import BreadCrumb from '@/components/modules_top_tools/bread_crumb'
import { formatDate } from '@/utils'
export default {
    data() {
        return {
            tableData: [],
            date: ''
        }
    },

    computed: {
        unSettlement() {
            return this.tableData.reduce((last, next) => {
                if (next.status === 0) {
                    last.count += 1
                    last.price += next.total_money
                }
                return last
            }, {
                count: 0,
                price: 0
            })
        }
    },

    created() {
        this.dateType = +this.$route.query.dateType
        this.date = this.$route.query.date
        this.getTableList()
    },

    methods: {
        getTableList(page = 0) {
            return this.$fetch.get({
                url: '/firmsettlementvouchers',
                params: {
                    from_date: this.getFormDate(),
                    before_date: this.getBeforeDate(),
                    page: page,
                    limit: 1000000
                }
            }).then(data => {
                if (page === 0) {
                    data.order_list.unshift({
                        _columnName: '累计',
                        total_money: data.order_list.reduce((last, next) => {
                            last += next.total_money
                            return last
                        }, 0),
                        amount: data.order_list.reduce((last, next) => {
                            last += next.amount
                            return last
                        }, 0),
                        status: -1
                    })
                    this.tableData = data.order_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.order_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        getFormDate() {
            let date = new Date(this.date.replace(/-/g, '/'))
            switch (this.dateType) {
                case 0: date = new Date(date); break
                case 1: date = new Date(date.setDate(1)); break
                case 2:
                    date = new Date(date.setDate(1))
                    date = new Date(date.setMonth(0)); break
                default:
                    this.openMessage(0, '日期类型错误')
            }

            return formatDate(new Date(date), 'yyyy-MM-dd')
        },

        getBeforeDate() {
            // debugger
            let date = new Date(this.date.replace(/-/g, '/'))
            switch (this.dateType) {
                case 0: date = date.setDate(date.getDate() + 1); break
                case 1:
                    date = new Date(date.setDate(1))
                    date = date.setMonth(date.getMonth() + 1); break
                case 2:
                    date = new Date(date.setDate(1))
                    date = new Date(date.setMonth(0))
                    date = date.setFullYear(date.getFullYear() + 1); break
                default:
                    this.openMessage(0, '日期类型错误')
            }

            return formatDate(new Date(date), 'yyyy-MM-dd')
        },

        clearingOrder(orderData) {
            this.$router.push({
                path: '/main/reconcileCenter/scavengingKnot',
                query: {
                    orderNo: orderData.order_no
                }
            })
        }
    },

    components: {
        BreadCrumb
    }
}
</script>

<style lang="scss" scoped>

</style>
