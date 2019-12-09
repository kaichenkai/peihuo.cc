<template>
    <div>
        <el-table
            :data="tableData"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            @sort-change='sort'
            style="width: 100%">
            <el-table-column
                min-width="230">
                <template slot="header" slot-scope="scope">
                    <table-data-filter title="商品名" allString="所有商品" :items="allGoodsData" itemKeyName="goods_name" itemKeyCode="goods_id"  v-model="searchObj.goods_ids" @confirm="getList"></table-data-filter>
                </template>
                <template slot-scope="scope">
                <span>{{ scope.row.name }}</span>
                </template>
            </el-table-column>
            <el-table-column
                prop="code"
                sortable='custom'
                label="商品编码"
                width="250">
            </el-table-column>
            <el-table-column
                label="当前库存"
                sortable='custom'
                prop="stock"
                width="180">
                <template slot-scope="scope">
                    {{scope.row.stock}}
                    <el-button @click="openModiStock(scope.row)" type="text" >修改</el-button>
                </template>
            </el-table-column>
            <el-table-column
                prop="stock_average_price"
                label="库存采购均价"
                sortable='custom'
                width="200">
                <template slot-scope="scope">
                    <span v-if="canIUse('admin', 10)">{{scope.row.stock_average_price}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
            </el-table-column>
            <el-table-column
                prop="stock_cost"
                sortable='custom'
                label="库存成本"
                width="">
                <template slot-scope="scope">
                    <span v-if="canIUse('admin', 10)">{{scope.row.stock_cost}}</span>
                    <span v-else style="font-size: 12px; color: #999">无权限</span>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <modi-stock ref="modiStock" :goodsData='goodsData'></modi-stock>
    </div>
</template>
<script>
import modiStock from './modi_stock.vue'
import _ from 'lodash'
import { mapGetters } from 'vuex'
export default {
    data() {
        return {
            tableData: [
                {}
            ],
            goodsData: {},
            allGoodsData: [],
            searchObj: {
                goods_ids: []
            },
            form: {
                order_by: '',
                asc: ''
            }
        }
    },

    props: {
        activeName: String
    },

    computed: {
        ...mapGetters(['canIUse'])
    },

    watch: {
        activeName(value) {
            if (value === 'third') {
                this.getList()
            }
        },
        form: {
            handler() {
                this.getList()
            },
            deep: true
        }
    },

    mounted() {
        this.getList().then(data => {
            this.allGoodsData = data.goods_list
        })
    },

    methods: {
        sort(obj) { // 排序
            this.form.order_by = obj.prop
            this.form.asc = obj.order === 'ascending'
        },
        openModiStock(obj) {
            this.goodsData = this.cloneObject(obj)
            this.$refs.modiStock.open({
                type: 'update',
                data: this.cloneObject(obj),
                callback: (modifiedStockCount) => {
                    // console.log(modifiedStockCount)
                    obj.stock = modifiedStockCount
                    // this.getList()
                }
            })
        },

        getTableList(page) {
            return this.getList(page)
        },

        getList(page = 0) {
            return this.$fetch.get({
                url: '/warehouse/stock/list',
                params: {
                    page,
                    ..._.mapValues(this.searchObj, obj => obj.join('|') || undefined),
                    ...this.form
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.stock_goods_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.stock_goods_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取仓库库存失败')
            })
        }
    },
    components: {
        modiStock
    }
}
</script>
