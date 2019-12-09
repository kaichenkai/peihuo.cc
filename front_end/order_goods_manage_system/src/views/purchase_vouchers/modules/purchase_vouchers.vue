// 采购单主页面
<template>
    <div>
        <title-and-tools :config="{title: '采购单'}"></title-and-tools>
        <el-table
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            :data="tableData"
            style="width: 100%">
            <el-table-column
            prop="wish_date"
            label="日期"
            width="200">
            <template slot-scope="scope">
                {{setCnDateText(scope.row.wish_date)}}
            </template>
            </el-table-column>
            <el-table-column
            prop="name"
            label=""
            width="180">
            <template slot-scope="scope">
                <el-button v-if="isCanCreateWishOrder(scope.row)" class="color-009688" size="mini" plain @click="createPurchaseVouchers(scope.row)">制作采购意向单</el-button>
                <el-button @click="editPurchaseVouchers(scope.row)" v-else type="text">采购意向单</el-button>
            </template>
            </el-table-column>
            <el-table-column
            prop="province"
            label="">
            <template slot-scope="scope">
                <div>
                    <!-- 判断是不是第一行，并且明天的意向单是否创建 -->
                    <el-button @click="viewOrdersVouchers(scope.row)" v-if="!isCanCreateWishOrder(scope.row)" type="text">订货汇总单</el-button>
                    <!-- 判断是否有门店要货 -->
                    <span
                    v-if="demandOrderUpDateStatus.order_update_dict
                    && scope.row.id in demandOrderUpDateStatus.order_update_dict
                    && demandOrderUpDateStatus.order_update_dict[scope.row.id] > 0"
                    style="color: #ff6666;margin-left: 8px;">
                    +{{demandOrderUpDateStatus.order_update_dict[scope.row.id]}}
                    </span>
                </div>
            </template>
            </el-table-column>
            <el-table-column
            prop="city"
            label="">
            <template slot-scope="scope">
                <el-button type="text" v-if="!isCanCreateWishOrder(scope.row)" @click="goToMakeQuotedPriceVoucher(scope.row)">报价单</el-button>
            </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
    </div>
</template>

<script>
import titleAndTools from '@/components/modules_top_tools/title_&_tools.vue'
import * as utils from '@/utils'
import { mapState } from 'vuex'

/**
 * 难点业务逻辑：
 * 如果今天或者明天的意向单没有创建，那么需要展示创建意向单按钮
 * 因为没创建意向单，那么服务器是不会返回这两天的数据的
 * 所以需要判断服务器返回的数据来手动将今天或者明天的数据push到tabledata前面来让表格组件渲染这一天的数据
 */
export default {
    data() {
        return {
            tableData: [],
            serverData: []
        }
    },

    computed: {
        ...mapState(['demandOrderUpDateStatus'])
    },

    created() {
        this.getWishOrders()
        this.today = new Date()
        this.tomorrow = new Date(new Date().setDate(new Date().getDate() + 1))
        this.yesterday = new Date(new Date().setDate(new Date().getDate() - 1))
    },

    methods: {
        getTableList(page) {
            return this.getWishOrders(page)
        },
        getWishOrders(page = 0) {
            this.tableLoading = true
            return this.$fetch.get({
                url: '/wishorders',
                params: {
                    page: page
                }
            }).then(data => {
                if (page === 0) {
                    this.serverData = data.order_list // 将服务器数据做一个备份用于判断是否添加了明天的意向单
                    let wishOrderNeedsCreate = this.checkAndGetWishOrderNeedsCreate()
                    if (wishOrderNeedsCreate.length === 0) {
                        this.tableData = data.order_list
                    } else {
                        this.tableData = wishOrderNeedsCreate.concat(data.order_list)
                    }
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.order_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, '获取意向单列表失败,' + e)
            }).finally(() => {
                this.tableLoading = false
            })
        },

        // 用于设置前三天的中文
        setCnDateText(date) {
            let _date = date.replace(/-/g, '/')
            if (utils.formatDate(new Date(_date), 'yyyy-MM-dd') === utils.formatDate(new Date(this.tomorrow), 'yyyy-MM-dd')) {
                return '[明日] ' + date
            } else if (utils.formatDate(new Date(_date), 'yyyy-MM-dd') === utils.formatDate(new Date(this.today), 'yyyy-MM-dd')) {
                return '[今日] ' + date
            } else if (utils.formatDate(new Date(_date), 'yyyy-MM-dd') === utils.formatDate(new Date(this.yesterday), 'yyyy-MM-dd')) {
                return '[昨日] ' + date
            } else {
                return date
            }
        },

        createPurchaseVouchers(s) {
            this.$router.push({
                path: '/main/purchaseCenter/edit',
                query: {
                    date: s.wish_date
                }
            })
        },

        editPurchaseVouchers(data) {
            this.$router.push({
                path: '/main/purchaseCenter/edit',
                query: {
                    date: data.wish_date,
                    id: data.id
                }
            })
        },

        isCanCreateWishOrder(data) {
            return this.checkAndGetWishOrderNeedsCreate().some(value => value.wish_date === data.wish_date)
        },

        // 检查今天和明天是否创建了意向单，如果没创建，则返回需要创建的那一天
        checkAndGetWishOrderNeedsCreate() {
            let arr = []
            if (!this.isTheDateCreatedPurchaseVoucher(this.tomorrow)) {
                arr.push({
                    wish_date: utils.formatDate(new Date(this.tomorrow), 'yyyy-MM-dd')
                })
            }

            if (!this.isTheDateCreatedPurchaseVoucher(this.today)) {
                arr.push({
                    wish_date: utils.formatDate(new Date(this.today), 'yyyy-MM-dd')
                })
            }

            return arr
        },

        // 如果服务器返回的数据中有传入的这一天数据，说明这一天已经创建过意向单了
        isTheDateCreatedPurchaseVoucher(targetDate) {
            return this.serverData.some(obj => utils.formatDate(new Date(targetDate), 'yyyy-MM-dd') === utils.formatDate(new Date(obj.wish_date.replace(/-/g, '/')), 'yyyy-MM-dd'))
        },

        viewOrdersVouchers(order) {
            this.$router.push({
                path: '/main/purchaseCenter/orderGoodsVouchersGroup',
                query: {
                    wishOrderId: order.id,
                    date: order.wish_date
                }
            })
        },

        goToMakeQuotedPriceVoucher(data) {
            this.$router.push({
                path: '/main/purchaseCenter/makeQuotedPriceVoucher',
                query: {
                    wishOrderId: data.id,
                    date: data.wish_date
                }
            })
        }
    },

    components: {
        titleAndTools
    }
}
</script>

<style lang="scss" scoped>

</style>
