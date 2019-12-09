// 分店采购意向单
<template>
<div class="container">
    <div class="header-container">
        <img src="https://static.ls.senguo.cc/static/official/img/head_logo_active.png?v=b0f9bbe641bde586e1405dfc11f6a604" alt="">
        <div class="center">
            <h1>{{wishOrderData.wish_date && wishOrderData.wish_date.replace(/-/g, '.')}}采购意向单</h1>
            <p>店铺：{{currentShop.name || currentShop.abbreviation}}&nbsp;({{currentShop.station_name}})<shop-select @shopChanged="shopChanging = false" @beforeShopChang="shopChanging = true">&nbsp;<span class="change-shop-btn">切换</span></shop-select>&nbsp;|&nbsp;订货人：{{userInfo.realname || userInfo.nickname}}&nbsp;|&nbsp;状态：<!--
            --><span v-if="[3, 4].includes(demandOrderData.wish_order_status)">
                    <span v-if="demandOrderData.status == 1">已拒绝</span>
                    <span v-else><i class="el-icon el-icon-check"></i>已确认</span>
                </span>
                <span v-else>
                    <span v-if="demandOrderData.status != 0">待确认</span>
                    <span v-else>未提交</span>
                </span>
            </p>
        </div>
        <div class="right">
            <div class="total">
                <p>总体积：{{volumeTotal}}m³</p>
                <p>总重量：{{weightTotal}}kg</p>
                <p>订货总量: {{demandTotal}}</p>
            </div>
            <span v-if="[3, 4].includes(demandOrderData.wish_order_status)">
                <button @click="openMessage(2, '订货单已确认，不可修改')" class="btn disbled">点击修改</button>
            </span>
            <span v-else>
                <button v-if="demandOrderData.status == 0 || ismodify" @click="confirm" class="btn confirm">提交订货单</button>
                <button class="btn disbled" @click="ismodify = true" v-else-if="!ismodify">点击修改</button>
                <button class="btn disbled" v-if="demandOrderData.negative_order === 0" @click="changeOrderStatus(1)">今日不订货</button>
                <button class="btn disbled" v-if="demandOrderData.negative_order === 1" @click="changeOrderStatus(0)">今日订货</button>
            </span>
        </div>
    </div>
    <div class="main">
        <table class="header">
            <tr>
                <th class="t0">序号</th>
                <th class="t1">商品名</th>
                <th class="t2">意向单说明</th>
                <th class="t3">分店库存</th>
                <th class="t4">订货量</th>
                <th class="t5">订货备注</th>
            </tr>
        </table>
        <div class="outer-container" ref="outerContainer">
            <div class="inner-container" ref="innerContainer">
                <div class="title" ref="header1">
                    正常订货商品(订货量：{{status0DemandTotal}})
                </div>
                <table>
                    <tr v-for="(item, index) in tableData" :class="{'focus-line': index === +nowInputAt.split(':')[0]}" :key="item.goods_id" v-if="item._status == 0">
                        <td class="t0">{{index}}</td>
                        <td class="t1">
                            <span :style="[{'color': item.order_goods_name_modified ? '#f00':''}]">{{ item.goods_name }}</span>
                        </td>
                        <td class="t2">{{item._remarks}}</td>
                        <td class="t3"><input :ref="getRef(item, index, 1)" :data-ref="getRef(item, index, 1)" type="number" @focus="inputFocus($event)" v-removeMouseWheelEvent v-selectTextOnFocus :disabled="demandOrderData.status != 0 && !ismodify" class="input" v-model="item.current_storage"></td>
                        <td class="t4"><input :ref="getRef(item, index, 2)" :data-ref="getRef(item, index, 2)" type="number" @focus="inputFocus($event)" v-removeMouseWheelEvent v-selectTextOnFocus :disabled="demandOrderData.status != 0 && !ismodify" class="input" v-model="item.demand_amount" placeholder="单行输入"></td>
                        <td class="t5"><input :ref="getRef(item, index, 3)" :data-ref="getRef(item, index, 3)" @focus="inputFocus($event)" :disabled="demandOrderData.status != 0 && !ismodify" v-model="item.remarks" maxlength="120" class="input" type="text" placeholder="单行输入"></td>
                    </tr>
                </table>
                <div class="title" ref="header2">
                    可能缺货商品(订货量：{{status1DemandTotal}})
                </div>
                <table>
                    <tr v-for="(item, index) in tableData" :class="{'focus-line': index === +nowInputAt.split(':')[0]}" :key="item.goods_id" v-if="item._status == 1">
                        <td class="t0">{{index}}</td>
                        <td class="t1">
                            <span :style="[{'color': item.order_goods_name_modified ? '#f00':''}]">{{ item.goods_name }}</span>
                        </td>
                        <td class="t2">{{item._remarks}}</td>
                        <td class="t3"><input :ref="getRef(item, index, 1)" :data-ref="getRef(item, index, 1)" type="number" @focus="inputFocus($event)" v-removeMouseWheelEvent v-selectTextOnFocus :disabled="demandOrderData.status != 0 && !ismodify" class="input" v-model="item.current_storage"></td>
                        <td class="t4"><input :ref="getRef(item, index, 2)" :data-ref="getRef(item, index, 2)" type="number" @focus="inputFocus($event)" v-removeMouseWheelEvent v-selectTextOnFocus :disabled="demandOrderData.status != 0 && !ismodify" class="input" v-model="item.demand_amount" placeholder="单行输入"></td>
                        <td class="t5"><input :ref="getRef(item, index, 3)" :data-ref="getRef(item, index, 3)" @focus="inputFocus($event)" :disabled="demandOrderData.status != 0 && !ismodify" v-model="item.remarks" maxlength="120" class="input" type="text" placeholder="单行输入"></td>
                    </tr>
                </table>
                <div class="title" ref="header3">
                    暂时无货商品(订货量：{{status2DemandTotal}})
                </div>
                <table>
                    <tr v-for="(item, index) in tableData" :class="{'focus-line': index === +nowInputAt.split(':')[0]}" :key="item.goods_id" v-if="item._status == 2">
                        <td class="t0">{{index}}</td>
                        <td class="t1">
                            <span :style="[{'color': item.order_goods_name_modified ? '#f00':''}]">{{ item.goods_name }}</span>
                        </td>
                        <td class="t2">{{item._remarks}}</td>
                        <td class="t3"><input :ref="getRef(item, index, 1)" :data-ref="getRef(item, index, 1)" type="number" @focus="inputFocus($event)" v-removeMouseWheelEvent v-selectTextOnFocus :disabled="demandOrderData.status != 0 && !ismodify" class="input" v-model="item.current_storage"></td>
                        <td class="t4"><input :ref="getRef(item, index, 2)" :data-ref="getRef(item, index, 2)" type="number" @focus="inputFocus($event)" v-removeMouseWheelEvent v-selectTextOnFocus :disabled="demandOrderData.status != 0 && !ismodify" class="input" v-model="item.demand_amount" placeholder="单行输入"></td>
                        <td class="t5"><input :ref="getRef(item, index, 3)" :data-ref="getRef(item, index, 3)" @focus="inputFocus($event)" :disabled="demandOrderData.status != 0 && !ismodify" v-model="item.remarks" maxlength="120" class="input" type="text" placeholder="单行输入"></td>
                    </tr>
                </table>
            </div>
        </div>
        <div class="footer">
            <h2>今日已订货({{orderStoreList.length}})</h2>
            <div class="shops" @click="showOrderStores">
                <el-tooltip v-for="(item, index) in orderStoreList" :key="item.shop_id" v-if="index < 10" class="item" effect="dark" :content="item.shop" placement="top">
                    <img :src="item.headimgurl" />
                </el-tooltip>
                <span v-if="orderStoreList.length > 10">+{{orderStoreList.length - 10}}</span>
            </div>
        </div>
    </div>
    <order-stores ref="orderStores" :orderStoreList="orderStoreList"></order-stores>
</div>
</template>

<script>
import StickyListHeaders from 'sticky-list-headers'
import OrderStores from './components/order_stores'
import ShopSelect from '../../components/shop_select'
import INDENT_MIXIN from '../../mixin/indent'
export default {
    mixins: [INDENT_MIXIN],

    data() {
        return {
            nowInputAt: '-1:-1',
            shopChanging: false
        }
    },

    watch: {
        'currentShop': function(newVal, oldVal) {
            if (newVal.id !== oldVal.id) {
                // 代码在mixin里，移动端和pc用的同一个mixin函数，不要随意修改
                this.init().then(() => {
                    this.stickyListHeaders = new StickyListHeaders({
                        outerContainer: this.$refs.outerContainer,
                        innerContainer: this.$refs.innerContainer,
                        headers: [this.$refs.header1, this.$refs.header2, this.$refs.header3]
                    })
                }).catch(e => {
                    console.log(e)
                    this.openMessage(0, '获取数据失败,' + e)
                })
            }
        }
    },

    created() {
        // this.wishOrderId = this.$route.query.wishOrderId

        window.addEventListener('keydown', this.keydown)
    },

    beforeDestroy() {
        window.removeEventListener('keydown', this.keydown)
    },

    methods: {
        // getDemandAmount(status) {
        //     return this.tableData.filter(value => value._status === status).reduce((last, next) => {
        //         return +last + (+next.demand_amount || 0)
        //     }, 0)
        // },

        getRef(item, row, column) {
            return row + ':' + column
        },

        keydown(event) {
            // 上 38
            // 下 40
            // 左 37
            // 右 39
            // 回车 13
            this.cacheUserInput()

            let [row, column] = [...this.nowInputAt.split(':').map(value => parseInt(value))]
            let pos = {
                row,
                column
            }
            if ([38, 40, 37, 39, 13].includes(event.keyCode)) {
                event.preventDefault()
            }

            function up() {
                if (pos.row === 0) return
                pos.row -= 1
            }

            function down() {
                if (pos.row === this.tableData.length - 1) return
                pos.row += 1
            }

            function left() {
                if (pos.row === 0 && pos.column === 1) return
                if (pos.column === 1) {
                    pos.row -= 1
                    pos.column = 3
                } else {
                    pos.column -= 1
                }
            }

            function right() {
                if (pos.row === this.tableData.length - 1 && pos.column === 3) return
                if (pos.column === 3) {
                    pos.row += 1
                    pos.column = 1
                } else {
                    pos.column += 1
                }
            }

            switch (event.keyCode) {
                case 38: up.call(this); break
                case 40: down.call(this); break
                case 37: left.call(this); break
                case 39: right.call(this); break
                case 13: right.call(this); break
            }
            this.nowInputAt = pos.row + ':' + pos.column
            this.$refs[pos.row + ':' + pos.column] && this.$refs[pos.row + ':' + pos.column][0] && this.$refs[pos.row + ':' + pos.column][0].focus()
        },

        inputFocus(e) {
            this.nowInputAt = e.target.getAttribute('data-ref')
        },

        showOrderStores() {
            this.$refs.orderStores.open()
        },

        changeOrderStatus(status) {
            this.$myWarning({
                message: '确认修改订货状态吗？'
            }).then(() => {
                this.$fetch.put({
                    url: '/shop/demandorder/' + this.demandOrderId,
                    params: {
                        action: 'update_dorder_negative_status',
                        negative_order: status
                    }
                }).then(data => {
                    this.demandOrderData.negative_order = status === 0 ? 0 : 1
                    this.openMessage(1, '修改订货单状态成功')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            })
        },

        confirm() {
            // console.log(this.tableData)
            if (this.shopChanging) return
            if (this.wishOrderData.status !== 2) {
                return this.openMessage(2, '该意向单暂未开放下单')
            }
            this.$fetch.put({
                url: '/shop/demandorder/' + this.demandOrderId,
                params: {
                    goods_list: this.tableData.map(value => {
                        let obj = {}
                        obj.id = value.id
                        obj.current_storage = value.current_storage
                        obj.demand_amount = value.demand_amount
                        obj.demand_remarks = value.remarks

                        return obj
                    }),
                    shop_id: this.currentShop.id
                }
            }).then(data => {
                this.ismodify = false
                this.nowInputAt = '-1:-1'
                this.init().then(() => {
                    this.stickyListHeaders.refresh()
                })
                this.openMessage(1, '提交成功')
            }).catch(e => {
                this.openMessage(0, '提交失败,' + e)
            })
        }
    },

    components: {
        ShopSelect,
        OrderStores
    }
}
</script>

<style lang="scss" scoped>
.container {
    position: relative;
    margin: 0 92px;
    height: 100%;
    background: #fff;
}
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 83px;

    img {
        margin-left: 15px;
        width: 100px;
    }

    .center {
        h1 {
            text-align: center;
            font-size: 20px;
            color: #333333;
        }

        p {
            margin-top: 5px;
            font-size: 14px;
            color: #333333;
        }

        .change-shop-btn {
            color: #009688;
            cursor: pointer;
        }
    }

    .right {
        position: relative;

        .total {
            // position: absolute;
            // right: 94px;
            // top: -5px;
            display: inline-block;
            vertical-align: middle;
            white-space: nowrap;

            p {
                line-height: 16px;
                font-size: 12px;
                color: #333;
            }
        }

        span {
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
            line-height: 30px;
        }

        button {
            margin-left: 15px;
            white-space: nowrap;
        }
    }
}

.main {
    .outer-container {
        position: absolute;
        top: 125px;
        bottom: 120px;
        left: 0;
        right: 0;
        border-bottom: 1px #F2F2F2 solid;
        // box-shadow: 0px 5px 20px -9px rgba(0, 0, 0, 0.3);
    }

    @mixin tableColumnStyle {
        td, th {
            // box-sizing: border-box;
            padding: 0px 10px;
            height: 40px;
            line-height: 40px;
        }

        th,td {
            text-align: left;
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
        }
        .t0 {
            max-width: 70px;
            min-width: 70px;
        }

        .t1 {
            min-width: 331px;
            max-width: 331px;
            word-break: break-all;
        }

        .t2 {
            min-width: 212px;
            word-break: break-all;
        }

        .t3 {
            width: 144px;
        }

        .t4 {
            width: 144px;
        }

        .t5 {
            width: 258px;
        }
    }

    .inner-container::-webkit-scrollbar {display:none}
    .inner-container {
        height: 100%;
        width: 100%;
        overflow: auto;

        .title {
            padding-left: 10px;
            height: 40px;
            line-height: 40px;
            border: 1px solid #F2F2F2;
            font-size: 16px;
            color: #333333;
            letter-spacing: 0;
            background: #fff;
            z-index: 1;
            font-weight: bold;
        }

        .tag {
            display: inline-block;
            vertical-align: middle;
            width: 40px;
            height: 21px;
            margin-right: 6px;
            line-height: 19px;
            text-align: center;
            background: #FFFFFF;
            border-radius: 2px;
            font-size: 12px;
            color: #F88B30;
            letter-spacing: 0;
            border: 1px #F88B30 solid;
        }

        table {
            width: 100%;
            td {
                height: 40px;
                border: 1px solid #F2F2F2;
            }

            .focus-line {
                background: #00968833 !important;
            }

            tr:hover {
                background: #f5f7fa;
            }

            @include tableColumnStyle;
        }
    }

    table.header {
        width: 100%;
        background: #F2F2F2;
        border: 1px solid #F2F2F2;

        @include tableColumnStyle;

        tr {
            height: 40px;
        }
    }

    td {
        position: relative;
    }

    .footer {
        position: absolute;
        bottom: 0;
        height: 120px;

        h2 {
            margin-top: 20px;
            font-size: 20px;
            color: #419688;
        }

        .shops {
            display: inline-block;
            margin-top: 10px;
            padding: 5px 9px;
            background: #F4F4F4;
            border-radius: 4px;
            cursor: pointer;

            .item + .item {
                margin-left: 9px;
            }

            img {
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: #D8D8D8;
            }

            span {
                margin-left: 9px;
                vertical-align: text-top;
                font-size: 14px;
                color: #333333;
            }
        }
    }
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
}
input[type="number"]{
    -moz-appearance: textfield;
}

.input {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 0 10px;
    height: 100%;
    width: 100%;
    border: none;
    outline: none;
    appearance: none;
    font-size: 14px;
    background: transparent;
}

.input[disabled] {
    background: transparent;
}

.button-group {
    margin-top: 208px;
    text-align: center;
    height: 67px;
    line-height: 67px;
}

.btn {
    box-sizing: border-box;
    padding: 8px 10px;
    font-size: 14px;
    border-radius: 2px;
    outline: none;
    border: none;
    line-height: initial;
    user-select: none;

    &:active {
        transform: scale(.9);
    }
}

.confirm {
    margin-left: 15px;
    background: #009688;
    color: #fff;
}

.disbled {
    background: #E7E7E7;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    font-size: 14px;
    color: #666666;
}

.share {
    margin-left: 20px;
    color: #009688;
    border: 1px solid #009688;
    border-radius: 2px;
}

.status {
    font-size: 16px;
    color: #999999;
    user-select: none;

    i {
        margin-right: 6px;
        font-size: 18px;
    }
}

.confirmed {
    color: #009688;
    margin-left: 20px;
}

.reject {
    color: #FF6666;
    margin-left: 20px;
}

.text-btn {
    margin-left: 20px;
    color: #009688;
    text-decoration: underline;
    text-underline-position: under;
}

</style>
