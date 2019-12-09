<template>
    <div>
        <el-radio-group v-model="form.scope" style="margin-bottom: 10px">
            <el-radio-button :label="0">按日</el-radio-button>
            <el-radio-button :label="1">按月</el-radio-button>
            <el-radio-button :label="2">按年</el-radio-button>
        </el-radio-group>
        <div class="choose_date">
            <template v-if="form.scope===0">
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
            <template v-else-if="form.scope===1">
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
        <el-button class="btn add-expenses" @click="addExpenses" type="text">+添加费用</el-button>
        <el-table
            :data="tableData"
            :height="tableHeight-50"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
            prop="date"
            label="日期"
            width="100">
            </el-table-column>
            <el-table-column
            prop="voucher_sum"
            label="货品采购"
            width="150">
            <template slot-scope="scope">
                <el-button @click="showPurchaseDetail(scope.row)" type="text">{{scope.row.voucher_sum}}</el-button>
            </template>
            </el-table-column>
            <el-table-column
            prop="delivery_sum"
            label="运杂费"
            width="150">
            <template slot-scope="scope">
                <el-button type="text" @click="showDetail(1, scope.row)">{{scope.row.delivery_sum}}</el-button>
            </template>
            </el-table-column>
            <el-table-column
            prop="routine_sum"
            label="日常杂费">
            <template slot-scope="scope">
                <el-button type="text" @click="showDetail(2, scope.row)">{{scope.row.routine_sum}}</el-button>
            </template>
            </el-table-column>
            <el-table-column
            prop="address"
            width="140"
            label="总费用">
            <template slot-scope="scope">
                <span>{{scope.row.voucher_sum + scope.row.delivery_sum + scope.row.routine_sum}}</span>
            </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <add-expensses ref="addExpenses"></add-expensses>
        <fees-list ref="feesList"></fees-list>
    </div>
</template>

<script>
import { formatDate } from '@/utils'
import AddExpensses from './components/add_expenses'
import FeesList from './components/fees-list'
export default {
    data() {
        return {
            tableData: [],
            form: {
                scope: 0,
                from_date: formatDate(new Date(new Date().setDate(1)), 'yyyy-MM-dd'), // 起始日
                to_date: formatDate(new Date(), 'yyyy-MM-dd'), // 截止日
                month_date: formatDate(new Date(new Date().setDate(1)), 'yyyy-MM-dd'),
                year_date: formatDate(new Date(new Date().getFullYear(), 0, 1), 'yyyy-MM-dd')
            }
        }
    },

    props: {
        activeName: String
    },

    computed: {
        from_date() {
            let fromDate = ''
            switch (this.form.scope) {
                case 0:
                    fromDate = this.form.from_date
                    break
                case 1:
                    fromDate = this.form.month_date
                    break
                case 2:
                    fromDate = this.form.year_date
                    break
            }
            return fromDate
        },
        to_date() {
            let toDate = ''
            let yearStr = ''
            switch (this.form.scope) {
                case 0:
                    toDate = this.form.to_date
                    break
                case 1:
                    toDate = this.form.month_date
                    yearStr = parseInt(toDate.substr(0, 4))
                    let monthStr = parseInt(toDate.substr(5, 2))
                    toDate = formatDate(new Date(yearStr, monthStr, 1), 'yyyy-MM-dd')
                    break
                case 2:
                    toDate = this.form.year_date
                    yearStr = parseInt(toDate.substr(0, 4))
                    toDate = formatDate(new Date(yearStr + 1, 0, 1), 'yyyy-MM-dd')
                    break
            }
            return toDate
        }
    },

    watch: {
        activeName(newVal) {
            if (newVal === 'first') {
                this.getTableList()
            }
        },

        form: {
            handler() {
                this.getTableList()
            },
            deep: true
        }
    },

    created() {
        this.getTableList()
    },

    methods: {
        getTableList(page = 0) {
            return this.$fetch.get({
                url: '/feesummarys',
                params: {
                    scope: this.form.scope,
                    from_date: this.from_date,
                    to_date: this.to_date
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.summarys
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.summarys)
                }
                return data
            })
        },

        addExpenses() {
            this.$refs.addExpenses.open({
                callback: this.getTableList.bind(this)
            })
        },

        // 1 运杂费 2 日常杂费
        showDetail(type, data) {
            this.$refs.feesList.open({
                title: type === 1 ? '运杂费' : '日常杂费',
                type: type,
                data: data,
                dateType: this.form.scope
            })
        },

        showPurchaseDetail(row) {
            this.$router.push({
                path: '/main/reconcileCenter/purchaseDetail',
                query: {
                    dateType: this.form.scope,
                    date: row.date
                }
            })
        }
    },

    components: {
        AddExpensses,
        FeesList
    }
}
</script>

<style lang="scss" scoped>
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
.add-expenses {
    float: right;
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
</style>
