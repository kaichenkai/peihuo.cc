<template>
<transition name="slide-fade-100">
    <div class="in-out-stock-container" v-if="showDialog" @click="showDialog = false">
        <div class="container" @click.stop>
            <div class="header">
                <h2>仓库出入库</h2>
                <i class="el-icon el-icon-close" @click="showDialog = false"></i>
            </div>

            <div id="outerContainer">
                <div id="innerContainer">

                    <table class="table table-header" id="table-header">
                        <tr>
                            <th>商品名</th>
                            <th><sort name="stock" @sorted="sort">库存量</sort></th>
                            <th><sort name="wait_stock_out_amount" @sorted="sort">待出库</sort></th>
                            <th><sort name="stock_in_amount" @sorted="sort">已入库</sort></th>
                        </tr>
                        <tr>
                            <td>累计</td>
                            <td>{{sumData.total_stock}}</td>
                            <td>{{sumData.wait_stock_out_total_amount}}</td>
                            <td>{{sumData.stock_in_total_amount}}</td>
                        </tr>
                    </table>
                    <table class="table">
                        <tr v-for="item in tableData" :key="item.id">
                            <td>{{item.name}}</td>
                            <td>{{item.stock}}</td>
                            <td>{{item.wait_stock_out_amount}}</td>
                            <td>{{item.stock_in_amount}}</td>
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
            sumData: {},
            tableData: [],
            showDialog: false,
            search: ''
        }
    },

    mounted() {
        // new StickyListHeaders({
        //     outerContainer: 'outerContainer',
        //     innerContainer: 'innerContainer',
        //     headers: ['table-header']
        // })
    },

    methods: {
        open(obj) {
            this.showDialog = true
            this.cacheData = obj
            // this.goodsData = obj.goodsData
            // this.callback = obj.callback || function() {}
            this.wishOrderId = obj.wishOrderId
            this.getInOutStockDetail().then(() => {
                new StickyListHeaders({
                    outerContainer: 'outerContainer',
                    innerContainer: 'innerContainer',
                    headers: ['table-header']
                })
            })
        },

        getInOutStockDetail() {
            return this.$fetch.get({
                url: '/warehouse/stockoutin/statistics/list',
                params: {
                    page: 0,
                    limit: 1000,
                    wish_order_id: this.wishOrderId
                }
            }).then(data => {
                this.tableData = data.goods_list
                this.sumData = data.total_data_dict
                this.cachedServerData = JSON.parse(JSON.stringify(data.goods_list))
            }).catch(e => {
                this.openMessage(0, e || '获取仓库出入库记录失败')
            })
        },

        sort(type, name) {
            switch (type) {
                case 0: this.tableData = JSON.parse(JSON.stringify(this.cachedServerData)); break
                case 1: this.tableData = this.tableData.sort((a, b) => {
                    return a[name] - b[name]
                }); break
                case 2: this.tableData = this.tableData.sort((a, b) => {
                    return b[name] - a[name]
                }); break
            }
        }
    }
}
</script>

<style lang="scss" scoped>
.in-out-stock-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;

    .container {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 595px;
        background: #fff;
        box-shadow: 10px 0 10px 0 rgba(0,0,0,0.05);

        .header {
            display: flex;
            align-items: center;
            height: 56px;
            background: #f9f9f9;

            h2 {
                margin: 0 10px;
                font-size: 20px;
                color: #333333;
                margin-right: 436px;
            }

            button {
                margin-right: 136px;
                width: 100px;
                height: 30px;
                background: #009688;
                border-radius: 2px;
                font-size: 14px;
                color: #fff;
            }

            i {
                font-size: 20px;
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

                    input {
                        padding-left: 10px;
                        width: 286px;
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
                th {
                    font-weight: bold;
                    user-select: none;
                }
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
                    width: 180px;
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

.slide-fade-100-enter-active {
    transition: all .5s ease;
}
.slide-fade-100-leave-active {
    transition: all .5s ease;
}
.slide-fade-100-enter, .slide-fade-100-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
    transform: translateX(-100%);
    opacity: 0;
}
</style>
