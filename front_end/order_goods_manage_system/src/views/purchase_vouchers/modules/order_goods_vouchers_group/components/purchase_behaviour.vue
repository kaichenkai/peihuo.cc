<template>
<transition name="slide-fade-100">
    <div class="pruchase-behaviour-container" v-if="showDialog" @click="showDialog = false">
        <div class="container" @click.stop>
            <div class="header">
                <h2>采购动态</h2>
                <i class="el-icon el-icon-close" @click="showDialog = false"></i>
            </div>
            <div class="behaviour-container">
                <ul class="behaviour-wrap" v-if="dataList.length > 0">
                    <i class="line"></i>
                    <li class="item" v-for="(data, index) in dataList" :key="index">
                        <i class="dot new"></i>
                        <div v-for="(item, index) in data.purchasing_dynamic_info" :key="'b' + index">
                            <p v-if="index == 0">
                                <img class="avatar" :src="item.headimgurl" alt="">
                                <span class="name">{{item.creator_name}}</span>
                                <span class="action">{{item.record_type | getActionName}}</span>
                                <time class="time">{{data.date_time}}</time>
                            </p>
                            <p style="margin-top: 10px;line-height: 28px">
                                <span class="goods-name" :style="[{'color': [2, 6].includes(item.record_type) ? '#999' : ''}]" v-if="new Set(item.goods_name).size === 1">{{item.goods_name[1]}}</span>
                                <el-tooltip v-else effect="dark" :content="item.goods_name[0] + '→' + item.goods_name[1]" placement="top">
                                    <span :style="[{'color': [2, 6].includes(item.record_type) ? '#999' : '#3C90FF'}]" class="goods-name">{{item.goods_name[1]}}</span>
                                </el-tooltip>
                            </p>
                            <p  class="l-20">
                                <span class="amount mr-12" v-if="new Set(item.actual_amount).size === 1">{{item.actual_amount[1]}}件</span>
                                <el-tooltip v-else effect="dark" :content="item.actual_amount[0] + '→' + item.actual_amount[1]" placement="top">
                                    <span class="amount mr-12" style="color: #3C90FF;">{{item.actual_amount[1]}}件</span>
                                </el-tooltip>
                                <!-- <span class="mr-12" v-if="new Set(item.price).size === 1">{{item.price[1]}}元/1件</span>
                                <el-tooltip v-else effect="dark" :content="item.price[0] + '→' + item.price[1]" placement="top">
                                    <span class="mr-12" style="color: #3C90FF;">{{item.price[1]}}元/1件</span>
                                </el-tooltip>
                                <span class="mr-12" v-if="new Set(item.subtotal).size === 1">{{item.subtotal[1]}}元</span>
                                <el-tooltip v-else effect="dark" :content="item.subtotal[0] + '→' + item.subtotal[1]" placement="top">
                                    <span class="mr-12" style="color: #3C90FF;">{{item.subtotal[1]}}元</span>
                                </el-tooltip> -->
                                <span class="mr-12" v-if="new Set(item.firm_name).size === 1">{{item.firm_name[1]}}</span>
                                <el-tooltip v-else effect="dark" :content="item.firm_name[0] + '→' + item.firm_name[1]" placement="top">
                                    <span class="mr-12" style="color: #3C90FF;">{{item.firm_name[1]}}</span>
                                </el-tooltip>
                            </p>
                            <p class="l-20">
                                <span class="remark">{{item.remarks}}</span>
                            </p>
                        </div>
                    </li>
                </ul>
                <p v-else style="text-align: center; margin-top: 20px">暂无采购动态</p>
            </div>
        </div>
    </div>
</transition>
</template>

<script>
export default {
    data() {
        return {
            dataList: [],
            showDialog: false,
            tableHeigth: window.innerHeight - 56
            // search: ''
        }
    },

    props: {
        wishOrderId: Number
    },

    filters: {
        getActionName(id) {
            let text = ''
            switch (id) {
                case 0: text = '录入采购数据'; break
                case 1: text = '修改采购数据'; break
                case 2: text = '不采了'; break
                case 3: text = '添加采购备注'; break
                case 4: text = '修改商品名称'; break
                case 5: text = '新增采购商品'; break
                case 6: text = '移除商品'; break
            }

            return text
        }
    },

    methods: {
        open(obj) {
            this.showDialog = true
            this.callback = obj.callback || function() {}
            this.getList()
            this.purchaseOrderId = obj.purchaseOrderId
            this.refreshBehaviour()
        },

        getCellClassName({ row }) {
            if (row.remarks) {
                return 'have-remark'
            }
        },

        refreshBehaviour() {
            this.$fetch.delete({
                url: '/summarynotifications',
                params: {
                    notification_type: 'purchasing_dynamics',
                    purchase_order_id: this.purchaseOrderId
                }
            }).then(data => {
                this.callback()
            })
        },

        getList() {
            return this.$fetch.get({
                url: '/summary/purchasing/dynamics',
                params: {
                    page: 0,
                    limit: 10000,
                    wish_order_id: this.wishOrderId
                }
            }).then(data => {
                this.dataList = data.purchasing_dynamic_list
            }).catch(e => {
                this.openMessage(0, e || '获取采购动态失败')
            })
        }
    }
}
</script>

<style lang="scss" scoped>
.pruchase-behaviour-container {
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
                margin-right: 466px;
            }

            i {
                font-size: 24px;
                color: #999;
            }
        }

        .behaviour-container {
            position: absolute;
            left: 0;
            right: 0;
            top: 56px;
            bottom: 0;
            overflow: auto;

            .line {
                position: absolute;
                top: 23px;
                left: -15px;
                bottom: 23px;
                width: 2px;
                background: #DDDDDD;
            }

            .behaviour-wrap {
                position: relative;
                margin-left: 30px;

                .item {
                    position: relative;
                    padding: 10px 8px;
                    font-size: 14px;
                    color: #151515;

                    & + .item {
                        border-top: 1px solid #EBEEF5;
                    }

                    .dot {
                        position: absolute;
                        top: 23px;
                        left: -18px;
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background: #ddd;
                    }

                    .new {
                        background: #419688;
                    }

                    p {
                        margin: 4px;
                    }

                    .l-20 {
                        line-height: 20px;
                    }

                    .avatar {
                        display: inline-block;
                        vertical-align: middle;
                        margin-right: 4px;
                        width: 20px;
                        height: 20px;
                        border-radius: 50%;
                        background: #D8D8D8;
                    }

                    .name {
                        margin-right: 4px;
                        font-size: 14px;
                        color: #333333;
                    }

                    .action {
                        font-size: 14px;
                        color: #151515;
                    }

                    time {
                        float: right;
                    }

                    .goods-name {
                        font-size: 20px;
                        color: #333333;
                    }

                    .amount {

                    }

                    .mr-12 {
                        margin-right: 12px;
                    }

                    .remark {
                        color: #EE5B5B;
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
