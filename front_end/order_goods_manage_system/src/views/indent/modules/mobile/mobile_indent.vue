<template>
    <div class="mobile-indent-container">
        <div class="header">
            <h1>{{wishOrderData.wish_date}}采购意向单</h1>
            <p>
                <span><img src="~@/assets/images/a15.png" alt=""><span>{{currentShop.name || currentShop.abbreviation}}({{currentShop.station_name}})</span></span>
                <span><img src="~@/assets/images/a16.png" alt=""><span>{{userInfo.realname || userInfo.nickname}}</span></span>
            </p>
            <shop-select @shopChanged="shopChanging = false" @beforeShopChang="shopChanging = true" class="change-shop">切换店铺</shop-select>
        </div>
        <div id="outer-container">
        <div class="content" id="inner-container">
            <div class="title" id="header1">
                <p><i class="color-009688"></i>正常订货商品</p>
                <p class="title-p-2">
                    <span class="title-p-2__1">分店库存</span>
                    <span class="title-p-2__2">订货量({{status0DemandTotal}})</span>
                </p>
            </div>
            <ul class="goods-list">
                <li @click="editRemark(item)" class="goods-list-item" v-if="item._status == 0" v-for="(item, index) in tableData" :key="item.id">
                    <span v-if="item.remarks" class="remark-tag">注</span>
                    <div class="detail-wrapper">
                        <p class="index">{{index + 1}}</p>
                        <p class="detail">
                            <span class="name" :style="[{'color': item.order_goods_name_modified ? '#f00':''}]">{{ item.goods_name }}</span>
                            <!-- <span class="name">{{item.goods_name}}</span> -->
                            <span class="remark">{{item._remarks}}</span>
                        </p>
                    </div>
                    <p class="amount" v-if="item.demand_amount || item.current_storage" @click.stop="modify(item)">
                        <span>{{item.current_storage}}</span>
                        <span>{{item.demand_amount}}</span>
                    </p>
                    <button class="btn-insert" v-else @click.stop="modify(item)">数据录入</button>
                </li>
            </ul>
            <div class="title" id="header2">
                <p><i class="color-FF7C56"></i>可能缺货商品</p>
                <p class="title-p-2">
                    <span class="title-p-2__1">分店库存</span>
                    <span class="title-p-2__2">订货量({{status1DemandTotal}})</span>
                </p>
            </div>
            <ul class="goods-list">
                <li @click="editRemark(item)" class="goods-list-item" v-if="item._status == 1" v-for="(item, index) in tableData" :key="item.id">
                    <span v-if="item.remarks" class="remark-tag">注</span>
                    <div class="detail-wrapper">
                        <p class="index">{{index + 1}}</p>
                        <p class="detail">
                            <span class="name" :style="[{'color': item.order_goods_name_modified ? '#f00':''}]">{{ item.goods_name }}</span>
                            <!-- <span class="name">{{item.goods_name}}</span> -->
                            <span class="remark">{{item._remarks}}</span>
                        </p>
                    </div>
                    <p class="amount" v-if="item.demand_amount || item.current_storage" @click.stop="modify(item)">
                        <span>{{item.current_storage}}</span>
                        <span>{{item.demand_amount}}</span>
                    </p>
                    <button class="btn-insert" v-else @click.stop="modify(item)">数据录入</button>
                </li>
            </ul>
            <div class="title" id="header3">
                <p><i class="color-999999"></i>暂时无货商品</p>
                <p class="title-p-2">
                    <span class="title-p-2__1">分店库存</span>
                    <span class="title-p-2__2">订货量({{status2DemandTotal}})</span>
                </p>
            </div>
            <ul class="goods-list">
                <li @click="editRemark(item)" class="goods-list-item" v-if="item._status == 2" v-for="(item, index) in tableData" :key="item.id">
                    <span v-if="item.remarks" class="remark-tag">注</span>
                    <div class="detail-wrapper">
                        <p class="index">{{index + 1}}</p>
                        <p class="detail">
                            <span class="name" :style="[{'color': item.order_goods_name_modified ? '#f00':''}]">{{ item.goods_name }}</span>
                            <!-- <span class="name">{{item.goods_name}}</span> -->
                            <span class="remark">{{item._remarks}}</span>
                        </p>
                    </div>
                    <p class="amount" v-if="item.demand_amount || item.current_storage" @click.stop="modify(item)">
                        <span>{{item.current_storage}}</span>
                        <span>{{item.demand_amount}}</span>
                    </p>
                    <button class="btn-insert" v-else @click.stop="modify(item)">数据录入</button>
                </li>
            </ul>
            <p class="no-more">没有更多商品了～</p>
        </div>
        </div>
        <div class="order-stores-container" @click="showOrderStores">
            <span>今日已订货({{orderStoreList.length}})：</span><div>
                <img class="avatar" v-for="(item, index) in orderStoreList" :key="item.shop_id" v-if="index < 8" :src="item.headimgurl" alt=""><img class="arrow" src="~@/assets/images/a22.png" alt="">
            </div>
        </div>
        <div class="footer">
            <div class="left">
                <p>
                    <span>{{demandTotal}}</span>
                    <span>总订货量</span>
                </p>
                <p>
                    <span>{{volumeTotal}}m³</span>
                    <span>总体积</span>
                </p>
                <p>
                    <span>{{weightTotal}}kg</span>
                    <span>总重量</span>
                </p>
                <!-- <p class="status">
                    <span v-if="[1, 2].includes(demandOrderData.wish_order_status)">
                        <span v-if="demandOrderData.status == 0">未提交</span>
                        <span v-else>待确认</span>
                    </span>
                    <span v-else>
                        <span v-if="demandOrderData.status == 1" style="color: #FF6666">已拒绝</span>
                        <span v-else style="color: #009688">已确认</span>
                    </span>

                    <span>订货单状态</span>
                </p> -->

            </div>
            <span class="right">
                <!-- <button class="primary">今日不订货</button> -->
                <button class="primary" v-if="demandOrderData.negative_order === 0" @click="changeOrderStatus(1)">今日不订货</button>
                <button class="primary" v-if="demandOrderData.negative_order === 1" @click="changeOrderStatus(0)">今日订货</button>
            </span>
            <span class="right" v-if="[1, 2].includes(demandOrderData.wish_order_status)">
                <!-- 0 未提交 1 已提交 2 已被汇总 -->
                <button class="submit" @click="submit" v-if="demandOrderData.status == 0">提交订货单</button>
                <button class="modify" @click="isModify = true" v-else-if="!isModify">点击修改</button>
                <button class="submit" @click="submit" v-else-if="isModify">提交修改</button>
            </span>
            <span class="right" v-else>
                <button @click="$myToast.show('订货单已确认，无法修改')" class="modify">已确认</button>
            </span>

        </div>
        <edit-remark ref="editRemark"></edit-remark>
        <edit-quantity ref="editQuantity"></edit-quantity>
        <order-stores ref="orderStores" :orderStoreList="orderStoreList"></order-stores>
    </div>
</template>

<script>
import INDENT_MIXIN from '../../mixin/indent'
import EditRemark from './components/edit_remarks'
import EditQuantity from './components/edit_quantity'
import ShopSelect from '../../components/shop_select'
import OrderStores from './components/order_stores'
// import StickyListHeaders from 'sticky-list-headers'
export default {
    mixins: [INDENT_MIXIN],
    data() {
        return {
            isModify: false,
            shopChanging: false
        }
    },

    computed: {
        total() {
            return this.tableData.reduce((last, next) => {
                last += (next.demand_amount || 0)
                return last
            }, 0)
        },

        isOrderFinished() {
            return [3, 4].includes(this.demandOrderData.wish_order_status)
        }
    },

    watch: {
        'currentShop': function(newVal, oldVal) {
            if (newVal.id !== oldVal.id) {
                // 代码在mixin里，移动端和pc用的同一个mixin函数，不要随意修改
                this.init().then(() => {

                }).catch(e => {
                    console.log(e)
                    this.$myToast.show(e || '获取数据失败')
                })
            }
        }
    },

    mounted() {
        // this.stationId = this.$route.query.stationId
        // this.wishOrderId = this.$route.query.wishOrderId
    },

    methods: {
        modify(row) {
            if (this.isOrderFinished) return this.$myToast.show('意向单已截止订货')
            if (this.demandOrderData.status !== 0 && this.isModify === false) {
                this.$myMWarning({
                    message: '确认要修改吗？'
                }).then(() => {
                    this.isModify = true
                    open.call(this)
                })
            } else {
                open.call(this)
            }
            function open() {
                this.$refs.editQuantity.open({
                    data: row,
                    allGoods: this.tableData,
                    demandOrderId: this.demandOrderId,
                    callback: (obj) => {
                        row.current_storage = obj.current_storage
                        row.demand_amount = obj.demand_amount
                    }
                })
            }
        },

        showOrderStores() {
            this.$refs.orderStores.open()
        },

        editRemark(data) {
            if (this.isOrderFinished) return this.$myToast.show('意向单已截止订货')
            if (this.demandOrderData.status !== 0 && this.isModify === false) {
                this.$myMWarning({
                    message: '确认要修改吗？'
                }).then(() => {
                    this.isModify = true
                    open.call(this)
                })
            } else {
                open.call(this)
            }

            function open() {
                this.$refs.editRemark.open({
                    data: data,
                    callback: (remarks) => {
                        // data.remarks = remarks
                        this.$set(data, 'remarks', remarks)
                        this.cacheUserInput()
                    }
                })
            }
        },

        changeOrderStatus(status) {
            this.$myMWarning({
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
                    this.$myToast.show('修改订货单状态成功')
                }).catch(e => {
                    this.$myToast.show(e)
                })
            })
        },

        submit() {
            // console.log(this.tableData)
            if (this.shopChanging) return
            if (this.wishOrderData.status !== 2) {
                return this.$myToast.show('该意向单暂未开放下单')
            }
            this.$myMWarning({
                message: '确定要提交吗？'
            }).then(() => {
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
                    this.isModify = false
                    this.init()
                    this.$myToast.show('提交成功')
                }).catch(e => {
                    this.$myToast.show('提交失败')
                    // this.openMessage(0, '提交失败,' + e)
                })
            }).catch(e => {})
        }
    },

    components: {
        EditRemark,
        EditQuantity,
        ShopSelect,
        OrderStores
    }
}
</script>

<style lang="scss" scoped>
.mobile-indent-container {
    background: #f9f9f9;
    .header {
        position: fixed;
        left: 0;
        right: 0;
        height: 57px;
        // line-height: 57px;
        background-image: linear-gradient(-135deg, #009688 0%, #58D0A6 100%);
        // transform: translateZ(2px);
        z-index: 999;
        h1 {
            padding-left: 12px;
            font-size: 20px;
            line-height: 40px;
            color: #FFFFFF;
            text-align: left;
        }

        p {

            >span {
                display: inline-flex;
                align-items: center;
                margin-left: 12px;
                white-space: nowrap;

                img {
                    margin-right: 4px;
                    height: 12px;
                }
            }

            font-size: 12px;
            color: #fff;
        }

        .change-shop {
            position: absolute;
            top: 12px;
            right: 10px;
            width: 76px;
            height: 30px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 100px;
            font-size: 14px;
            color: #009688;
            letter-spacing: 0;
            text-align: center;
            line-height: 30px;
        }
    }

    #outer-container {
        position: absolute;
        top: 57px;
        bottom: 90px;
        left: 0;
        right: 0;
    }

    .title {
            position: sticky;
            top: 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px;
            height: 36px;
            font-size: 12px;
            color: #999999;
            border-top: 1px #EFF2F4 solid;
            border-bottom: 1px #EFF2F4 solid;
            background: #f9f9f9;
            z-index: 100;

            i {
                display: inline-block;
                margin-right: 5px;
                height: 10px;
                width: 10px;
                border-radius: 50%;
            }

            .color-009688 {
                background: #009688;
            }

            .color-FF7C56 {
                background: #FF7C56;
            }

            .color-999999 {
                background: #999999;
            }

            .title-p-2__1 {
                margin-right: 26px;
            }

            .title-p-2__2 {
                margin-right: 10px;
            }
        }

    #inner-container::-webkit-scrollbar {display:none}

    #inner-container {
        // position: absolute;
        // top: 0px;
        // bottom: 0px;
        // left: 0;
        // right: 0;
        height: 100%;
        width: 100%;
        overflow: auto;
        -webkit-overflow-scrolling: touch;

        .goods-list {
            background: #fff;
            // width: 100%;
            .goods-list-item {
                position: relative;
                padding: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                height: 52px;

                &+.goods-list-item {
                    border-top: 1px #EFF2F4 solid;
                }

                .remark-tag {
                    position: absolute;
                    top: 5px;
                    left: 0;
                    // padding: 2px;
                    font-size: 12px;
                    height: 16px;
                    line-height: 16px;
                    width: 20px;
                    text-align: center;
                    background: #f5c168;
                    color: #fff;
                    transform: translate3D(-2px , -2px, 0) scale(.8);
                    border-top-right-radius: 9px;
                    border-bottom-right-radius: 9px;
                }

                .detail-wrapper {
                    display: flex;
                    align-items: center;
                    flex: 1;
                    width: 0;
                    // overflow: hidden；
                }

                .index {
                    margin-right: 20px;
                    font-size: 12px;
                    color: #9F9F9F;
                }

                .detail {
                    display: flex;
                    flex-direction: column;
                    // min-width: 200px;
                    width: 80%;
                    // overflow: hidden;

                    span {
                        width: 100%;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }

                    .name {
                        font-size: 14px;
                        color: #333333;
                        line-height: 16px;
                    }
                    .remark {
                        font-size: 12px;
                        color: #FF6666;
                        line-height: 16px;
                    }
                }

                .amount {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    // margin-right: 10px;
                    padding: 10px;
                    height: 32px;
                    min-width: 120px;
                    background: #FFFFFF;
                    border: 1px solid #999999;
                    border-radius: 100px;

                    span {
                        font-size: 14px;
                        color: #333333;
                        line-height: 16px;
                    }
                }

                .btn-insert {
                    width: 120px;
                    height: 32px;
                    background: #FFFFFF;
                    border: 1px solid #009688;
                    border-radius: 100px;
                    font-size: 14px;
                    color: #009688;
                    line-height: 16px;
                }
            }
        }

        .no-more {
            margin-top: 11px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 12px;
            color: #999999;
            line-height: 16px;
        }
    }

    .order-stores-container {
        position: absolute;
        display: flex;
        align-items: center;
        height: 40px;
        width: 100%;
        bottom: 50px;
        background: #F4F4F4;

        white-space: nowrap;

        > span {
            font-size: 12px;
            color: #333333;
            margin-right: 4px;
            margin-left: 12px;
        }

        .avatar {
            height: 16px;
            width: 16px;
            border-radius: 50%;
            background: #D8D8D8;

            & + .avatar {
                margin-left: 4px;
            }
        }

        .arrow {
            height: 14px;
            margin-left: 4px;
        }
    }

    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 50px;
        background: #FFFFFF;
        // box-shadow: 0 -1px 2px 0 #D4D4D4;
        // transform: translateZ(2px);

        .left {
            // margin-left: 10px;
            display: flex;
            flex-grow: 1;
            align-items: center;
            justify-content: space-around;

            p {
                display: flex;
                flex-direction: column;
                justify-content: center;
                text-align: center;

                span:nth-of-type(1) {
                    font-size: 14px;
                    color: #333333;
                    line-height: 16px;
                }

                span:nth-of-type(2) {
                    font-size: 12px;
                    color: #9B9B9B;
                    line-height: 16px;
                }
            }

            // .status {
            //     margin-left: 40px;
            // }

            > button {
                display: block;
                height: 100%;
                width: 50px;
                font-size: 14px;
                color: #FFFFFF;

                &:active {
                    font-size: 12px;
                    transform: scale(1);
                }
            }
        }

        .right {
            width: 84px;
            height: 100%;

            > button {
                display: block;
                height: 100%;
                width: 100%;
                font-size: 14px;
                color: #FFFFFF;
                white-space: nowrap;

                &:active {
                    font-size: 12px;
                    transform: scale(1);
                }
            }

            .modify {
                background: rgba(153,153,153,0.50);
            }

            .submit {
                background: #FF7C56;
            }

            .primary {
                background: #009688;
            }
        }
    }
}
</style>
