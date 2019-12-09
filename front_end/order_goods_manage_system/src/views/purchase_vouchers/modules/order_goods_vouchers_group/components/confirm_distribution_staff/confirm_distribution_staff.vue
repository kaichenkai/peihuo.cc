<template>
<transition name="slide-fade">
    <div class="distribution-staff-bg" @click.stop v-if="showDialog" @click="showDialog = false">
        <div class="container" @click.stop>
            <div class="header">
                <h2 v-if="!isModify">确认配货</h2>
                <h2 v-else>修改实配量</h2>
                <button v-if="!isModify" @click="confirm">确认配货</button>
                <i class="el-icon el-icon-close" @click="showDialog = false"></i>
            </div>
            <div id="outerContainer">
                <div id="innerContainer">
                    <div class="order-info">
                        <p class="item"><span class="item-name">商品名：</span>{{goodsData.goods_name}}</p>
                        <p class="item"><span class="item-name">供货商：</span>{{goodsData.firm_name}}</p>
                        <p class="item"><span class="item-name">到货量：</span><input :disabled="!isModify" :class="{'disabled': !isModify}" v-model="goodsData.allocated_amount" v-selectTextOnFocus v-removeMouseWheelEvent type="number" /></p>
                        <p class="item"><span class="item-name">备注：</span><input class="input" v-model="remarks" type="text" /></p>
                    </div>
                    <table class="table table-header" id="table-header">
                        <tr>
                            <th>店铺</th>
                            <th>已配货</th>
                        </tr>
                        <tr>
                            <td>累计</td>
                            <td>{{+totalAllocateingamount.toFixed(2)}}</td>
                        </tr>
                    </table>
                    <table class="table">
                        <tr v-for="(item, index) in goodsData.allocation_list" :key="'a' + index">
                            <td>{{item.shop_name}}</td>
                            <td>
                                <input :disabled="!isModify" :class="{'disabled': !isModify}"  type="number" v-selectTextOnFocus v-removeMouseWheelEvent @input="computeTotalAllocateingamount" @change="computeTotalAllocateingamount" min="0" v-model.number="item.allocated_amount">
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="footer">
                <template v-if="isModify === false">
                    <el-button type="text" @click="modify" icon="el-icon-edit">修改实配量</el-button>
                </template>
                <template v-if="isModify">
                    <el-button type="primary" :loading="btnLoading" @click="confirmModify">确认修改</el-button>
                    <el-button type="text" @click="cancelModify">取消修改</el-button>
                </template>
            </div>
        </div>
        <confirm-modal @click.native.stop ref="confirmModal"></confirm-modal>
    </div>
</transition>
</template>

<script>
import StickyListHeaders from 'sticky-list-headers'
import ConfirmModal from './confirm_modal'
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
            isModify: false,
            btnLoading: false,
            remarks: ''
        }
    },

    methods: {
        open(obj) {
            this.showDialog = true
            this.catchedData = obj
            this.goodsData = JSON.parse(JSON.stringify(obj.data))
            this.callback = obj.callback || function() {}
            this.isDistributionCar = obj.isDistributionCar
            this.init()
            console.log(obj)
            this.$nextTick(() => {
                new StickyListHeaders({
                    outerContainer: 'outerContainer',
                    innerContainer: 'innerContainer',
                    headers: ['table-header']
                })
            })
        },

        init() {
            this.isModify = false
            this.remarks = ''
            this.setTableOtherData()
            this.computeTotalAllocateingamount()
        },

        // 判断数据中是否有其他或者仓库的数据，没有的话就向数组中添加，有则不添加
        setTableOtherData() {
            // debugger
            this.goodsData.allocation_list.reduce((last, next) => {
                if ([1, 2].includes(next.destination)) {
                    last.splice(last.findIndex(value => value === next.destination), 1)
                }
                return last
            }, [1, 2]).forEach(value => {
                if (value === 1) {
                    this.goodsData.allocation_list.push({
                        shop_name: '待入库',
                        allocated_amount: 0,
                        destination: 1
                    })
                } else if (value === 2) {
                    this.goodsData.allocation_list.push({
                        shop_name: '其它',
                        allocated_amount: 0,
                        destination: 2
                    })
                }
            })
        },

        computeTotalAllocateingamount() {
            this.goodsData.allocated_amount = this.totalAllocateingamount = this.goodsData.allocation_list.reduce((last, next) => {
                last += (next.allocated_amount || 0)
                return last
            }, 0)
        },

        modify() {
            this.isModify = true
            this.cachedTableData = JSON.parse(JSON.stringify(this.goodsData.allocation_list))
        },

        cancelModify() {
            this.isModify = false
            this.goodsData.allocation_list = this.cachedTableData
        },

        confirmModify() {
            if (this.btnLoading) return
            if (+this.goodsData.allocated_amount !== +this.totalAllocateingamount) {
                return this.openMessage(2, '配货累计数量和到货量不一致')
            }
            this.btnLoading = true
            this.$fetch.put({
                url: '/allocationorder/' + this.goodsData.allocation_order_id,
                params: {
                    action: 'update_goods_list',
                    goods_list: this.goodsData.allocation_list.filter(value => {
                        return value.destination === 0
                    }),
                    amount_other_dest: getAllocatedAmount.call(this, 2),
                    amount_stock_in: getAllocatedAmount.call(this, 1)
                }
            }).then(data => {
                this.openMessage(1, '修改成功')
                this.isModify = false
            }).catch(e => {
                this.openMessage(0, e || '修改失败')
                this.cancelModify()
            }).finally(() => {
                this.btnLoading = false
            })

            // 仓库 1 其他 2
            function getAllocatedAmount(destination) {
                return this.goodsData.allocation_list.find(value => value.destination === destination).allocated_amount
            }
        },

        confirm() {
            this.$refs.confirmModal.open({
                data: this.goodsData,
                isDistributionCar: this.isDistributionCar,
                remarks: this.remarks,
                allocationOrderId: this.catchedData.data.allocation_order_id,
                callback: () => {
                    this.remarks = ''
                    this.showDialog = false
                }
            })
        }

        // confirmDistributionCar() {
        //     this.$fetch.put({
        //         url: '/allocationorder/' + this.catchedData.data.allocation_order_id,
        //         params: {
        //             action: 'confirm',
        //             remarks: this.remarks
        //         }
        //     }).then(() => {
        //         this.openMessage(1, '分车成功')
        //         this.print()
        //     }).catch(e => {
        //         this.openMessage(0, e)
        //     })
        // },

        // print() {
        //     this.$fetch.post({
        //         url: '/firmsettlementvoucher',
        //         params: {
        //             allocation_order_id: this.catchedData.data.allocation_order_id,
        //             remarks: this.remarks
        //         }
        //     }).then(() => {
        //         this.callback()
        //         this.showDialog = false
        //         this.remarks = ''
        //         this.openMessage(1, '打印成功')
        //     }).catch(e => {
        //         this.openMessage(0, e || '打印失败')
        //     })
        // }
    },

    components: {
        ConfirmModal
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
                // margin-right: 156px;
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
                position: absolute;
                right: 14px;
                font-size: 20px;
                cursor: pointer;
            }
        }

        #outerContainer {
            position: absolute;
            top: 56px;
            left: 0;
            right: 0;
            bottom: 60px;

            #innerContainer {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                overflow: auto;

                .disabled {
                    border: none;
                    background: transparent;
                }
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
                        width: 75px;
                    }

                    input {
                        padding-left: 10px;
                        width: 310px;
                        height: 30px;
                        background: #FFFFFF;
                        border: 1px solid;
                        border-color: #999999;
                        outline: none;
                        margin-bottom: 10px;

                        &:focus {
                            border-color: #009688;
                        }
                    }
                }

                .flex {
                    display: flex;

                    .p-2 {
                        margin-left: 28px;
                        color: #999999;
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

        .footer {
            position: absolute;
            height: 60px;
            bottom: 0;
            left: 0;
            right: 0;
            line-height: 60px;
            padding: 0 10px;
            border-top: 1px #999 solid;
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
