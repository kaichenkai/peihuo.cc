<template>
    <transition name="slide-fade-100">
        <div class="order-detail-1" v-if="isShow" :style="{'left': left + 'px'}">
            <div class="tabal-top">
                <div>
                    <h3>店铺订单详情</h3>
                    <button type="text" @click="print">打印店铺配货单</button>
                    <button type="text" style="margin-left: 15px" @click="exportVercher">导出店铺配货单</button>
                    <button type="text" style="margin-left: 15px" v-if="canIUse('admin', 9)" @click="openAllocationPriceSetting()">配货价设置</button>
                </div>
                <span type="icon" class="el-icon el-icon-close" @click="close"></span>
            </div>
            <div class="create-info">
                <span class="create-time">提交时间：{{activedOrderData.create_time}}</span>
                <span>提交人：<img :src="activedOrderData.creator_avatar" alt="">{{activedOrderData.creator_name}}</span>
            </div>
            <el-table
                :data="tableData"
                stripe
                v-loading="loading"
                :height="tableHeight"
                style="width: 100%">
                <el-table-column
                prop="goods_name"
                label="商品名"
                width="170">
                </el-table-column>
                <el-table-column
                prop="current_storage"
                width="70"
                align="right"
                label="分店库存">
                </el-table-column>
                <el-table-column
                prop="demand_amount"
                width="60"
                align="right"
                label="订货量">
                </el-table-column>
                <el-table-column
                prop="packed_amount"
                width="60"
                align="right"
                label="实配量">
                </el-table-column>
                <el-table-column
                prop="packed_weight"
                width="70"
                align="right"
                v-if="tableHeader.orderGroupStoreDetailTable.includes(2)"
                label="实配/kg">
                </el-table-column>
                <el-table-column
                prop="packed_volume"
                width="70"
                align="right"
                v-if="tableHeader.orderGroupStoreDetailTable.includes(1)"
                label="实配/m³">
                </el-table-column>
                <!-- <el-table-column
                prop="remarks"
                width="180"
                label="备注">
                </el-table-column> -->
                <el-table-column
                prop="purchase_price"
                width="60"
                align="right"
                label="采购价">
                <template slot-scope="scope">
                    <span v-if="canIUse('admin', 9)">{{scope.row.purchase_price}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
                </el-table-column>
                <el-table-column
                prop="allocation_price"
                width="60"
                align="right"
                label="配货价">
                <template slot-scope="scope">
                    <!-- <input type="text" name="" id=""> -->
                    <span v-if="canIUse('admin', 9)">{{scope.row.allocation_price}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
                </el-table-column>
                <el-table-column
                prop="allocation_subtotal"
                align="center"
                width="90"
                label="配货小计">
                <template slot-scope="scope">
                    <span v-if="canIUse('admin', 9)">{{scope.row.allocation_subtotal}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
                </el-table-column>
            </el-table>
            <printer ref="printer" title="打印店铺配货单">
            <h2 style="font-size: 20px;color: #333333;margin-bottom: 10px">店铺配货单({{store.shop_name}})</h2>
            <el-table
                :data="tableData"
                stripe
                height="320"
                v-loading="loading"
                style="width: 100%">
                <el-table-column
                prop="goods_name"
                label="商品名"
                width="140">
                </el-table-column>
                <el-table-column
                prop="demand_amount"
                width="100"
                label="订货量">
                </el-table-column>
                <el-table-column
                prop="packed_amount"
                label="实配量">
                </el-table-column>
            </el-table>
        </printer>
        <allocation-price-setting :wishOrderId="wishOrderId" ref="allocationPriceSetting"></allocation-price-setting>
        </div>
    </transition>
</template>

<script>
import AllocationPriceSetting from './allocation_price_setting'
import Printer from '@/components/printer/printer'
import ApiUrl from '@/api/ip_config/main'
import { mapGetters, mapState } from 'vuex'
export default {
    data() {
        return {
            isShow: false,
            tableHeight: window.innerHeight - 66,
            loading: false,
            activedOrderData: {},
            store: {},
            tableData: [],
            left: 325
        }
    },

    props: {
        wishOrderId: Number
    },

    computed: {
        ...mapState(['tableHeader']),
        ...mapGetters(['canIUse'])
    },

    watch: {
        'tableHeader.orderGroupStoresTable': function() {
            this.getLeftStoresContainerWidthAndSetPosLeft()
        }
    },

    created() {
        // this.wishOrderId = this.$route.query.wishOrderId
    },

    methods: {
        open(obj) {
            this.store = JSON.parse(JSON.stringify(obj.store))
            this.callback = obj.callback || function() {}
            this.getLeftStoresContainerWidthAndSetPosLeft()
            this.isShow = true
            this.getOrderDetail()
            this.$refs.allocationPriceSetting && this.$refs.allocationPriceSetting.close()
        },

        // 获取左侧容器的宽度，用于右侧容器的定位
        getLeftStoresContainerWidthAndSetPosLeft() {
            setTimeout(() => {
                this.left = this.$parent.$el.getElementsByClassName('stores-list')[0].getBoundingClientRect().width
            }, 50)
        },

        close() {
            this.isShow = false
            this.callback && this.callback()
        },

        getOrderDetail() {
            this.loading = true
            this.$fetch.get({
                url: '/station/demandorder/' + this.store.demand_order_id
            }).then(data => {
                this.activedOrderData = data.order_data
                data.order_data.goods_data.unshift({
                    isTotalColumn: true,
                    goods_name: '累计',
                    current_storage: '-',
                    purchase_price: this.computeTotal(data.order_data.goods_data, 'purchase_price'),
                    allocation_price: this.computeTotal(data.order_data.goods_data, 'allocation_price'),
                    packed_volume: this.computeTotal(data.order_data.goods_data, 'packed_volume'),
                    packed_weight: this.computeTotal(data.order_data.goods_data, 'packed_weight'),
                    demand_amount: this.computeTotal(data.order_data.goods_data, 'demand_amount'),
                    packed_amount: this.computeTotal(data.order_data.goods_data, 'packed_amount'),
                    allocation_subtotal: this.computeTotal(data.order_data.goods_data, 'allocation_subtotal')
                })
                this.tableData = data.order_data.goods_data
            }).catch(e => {
                this.openMessage(0, '获取订货单数据失败,' + e)
            }).finally(() => {
                this.loading = false
            })
        },

        computeTotal(data, key) {
            return +data.reduce((last, next) => {
                last += next[key]
                return last
            }, 0).toFixed(2)
        },

        print() {
            this.$refs.printer.open({
                callback: (printID) => {
                    this.$fetch.post({
                        url: '/print/shoppacking',
                        params: {
                            wish_order_id: this.wishOrderId,
                            printer_id: printID,
                            shop_id: this.store.shop_id
                        }
                    }).then(data => {
                        this.openMessage(1, '打印成功')
                    }).catch(e => {
                        this.openMessage(0, '打印失败')
                    })
                }
            })
        },

        exportVercher() {
            window.open(ApiUrl + '/export/shoppackingorder/' + this.store.demand_order_id)
        },

        openAllocationPriceSetting() {
            this.$refs.allocationPriceSetting.open({
                store: this.store,
                callback: () => {
                    this.getOrderDetail()
                }
            })
        }
    },

    components: {
        Printer,
        AllocationPriceSetting
    }
}
</script>

<style lang="scss" scoped>
.order-detail-1 {
    position: absolute;
    left: 400px;
    top: 0;
    bottom: 0;
    // width: 600px;
    // display: inline-block;
    // height: 100%;
    overflow: auto;
    // width: 680px;
    // max-width: 680px;
    background: #fff;
    box-shadow: 9px 3px 20px -10px rgba(0, 0, 0, 0.4);
    z-index: 1;
    transition: left .3s ease;
}

    .tabal-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 36px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        // line-height: 60px;

        > * {
            // display: inline-block;
            // vertical-align: middle;
        }

        // /deep/ .el-button--text {
        //     position: relative;
        //     z-index: 10;
        // }

        button {
            width: 100px;
            height: 23px;
            border: 1px solid #009688;
            border-radius: 2px;
            font-size: 12px;
            color: #009688;
            line-height: 20px;
            white-space: nowrap;
        }

        h3 {
            display: inline-block;
            position: relative;
            // left: -50px;
            padding: 0 15px 0 13px;
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
        }

        .el-icon {
            margin-right: 10px;
            font-size: 24px;
            color: #999999;
        }
    }

    .create-info {
        padding: 0 15px 0 13px;
        /* margin: -1px; */
        height: 30px;
        line-height: 30px;
        font-size: 14px;
        color: #333333;

        .create-time {
            margin-right: 10px;
        }

        img {
            margin-right: 10px;
            vertical-align: middle;
            width: 20px;
            border-radius: 50%;
        }
    }

    /deep/ .el-table {
        margin-top: 0px;

        .cell {
            padding: 0 !important;
            padding-left: 6px !important;
        }
    }

.slide-fade-100-enter-active {
    transition: all .3s ease;
}
.slide-fade-100-leave-active {
    transition: all .3s ease;
}
.slide-fade-100-enter, .slide-fade-100-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
    // transform: translateX(-100%);
    width: 0;
    opacity: 0;
}
</style>
