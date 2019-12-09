<template>
<transition name="slide-fade">
<div class="order-store-list-bg" @click="showStores = false"  v-if="showStores">
    <div @click.stop class="stores">
        <!-- <div class="store-contianer" id="store-contianer"> -->
            <div class="stores-list">
                <div class="header">
                    <h2>订货门店</h2>
                    <el-button type="primary" :loading="btnLoading" v-if="wishOrderStatus == 2" @click="save" round>完成汇总</el-button>
                    <button class="disabled" v-if="wishOrderStatus > 2">汇总已完成</button>
                    <i class="el-icon el-icon-close" @click="showStores = false"></i>
                </div>
                <el-table
                :data="shopList"
                style="width: 100%;margin-top: 0px;"
                :cell-style="{padding: 0}"
                :header-cell-style="{padding: 0}"
                :span-method="arraySpanMethod"
                @row-click="activeStore"
                :height="leftTableHeight">
                    <el-table-column
                    prop="date"
                    align="center"
                    width="59">
                    <template slot-scope="scope">
                        <span v-if="scope.row.status == -1 || scope.row.isTotalColumn"></span>
                        <el-switch v-else  v-model="scope.row.status" :inactive-value="1" :active-value="2" @change="changeStatus(scope.row)" @click.native.stop class="switch"></el-switch>
                    </template>
                    </el-table-column>
                    <el-table-column
                    prop="shop_abbr"
                    width="60"
                    label="店铺名">
                    <template slot-scope="scope">
                        <span>{{scope.row.shop_abbr}}</span>
                        <span style="margin-left: 10px; color: #f00" v-if="scope.row.negative_order == 1">今日不订货</span>
                        <span style="margin-left: 10px; color: #999" v-else-if="scope.row.status == -1">暂未提交订货单</span>
                    </template>
                    </el-table-column>
                    <el-table-column
                    prop="purchasing_amount"
                    width="45"
                    align="center"
                    label="预采">
                    </el-table-column>
                    <el-table-column
                    prop="allocated_amount"
                    width="45"
                    align="center"
                    label="实配">
                    </el-table-column>
                    <el-table-column
                    prop="purchasing_volume"
                    width="58"
                    v-if="tableHeader.orderGroupStoresTable.includes(1)"
                    align="center"
                    label="预采/m³">
                    </el-table-column>
                    <el-table-column
                    prop="purchasing_weight"
                    width="55"
                    align="center"
                    v-if="tableHeader.orderGroupStoresTable.includes(2)"
                    label="预采/kg">
                    </el-table-column>
                    <el-table-column
                    prop="allocation_volume"
                    width="58"
                    align="center"
                    v-if="tableHeader.orderGroupStoresTable.includes(3)"
                    label="实配/m³">
                    </el-table-column>
                    <el-table-column
                    prop="allocation_weight"
                    width="55"
                    v-if="tableHeader.orderGroupStoresTable.includes(4)"
                    align="center"
                    label="实配/kg">
                    </el-table-column>
                    <el-table-column
                    prop="allocation_subtotal"
                    width="70"
                    align="center"
                    label="实配金额">
                    <template slot-scope="scope">
                        <span v-if="canIUse('admin', 9)">{{scope.row.allocation_subtotal}}</span>
                        <span v-else style="font-size: 12px; color: #999">无权限</span>
                    </template>
                    </el-table-column>
                    <el-table-column
                    prop="date"
                    width="44"
                    label="操作">
                    <template slot-scope="scope">
                        <i v-if="!scope.row.isTotalColumn" class="el-icon el-icon-arrow-right"></i>
                    </template>
                    </el-table-column>
                </el-table>
                <div class="configuration">
                    <p @click="settingTable"><img src="~@/assets/images/a21.png" alt=""><span>设置</span></p>
                    <div class="items-container-bg" @click="isShowTableSetting=false" v-if="isShowTableSetting">
                        <div class="items-container">
                        <!-- 123123 -->
                        <el-popover
                            popper-class="order-store-list-popper"
                            placement="right"
                            title="订货门店汇总表表头设置"
                            width="400"
                            trigger="hover">
                            <div>
                                <el-checkbox-group @change="orderGroupStoresTableChange" v-model="tableHeader.orderGroupStoresTable">
                                    <el-checkbox :label="1">显示预采体积</el-checkbox>
                                    <el-checkbox :label="2">显示预采重量</el-checkbox>
                                    <el-checkbox :label="3">显示实配体积</el-checkbox>
                                    <el-checkbox :label="4">显示实配重量</el-checkbox>
                                </el-checkbox-group>
                            </div>
                            <p class="item" @click.stop slot="reference">订货门店汇总表表头设置</p>
                        </el-popover>
                        <el-popover
                            popper-class="order-store-list-popper"
                            placement="right"
                            title="店铺订单详情表头设置"
                            width="400"
                            trigger="hover">
                            <div>
                                <el-checkbox-group @change="orderGroupStoreDetailTableChange" v-model="tableHeader.orderGroupStoreDetailTable">
                                    <el-checkbox :label="1">显示实配体积</el-checkbox>
                                    <el-checkbox :label="2">显示实配重量</el-checkbox>
                                </el-checkbox-group>
                            </div>
                            <p class="item" @click.stop slot="reference">店铺订单详情表头设置</p>
                        </el-popover>
                        </div>
                    </div>
                </div>
            </div>
        <!-- </div> -->
        <order-store-detail :wishOrderId="wishOrderId" ref="orderStoreDetail"></order-store-detail>
    </div>
</div>
</transition>
</template>

<script>
import Printer from '@/components/printer/printer'
import OrderStoreDetail from './store_order_detail'
import { mapState, mapGetters } from 'vuex'
export default {
    data() {
        return {
            showStores: false,
            shopList: [],
            activedStore: {},
            leftTableHeight: window.innerHeight - 110,
            btnLoading: false,
            isShowTableSetting: false
        }
    },

    props: {
        wishOrderStatus: Number,
        wishOrderData: Array,
        wishOrderId: Number
    },

    computed: {
        ...mapState(['stationConfig', 'tableHeader']),
        ...mapGetters(['canIUse'])
    },

    watch: {
        wishOrderId: function(newVal) {
            // console.log('new', newVal)
            this.getOrderList()
        }
    },

    created() {
        // this.wishOrderId = this.$route.query.wishOrderId
        // this.getOrderList()
    },

    methods: {
        open() {
            this.showStores = true
            this.getOrderList()
        },

        close() {
            this.showStores = false
            this.tableData = []
            this.activedStore = {}
        },

        getOrderList() {
            this.$fetch.get({
                url: '/shopdemandinglist',
                params: {
                    wish_order_id: this.wishOrderId
                }
            }).then(data => {
                // console.log(data)
                data.data_list.unshift({
                    isTotalColumn: true,
                    shop_abbr: '累计',
                    purchasing_amount: this.computeTotal(data.data_list, 'purchasing_amount'),
                    allocated_amount: this.computeTotal(data.data_list, 'allocated_amount'),
                    allocation_subtotal: this.computeTotal(data.data_list, 'allocation_subtotal'),
                    allocation_volume: this.computeTotal(data.data_list, 'allocation_volume'),
                    allocation_weight: this.computeTotal(data.data_list, 'allocation_weight'),
                    purchasing_volume: this.computeTotal(data.data_list, 'purchasing_volume'),
                    purchasing_weight: this.computeTotal(data.data_list, 'purchasing_weight')
                })
                this.shopList = data.data_list
                this.$emit('shopListChange', data.data_list)
            }).catch(e => {
                this.openMessage(0, '获取订货单失败,' + e)
            })
        },

        orderGroupStoresTableChange(newVal) {
            this.$store.commit("SET_TABLE_HEADER", { table: 'orderGroupStoresTable', columnsSetting: newVal })
        },

        orderGroupStoreDetailTableChange(newVal) {
            this.$store.commit("SET_TABLE_HEADER", { table: 'orderGroupStoreDetailTable', columnsSetting: newVal })
        },

        computeTotal(data, key) {
            return +data.reduce((last, next) => {
                // if (next.status !== -1 && next.negative_order !== 1) {
                last += next[key]
                // }
                return last
            }, 0).toFixed(2)
        },

        settingTable() {
            this.isShowTableSetting = true
        },

        arraySpanMethod({ row, column, rowIndex, columnIndex }) {
            if (row.status === -1 || row.negative_order === 1) {
                if ([1, 2, 3, 4, 5].includes(columnIndex)) {
                    if (columnIndex === 1) {
                        return {
                            rowspan: 1,
                            colspan: 5
                        }
                    } else {
                        return [0, 0]
                    }
                }
            }
        },

        activeStore(store) {
            if (store.isTotalColumn) return
            if (store.negative_order === 1) {
                this.$refs.orderStoreDetail && this.$refs.orderStoreDetail.close()
                return this.openMessage(2, '该店今日不订货')
            }
            if (store.status === -1) {
                this.$refs.orderStoreDetail && this.$refs.orderStoreDetail.close()
                return this.openMessage(2, '该店暂未提交订货单')
            }
            this.activedStore = store
            this.$refs.orderStoreDetail.open({
                store: store,
                callback: () => { }
            })
        },

        changeStatus(item) {
            console.log(item)
            this.$fetch.put({
                url: '/station/demandorder/' + item.demand_order_id,
                params: {
                    status: item.status === 1 ? 1 : 2
                }
            }).then(data => {
                this.openMessage(1, '修改状态成功')
                this.getOrderList()
                this.$emit('statusChanged')
            }).catch(e => {
                item.status = item.status === 1 ? 2 : 1
                this.openMessage(0, '修改失败，' + e)
            })
        },

        save() {
            // this.validator().then(() => {
            // 将没选择采购员的商品提取出来
            if (this.btnLoading) return
            let unChoosedPurchaseGoods = this.wishOrderData.reduce((last, next) => {
                if (next.purchaser_id === 0) {
                    return [...last, next.goods_name]
                } else {
                    return last
                }
            }, [])

            if (unChoosedPurchaseGoods.length > 0) {
                this.$myWarning({
                    message: `${unChoosedPurchaseGoods.slice(0, 2).join(',')}等${unChoosedPurchaseGoods.length}个商品暂未设置采购员，确定完成汇总吗？`
                }).then(() => {
                    next.call(this)
                }).catch(() => {})
            } else {
                next.call(this)
            }

            function next() {
                const message = this.stationConfig.purchase_type === 0
                    ? '点击完成汇总后，今日将不再接收分店的订货和修改订货请求，同时系统将给采购员发送采购单，给仓库发出调货通知，确认完成汇总吗？'
                    : '点击完成汇总后，今日将不再接收分店的订货和修改订货请求，同时系统将给仓库发出调货通知，在后台生成待采购单，确认完成汇总吗？'
                this.$myWarning({
                    message: message
                }).then(() => {
                    this.btnLoading = true
                    this.$fetch.post({
                        url: '/demandcutoff',
                        params: {
                            "wish_order_id": this.wishOrderId,
                            goods_list: this.wishOrderData.map(value => { // 转换成服务器需要的数据
                                let obj = {}
                                obj.goods_id = value.goods_id
                                obj.goods_name = value.goods_name
                                obj.purchaser_id = value.purchaser_id || 0
                                obj.demand_amount = value.demand_amount
                                obj.modified_demand_amount = value.modified_demand_amount
                                obj.storage = value.storage

                                return obj
                            })
                        }
                    }).then(data => {
                        console.log(data)
                        this.openMessage(1, '汇总成功')
                        this.$emit('statusChanged')
                    }).catch(e => {
                        this.openMessage(0, e || '汇总失败')
                    }).finally(() => {
                        this.btnLoading = false
                    })
                }).catch(e => {})
            }
        }
    },

    components: {
        Printer,
        OrderStoreDetail
    }
}
</script>

<style lang="scss">
.order-store-list-bg {
    position: fixed;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    z-index: 2001;
}
.stores {
    position: absolute;
    top: 0px;
    left: 0px;
    bottom: 0px;
    // min-width: 550px;
    user-select: none;
    transition: min-width .7s;
    box-shadow: 9px 3px 20px -10px rgba(0, 0, 0, 0.4);

    .count {
        display: inline-block;
        padding: 0 10px;
        height: 30px;
        // width: 126px;
        line-height: 30px;
        background: rgba(71,184,160, .3);
        color: #009688;
        border-radius: 0 15px 15px 0;
    }

    // .store-contianer {
    //     position: absolute;
    //     top: 0px;
    //     bottom: 0;
    //     width: 100%;
    //     background: #fff;
    //     box-shadow: 9px 3px 20px -10px rgba(0, 0, 0, 0.4);
    // }

    .stores-list {
        // position: absolute;
        position: relative;
        display: inline-block;
        vertical-align: top;
        // width: 100%;
        height: 100%;
        // padding: 10px;
        border-right: 1px #f2f2f2 solid;

        .header {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            width: 100%;
            height: 66px;
            background: #F9F9F9;

            h2 {
                margin-left: 10px;
                font-size: 20px;
                color: #333333;
            }

            /deep/ .el-button.is-round {
                padding: 0;
            }

            button {
                margin: 0px 96px 0 12px;
                width: 86px;
                height: 30px;
                // background: #009688;
                // border: 1px solid #009688;
                border-radius: 15px;
                font-size: 14px;

                // color: #FFFFFF;
            }

            .confirm {
                background: #009688;
                border: 1px solid #009688;
                color: #FFFFFF;
            }

            .disabled {
                background: #DDDDDD;
                font-size: 14px;
                color: #666666;
            }

            i {
                font-size: 20px;
                color: #999999;
                cursor: pointer;
                position: absolute;
                right: 20px;
            }
        }

        /deep/ .cell {
            padding: 0 !important;
            white-space: nowrap;
        }

        .el-icon-arrow-right {
            font-size: 18px;

            &:hover {
                cursor: pointer;
                color: #009688;
            }
        }
    }

    .configuration {
        // position: relative;
        height: 46px;
        padding-left: 10px;
        line-height: 46px;
        box-shadow: 0px -5px 10px 0 rgba(0, 0, 0, 0.05);
        font-size: 14px;
        color: #333333;
        background: #fff;
        cursor: pointer;

        img {
            margin-right: 5px;
            width: 22px;
            height: 22px;
            vertical-align: middle;
        }

        .items-container-bg {
            position: absolute;
            // top: -100%;
            top: 0;
            left: 0;
            bottom: 46px;
            width: 100%;
            z-index: 1;
            // padding: 10px;

            .items-container {
                position: absolute;
                bottom: 0;
                background: #fff;
                width: 100%;
                box-shadow: 0px -5px 10px 0 rgba(0, 0, 0, 0.05);
            }
            .item {
                padding-left: 10px;
                height: 30px;
                line-height: 30px;

                &:hover {
                    background: #f5f5f5;
                }
            }
        }
    }
}

.order-store-list-popper {
    /deep/ .el-checkbox + .el-checkbox {
        margin-left: 0px;
    }

    /deep/ .el-checkbox {
        margin-right: 10px;
        margin-bottom: 10px;
    }
}

.slide-fade-enter-active {
    transition: all .3s ease;
}
.slide-fade-leave-active {
    transition: all .3s ease;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
    transform: translateX(-232px);
    opacity: 0;
}

</style>
