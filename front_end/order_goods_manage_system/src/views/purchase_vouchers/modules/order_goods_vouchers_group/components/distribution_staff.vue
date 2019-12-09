<template>
<transition name="slide-fade">
    <div class="distribution-staff-bg" v-if="showDialog" @click="close">
        <div class="container" @click.stop>
            <div class="header">
                <h2>单品配货单</h2>
                <button :class="{'diabled': !isDistributionStaffComplete}" :disabled="!isDistributionStaffComplete" @click="confirm">确认并打印</button>
                <i class="el-icon el-icon-close" @click="close"></i>
            </div>
            <div id="outerContainer">
                <div id="innerContainer">
                    <div class="order-info">
                        <p class="item"><span class="item-name">商品名：</span>{{goodsData.goods_name}}</p>
                        <p class="item" v-if="goodsData.purchaser_name"><span class="item-name">采购员：</span>{{goodsData.purchaser_name}}</p>
                        <p class="item">
                        <span class="item-name">实际到货：</span>
                        <input style="width: 80px;" type="number" v-removeMouseWheelEvent v-selectTextOnFocus v-model="practical">
                        <span class="item-name" style="margin-left: 10px;">更改配货量：</span>
                        <el-select v-model="distributionMode" placeholder="请选择">
                            <el-option
                            v-for="item in distributionModes"
                            :key="item.id"
                            :label="item.name"
                            :value="item.id">
                            </el-option>
                        </el-select>
                        </p>
                        <div class="item flex">
                            <span class="item-name">到货信息：</span>
                            <div class="info-container">
                                <table>
                                    <tr>
                                        <th></th>
                                        <th class="left">来源</th>
                                        <th>实采</th>
                                        <th>实配</th>
                                        <th>剩余</th>
                                    </tr>
                                    <template
                                        v-for="item in goodsData.purchase_data"
                                        v-if="item.firm_id">
                                        <tr :key="item.firm_id">
                                            <td><my-radio v-model="choosedFirm" :label="item.firm_name + '$' + item.purchase_goods_id"></my-radio></td>
                                            <td class="left">{{item.firm_name}}</td>
                                            <td>{{item.purchased_amount}}</td>
                                            <td>{{item.allocated_amount}}</td>
                                            <td>{{item.purchased_amount - item.allocated_amount}}</td>
                                        </tr>
                                        <tr v-if="item.remarks" :key="'a' + item.firm_id">
                                            <td></td>
                                            <td class="left" style="color: #EE5B5B" colspan="4">{{item.remarks}}</td>
                                        </tr>
                                    </template>

                                    <tr
                                    v-for="(item) in goodsData.stock_out_data"
                                    v-if="item.record_id"
                                    :key="item.record_id">
                                        <td><my-radio v-model="choosedFirm" :label="'仓库$' + item.record_id"></my-radio></td>
                                        <td class="left">仓库</td>
                                        <td>{{item.amount}}</td>
                                        <td>{{item.allocated_amount}}</td>
                                        <td>{{item.amount - item.allocated_amount}}</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                    <table class="table table-header" id="table-header">
                        <tr>
                            <th>店铺</th>
                            <th>库存量</th>
                            <th>订货量</th>
                            <th v-if="sumData.total_allocated_amount>0">已配量</th>
                            <th>配货量</th>
                        </tr>
                        <tr>
                            <td>累计</td>
                            <td>{{sumData.total_storage}}</td>
                            <td>{{sumData.total_demand_amount}}</td>
                            <td v-if="sumData.total_allocated_amount>0">{{sumData.total_allocated_amount}}</td>
                            <td :style="{'color': isDistributionStaffComplete ? '#009688':'#f00'}">{{totalAllocateingamount}}</td>
                        </tr>
                    </table>
                    <table class="table">
                        <tr v-for="(item, index) in tableData" :key="index">
                            <td :style="[{'color': item.negative_order ? '#f00' : ''}]">{{item.shop_name}}</td>
                            <td>{{item.current_storage}}</td>
                            <td>{{item.demand_amount}}</td>
                            <td v-if="sumData.total_allocated_amount>0">{{item.allocated_amount}}</td>
                            <td>
                                <input type="number" v-removeMouseWheelEvent v-selectTextOnFocus @input="computeTotalAllocateingamount" @change="computeTotalAllocateingamount" min="0" v-model.number="item.allocating_amount">
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="bottom_operate">
                <span @click="modifyOrderAmount">修改订货量</span>
                <span @click="peihuoHistory">配货历史</span>
            </div>
        </div>
        <modify-order-amount ref="modifyOrderAmount"></modify-order-amount>
        <peihuo-history ref="peihuoHistory"></peihuo-history>
    </div>
</transition>
</template>

<script>
import StickyListHeaders from 'sticky-list-headers'
import ModifyOrderAmount from './modify_order_amount'
import peihuoHistory from './peihuo_history'
// import distributionManager from '../../js/distribution_staff_manager'
export default {
    data() {
        return {
            showDialog: false,
            sumData: {},
            tableData: [],
            goodsData: {},
            choosedFirm: '',
            practical: 0,
            totalAllocateingamount: 0,
            distributionMode: 0,
            distributionModes: [{
                id: 0,
                name: '等于订货'
            }, {
                id: 1,
                name: '按比例'
            }, {
                id: 2,
                name: '顺序配货'
            }]
        }
    },

    computed: {
        // totalAllocateingamount() {

        // },

        isDistributionStaffComplete() {
            if (+this.practical === this.totalAllocateingamount && this.choosedFirm) {
                return true
            } else {
                return false
            }
        }
    },

    watch: {
        practical(newVal) {
            this.setAllDistributionAmountByMode()
        },

        distributionMode() {
            this.setAllDistributionAmountByMode()
        }
    },

    mounted() {

    },

    methods: {
        open(obj) {
            this.practical = 0
            this.showDialog = true
            this.cacheData = obj
            this.goodsData = JSON.parse(JSON.stringify(obj.goodsData))
            this.callback = obj.callback || function() {}
            console.log(obj)
            this.getOrderDetail().then(() => {
                this.setDefaultFirmAndStaffAmount()
                // this.setDefaultDistributionAmount()
                this.setAllDistributionAmountByMode()
                new StickyListHeaders({
                    outerContainer: 'outerContainer',
                    innerContainer: 'innerContainer',
                    headers: ['table-header']
                })
            })
        },

        close() {
            this.showDialog = false
            this.totalAllocateingamount = 0
        },

        peihuoHistory() {
            this.$refs.peihuoHistory.open({
                wishOrderId: this.cacheData.wishOrderId,
                goodsData: this.goodsData,
                callback: this.callback
            })
        },

        modifyOrderAmount() {
            this.$refs.modifyOrderAmount.open({
                wishOrderId: this.cacheData.wishOrderId,
                goodsData: this.goodsData,
                callback: () => {
                    this.getOrderDetail()
                    this.callback()
                }
            })
        },

        getOrderDetail() {
            return this.$fetch.get({
                url: '/goodsallocations',
                params: {
                    wish_order_id: this.cacheData.wishOrderId,
                    goods_id: this.cacheData.goodsData.goods_id
                }
            }).then(data => {
                this.sumData = data.sum_data
                this.tableData = data.data_list
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        setDefaultFirmAndStaffAmount() {
            let purchaseData = this.goodsData.purchase_data.concat(this.goodsData.stock_out_data).filter(value => {
                return value.firm_id || value.record_id
            })

            if (purchaseData.length === 1) {
                if (purchaseData[0].record_id) {
                    this.practical = +purchaseData[0].amount
                    this.choosedFirm = '仓库$' + purchaseData[0].record_id
                } else {
                    this.practical = +purchaseData[0].purchased_amount
                    this.choosedFirm = purchaseData[0].firm_name + '$' + purchaseData[0].purchase_goods_id
                }
            }
        },

        // setDefaultDistributionAmount() {
        //     let cachedData = distributionManager.get(this.cacheData.wishOrderId, this.goodsData.goods_id)
        //     this.tableData = this.tableData.map(value => {
        //         let distributionInfo = cachedData.find(cache => +value.shop_id === +cache.shop_id)
        //         if (distributionInfo) {
        //             value.allocating_amount = distributionInfo.allocating_amount
        //         } else {
        //             value.allocating_amount = value.demand_amount
        //         }

        //         return value
        //     })
        //     console.log(this.tableData)
        //     this.computeTotalAllocateingamount()
        // },

        setAllDistributionAmountByMode(mode) {
            let modeDict = {
                0: () => {
                    this.tableData = this.tableData.map(value => {
                        value.allocating_amount = value.demand_amount
                        return value
                    })
                },

                1: () => {
                    if (this.practical > 0) {
                        this.tableData = this.tableData.map(value => {
                            value.allocating_amount = Math.floor(this.practical * (value.demand_amount / this.sumData.total_demand_amount))
                            return value
                        })
                    } else {
                        this.tableData = this.tableData.map((value, index) => {
                            value.allocating_amount = 0
                            return value
                        })
                    }
                },

                2: () => {
                    let practical = this.practical
                    let tag = true

                    this.tableData = this.tableData.map(value => {
                        let needs = Math.max(0, value.demand_amount - (value.allocated_amount || 0))
                        practical -= needs
                        if (practical >= 0) {
                            value.allocating_amount = needs
                        } else if (tag) {
                            value.allocating_amount = needs + practical
                            tag = false
                        } else {
                            value.allocating_amount = 0
                        }

                        return value
                    }).map(value => {
                        if (value.shop_id === 0 && practical > 0) {
                            value.allocating_amount = practical
                        }
                        return value
                    })
                }
            }

            modeDict[this.distributionMode]()
            this.computeTotalAllocateingamount()
        },

        setOneStaffDistributionAmount() {
            this.computeTotalAllocateingamount()
        },

        setDistributionData() {
            this.goodsData.purchase_data = this.goodsData.purchase_data.filter(ele => {
                return ele.firm_id
            })
            if (this.goodsData.purchase_data.length === 1 && !(this.goodsData.stock_out_data && this.goodsData.stock_out_data.record_id)) {
                this.practical = this.goodsData.purchase_data[0].purchased_amount
                this.choosedFirm = this.goodsData.purchase_data[0].firm_name + '$' + this.goodsData.purchase_data[0].purchase_goods_id
            } else if (this.goodsData.purchase_data.length === 0 && this.goodsData.stock_out_data && this.goodsData.stock_out_data.record_id) {
                this.practical = this.goodsData.stock_out_data.amount
                this.choosedFirm = '仓库$' + this.goodsData.stock_out_data.record_id
            }
        },

        computeTotalAllocateingamount() {
            this.totalAllocateingamount = this.tableData.reduce((last, next) => {
                last += (next.allocating_amount || 0)
                return last
            }, 0)
        },

        confirm() {
            if (!this.choosedFirm) {
                return this.openMessage(2, '请选择到货来源')
            }
            let [firmName, id] = this.choosedFirm.split('$')
            let params = {
                firm_name: firmName
            }

            if (firmName !== '仓库') {
                params.purchase_goods_id = id
            } else {
                params.stock_out_record_id = id
            }
            // params.warehousing_amount = this.tableData.filter(value => value.shop_id === 0)[0].allocating_amount
            params.allocate_list = this.tableData.map(value => {
                return {
                    shop_id: value.shop_id,
                    shop_name: value.shop_name,
                    allocating_amount: value.allocating_amount,
                    destination: value.destination
                }
            })

            this.$fetch.post({
                url: '/allocationorder',
                params: params
            }).then(data => {
                this.choosedFirm = ''
                this.showDialog = false
                this.practical = 0
                this.callback()
                this.openMessage(1, '确认成功')
            }).catch(e => {
                this.openMessage(0, e || '提交失败')
            })
        }
    },

    components: {
        ModifyOrderAmount,
        peihuoHistory
    }
}
</script>

<style lang="scss" scoped>
.distribution-staff-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1001;
    transform: translateZ(1px);

    .container {
        position: absolute;
        top: 0;
        right: 0;
        width: 420px;
        bottom: 0;
        background: #fff;
        box-shadow: -10px 0 10px 0 rgba(0, 0, 0, 0.05);

        .header {
            display: flex;
            align-items: center;
            height: 56px;
            background: #f9f9f9;

            h2 {
                margin: 0 10px;
                font-size: 20px;
                color: #333333;
            }

            button {
                margin-right: 156px;
                width: 100px;
                height: 30px;
                background: #009688;
                border-radius: 2px;
                font-size: 14px;
                color: #fff;
                border-radius: 15px;
            }

            .diabled {
                background: #999;
            }

            i {
                font-size: 20px;
                cursor: pointer;
            }
        }

        #outerContainer {
            position: absolute;
            top: 56px;
            left: 0;
            right: 0;
            bottom: 50px;

            #innerContainer {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                overflow: auto;
            }

            .order-info {
                padding: 13px 10px;

                .item {
                    font-size: 14px;
                    color: #333333;
                    letter-spacing: 0;
                    line-height: 30px;

                    .item-name {
                        display: inline-block;
                        width: 90px;
                    }

                    input {
                        padding-left: 10px;
                        width: 310px;
                        height: 30px;
                        background: #FFFFFF;
                        border: 1px solid;
                        border-color: #999999;
                        outline: none;

                        &:focus {
                            border-color: #009688;
                        }
                    }

                    /deep/ .el-select {
                        width: 105px;
                    }
                }

                .flex {
                    display: flex;

                    .p-2 {
                        margin-left: 28px;
                        color: #999999;
                    }
                }

                .info-container {
                    width: 310px;
                    padding: 10px;
                    padding-top: 0px;
                    margin-top: 8px;
                    background: #FFFFFF;
                    border: 1px solid #F4F4F4;

                    @mixin tableColumnWidth {
                        &:nth-of-type(1) {
                            width: 20px;
                        }

                        &:nth-of-type(2) {
                            width: 100px;
                        }

                        // &:nth-of-type(1) {
                        //     width: 80px;
                        // }

                        // &:nth-of-type(1) {
                        //     width: 80px;
                        // }

                        // &:nth-of-type(1) {
                        //     width: 80px;
                        // }
                    }

                    >table {
                        width: 100%;

                        th {
                            color: #999999;
                        }

                        td {
                            color: #333333;
                        }

                        th,td {
                            @include tableColumnWidth;
                            text-align: right;
                        }

                        .left {
                            text-align: left;
                        }
                    }
                }
            }

            .table {
                width: 100%;
                max-height: calc(100% - 300px);
                tr,td,th {
                    padding: 0 10px;
                    text-align: left;
                    font-size: 14px;
                    color: #333333;
                    height: 36px;
                    line-height: 36px;
                }

                td {
                    background: #fff;
                }
                th:nth-of-type(1),tr:nth-of-type(1),td:nth-of-type(1) {
                    width: 100px;
                }
                th:nth-of-type(2),tr:nth-of-type(2),td:nth-of-type(2) {
                    width: 70px;
                }
                th:nth-of-type(3),tr:nth-of-type(3),td:nth-of-type(3) {
                    width: 70px;
                }
                th:nth-of-type(4),tr:nth-of-type(4),td:nth-of-type(4) {
                    width: 70px;
                }
                th:nth-of-type(5),tr:nth-of-type(5),td:nth-of-type(5) {
                    width: 80px;
                }

                input {
                    width: 100%;
                }
            }

            .table-header {
                box-shadow: 0 4px 4px 0 rgba(0,0,0,0.05);
                th {
                    background: #F2F2F2;
                    height: 36px;
                    line-height: 36px;
                    font-size: 14px;
                    color: #333333;
                    font-weight: bold;
                }

                tr:nth-of-type(2) {
                    td {
                        font-size: 14px;
                        color: #333333;
                        font-weight: bold;
                    }
                }
            }
        }

        .bottom_operate{
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 50px;
            padding-top: 13px;
            background-color: #fff;
            box-shadow: 0 -3px 10px 0 rgba(0, 0, 0, 0.05);
            span{
                display: inline-block;
                padding: 5px 10px;
                color: #000;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                &:nth-of-type(1){
                    border-right: 1px solid #ccc;
                }
            }
        }
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
    transform: translateX(390px);
    opacity: 0;
}
</style>
