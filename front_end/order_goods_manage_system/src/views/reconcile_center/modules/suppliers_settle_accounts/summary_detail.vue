<template>
    <el-dialog
        title="供货商结算记录"
        :visible.sync="dialogVisible"
        width="1076px">
        <div class="left" v-show="show_1" style="float: left;width: 340px;height: 550px;box-shadow: 0 0 10px 0 rgba(0,0,0,0.05);border-top: 1px solid #d9d9d9;">
            <el-table
                @row-click='rowClick'
                :highlight-current-row='true'
                :data="tableData_1"
                style="width: 100%;height:100%;">
                <el-table-column
                    prop="date"
                    label="日期"
                    width="100">
                </el-table-column>
                <el-table-column
                    prop="order_count"
                    label="结算次数"
                    width="">
                </el-table-column>
                <el-table-column
                    prop="voucher_count"
                    label="结算票数"
                    width="">
                </el-table-column>
                <el-table-column
                    prop="total_money"
                    label="结算金额"
                    width="">
                </el-table-column>
            </el-table>
        </div>
        <div class="right" style="float: left;height: 550px;padding: 10px;" :style="{width:width}">
            <div class="table" style="width: 100%;height: 100%;border: 1px solid #f2f2f2;">
                <el-table
                    :data="tableData_2"
                    height="530"
                    style="width: 100%">
                    <el-table-column
                    prop="create_time"
                    label="开票时间"
                    width="100">
                    </el-table-column>
                    <el-table-column
                    prop="order_no"
                    label="待结算单号"
                    width="160">
                    </el-table-column>
                    <el-table-column
                    prop="goods_name"
                    label="商品名">
                    </el-table-column>
                    <el-table-column
                    prop="remarks"
                    width="130"
                    label=备注>
                    </el-table-column>
                    <el-table-column
                    width="60"
                    label="件数">
                        <template slot-scope="scope">
                            {{scope.row.settled_amount}}
                            <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.settled_amount===scope.row.amount?'':scope.row.amount}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                    width="80"
                    label="采购价">
                        <template slot-scope="scope">
                            {{scope.row.settled_price}}
                            <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.settled_price===scope.row.price?'':scope.row.price}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                    width="90"
                    label="应结金额">
                        <template slot-scope="scope">
                            {{mostSaveTwoDecimal((scope.row.settled_price*scope.row.settled_amount).toFixed(2))}}
                            <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{modi_total(scope.row)}}</span>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </div>
    </el-dialog>
</template>
<script>
import { formatDate } from '@/utils'
export default {
    data() {
        return {
            dialogVisible: false,
            tableData_1: [],
            tableData_2: [],
            show_1: false,
            item: {},
            date: '',
            form: {}
        }
    },

    computed: {
        width() { // 日汇总详情左边的内容不显示,所以右边的宽度是变化的
            if (this.show_1) {
                return 'calc(100% - 340px)'
            } else {
                return '100%'
            }
        },
        before_date() { // 如果按月就是下个月的第一天，如果按年就是下一年的第一天formatDate
            if (this.scope === 1) {
                let yearStr = parseInt(this.date.substr(0, 4))
                let monthStr = parseInt(this.date.substr(5, 2))
                return formatDate(new Date(yearStr, monthStr, 1), 'yyyy-MM-d')
            } else {
                let yearStr = parseInt(this.date.substr(0, 4))
                return formatDate(new Date(yearStr + 1, 0, 1), 'yyyy-M-d')
            }
        }
    },
    
    methods: {
        rowClick(row) {
            if (this.scope === 1) { // 按月
                this.date = row.date
                this.settled_from_date = ''
                this.settled_before_date = ''
            } else { // 按年
                this.changeDate(row.date)
            }
            this.queryBillSummarys()
        },
        modi_total(item) { // 修改之后的应结金额
            if (item.settled_amount !== item.amount || item.settled_price !== item.price) {
                return item.total_money
            } else {
                return ''
            }
        },
        mostSaveTwoDecimal(num) { // 最多保留两位小数
            num = String(num)
            var size = num.length
            if (num.charAt(size - 1) === '0') {
                num = num.slice(0, -1)
                size = num.length
                if (num.charAt(size - 1) === '0') {
                    num = num.slice(0, -2)
                }
            }
            return Number(num)
        },
        open(obj, scope, date) { // 1该条汇总数据2 3查询汇总数据的日期参数
            this.dialogVisible = true
            this.show_1 = !(scope === 0)
            this.item = obj
            this.date = date
            this.scope = scope
            if ((scope === 0)) { // 日汇总
                this.queryBillSummarys()
            } else {
                this.queryDateSummarys()
            }
        },
        queryDateSummarys() { // 查询结算汇总
            this.$fetch.get({
                url: '/firmsettlementsummary',
                params: {
                    dimension: 'time',
                    firm_id: this.item.firm_id,
                    size: this.scope - 1, // 0月汇总详情1年汇总详情
                    from_date: this.date, // 月汇总的格式yyyy-MM-1,年汇总的格式yyyy-1-1
                    before_date: this.before_date // 同上
                }
            }).then(data => {
                this.tableData_1 = data.summarys
                if (this.scope === 1) { // 按月
                    this.date = data.summarys[0].date
                    this.settled_from_date = ''
                    this.settled_before_date = ''
                } else { // 按年
                    this.changeDate(data.summarys[0].date)
                }
                this.queryBillSummarys()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        queryBillSummarys() { // 查询结算单
            this.$fetch.get({
                url: '/firmsettlementvouchers',
                params: {
                    status: 1,
                    keyword: this.item.firm_name,
                    limit: 1000,
                    settled_date: this.date, // 当天
                    settled_from_date: this.settled_from_date, // 年汇总的格式yyyy-MM-1
                    settled_before_date: this.settled_before_date
                }
            }).then(data => {
                this.tableData_2 = data.order_list
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        changeDate(date) { // 从当月一号至下月一号,格式:yyyy-MM-1
            this.date = ''
            this.settled_from_date = date + '-1' // 起始时间
            // let str = date.substr(5, 2)
            // let month = Number(str)
            // let monthAdd = month + 1
            // monthAdd = monthAdd < 10 ? '0' + monthAdd : monthAdd
            // this.settled_before_date = date.replace(str, monthAdd) + '-1' // 截止时间
            let yearStr = parseInt(date.substr(0, 4))
            let monthStr = parseInt(date.substr(5, 2))
            this.settled_before_date = formatDate(new Date(yearStr, monthStr, 1), 'yyyy-MM-d')
        }
    }
}
</script>
<style lang="scss" scoped>
    /deep/ .el-dialog .el-dialog__body{
        padding: 0!important;
        overflow: hidden;
    }
    /deep/ .el-table{
        margin-top: 0;
    }
    /deep/ .el-table__body tr.current-row > td{
        background-color: #f5f7fa;
    }
</style>
