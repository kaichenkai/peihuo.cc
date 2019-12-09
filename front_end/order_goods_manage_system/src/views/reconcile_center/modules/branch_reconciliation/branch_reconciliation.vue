<template>
    <div class="branch_reconciliation">
        <el-radio-group v-model="radio3" style="margin-bottom: 10px">
            <el-radio-button label="日账单"></el-radio-button>
            <el-radio-button label="月汇总"></el-radio-button>
            <el-radio-button label="年汇总"></el-radio-button>
        </el-radio-group>
        <div class="choose_date">
            <template v-if="radio3==='日账单'">
                <span>起始日</span>
                <el-date-picker
                    v-model="form.from_date"
                    :editable='false'
                    :clearable='false'
                    type="date"
                    size="small"
                    value-format="yyyy-MM-dd"
                    placeholder="选择日期">
                </el-date-picker>
                <span>截止日</span>
                <el-date-picker
                    v-model="form.to_date"
                    :editable='false'
                    :clearable='false'
                    type="date"
                    size="small"
                    value-format="yyyy-MM-dd"
                    placeholder="选择日期">
                </el-date-picker>
            </template>
            <template v-else-if="radio3==='月汇总'">
                <span>日期选择</span>
                <el-date-picker
                    v-model="form.month_date"
                    :editable='false'
                    :clearable='false'
                    type="month"
                    size="small"
                    value-format="yyyy-MM-dd"
                    placeholder="选择日期">
                </el-date-picker>
            </template>
            <template v-else>
                <span>日期选择</span>
                <el-date-picker
                    v-model="form.year_date"
                    :editable='false'
                    :clearable='false'
                    type="year"
                    size="small"
                    value-format="yyyy-MM-dd"
                    placeholder="选择日期">
                </el-date-picker>
            </template>
        </div>
        <el-table
            :data="tableData"
            :height="tableHeight-50"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%"
            @sort-change='sort'
            >
            <el-table-column
                prop="date"
                label="日期"
                width="120">
            </el-table-column>
            <el-table-column
                min-width="200">
                <template slot="header" slot-scope="scope">
                    <table-data-filter title="店铺名" allString="所有店铺" :items="allshopsData" itemKeyName="name" itemKeyCode="id"  v-model="searchObj.shop_ids" @confirm="search"></table-data-filter>
                </template>
                <template slot-scope="scope">
                    <span class="name">{{ scope.row.shop_name }}</span>
                </template>
            </el-table-column>
            <el-table-column
                prop="packing_money"
                width="200"
                sortable='custom'
                label="实配金额">
            </el-table-column>
            <el-table-column
                prop="other_payout"
                label="其它支出"
                sortable='custom'
                width="200">
            </el-table-column>
            <el-table-column
                prop="payout_sum"
                label="金额小计"
                sortable='custom'
                width="200">
            </el-table-column>
            <el-table-column
                label=""
                width="">
                <template slot-scope="scope">
                    <el-button @click="seeDetail(scope.row)" type="text" >查看详情</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
    </div>
</template>
<script>
import { formatDate } from '@/utils'
import _ from 'lodash'
export default {
    data() {
        return {
            tableData: [],
            radio3: '日账单',
            form: {
                from_date: formatDate(new Date(new Date().setDate(1)), 'yyyy-MM-dd'), // 起始日
                to_date: formatDate(new Date(), 'yyyy-MM-dd'), // 截止日
                month_date: formatDate(new Date(new Date().setDate(1)), 'yyyy-MM-dd'),
                year_date: formatDate(new Date(new Date().getFullYear(), 0, 1), 'yyyy-MM-dd'),
                order_by: '',
                asc: ''
            },
            allshopsData: [],
            searchObj: {
                shop_ids: []
            }
        }
    },
    props: {
        activeName: {
            type: String,
            default: ''
        }
    },

    computed: {
        scope() {
            let scope = ''
            switch (this.radio3) {
                case '日账单':
                    scope = 0
                    break
                case '月汇总':
                    scope = 1
                    break
                case '年汇总':
                    scope = 2
                    break
            }
            return scope
        },
        from_date() {
            let fromDate = ''
            switch (this.radio3) {
                case '日账单':
                    fromDate = this.form.from_date
                    break
                case '月汇总':
                    fromDate = this.form.month_date
                    break
                case '年汇总':
                    fromDate = this.form.year_date
                    break
            }
            return fromDate
        },
        to_date() {
            let toDate = ''
            let yearStr = ''
            switch (this.radio3) {
                case '日账单':
                    toDate = this.form.to_date
                    break
                case '月汇总':
                    toDate = this.form.month_date
                    yearStr = parseInt(toDate.substr(0, 4))
                    let monthStr = parseInt(toDate.substr(5, 2))
                    toDate = formatDate(new Date(yearStr, monthStr, 1), 'yyyy-MM-dd')
                    break
                case '年汇总':
                    toDate = this.form.year_date
                    yearStr = parseInt(toDate.substr(0, 4))
                    toDate = formatDate(new Date(yearStr + 1, 0, 1), 'yyyy-MM-dd')
                    break
            }
            return toDate
        }
    },

    watch: {
        activeName(val) {
            if (val === 'fourth') {
                this.getShopaccounting()
            }
        },
        radio3() {
            this.getShopaccounting()
        },
        form: {
            handler() {
                this.getShopaccounting()
            },
            deep: true
        }
    },

    created() {
        this.getShopaccounting()
    },

    methods: {
        search() {
            this.getShopaccounting(0, this.searchObj)
        },
        seeDetail(item) {
            item.scope = this.scope
            this.$router.push({
                path: '/main/reconcileCenter/fendianDetail',
                query: {
                    item: JSON.stringify(item)
                }
            })
        },
        sort(obj) { // 排序
            this.form.order_by = obj.prop
            this.form.asc = obj.order === 'ascending'
        },
        getTableList(page) {
            return this.getShopaccounting(page)
        },
        getShopaccounting(page = 0, search = {}) {
            return this.$fetch.get({
                url: '/shopaccounting',
                params: {
                    from_date: this.from_date,
                    to_date: this.to_date,
                    page,
                    ..._.mapValues(search, obj => obj.join('|') || undefined),
                    order_by: this.form.order_by,
                    asc: this.form.asc,
                    scope: this.scope
                }
            }).then(data => {
                this.allshopsData = data.sum_data.shops
                if (page === 0) {
                    this.tableData = data.data_list
                    if (data.data_list.length > 0 && this.tableData[0].date !== '累计') {
                        this.tableData.unshift({
                            date: '累计',
                            packing_money: data.sum_data.packing_money,
                            other_payout: data.sum_data.other_payout,
                            payout_sum: data.sum_data.payout_sum
                        })
                    }
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.data_list)
                    if (data.data_list.length > 0 && this.tableData[0].date !== '累计') {
                        this.tableData.unshift({
                            date: '累计',
                            packing_money: data.sum_data.packing_money,
                            other_payout: data.sum_data.other_payout,
                            payout_sum: data.sum_data.payout_sum
                        })
                    }
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    },
    components: {
    }
}
</script>
<style lang="scss" scoped>
    .branch_reconciliation{
        .choose_date{
            position: relative;
            top: -4px;
            display: inline-block;
            span{
                margin-left: 20px;
                margin-right: 3px;
                font-size: 14px;
                color: #333333;
            }
        }
    }
    /deep/ .el-date-editor.el-input{
        margin-top: 8px;
        width: 150px;
        .el-input__inner{
            height: 30px;
            line-height: 30px;
            border-radius: 15px;
            font-size: 16px;
            color: #333333;
        }
    }
    /deep/ .el-picker-panel {
        position: absolute;
        z-index: 2;
    }
    /deep/ .el-table__row:nth-of-type(1) td {
        color: #333;
        font-weight: bold;
    }
    /deep/ .el-table__row:nth-of-type(1) td:nth-last-of-type(1) .cell{
        display: none;
    }
</style>
