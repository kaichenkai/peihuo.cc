<template>
    <div class="bill_detail" v-if="show_1">
        <div class="tool-container"><img src="~@/assets/images/a1.png" alt="" @click="cancel"><span @click="cancel">对账中心/分店对账</span><span>/</span><span class="now">账单详情</span></div>
        <div class="top">
            <span>日期：<span>{{item.date}}</span></span>
            <span>店铺：<span>{{item.shop_name}}</span></span>
            <span>账单金额：<span>{{item.payout_sum}}元</span></span>
            <span @click="addExpenditure" v-show="item.scope===0">添加支出</span>
        </div>
        <div class="tab">
            <span :class="{active:active===1}" @click="active=1">货品实配</span>
            <span :class="{active:active===2}" @click="active=2">其它支出</span>
        </div>
        <el-table
            :key="1"
            v-if="active===1"
            :data="tableData"
            :height="tableHeight-50"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%"
            @sort-change='sort'
            >
            <el-table-column
                prop="goods_name"
                label="货品名"
                width="300">
            </el-table-column>
            <el-table-column
                prop="allocated_amount"
                label="实配量"
                sortable='custom'
                width="150">
            </el-table-column>
            <el-table-column
                prop="packing_price"
                width="150"
                sortable='custom'
                label="单价">
            </el-table-column>
            <el-table-column
                prop="packing_money"
                label="金额小计"
                sortable='custom'
                width="150">
            </el-table-column>
            <el-table-column
                prop="goods_volume"
                label="体积"
                sortable='custom'
                width="150">
            </el-table-column>
            <el-table-column
                prop="goods_weight"
                label="重量"
                sortable='custom'
                width="">
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <el-table
            v-else
            :key="2"
            :data="tableData"
            :height="tableHeight-50"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%"
            @sort-change='sort'
            >
            <el-table-column
                prop="creator"
                label="添加人"
                width="200">
            </el-table-column>
            <el-table-column
                prop="create_time"
                label="添加时间"
                width="200">
            </el-table-column>
            <el-table-column
                prop="type"
                width="250"
                label="类型">
            </el-table-column>
            <el-table-column
                prop="money"
                label="金额"
                sortable='custom'
                width="150">
            </el-table-column>
            <el-table-column
                prop="remarks"
                label="备注"
                width="250">
            </el-table-column>
            <el-table-column
                label="操作"
                width="">
                <template slot-scope="scope">
                    <el-button type="text" @click="updateGoods(scope.row)">修改</el-button>
                    <el-button type="text" @click="deleteGoods(scope.row,$event)" style="color: #FF6666;">删除</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <add-expenditure ref="addExpenditure" @finishAdd='finishAdd'></add-expenditure>
    </div>
</template>
<script>
import { formatDate } from '@/utils'
import addExpenditure from './add_expenditure.vue'
export default {
    data() {
        return {
            show_1: true,
            active: 1,
            tableData: [],
            item: {},
            form: {
                order_by: '',
                asc: ''
            },
            params_date: {
                from_date: '',
                to_date: '',
                before_date: ''
            }
        }
    },

    watch: {
        form: {
            handler() {
                if (this.active === 1) {
                    this.getAllocationgoodslist()
                } else {
                    this.getShoppayoutlist()
                }
            },
            deep: true
        },
        active(val) {
            if (val === 1) {
                this.getAllocationgoodslist()
            } else {
                this.getShoppayoutlist()
            }
        }
    },

    created() {
        this.item = JSON.parse(this.$route.query.item)
        this.initParamsDate(this.item.scope)
        this.getAllocationgoodslist()
    },

    methods: {
        initParamsDate(scope) {
            let date = this.item.date
            let fromDate = ''
            let toDate = ''
            let beforeDate = ''
            if (scope === 0) {
                fromDate = date
                toDate = date
                beforeDate = ''
            } else if (scope === 1) {
                toDate = ''
                fromDate = date + '-01'
                beforeDate = formatDate(new Date(parseInt(date.substr(0, 4)), parseInt(date.substr(5, 2)), 1), 'yyyy-MM-dd')
            } else {
                toDate = ''
                fromDate = date + '-01-01'
                beforeDate = formatDate(new Date(parseInt(date.substr(0, 4)) + 1, 0, 1), 'yyyy-MM-dd')
            }
            this.params_date = {
                from_date: fromDate,
                to_date: toDate,
                before_date: beforeDate
            }
        },
        sort(obj) { // 排序
            this.form.order_by = obj.prop
            this.form.asc = obj.order === 'ascending'
        },
        finishAdd() {
            this.getShoppayoutlist()
        },
        getAllocationgoodslist(page = 0) { // 货品实配
            return this.$fetch.get({
                url: '/allocationgoodslist',
                params: {
                    shop_id: this.item.shop_id,
                    ...this.params_date,
                    order_status: 1,
                    page,
                    ...this.form
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.data_list
                    if (data.data_list.length > 0) {
                        this.tableData.unshift({
                            goods_name: '累计',
                            allocated_amount: data.sum_data.allocated_amount,
                            packing_money: data.sum_data.packing_money,
                            goods_volume: data.sum_data.goods_volume,
                            goods_weight: data.sum_data.goods_weight
                        })
                    }
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.data_list)
                    if (data.data_list.length > 0) {
                        this.tableData.unshift({
                            goods_name: '累计',
                            allocated_amount: data.sum_data.allocated_amount,
                            packing_money: data.sum_data.packing_money,
                            goods_volume: data.sum_data.goods_volume,
                            goods_weight: data.sum_data.goods_weight
                        })
                    }
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        getShoppayoutlist(page = 0) { // 其它支出
            return this.$fetch.get({
                url: '/shoppayoutlist',
                params: {
                    ...this.params_date,
                    shop_id: this.item.shop_id,
                    page,
                    ...this.form
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.data_list
                    if (data.data_list.length > 0 && this.tableData[0].creator !== '累计') {
                        this.tableData.unshift({
                            creator: '累计',
                            money: data.sum_data.money
                        })
                    }
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.data_list)
                    if (data.data_list.length > 0 && this.tableData[0].creator !== '累计') {
                        this.tableData.unshift({
                            creator: '累计',
                            money: data.sum_data.money
                        })
                    }
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        addExpenditure() {
            this.$refs.addExpenditure.open(this.item)
        },
        updateGoods(item) {
            this.$refs.addExpenditure.open(this.item, item)
        },
        deleteGoods(item) {
            this.$myWarning({
                message: `确认删除吗？`
            }).then(() => {
                this.$fetch.delete({
                    url: `/shoppayout/${this.item.shop_id}`
                }).then(() => {
                    this.openMessage(1, '删除成功')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(e => {

            })
        },
        cancel() {
            this.$router.go(-1)
        }
    },

    components: {
        addExpenditure
    }
}
</script>
<style lang="scss" scoped>
    .bill_detail{
        background-color: #fff;
        .tool-container {
            font-family: PingFangSC-Regular;
            font-size: 16px;
            color: #999999;
            letter-spacing: 0;
            line-height: 30px;
            user-select: none;
            background-color: #fff;
            img {
                margin-right: 5px;
                cursor: pointer;
            }

            span {
                padding: 2px;
                &:nth-of-type(1){
                    cursor: pointer;
                }
            }

            > * {
                display: inline-block;
                vertical-align: middle;
            }

            .now {
                color: #151515;
            }
        }
        .top{
            height: 50px;
            padding: 16px 10px;
            background: #f5f8f7;
            >span{
                display: inline-block;
                width: 140px;
                font-size: 14px;
                color: #999;
                span{
                    font-size: 14px;
                    color: #333;
                }
                &:nth-last-of-type(1){
                    float:right;
                    color:rgba(107, 164, 239, 0.95);
                    text-align:right;
                    margin-top: 2px;
                    cursor:pointer;
                }
                & + span{
                    margin-left: 25px;
                }
            }
        }
        .tab{
            padding: 10px;
            span{
                display: inline-block;
                width: 100px;
                height: 26px;
                margin-right: 14px;
                line-height: 24px;
                border: 1px solid #999999;
                border-radius: 13px;
                font-size: 14px;
                color: #333333;
                text-align: center;
                &.active{
                    background: rgba(0, 150, 136, 0.1);
                    border: 1px solid transparent;
                    color: #009688;
                }
            }
        }
    }
    /deep/ .el-table{
        margin-top: 0;
    }
    /deep/ .el-table__row:nth-of-type(1) td {
        color: #333;
        font-weight: bold;
    }
    /deep/ .el-table__row:nth-of-type(1) td:nth-last-of-type(1) .cell{
        display: none;
    }
</style>
