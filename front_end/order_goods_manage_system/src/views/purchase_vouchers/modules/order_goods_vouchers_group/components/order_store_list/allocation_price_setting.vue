<template>
    <transition name="slide-fade-100">
        <div class="order-detail" v-if="isShowAllocationPriceSetting">
            <div class="tabal-top">
                <div>
                    <h3>配货价设置</h3>
                    <button type="text" @click="confirm">完成设置</button>
                </div>
                <span type="icon" class="el-icon el-icon-close" @click="isShowAllocationPriceSetting = false"></span>
            </div>
            <el-table
                class="table"
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
                prop="packed_amount"
                align="right"
                label="实配量">
                </el-table-column>
                <el-table-column
                prop="purchase_price"
                align="right"
                label="采购价">
                <template slot-scope="scope">
                    <span v-if="canIUse('admin', 9)">{{scope.row.purchase_price}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
                </el-table-column>
                <el-table-column
                prop="allocation_price"
                align="right"
                label="配货价">
                <template slot-scope="scope">
                    <input @keyup="inputChange" v-removeMouseWheelEvent v-selectTextOnFocus  style="text-align:right" v-if="!scope.row.isTotalColumn" v-model="scope.row.packing_price" type="number">
                </template>
                </el-table-column>
                <el-table-column
                prop="allocation_subtotal"
                align="right"
                label="配货小计">
                <template slot-scope="scope">
                    <span v-if="scope.row.isTotalColumn">{{scope.row.allocation_subtotal}}</span>
                    <span v-else-if="canIUse('admin', 9)">{{(scope.row.packing_price * scope.row.packed_amount).toFixed(2)}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
                </el-table-column>
                <el-table-column
                prop="packed_amount"
                align="center"
                label="加价率">
                <template slot-scope="scope">
                    <span v-if="scope.row.isTotalColumn || scope.row.purchase_price === 0">-</span>
                    <span v-else>{{((scope.row.packing_price - scope.row.purchase_price) / scope.row.purchase_price * 100).toFixed(2) + '%'}}</span>
                </template>
                </el-table-column>
            </el-table>
        </div>
    </transition>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
    data() {
        return {
            isShowAllocationPriceSetting: false,
            tableData: [],
            loading: false,
            tableHeight: window.innerHeight - 36
        }
    },

    props: {
        wishOrderId: Number
    },

    computed: {
        ...mapGetters(['canIUse'])
    },

    created() {
        // this.wishOrderId = this.$route.query.wishOrderId
    },

    methods: {
        open(obj) {
            this.isShowAllocationPriceSetting = true
            this.storeData = JSON.parse(JSON.stringify(obj.store))
            this.callback = obj.callback || function() {}
            this.getStoreData()
        },

        close() {
            this.isShowAllocationPriceSetting = false
        },

        getStoreData() {
            this.loading = true
            this.$fetch.get({
                url: '/station/demandorder/' + this.storeData.demand_order_id
            }).then(data => {
                this.activedOrderData = data.order_data
                data.order_data.goods_data.unshift({
                    isTotalColumn: true,
                    goods_name: '累计',
                    current_storage: '-',
                    purchase_price: '-',
                    allocation_price: '-',
                    demand_amount: this.computeTotal(data.order_data.goods_data, 'demand_amount'),
                    packed_amount: this.computeTotal(data.order_data.goods_data, 'packed_amount'),
                    allocation_subtotal: this.computeTotal(data.order_data.goods_data, 'allocation_subtotal')
                })
                this.tableData = data.order_data.goods_data.map(value => {
                    value.packing_price = value.allocation_price || value.purchase_price
                    return value
                })
            }).catch(e => {
                console.log(e)
                this.openMessage(0, '获取订货单数据失败,' + e)
            }).finally(() => {
                this.loading = false
            })
        },

        inputChange() {
            this.tableData[0].allocation_subtotal = this.tableData.reduce((last, next, index) => {
                if (index === 0) {
                    return last
                } else {
                    last += +next.packing_price * +next.packed_amount
                    return last
                }
            }, 0)

            this.tableData = this.tableData
        },

        computeTotal(data, key) {
            return data.reduce((last, next) => {
                last += next[key]
                return last
            }, 0)
        },

        confirm() {
            this.$fetch.put({
                url: '/shoppackingprice',
                params: {
                    "wish_order_id": this.wishOrderId,
                    "shop_id": this.storeData.shop_id,
                    price_list: this.tableData.map(value => {
                        let obj = {}
                        obj.goods_id = value.goods_id
                        obj.packing_price = value.packing_price
                        return obj
                    }).filter(value => value.goods_id)
                }
            }).then(data => {
                this.close()
                this.callback()
                this.openMessage(1, '设置成功')
            }).catch(e => {
                console.log(e)
                this.openMessage(0, e)
            })
        }
    }
}
</script>

<style lang="scss" scoped>
.order-detail {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    // width: 600px;
    // display: inline-block;
    // height: 100%;
    overflow: auto;
    width: 100%;
    // max-width: 650px;
    background: #fff;
    box-shadow: 9px 3px 20px -10px rgba(0, 0, 0, 0.4);
    z-index: 1;
}

.tabal-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 36px;
    text-align: center;
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

.table {
    input {
        width: 100%;
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
    transform: translateX(-100%);
    opacity: 0;
}
</style>
