<template>
    <div class="suppliers_settle_accounts">
        <el-radio-group v-model="radio3" style="margin-bottom: 10px">
            <el-radio-button label="结算流水"></el-radio-button>
            <el-radio-button label="按日"></el-radio-button>
            <el-radio-button label="按月"></el-radio-button>
            <el-radio-button label="按年"></el-radio-button>
        </el-radio-group>
        <div class="choose_date">
            <template v-if="radio3==='结算流水'">
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
            <template v-else>
                <span>日期选择</span>
                <el-date-picker
                    v-model="summary_date"
                    :editable='false'
                    :clearable='false'
                    :type="date_type"
                    size="small"
                    @change="dateChange"
                    :value-format="value_format"
                    placeholder="选择日期">
                </el-date-picker>
            </template>
        </div>
        <el-table
            v-show="show_1"
            :data="tableData"
            :height="tableHeight-58"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
            prop="create_time"
            label="结款时间"
            width="100">
            </el-table-column>
            <el-table-column
            prop="creator_name"
            label="操作人"
            width="150">
            </el-table-column>
            <el-table-column
            label="结款金额"
            width="150">
                <template slot-scope="scope">
                    {{scope.row.total_money}}
                    <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{''}}</span>
                </template>
            </el-table-column>
            <el-table-column
            prop=""
            min-width="200">
                <template slot="header" slot-scope="scope">
                    <table-data-filter title="供货商" allString="所有供货商" :items="allFirmsData" itemKeyName="name" itemKeyCode="id"  v-model="searchObj.firm_ids" @confirm="queryData"></table-data-filter>
                </template>
                <template slot-scope="scope">
                    <span v-if="scope.row.firms.length == 1">{{scope.row.firms[0].name}}</span>
                    <span v-else>
                        <el-popover trigger="hover" placement="top">
                            <p v-for="(item,key) in scope.row.firms" :key="key">姓名: {{ item.name }}</p>
                            <el-tag size="medium" slot="reference">{{scope.row.firms.length}}个供货商</el-tag>
                        </el-popover>
                    </span>
                </template>
            </el-table-column>
            <el-table-column
            prop="remarks"
            width="200"
            label="结算备注">
            </el-table-column>
            <el-table-column
            prop=""
            width="200"
            label="结算人">
                <template slot-scope="scope">
                    {{scope.row.agent_name}} {{scope.row.agent_phone}}
                </template>
            </el-table-column>
            <el-table-column
            prop="settlement_account_num"
            width="170"
            label="结款账号">
            </el-table-column>
            <el-table-column
            prop=""
            width="100"
            label="">
                <template slot-scope="scope">
                    <el-button @click="seeDetail(scope.row)" type="text" >查看详情</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <div class="scavenging" @click="scavenging">扫码结款</div>
        <settlement-flow-summary ref="settlementFlowSummary"></settlement-flow-summary>
    </div>
</template>

<script>
import { formatDate } from '@/utils'
import settlementFlowSummary from './settlement_flow_summary.vue'
import _ from 'lodash'
import scavengingKnot from './scavenging_knot.vue'
export default {
    data() {
        return {
            tableData: [],
            allFirmsData: [],
            radio3: '结算流水',
            searchObj: {
                firm_ids: []
            },
            form: {
                from_date: formatDate(new Date(new Date().getTime() - 30 * 24 * 3600 * 1000), 'yyyy-MM-dd'), // 起始日
                to_date: formatDate(new Date(), 'yyyy-MM-dd') // 截止日
            },
            show_1: true,
            summary_date: '' // 按日yyyy-MM-dd按月yyyy-MM-1按年yyyy-1-1
        }
    },
    props: {
        activeName: {
            type: String,
            default: ''
        }
    },
    watch: {
        activeName(val) {
            if (val === 'third') {
                this.queryData()
            }
        },
        form: {
            handler() {
                this.queryData()
            },
            deep: true
        },
        radio3: {
            handler(val) {
                this.$nextTick(() => {
                    if (val === '结算流水') {
                        this.show_1 = true
                        this.queryData()
                        this.$refs.settlementFlowSummary.close()
                    } else {
                        switch (this.radio3) {
                            case '按日':
                                this.summary_date = formatDate(new Date(), 'yyyy-MM-dd')
                                break
                            case '按月':
                                this.summary_date = formatDate(new Date(), 'yyyy-MM') + '-1'
                                break
                            case '按年':
                                this.summary_date = formatDate(new Date(), 'yyyy') + '-1-1'
                                break
                        }
                        this.show_1 = false
                        this.$refs.settlementFlowSummary.open({
                            scope: this.scope,
                            summary_date: this.summary_date
                        })
                    }
                })
            },
            immediate: true
        }
    },

    computed: {
        date_type() { // 日期插件的属性
            switch (this.radio3) {
                case '按日':
                    return 'date'
                case '按月':
                    return 'month'
                case '按年':
                    return 'year'
            }
        },
        value_format() { // 日期插件返回的日期的格式
            switch (this.radio3) {
                case '按日':
                    return 'yyyy-MM-dd'
                case '按月':
                    return 'yyyy-MM-d'
                case '按年':
                    return 'yyyy-M-d'
            }
        },
        scope() {
            switch (this.radio3) {
                case '按日':
                    return 0
                case '按月':
                    return 1
                case '按年':
                    return 2
            }
        }
    },

    created() {
        this.queryData()
    },

    methods: {
        scavenging() {
            this.$router.push({
                path: '/main/reconcileCenter/scavengingKnot'
            })
        },
        dateChange(date) {
            this.$refs.settlementFlowSummary.open({
                scope: this.scope,
                summary_date: date
            })
        },
        seeDetail(item) { // 查看详情按钮
            this.$router.push({
                path: '/main/reconcileCenter/supplierJiekuanDetail',
                query: {
                    id: item.id
                }
            })
        },
        getTableList(page) { // 滚动分页
            return this.queryData(page)
        },
        queryData(page = 0) { // 查询结算流水
            if (new Date(this.form.from_date) - new Date(this.form.to_date) > 0) {
                return this.openMessage(0, '截止日期不能比起始日期早')
            }
            return this.$fetch.get({
                url: '/firmsettlementorders',
                params: {
                    page,
                    ...this.form,
                    ..._.mapValues(this.searchObj, obj => obj.join('|') || undefined)
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.orders
                    this.allFirmsData = data.all_firms
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.orders)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    },
    components: {
        settlementFlowSummary,
        scavengingKnot
    }
}
</script>

<style lang='scss' scoped>
    .suppliers_settle_accounts{
        position: relative;
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
        .scavenging{
            position: absolute;
            top: 1px;
            right: 1px;
            width: 90px;
            height: 40px;
            line-height: 40px;
            border-radius: 4px;
            text-align: center;
            border:1px solid #009688;
            color: #009688;
            font-size: 14px;
            cursor: pointer;
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
</style>
