<template>
<transition name="slide-fade">
    <div class="distribution-staff-bg" v-if="showDialog" @click="showDialog = false">
        <div class="container" @click.stop>
            <div class="header">
                <h2>修改订货量</h2>
                <button @click="confirm">确认修改</button>
                <i class="el-icon el-icon-close" @click="showDialog = false"></i>
            </div>
            <div id="outerContainer">
                <div id="innerContainer">
                    <div class="order-info">
                        <p class="item"><span class="item-name">商品名：</span>{{goodsData.goods_name}}</p>
                        <p class="item" v-if="goodsData.purchaser_name"><span class="item-name">采购员：</span>{{goodsData.purchaser_name}}</p>
                    </div>
                    <table class="table table-header" id="table-header">
                        <tr>
                            <th>店铺</th>
                            <th>库存量</th>
                            <th>订货量</th>
                            <th>修改后的订货量</th>
                        </tr>
                        <tr>
                            <td>累计</td>
                            <td>{{sumData.total_stock}}</td>
                            <td>{{sumData.total_demand_amount}}</td>
                            <td>{{totalModifyOrderAmount}}</td>
                        </tr>
                    </table>
                    <table class="table">
                        <tr v-for="item in tableData" :key="item.shop_id">
                            <td>{{item.shop_name}}</td>
                            <td>{{item.current_storage}}</td>
                            <td>
                                <span v-if="item.modify_status">
                                    <span>{{item.modified_demand_amount}}</span>
                                    <del style="margin-left: 8px;color:#999">{{item.demand_amount}}</del>
                                </span>
                                <span v-else>
                                    <span>{{item.demand_amount}}</span>
                                </span>
                            </td>
                            <td>
                                <input type="number" v-removeMouseWheelEvent v-selectTextOnFocus v-model.number="item.modified_demand_amount">
                            </td>
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
export default {
    data() {
        return {
            showDialog: false,
            sumData: {},
            tableData: [],
            goodsData: {}
        }
    },

    computed: {
        totalModifyOrderAmount() {
            return this.tableData.reduce((last, next) => {
                last += (next.modified_demand_amount || 0)
                return last
            }, 0)
        }
    },
    mounted() {

    },

    methods: {
        open(obj) {
            this.showDialog = true
            this.cacheData = obj
            this.goodsData = obj.goodsData
            this.callback = obj.callback || function() {}
            console.log(obj)
            this.getOrdeGoodsShopList().then(() => {
                new StickyListHeaders({
                    outerContainer: 'outerContainer',
                    innerContainer: 'innerContainer',
                    headers: ['table-header']
                })
            })
        },

        getOrdeGoodsShopList() {
            return this.$fetch.get({
                url: '/demand/amount',
                params: {
                    wish_order_id: this.cacheData.wishOrderId,
                    goods_id: this.cacheData.goodsData.goods_id
                }
            }).then(data => {
                console.log(data)
                this.sumData = data.total_data_dict
                this.tableData = data.demand_goods_list
                this.setDefaultModifiedDemandAmount()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        setDefaultModifiedDemandAmount() {
            this.tableData = this.tableData.map(value => {
                if (!value.modified_demand_amount && value.modified_demand_amount !== 0) {
                    value.modified_demand_amount = value.demand_amount
                }

                return value
            })
        },

        confirm() {
            console.log(this.tableData)
            this.$fetch.put({
                url: '/demand/amount',
                params: {
                    wish_order_id: this.cacheData.wishOrderId,
                    goods_id: this.cacheData.goodsData.goods_id,
                    goods_demand_list: this.tableData.filter(value => {
                        if (value.modified_demand_amount || value.modified_demand_amount === 0) {
                            if (value.modified_demand_amount === value.demand_amount) {
                                return false
                            } else {
                                return true
                            }
                        } else {
                            return false
                        }
                    }).map(value => {
                        return {
                            "shop_id": value.shop_id,
                            "demand_order_goods_id": value.id || 0,
                            "modified_demand_amount": value.modified_demand_amount
                        }
                    })
                }
            }).then(data => {
                this.showDialog = false
                this.callback()
                this.openMessage(1, '修改成功')
            }).catch(e => {
                this.openMessage(0, e || '修改失败')
            })
        }
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
    z-index: 3001;

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

                .item {
                    font-size: 14px;
                    color: #333333;
                    letter-spacing: 0;
                    line-height: 30px;

                    .item-name {
                        display: inline-block;
                        width: 70px;
                    }

                    input {
                        padding-left: 10px;
                        width: 320px;
                        height: 30px;
                        background: #FFFFFF;
                        border: 1px solid;
                        border-color: #999999;
                        outline: none;

                        &:focus {
                            border-color: #009688;
                        }
                    }
                }

                .flex {
                    display: flex;

                    .p-2 {
                        margin-left: 10px;
                        color: #999999;
                    }
                }
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
                    width: 150px;
                }
                // th:nth-of-type(5),tr:nth-of-type(5),td:nth-of-type(5) {
                //     width: 80px;
                // }

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
    transition: all .5s ease;
}
.slide-fade-leave-active {
    transition: all .7s ease;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
    transform: translateX(100%);
    opacity: 0;
}

</style>
