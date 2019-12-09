<template>
    <transition name="slide-fade">
        <div class="caigou_detail" @click="close" v-if="show_1">
            <div class="content" @click.stop>
                <div class="top">
                    <i class="el-icon-back" @click="close"></i>
                    配货历史
                    <i class="el-icon-close" @click="close"></i>
                </div>
                <div class="middle">
                    <p>商品名：{{item.goodsData.goods_name}}</p>
                    <p>采购员：{{item.goodsData.purchaser_name}}</p>
                </div>
                <el-table
                    :data="tableData"
                    :height="height"
                    style="width: 100%"
                >
                    <el-table-column
                        prop="create_time"
                        label="时间"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="order_no"
                        label="单号"
                        width="">
                        <template slot-scope="scope">
                            <span @click="openConfirmDistributionStaff(scope.row)" style="cursor: pointer;color: rgba(107, 164, 239, 0.95);">{{scope.row.order_no}}</span>
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="source"
                        label="到货来源"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="allocated_amount"
                        label="配货量"
                        width="80">
                    </el-table-column>
                    <el-table-column
                        label="货品状态"
                        width="120">
                        <template slot-scope="scope">
                            {{scope.row.status?'已打印待结算单':'已打印分车单'}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="操作"
                        width="80">
                        <template slot-scope="scope">
                            <el-button @click="printAgain(scope.row)" type="text">重新打印</el-button>
                        </template>
                    </el-table-column>
                    <el-table-column type="expand"
                        width="50">
                        <template slot-scope="scope">
                            <div class="expand_tr">
                                <p class="bold">
                                    <span>店铺</span>
                                    <span>库存量</span>
                                    <span>订货量</span>
                                    <span>配货量</span>
                                </p>
                                <p class="bold">
                                    <span>累计</span>
                                    <span>{{scope.row.storage}}</span>
                                    <span>{{scope.row.demand_amount}}</span>
                                    <span>{{scope.row.allocated_amount}}</span>
                                </p>
                                <p v-for="(item,index) in scope.row.order_goods_list" :key="index">
                                    <span>{{item.shop_name}}</span>
                                    <span>{{item.storage}}</span>
                                    <span>{{item.demand_amount}}</span>
                                    <span>{{item.allocated_amount}}</span>
                                </p>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
            <confirm-distribution-staff ref="confirmDistributionStaff"></confirm-distribution-staff>
        </div>
    </transition>
</template>
<script>
import ConfirmDistributionStaff from './confirm_distribution_staff/confirm_distribution_staff'
export default {
    data() {
        return {
            show_1: false,
            tableData: [],
            item: {},
            height: window.innerHeight - 150
        }
    },
    methods: {
        printAgain(item) {
            this.$fetch.post({
                url: '/print/allocationorderreprint',
                params: {
                    allocation_order_id: item.order_id
                }
            }).then(() => {
                this.openMessage(1, '再次打印成功')
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        open(obj) {
            this.show_1 = true
            this.item = obj
            this.queryData()
        },

        close() {
            this.show_1 = false
        },

        queryData(page = 0) {
            this.$fetch.get({
                url: `/allocationrecords`,
                params: {
                    wish_order_id: this.item.wishOrderId,
                    goods_id: this.item.goodsData.goods_id
                }
            }).then(data => {
                this.tableData = data.data_list
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        openConfirmDistributionStaff(row) {
            // .open()
            this.searchDistributionStaffOrder(row.order_no)
        },

        searchDistributionStaffOrder(orderNumber) {
            this.$fetch.get({
                url: '/ordersearch/' + orderNumber
            }).then(data => {
                switch (data.data.order_type) {
                    case 5: this.allocationType5order(data.data); break
                    case 6: this.allocationType6order(data.data); break
                    default: this.openMessage(2, '不是一个有效的分车单或者出库单')
                }
            }).catch(e => {
                console.log(e)
                this.openMessage(0, e)
            })
        },

        allocationType5order(data) {
            // confirmDistributionCar
            // confirmDistributionStaff
            this.$refs.confirmDistributionStaff.open({
                data: data,
                isDistributionCar: data.allocation_status !== 0,
                callback: () => {
                    // this.search = ''
                }
            })
        },

        allocationType6order(data) {
            this.$myWarning({
                message: '是否已分车？'
            }).then(() => {
                this.$fetch.put({
                    url: '/allocationorder/' + data.allocation_order_id,
                    params: {
                        action: 'confirm'
                    }
                }).then(() => {
                    // this.getOrderGoodsVouchers()
                    this.openMessage(1, '分车成功')
                    // this.search = ''
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(e => {})
        }
    },

    components: {
        ConfirmDistributionStaff
    }
}
</script>
<style lang="scss" scoped>
    .caigou_detail{
        position: fixed;
        top: 0;
        right: 0;
        z-index: 2;
        width: 100%;
        height: 100%;
        background: transparent;
        .content{
            position: absolute;
            top: 0;
            right: 0;
            width: 640px;
            height: 100%;
            background: #FFFFFF;
            box-shadow: -10px 0 10px 0 rgba(0,0,0,0.05);
            .top{
                width: 100%;
                height: 56px;
                line-height: 56px;
                padding-left: 10px;
                font-size: 20px;
                color: #333333;
                background: #F9F9F9;
                .el-icon-close{
                    float: right;
                    margin-right: 15px;
                    margin-top: 19px;
                    cursor: pointer;
                }
            }
            .middle{
                padding-top: 10px;
                padding-left: 10px;
                p{
                    line-height: 30px;
                }
            }
            .search{
                padding: 15px;
            }
        }
    }
    /deep/ .el-date-editor.el-input{
        margin-top: 8px;
        width: 150px;
        .el-input__inner{
            margin-top: 6px;
            height: 30px;
            line-height: 30px;
            border-radius: 15px;
            font-size: 16px;
            color: #333333;
        }
    }
    /deep/ .expand_tr{
        background-color: #f8f8f8;
        p.bold{
            span{
                font-weight: bold;
            }
        }
        span{
            display: inline-block;
            height: 40px;
            line-height: 40px;
            padding-left: 11px;
            vertical-align: top;
            &:nth-of-type(1){
                width: 190px;
            }
            &:nth-of-type(2){
                width: 190px;
            }
            &:nth-of-type(3){
                width: 190px;
            }
        }
    }
    .slide-fade-enter-active,.slide-fade-leave-active {
        transition: all .5s ease;
    }
    .slide-fade-enter, .slide-fade-leave-to
    /* .slide-fade-leave-active for below version 2.1.8 */ {
        transform: translateX(680px);
        opacity: 0;
    }
    /deep/ .el-table__expanded-cell[class*=cell]{
        padding: 0;
    }
    /deep/ .el-icon-arrow-right:before{
        content: '\E60E'
    }
    /deep/ .el-table__expand-icon > .el-icon{
        left: 29%;
        top: 24%;
        font-size: 22px;
    }
    /deep/ .no_expand .el-table__expand-icon{
        display: none;
    }
    /deep/ .el-table__row:nth-of-type(1) td{
        // color: #333;
        // font-weight: bold;
    }
    /deep/ .el-table:before{
        height: 0;
    }
    /deep/ .el-input__prefix{
        top: 2px;
    }
    /deep/ .el-input__suffix{
        top: 2px;
    }
    /deep/ .el-icon-back{
        font-weight: bold;
        position: relative;
        font-size: 23px;
        top: 2px;
        border-right: 1px solid #ccc;
        margin-right: 10px;
        padding-right: 10px;
        cursor: pointer;
    }
</style>
