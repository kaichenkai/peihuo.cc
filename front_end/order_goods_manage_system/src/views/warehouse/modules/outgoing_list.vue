<template>
    <div>
        <div class="date_addgoods">
            <el-date-picker
                v-model="form.record_date"
                type="date"
                size="small"
                :clearable="true"
                :editable="true"
                value-format="yyyy-MM-dd"
                placeholder="选择日期">
            </el-date-picker>
            <span @click="addOutStockGood">+增加出库货品</span>
        </div>
        <el-table
            :data="tableData"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
                type="index"
                label="序号"
                width="100">
            </el-table-column>
            <el-table-column
                prop="wish_date"
                label="意向单日期"
                sortable
                width="200">
            </el-table-column>
            <el-table-column
                min-width="200">
                <template slot="header" slot-scope="scope">
                    <table-data-filter title="商品名" allString="所有商品" :items="allGoodsData" itemKeyName="name" itemKeyCode="id"  v-model="searchObj.goods_ids" @confirm="getList"></table-data-filter>
                </template>
                <template slot-scope="scope">
                    <span class="name">{{ scope.row.goods_name }}</span>
                </template>
            </el-table-column>
            <!-- <el-table-column
                label="类别"
                width="150">
                <template slot-scope="scope">
                    <span>出库</span>
                </template>
            </el-table-column> -->
            <el-table-column
                prop="amount"
                label="数量"
                sortable
                width="150">
            </el-table-column>
            <el-table-column
                prop="operator_name"
                label="操作人"
                sortable
                width="200">
            </el-table-column>
            <el-table-column
                label=""
                width="180">
                <template slot-scope="scope">
                    <el-button @click="sureStockOut(scope.row)" type="text" >确认出库</el-button>
                    <el-button @click="deleteStockOut(scope.row)" type="text" >删除</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <stoke-out-bill ref="stokeOutBill"></stoke-out-bill>
        <choose-goods ref="chooseGoods" @addStockOut='addStockOut'></choose-goods>
    </div>
</template>
<script>
import { formatDate } from '@/utils'
import stokeOutBill from './stock_out_bill.vue'
import _ from 'lodash'
import chooseGoods from './choose_goods.vue'
export default {
    data() {
        return {
            tableHeight: window.innerHeight - 300,
            tableData: [],
            allGoodsData: [],
            form: {
                record_date: formatDate(new Date(), 'yyyy-MM-dd')
            },
            searchObj: {
                goods_ids: []
            }
        }
    },

    props: {
        activeName: String
    },

    watch: {
        'form.record_date'() {
            this.getList()
        },
        activeName(value) {
            if (value === 'first') {
                this.getList()
            }
        }
    },

    created() {
        this.getList().then(data => {
            this.allGoodsData = data.goods_data
        })
    },

    methods: {
        deleteStockOut(item) {
            this.$myWarning({
                message: '是否确认删除'
            }).then(() => {
                this.$fetch.delete({
                    url: `/warehouse/stockout/${item.id}`,
                    params: {}
                }).then(data => {
                    this.openMessage(1, '删除成功')
                    this.getList()
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(() => {})
        },
        addStockOut() {
            this.getList()
        },
        addOutStockGood() {
            this.$refs.chooseGoods.open()
        },
        getTableList(page) {
            return this.getList(page)
        },

        getList(page = 0) {
            return this.$fetch.get({
                url: '/warehouse/stockout/list',
                params: {
                    ...this.form,
                    page,
                    ..._.mapValues(this.searchObj, obj => obj.join('|') || undefined)
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.record_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.record_list)
                }
                return data
            }).catch(e => {
                this.opemMessage(0, e || '获取出库清单失败')
            })
        },

        sureStockOut(data) {
            this.$refs.stokeOutBill.open({
                data: data,
                callback: () => this.getList()
            })
        }
    },

    components: {
        stokeOutBill,
        chooseGoods
    }
}
</script>
<style lang="scss" scoped>
    .date_addgoods{
        overflow: hidden;
        span{
            position: relative;
            top: 16px;
            float: right;
            font-size: 14px;
            color: #009688;
            cursor: pointer;
        }
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
    /deep/ .el-table{
        margin-top: 8px;
    }
</style>
