<template>
<transition name="slide-fade">
    <div class="distribution-staff-bg" v-if="showDialog" @click="showDialog = false">

        <div class="container" @click.stop="closeFirmsContainer()">
            <div class="header">
                <h2>选择供货商</h2>
                <button :class="{'diabled': false}" @click="confirm">确认</button>
                <i class="el-icon el-icon-close" @click="showDialog = false"></i>
            </div>
            <div id="outerContainer">
                <div id="innerContainer">
                    <div class="order-info">
                        <h3>采购数据录入</h3>
                        <div class="item-group" v-for="(item, index) in form" :key="'a' + index">
                            <p class="item firm" @click.stop="openFirmsContainer(item, $event)">
                                <span>{{item.firm_name || '选择供货商'}}</span><img src="~@/assets/images/a19.png" alt="">
                            </p>
                            <p class="item">
                                <input type="number" v-selectTextOnFocus v-removeMouseWheelEvent v-model.number="item.price" min="0" placeholder="进货价"><span>元</span>
                            </p>
                            <p class="item">
                                <input type="number" v-selectTextOnFocus v-removeMouseWheelEvent v-model.number="item.actual_amount" min="0" placeholder="实采量"><span>件</span>
                            </p>
                            <p class="item">
                                <el-select v-model="item.payment" placeholder="请选择">
                                    <el-option
                                    v-for="item in payTypes"
                                    :key="item.id"
                                    :label="item.name"
                                    :value="item.id">
                                    </el-option>
                                </el-select>
                            </p>
                            <span class="result">小计：{{(item.price * item.actual_amount).toFixed(2) || 0}}</span>
                            <el-button @click="deleteThePurchaseData(item)" class="delete-btn" type="text" style="color: #f55">删除</el-button>
                        </div>
                        <button class="btn add-firm" @click="addFirm">+添加供货商</button>
                    </div>
                    <firms-list @click.native.stop ref="firmsContainer" :goodsData="goodsData"></firms-list>
                    <div class="goods-info">
                        <span>【{{goodsData.goods_name}}】一周购买记录</span>
                    </div>
                    <table class="table table-header" id="table-header">
                        <tr>
                            <th>日期</th>
                            <th>供货商</th>
                            <th>单价</th>
                            <th>数量</th>
                            <th>小计</th>
                        </tr>
                    </table>
                    <table class="table">
                        <tr v-if="tableData.length > 0" v-for="item in tableData" :key="item.id">
                            <td>{{item.date}}</td>
                            <td>{{item.firm_name}}</td>
                            <td>{{item.price}}</td>
                            <td>{{item.actual_amount}}</td>
                            <td>
                                {{item.subtotal}}
                            </td>
                        </tr>
                        <tr v-else>
                            <td colspan="5">暂无数据</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>

    </div>
</transition>
</template>

<script>
import StickyListHeaders from 'sticky-list-headers'
import FirmsList from './firms_list.vue'
import { payTypes } from '@/config/pay_types'
export default {
    data() {
        return {
            showDialog: false,
            payType: 0,
            payTypes: payTypes,
            form: [],
            tableData: [],
            goodsData: {}
        }
    },

    methods: {
        open(obj) {
            console.log(obj)
            this.showDialog = true
            this.goodsData = JSON.parse(JSON.stringify(obj.goodsData))
            this.callback = obj.callback || function() {}

            this.form = obj.goodsData.purchase_data.map(value => {
                let obj = {}
                obj.id = value.purchase_goods_id
                obj.firm_id = value.firm_id
                obj.price = value.price
                obj.firm_name = value.firm_name
                obj.actual_amount = value.purchased_amount
                obj.payment = value.payment
                obj.subtotal = value.subtotal
                obj._ID = value.purchase_goods_id
                return obj
            })

            this.getGoodsPurchaseData().then(() => {
                new StickyListHeaders({
                    outerContainer: 'outerContainer',
                    innerContainer: 'innerContainer',
                    headers: ['table-header']
                })
            })
        },

        getGoodsPurchaseData() {
            return this.$fetch.get({
                url: '/purchase/order/goods/' + this.goodsData.purchase_data[0].purchase_goods_id,
                params: {
                    action: 'week_purchase_record'
                }
            }).then(data => {
                this.tableData = data.purchase_goods_list
            }).catch(e => {
                this.openMessage(0, e || '获取最近采购数据失败')
            })
        },

        deleteThePurchaseData(item) {
            this.form.splice(this.form.findIndex(value => value._ID === item._ID), 1)
        },

        openFirmsContainer(item, event) {
            // this.isShowFirmsContainer = true
            const firmsContainer = this.$refs.firmsContainer
            const target = event.currentTarget
            let top = target.offsetTop + target.offsetHeight
            firmsContainer.open({
                data: item,
                choosedList: this.form.map(value => value.firm_id),
                callback: (firmData) => {
                    console.log(firmData)
                    item.firm_id = firmData.id
                    item.firm_name = firmData.name
                }
            })
            this.$nextTick(() => {
                firmsContainer.$el.style.top = top - 1 + 'px'
            })
        },

        closeFirmsContainer() {
            this.$refs.firmsContainer.close()
        },

        addFirm() {
            this.form.push({
                "id": 0,
                "firm_id": '',
                "firm_name": '',
                "price": '',
                "actual_amount": '',
                "payment": 0,
                "subtotal": '',
                _ID: Date.now()
            })
        },

        confirm() {
            this.validator().then(() => {
                this.$fetch.put({
                    url: '/purchase/order/goods/' + this.goodsData.purchase_data[0].purchase_goods_id,
                    params: {
                        action: 'batch_entering',
                        purchase_goods_list: this.form.map(value => {
                            value.subtotal = value.price * value.actual_amount
                            return value
                        })
                    }
                }).then(data => {
                    this.openMessage(1, '添加采购数据成功')
                    this.showDialog = false
                    this.callback()
                }).catch(e => {
                    this.openMessage(0, e || '添加采购数据失败')
                })
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        validator() {
            const validator = new this.$Validator()
            this.form.forEach(value => {
                validator.add('isEmpty', value.firm_id, '请选择供应商')
                validator.add('isEmpty', value.price, '请输入进货价')
                validator.add('isEmpty', value.actual_amount, '请输入实采量')
            })

            return validator.start()
        }
    },
    components: {
        FirmsList
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
        width: 680px;
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
                margin-right: 430px;
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
            bottom: 0;

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
                h3 {
                    font-size: 14px;
                    color: #333333;
                    font-weight: bold;
                }
                .item-group {
                    margin-top: 10px;

                    .item {
                        display: inline-flex;
                        vertical-align: middle;
                        align-items: center;
                        justify-content: space-between;
                        padding: 8px;

                        width: 120px;
                        height: 50px;
                        border-radius: 2px;
                        border: 1px solid #DDDDDD;
                        user-select: none;

                        & + .item {
                            margin-left: 8px;
                        }

                        input {
                            width: 84px;
                            font-size: 14px;
                            border: none !important;
                        }

                        span {
                            font-size: 14px;
                            color: #333333;
                        }

                        /deep/ .is-focus .el-input__inner {
                            border: none !important;
                        }

                        /deep/ .el-input__inner {
                            border: none !important;
                        }
                    }

                    .firm {
                        background: #00968822;
                        border: 1px solid #00968822;
                        cursor: pointer;
                    }

                    .result {
                        margin-left: 8px;
                        font-size: 14px;
                        color: #333;
                    }

                    .delete-btn {
                        padding: 0;
                        float: right;
                        line-height: 50px;
                    }
                }

                .add-firm {
                    margin-top: 10px;
                    background: #F9F9F9;
                    border-radius: 2px;
                    font-size: 14px;
                    color: #333333;
                }
            }

            .goods-info {
                margin: 10px 0;
                font-size: 14px;
                color: #333333;
            }

            .table {
                width: 100%;
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
