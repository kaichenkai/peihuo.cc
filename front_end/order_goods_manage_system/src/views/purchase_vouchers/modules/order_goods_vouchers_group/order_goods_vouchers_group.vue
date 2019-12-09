// 订货汇总单
<template>
    <div class="order_goods_container">
        <!-- <bread-crumb :titles="['采购单', '订货汇总单']"></bread-crumb> -->
        <el-upload
        v-if="isUserCanUploadFiles"
        class="fixed-btn import-btn"
        name="files"
        ref="upload"
        :limit="1"
        :show-file-list="false"
        :on-success="uploadSuccess"
        :on-error="uploadError"
        :data="{
            action: 'demand_order_parser',
            wish_order_id: wishOrderId
        }"
        action="/api/parser/order">
        <el-button size="small">导入订货单</el-button>
        </el-upload>
        <el-button size="small" class="fixed-btn export-btn" @click="exportOrder">导出各店进货单</el-button>
        <!-- <i class="one-px-line"></i> -->
        <div class="top">
            <div class="btn-group">
                <p @click="showOrderStoreList">
                    <img src="~@/assets/images/a14.png" alt="">
                    <span style="color: #009688">订货门店（{{storeCount}})</span>
                    <span v-if="demandOrderUpDateStatus.order_update_dict && wishOrderId in demandOrderUpDateStatus.order_update_dict && demandOrderUpDateStatus.order_update_dict[wishOrderId] > 0" style="color: #ff6666;margin-left: 8px;">+{{demandOrderUpDateStatus.order_update_dict[wishOrderId]}}</span>
                </p>
                <p @click="showInOutStockList">
                    <img src="~@/assets/images/a13.png" alt="">
                    <span style="color: #009688">仓库出货单</span>
                </p>
                <p @click="showPurchaseBehaviour">
                    <img src="~@/assets/images/a23.png" alt="">
                    <span style="color: #009688">采购动态</span>
                    <i v-if="isPurchaseHaveNewBehaviour"></i>
                </p>
                <el-date-picker
                    size="mini"
                    v-model="wishOrderdate"
                    type="date"
                    :clearable="false"
                    :editable="false"
                    @change="getWishOrderIdByDate"
                    value-format="yyyy-MM-dd"
                    placeholder="选择日期">
                </el-date-picker>
            </div>
            <!-- <h2><span>{{wishDate}}订货汇总单</span></h2> -->
        </div>
        <el-input
            ref="searchInput"
            v-selectTextOnFocus
            class="search"
            placeholder="输入分车单号"
            @keyup.enter.native="searchOrder"
            v-model="search">
            <span slot="suffix" @click="searchOrder">|&nbsp;搜索</span>
        </el-input>
        <el-table
            class="tabel"
            :data="tableData"
            :height="tableHeight"
            v-loading="loading"
            :row-class-name="tableRowClassName"
            :span-method="objectSpanMethod"
            style="width: 100%">
            <el-table-column
            prop="serial_number"
            min-width="40"
            label="序号">
            </el-table-column>
            <el-table-column
            min-width="220">
            <template slot="header" slot-scope="scope">
                <table-data-filter title="商品名" allString="所有商品" :items="allGoodsData" itemKeyName="goods_name" itemKeyCode="goods_id"  v-model="searchObj.goods_ids" @confirm="getOrderGoodsVouchers"></table-data-filter>
            </template>
            <template slot-scope="scope">
                <span class="name" :style="[{'color': scope.row.order_goods_name_modified ? '#f00':''}]">{{ scope.row.goods_name }}</span>
            </template>
            </el-table-column>
            <el-table-column
            prop="storage"
            sortable
            label="仓库库存"
            min-width="80">
            </el-table-column>
            <el-table-column
            prop="demand_amount"
            min-width="70"
            sortable
            :sort-method="(a, b) => {
                if (a.modify_status) {
                    if (b.modify_status) {
                        return a.modified_demand_amount - b.modified_demand_amount
                    } else {
                        return a.modified_demand_amount - b.demand_amount
                    }
                } else {
                    if (b.modify_status) {
                        return a.demand_amount - b.modified_demand_amount
                    } else {
                        return a.demand_amount - b.demand_amount
                    }
                }
            }"
            label="订货量">
            <template slot-scope="scope">
                <span v-if="scope.row.modify_status">
                    <span>{{scope.row.modified_demand_amount}}</span>
                    <del style="margin-left: 8px;color:#999">{{scope.row.demand_amount}}</del>
                </span>
                <span v-else>
                    <span>{{scope.row.demand_amount}}</span>
                </span>
            </template>
            </el-table-column>
            <el-table-column
            prop="purchasing_amount"
            min-width="70"
            sortable
            label="待采购">
            </el-table-column>
            <el-table-column
            prop="address"
            min-width="70"
            sortable
            sort-by="purchaser_id"
            label="采购员">
            <template slot-scope="scope">
                <span style="white-space: nowrap;">{{scope.row.purchaser_name || '-'}}</span>
            </template>
            </el-table-column>
            <el-table-column
            width="60"
            sortable
            :sort-method="(a, b) => {
                if(a.purchase_data.length > 0 && b.purchase_data.length > 0) {
                    return computePurchasedData(a).amount - computePurchasedData(b).amount
                } else if (a.purchase_data.length > 0) {
                    return 1
                } else {
                    return -1
                }
            }"
            :class-name="'p0'"
            label="实采">
            <template slot-scope="scope">
                <!-- <div v-if="stationConfig.purchase_type === 0">
                    <span v-if="scope.row.purchase_data.length > 0">{{computePurchasedData(scope.row).amount}}</span>
                    <span v-else>0</span>
                </div> -->
                <!-- 如果商品采购方式是采购员采购并且为采购状态或者有采购数据，那么显示采购的信息 -->
                <div @click="setPurchaseData(scope.row)" class="purchases-data" v-if="(stationConfig.purchase_type == 0 && scope.row.is_purchase == 0) || (scope.row.purchase_data.length > 0 && scope.row.purchase_data[0].firm_id)">
                    <div class="table-cell">
                        <span v-if="scope.row.purchase_data.length > 0">{{computePurchasedData(scope.row).amount}}</span>
                        <span v-else>0</span>
                    </div>
                    <div class="table-cell">
                        {{scope.row.purchase_price}}
                    </div>
                    <div class="table-cell">
                        <span v-if="computePurchasedData(scope.row).firms.length == 0">-</span>
                        <span v-else-if="computePurchasedData(scope.row).firms.length == 1">{{computePurchasedData(scope.row).firms[0]}}</span>
                        <span v-else>
                            <el-popover trigger="hover" placement="top">
                            <p v-for="(item,key) in computePurchasedData(scope.row).firms" :key="key">姓名: {{ item }}</p>
                            <div slot="reference" class="name-wrapper">
                                <el-tag size="medium">{{computePurchasedData(scope.row).firms.length}}人</el-tag>
                            </div>
                            </el-popover>
                        </span>
                    </div>
                    <div class="table-cell">
                        <span v-if="computePaymentData(scope.row).payTypes.length == 0">-</span>
                        <span v-else-if="computePaymentData(scope.row).payTypes.length == 1">{{computePaymentData(scope.row).payTypes[0]}}</span>
                        <span v-else>
                            <el-popover trigger="hover" placement="top">
                            <p v-for="(item,key) in computePaymentData(scope.row).payTypes" :key="key">支付方式: {{ item }}</p>
                            <div slot="reference" class="name-wrapper">
                                <el-tag size="medium">{{computePaymentData(scope.row).payTypes.length}}种</el-tag>
                            </div>
                            </el-popover>
                        </span>
                    </div>
                </div>
                <!-- is_purchase 0 采购 1不采购 -->
                <!-- else if 采购方式是手动录入数据，那么展示录入按钮 -->
                <div @click="setPurchaseData(scope.row)" v-else-if="stationConfig.purchase_type == 1" class="purchases-data">
                    <el-button type="text" style="margin-left: 10px;font-size: 14px;color: #009688;">录入采购数据</el-button>
                </div>
                <!-- is_purchase 0 采购 1不采购 -->
                <!-- else if 采购方式是采购员录入，并且采购状态为不采购，那么显示不采了 -->
                <div v-else-if="stationConfig.purchase_type == 0 && scope.row.is_purchase" class="purchases-data">
                    <p type="text" style="display: block; width: 100%; text-align: center; font-size: 14px; color: #ff6666;">不采了</p>
                </div>
            </template>
            </el-table-column>
            <el-table-column
            width="60"
            label="进货价"
            >
            </el-table-column>
            <el-table-column
            width="60"
            label="供货商">
            <!-- <template slot-scope="scope">
                <span v-if="computePurchasedData(scope.row).firms.length == 0">-</span>
                <span v-else-if="computePurchasedData(scope.row).firms.length == 1">{{computePurchasedData(scope.row).firms[0]}}</span>
                <span v-else>
                    <el-popover trigger="hover" placement="top">
                    <p v-for="(item,key) in computePurchasedData(scope.row).firms" :key="key">姓名: {{ item }}</p>
                    <div slot="reference" class="name-wrapper">
                        <el-tag size="medium">{{computePurchasedData(scope.row).firms.length}}个供货商</el-tag>
                    </div>
                    </el-popover>
                </span>
            </template> -->
            </el-table-column>
            <el-table-column
            width="80"
            label="付款方式"
            >
            </el-table-column>
            <el-table-column
            prop="allocated_amount"
            min-width="60"
            sortable
            label="实配">
            </el-table-column>
            <el-table-column
            prop="address"
            width="270"
            label="操作">
            <template slot-scope="scope">
                <div class="btn-wrapper">
                    <el-button v-if="scope.row.allocated_times == 0" class="table-btn color-009688" type="text" @click="distributionStaff(scope.row)">单品配货</el-button>
                    <el-button v-else class="table-btn color-ddd" type="text" @click="distributionStaff(scope.row)">已配货{{scope.row.allocated_times}}次</el-button>
                    <el-popover class="popover" trigger="hover" placement="top" :visible-arrow="true" popper-class="popover">
                        <!-- <p><button style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">修改品名</button></p> -->
                        <!-- <p><button style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">结算备注</button></p> -->
                        <p><button @click="modifyOrderAmount(scope.row)" style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">修改订货量</button></p>
                        <p><button @click="setPurchare(scope.row)" style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">设置采购员</button></p>
                        <p><button @click="refund(scope.row)" style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">退货</button></p>
                        <p v-if="!isOrderFinished(wishOrderId + ':' + scope.row.goods_id)"><button @click="setOrderFinished(scope.row)" style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">标记完成</button></p>
                        <p v-else><button @click="setOrderUnFinished(scope.row)" style="font-size: 14px;color: #333333;background: transparent;" class="text-btn" type="text">取消完成</button></p>
                        <div slot="reference" class="name-wrapper">
                            <img src="~@/assets/images/a12.png" alt="" style="margin-left: 10px;"><button class="text-btn" type="text">更多操作</button>
                        </div>
                    </el-popover>
                    <span v-if="isOrderFinished(wishOrderId + ':' + scope.row.goods_id)" style="color: #009688; margin-left: 14px;">已完成</span>
                </div>
            </template>
            </el-table-column>
        </el-table>
        <distribution-staff ref="distributionStaff"></distribution-staff>
        <modify-order-amount ref="modifyOrderAmount"></modify-order-amount>
        <set-purchaser ref="setPurchaser"></set-purchaser>
        <refund-goods ref="refundGoods"></refund-goods>
        <in-out-stock-list ref="inOutStockList"></in-out-stock-list>
        <order-store-list :wishOrderId="wishOrderId" ref="orderStoreList" @statusChanged="getOrderGoodsVouchers()" @shopListChange="shopListChange" :wishOrderData="tableData" :wishOrderStatus="wishOrderStatus"></order-store-list>
        <comfirm-distribution-car ref="confirmDistributionCar"></comfirm-distribution-car>
        <set-purchase-data ref="setPurchaseData"></set-purchase-data>
        <confirm-distribution-staff ref="confirmDistributionStaff"></confirm-distribution-staff>
        <purchase-behaviour ref="purchaseBehaviour" :wishOrderId="wishOrderId"></purchase-behaviour>
    </div>
</template>

<script>
import BreadCrumb from '@/components/modules_top_tools/bread_crumb'
import OrderStoreList from './components/order_store_list/order_store_list'
import DistributionStaff from './components/distribution_staff.vue'
import ModifyOrderAmount from './components/modify_order_amount'
import ComfirmDistributionCar from './components/confirm_distribution_car'
import ConfirmDistributionStaff from './components/confirm_distribution_staff/confirm_distribution_staff'
import setPurchaser from '../components/set_purchaser'
import InOutStockList from './components/in_out_stock_list'
import RefundGoods from './components/goods_refund'
import SetPurchaseData from './components/set_purchase_data'
import PurchaseBehaviour from './components/purchase_behaviour'
import { mapState, mapGetters } from 'vuex'
import statusSignal from '@/assets/js/status_signal'
import orderStatusManager from '../js/order_status_manager'
import { filterPayTypes } from '@/config/pay_types'
import _ from 'lodash'
import apiIpAddress from '@/api/ip_config/main'
import * as utils from '@/utils'

export default {
    data() {
        return {
            searchObj: {
                goods_ids: []
            },
            wishOrderId: 0,
            allGoodsData: [],
            tableData: [],
            loading: false,
            wishOrderStatus: 0,
            orderShops: [],
            // wishDate: '',
            search: '',
            wishOrderdate: '', // utils.formatDate(new Date(), 'yyyy-MM-dd')
            isPurchaseHaveNewBehaviour: false
        }
    },

    computed: {
        ...mapState(['demandOrderUpDateStatus', 'stationConfig']),
        ...mapGetters(['isUserCanUploadFiles']),
        storeCount() {
            return this.orderShops.reduce((last, next) => {
                return last + ([1, 2].includes(next.status) ? 1 : 0)
            }, 0) + '/' + (this.orderShops.length - 1)
        }
    },

    created() {
        this.$store.dispatch('getStationConfig')
        this.initNowDate()
        this.init().catch(e => {
            this.openMessage(0, e)
        })
    },

    beforeDestroy() {
        clearInterval(this.timer)
    },

    methods: {
        filterPayTypes,

        initNowDate() {
            let isBeforePM3 = (function() {
                let now = new Date().getHours()
                if (now >= 15) {
                    return false
                } else {
                    return true
                }
            })()

            if (isBeforePM3) {
                this.wishOrderdate = utils.formatDate(new Date(), 'yyyy-MM-dd')
            } else {
                let tomorrow = new Date().setDate(new Date().getDate() + 1)
                this.wishOrderdate = utils.formatDate(new Date(tomorrow), 'yyyy-MM-dd')
            }
        },

        async init() {
            await this.getWishOrderIdByDate()
            this.timer = setInterval(() => {
                this.getOrderGoodsVouchers()
            }, 60 * 1000)
        },

        getWishOrderIdByDate() {
            this.searchObj.goods_ids = []
            return this.$fetch.get({
                url: '/wishorderidbydate',
                params: {
                    wish_date: this.wishOrderdate
                }
            }).then(data => {
                this.wishOrderId = data.order_id
                this.getOrderGoodsVouchers().then(data => {
                    this.allGoodsData = data.summary_data // 存储所有的商品信息用于表头筛选
                })
            }).catch(e => {
                this.openMessage(0, e || '获取意向单Id失败')
            })
        },

        getOrderGoodsVouchers() {
            this.loading = true
            return this.$fetch.get({
                url: '/summary',
                params: {
                    wish_order_id: this.wishOrderId,
                    ..._.mapValues(this.searchObj, obj => obj.join('|') || undefined)
                }
            }).then(data => {
                this.tableData = data.summary_data
                // console.table(this.tableData)
                this.wishOrderStatus = data.wish_order_status
                this.purchaseOrderId = data.purchase_order_id
                if (this.purchaseOrderId) {
                    this.getPurchaseBehaviour()
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取订货汇总单失败')
            }).finally(() => {
                this.loading = false
            })
        },

        // 获取采购动态
        getPurchaseBehaviour() {
            this.$fetch.get({
                url: '/summarynotifications',
                params: {
                    purchase_order_id: this.purchaseOrderId
                }
            }).then(data => {
                // console.log(data)
                this.isPurchaseHaveNewBehaviour = data.purchasing_dynamics_update
            }).catch(e => {
                this.openMessage(0, e || '获取采购动态失败')
            })
        },

        shopListChange(data) {
            this.orderShops = data
        },

        showInOutStockList() {
            this.$refs.inOutStockList.open({
                wishOrderId: this.wishOrderId
            })
        },

        showPurchaseBehaviour() {
            this.$refs.purchaseBehaviour.open({
                purchaseOrderId: this.purchaseOrderId,
                callback: () => this.getPurchaseBehaviour()
            })
        },

        setOrderFinished(orderData) {
            orderStatusManager.setOrderStatus(this.wishOrderId + ':' + orderData.goods_id, 1)
            this.getOrderGoodsVouchers()
        },

        setOrderUnFinished(orderData) {
            orderStatusManager.setOrderStatus(this.wishOrderId + ':' + orderData.goods_id, 0)
            this.getOrderGoodsVouchers()
        },

        isOrderFinished(id) {
            return orderStatusManager.getOrderStatus(id)
        },

        tableRowClassName({ row }) {
            if (this.isOrderFinished(this.wishOrderId + ':' + row.goods_id) === 1) {
                return 'finished-order'
            } else {
                return ''
            }
        },

        objectSpanMethod({ row, column, rowIndex, columnIndex }) {
            if ([6, 7, 8, 9].includes(columnIndex)) {
                if (columnIndex === 6) {
                    return [1, 4]
                } else {
                    return [0, 0]
                }
            }
        },

        setPurchaseData(row) {
            if (this.stationConfig.purchase_type !== 1) {
                return
            }
            if (this.wishOrderStatus < 3) {
                return this.openMessage(2, '订货单未汇总')
            }
            this.$refs.setPurchaseData.open({
                goodsData: row,
                callback: this.getOrderGoodsVouchers.bind(this)
            })
        },

        setPurchare(row) {
            this.$refs.setPurchaser.open({
                data: row,
                wishOrderData: this.wishOrderId,
                callback: (id, name, remarks) => {
                    row.purchaser_id = id
                    row.purchaser_name = name
                }
            })
        },

        modifyOrderAmount(row) {
            this.$refs.modifyOrderAmount.open({
                wishOrderId: this.wishOrderId,
                goodsData: row,
                callback: this.getOrderGoodsVouchers.bind(this)
            })
        },

        exportOrder() {
            window.open(apiIpAddress + '/export/summary?wish_order_id=' + this.wishOrderId)
        },

        searchOrder() {
            this.$fetch.get({
                url: '/ordersearch/' + this.search
            }).then(data => {
                this.$refs.searchInput.blur()
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
        },

        computePurchasedData(data) {
            return {
                amount: data.purchase_data.reduce((last, next) => {
                    return last + next.purchased_amount
                }, 0),
                firms: [...new Set(data.purchase_data.reduce((last, next) => {
                    if (next.firm_id) {
                        return [...last, next.firm_name]
                    } else {
                        return last
                    }
                }, []))]
                // firmsCount: data.purchase_data.reduce((last, next) => {
                //     if (next.firm_id) {
                //         last += 1
                //     }
                //     return last
                // }, 0)
            }
        },

        computePaymentData(data) {
            return {
                payTypes: [...new Set(data.purchase_data.reduce((last, next) => {
                    if (next.purchased_amount > 0) {
                        return [...last, filterPayTypes(next.payment)]
                    } else {
                        return last
                    }
                }, []))]
            }
        },

        showOrderStoreList() {
            statusSignal.setPurchaseSignalStatus(this.wishOrderId)
            this.$refs.orderStoreList.open()
        },

        distributionStaff(data) {
            this.$refs.distributionStaff.open({
                wishOrderId: this.wishOrderId,
                goodsData: data,
                callback: this.getOrderGoodsVouchers
            })
        },

        refund(data) {
            this.$refs.refundGoods.open({
                wishOrderId: this.wishOrderId,
                data: data,
                callback: () => {
                    this.getOrderGoodsVouchers()
                }
            })
        },

        uploadSuccess(data) {
            // console.log(data)
            if (data.success) {
                this.openMessage(1, '上传成功')
                this.getOrderGoodsVouchers()
            } else {
                this.openMessage(0, data.error_text || '上传失败')
            }
            this.$refs.upload.clearFiles()
        },

        uploadError(data) {
            this.openMessage(0, '上传失败')
            this.$refs.upload.clearFiles()
        }
    },

    components: {
        BreadCrumb,
        OrderStoreList,
        DistributionStaff,
        setPurchaser,
        RefundGoods,
        InOutStockList,
        ModifyOrderAmount,
        ComfirmDistributionCar,
        SetPurchaseData,
        ConfirmDistributionStaff,
        PurchaseBehaviour
    }
}
</script>

<style lang="scss" scoped>
.order_goods_container {
    position: absolute;
    height: 100%;
    width: 100%;
    top: 0px;

    .fixed-btn {
        position: absolute;
        right: 0px;
        top: 0px;
    }

    .import-btn {
        position: absolute;
        right: 350px;
        top: 0px;
    }

    .export-btn {
        right: 220px;
    }

    .one-px-line {
        margin: 5px 0 25px 0;
    }

    .top {
        display: flex;
        align-items: center;
        justify-content: center;
        // margin-bottom: 20px;
        margin-top: 2px;

        // position:

        .btn-group {
            display: flex;
            flex: 1;
            user-select: none;

            p {
                img {
                    margin-right: 4px;
                }
                display: flex;
                align-items: center;
                margin-right: 12px;
                cursor: pointer;

                i {
                    position: relative;
                    top: -6px;
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #EE5B5B;
                }
            }
            // margin-right: 200px;
        }

        h2 {
            //
            flex: 1;
            // justify-self: flex-start;
            text-align: left;
            font-size: 20px;
            color: #333333;
            letter-spacing: 0;
            span {
                display: inline-block;
                transform: translateX(-50%);
            }
        }
    }

    .btn {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        bottom: 15px;
        height: 36px;
        padding: 7px 21px;
        font-size: 16px;
        border-radius: 2px;
        background: #009688;
        color: #FFF;
        outline: none;
        border: none;

        &:active {
            transform: translateX(-50%) scale(.9);
        }
    }

    .btn-disabled {
        color: #666;
        background: #E7E7E7;
        border: 1px solid #CCCCCC;
        cursor: not-allowed;
    }

.tabel {
    // margin-bottom: 200px;
    /deep/ .finished-order {
        background: #00968811;
    }
    .btn-wrapper {
        display: flex;
        align-items: center;
    }
    .table-btn {
        display: inline-block;
        min-width: 76px;
        padding: 4px 5px;
        margin-right: 10px;
        font-size: 14px;
        color:#009688;
        border: 1px #009688 solid;
        outline: none;
        white-space: nowrap;

        &:active {
            transform: scale(.9);
        }
    }

    .name-wrapper {
        img {
            width: 20px;
            vertical-align: middle;
        }
    }

    .color-009688 {
        color: #009688;
        border-color: #009688;
    }

    // .popover {
        /deep/ .text-btn {
            font-size: 14px;
            color: #333333;
            background: transparent;
        }
    // }

    .color-ddd {
        color: #333;
        background: #f9f9f9;
        border-color: #ddd;
    }

    // .table-btn.disabled {
    //     border: 1px #ccc solid !important;
    //     color: #ccc !important;
    //     cursor: not-allowed;
    // }

    // td.p0 {
        /deep/ div.cell {
            padding-left: 5px;
            padding-right: 5px;
            overflow: unset;
            white-space: nowrap;
            overflow: hidden;
        }
    // }

    .purchases-data {
        display: flex;
        align-items: center;
        height: 30px;
        width: 100%;
        background: #FFFFFF;
        border: 1px solid #F2F2F2;
        cursor: pointer;
        // transform: t
        >div {
            flex: 1;
            padding-left: 10px;
            line-height: 30px;
            // width: 100px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            transform: translateX(-10px);

            &:nth-of-type(1) {
                width: 60px;
            }

            &:nth-of-type(2) {
                width: 60px;
            }

            &:nth-of-type(3) {
                width: 60px;
            }

            &:nth-of-type(4) {
                width:80px;
            }
        }
    }
}
    .search {
        position: absolute;
        width: 205px;
        top: -6px;
        right: 0;

        /deep/ .el-input__suffix {
            right: 10px;
            line-height: 40px;
            color: #009688;
            cursor: pointer;
        }

        /deep/ .el-input__inner {
            padding-right: 54px;
        }
    }

    /deep/ .el-date-editor.el-input{
        width: 150px;
        .el-input__inner{
            height: 30px;
            line-height: 30px;
            border-radius: 15px;
            font-size: 16px;
            color: #333333;
        }
    }
}
</style>
