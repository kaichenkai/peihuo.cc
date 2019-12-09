<template>
    <div class="wait_to_settlement" @click="close" v-show="show_1">
        <div class="content" @click.stop>
            <div class="top">
                待结算列表
                <i class="el-icon-close" @click="close"></i>
            </div>
            <div class="search">
                <el-input v-model="params.keyword" placeholder="输入商品名/供货商搜索"></el-input>
            </div>
            <el-table
                :data="tableData"
                :height="tableHeight"
                v-scrollLoad="scrollLoad"
                v-loading="tableLoading"
                style="width: 100%"
                @sort-change='sort'
                >
                <el-table-column
                prop="date"
                label="待结算日期"
                sortable='custom'
                width="120">
                </el-table-column>
                <el-table-column
                prop="goods_name"
                label="商品名"
                sortable='custom'
                width="">
                </el-table-column>
                <el-table-column
                prop="total_money"
                width="100"
                label="应结金额">
                </el-table-column>
                <el-table-column
                prop="firm_name"
                label="供货商"
                sortable='custom'
                width="100">
                </el-table-column>
                <el-table-column
                prop="remarks"
                label="备注"
                width="100">
                </el-table-column>
                <el-table-column
                    label=""
                    width="100">
                    <template slot-scope="scope">
                        <el-button @click="addSettlement(scope.row)" type="text" >加入结算</el-button>
                    </template>
                </el-table-column>
                <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
            </el-table>
        </div>
    </div>
</template>
<script>
import { differenceSet } from '@/utils'
var _ = require('lodash')
export default {
    data() {
        return {
            show_1: false,
            tableData: [],
            params: {
                status: 0, // 0待结算1已结算
                order_by: '',
                desc: false,
                keyword: ''
            }
        }
    },

    props: {
        data_list: {
            default() {
                return []
            },
            type: Array
        }
    },

    watch: {
        params: {
            handler() {
                this.debouncedGetAnswer()
            },
            deep: true
        }
    },

    created() {
        this.debouncedGetAnswer = _.debounce(this.queryData, 300) // 请求数据的时间间隔最少为300毫秒
    },
    
    methods: {
        sort(obj) { // 排序
            this.params.order_by = obj.prop
            this.params.desc = !(obj.order === 'ascending')
        },
        open() {
            this.queryData()
            this.show_1 = true
        },
        addSettlement(item) { // 加入结算按钮
            this.tableData.splice(this.tableData.indexOf(item), 1) // 加入结算的项目要从待结算列表中移除
            this.$emit('addSettlement', item)
        },
        close() {
            this.show_1 = false
        },
        getTableList(page) { // 滚动分页
            return this.queryData(this.params.keyword, page)
        },
        queryData(str = '', page = 0) { // 查询待结算列表
            let that = this
            return that.$fetch.get({
                url: '/firmsettlementvouchers',
                params: {
                    ...that.params,
                    page
                }
            }).then(data => {
                let _dataList = differenceSet(data.order_list, that.data_list, 'order_no') // 过滤掉已加入结算的项目
                if (page === 0) {
                    that.tableData = _dataList
                    that.initScrollTable(data.has_more)
                } else {
                    that.tableData = that.tableData.concat(_dataList)
                }
                if (that.tableData.length < 20 && data.has_more) { // 如果列表中的数据少于20条且还有未返回的数据,则继续请求数据
                    // that.queryData(str, ++page)
                    that.scrollLoad()
                } else {
                    return data
                }
            }).catch(e => {
                that.openMessage(0, e)
            })
        }
    }
}
</script>
<style lang="scss" scoped>
    .wait_to_settlement{
        position: fixed;
        top: 0;
        left: 0;
        z-index: 2;
        width: 100%;
        height: 100%;
        background: transparent;
        .content{
            width: 625px;
            height: 100%;
            background: #FFFFFF;
            box-shadow: 10px 0 10px 0 rgba(0,0,0,0.05);
            .top{
                width: 100%;
                height: 56px;
                line-height: 56px;
                padding-left: 10px;
                font-size: 20px;
                color: #333333;
                background: #F9F9F9;
                i{
                    float: right;
                    margin-right: 15px;
                    margin-top: 17px;
                    cursor: pointer;
                }
            }
            .search{
                padding: 15px;
            }
        }
    }
    /deep/ .el-input__inner{
        border-radius: 20px;
    }
    /deep/ .el-button--text{
        font-size: 12px!important;
        padding:4px!important;
        border: 1px solid #009688;
        color: #009688!important;
        border-radius: 0!important;
    }
    /deep/ .el-button--text:hover{
        border: 1px solid #009688;
    }
</style>
