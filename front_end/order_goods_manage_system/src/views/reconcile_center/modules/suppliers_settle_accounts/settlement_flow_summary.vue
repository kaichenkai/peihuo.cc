<template>
    <div v-show="show">
        <el-table
            :data="tableData"
            :height="tableHeight-50"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
            type="index"
            label="序号"
            width="100">
            </el-table-column>
            <el-table-column
            prop=""
            min-width="200">
                <template slot="header" slot-scope="scope">
                    <table-data-filter title="供货商" allString="所有供货商" :items="allFirmsData" itemKeyName="name" itemKeyCode="id"  v-model="searchObj.firm_ids" @confirm="confirm"></table-data-filter>
                </template>
                <template slot-scope="scope">
                    {{scope.row.firm_name}}
                </template>
            </el-table-column>
            <el-table-column
            prop="times"
            width="200"
            label="结算次数">
            </el-table-column>
            <el-table-column
            prop="voucher_count"
            label="结算票数"
            width="200">
            </el-table-column>
            <el-table-column
            prop="total_money"
            width="170"
            label="结算金额">
            </el-table-column>
            <el-table-column
            prop=""
            width="100"
            label="">
                <template slot-scope="scope">
                    <el-button @click="seeDetail(scope.row)" type="text" >汇总详情</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <summary-detail ref="summaryDetail"></summary-detail>
    </div>
</template>
<script>
import _ from 'lodash'
import summaryDetail from './summary_detail.vue'
export default {
    data() {
        return {
            show: false,
            tableData: [],
            allFirmsData: [], // 供货商表头多选
            searchObj: {
                firm_ids: []
            },
            form: {
                scope: 0, // 0按日汇总1按月汇总2按年汇总
                summary_date: '' // 按日yyyy-MM-dd按月yyyy-MM-1按年yyyy-1-1
            }
        }
    },

    methods: {
        confirm() {
            this.queryData()
        },
        seeDetail(item) { // 汇总详情按钮
            this.$refs.summaryDetail.open(item, this.form.scope, this.form.summary_date)
        },
        getTableList(page) { // 滚动分页
            return this.queryData(page)
        },
        queryData(page = 0) { //
            return this.$fetch.get({
                url: '/firmsettlementsummary',
                params: {
                    page,
                    ...this.form,
                    ..._.mapValues(this.searchObj, obj => obj.join('|') || undefined),
                    dimension: 'firm' // 汇总传firm,汇总详情传time
                }
            }).then(data => {
                this.allFirmsData = data.sum_data.firms
                if (page === 0) {
                    this.tableData = data.summarys
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.summarys)
                }
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        open(obj) {
            this.show = true
            this.form = obj
            this.queryData()
        },
        close() {
            this.show = false
        }
    },
    
    components: {
        summaryDetail
    }
}
</script>
