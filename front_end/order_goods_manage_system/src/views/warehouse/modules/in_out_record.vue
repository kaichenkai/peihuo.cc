<template>
    <el-table
        :data="tableData"
        :height="tableHeight"
        v-scrollLoad="scrollLoad"
        v-loading="tableLoading"
        style="width: 100%">
        <el-table-column
            type="index"
            label="序号"
            width="80">
        </el-table-column>
        <el-table-column
            prop="goods_name"
            label="商品名称"
            min-width="200"
            width="">
            <template slot="header" slot-scope="scope">
                <table-data-filter title="商品名" allString="所有商品" :items="allGoodsData" itemKeyName="goods_name" itemKeyCode="goods_id"  v-model="searchObj.goods_ids" @confirm="getList"></table-data-filter>
            </template>
            <template slot-scope="scope">
                <span class="name">{{ scope.row.goods_name }}</span>
            </template>
        </el-table-column>
        <el-table-column
            prop="record_datetime"
            label="时间"
            sortable
            width="200">
        </el-table-column>
        <el-table-column
            prop="type"
            label="类别"
            sortable
            width="100">
            <template slot-scope="scope">
                <span v-if="scope.row.type == 0">出库</span>
                <span v-if="scope.row.type == 1">入库</span>
            </template>
        </el-table-column>
        <el-table-column
            prop="amount"
            label="数量"
            sortable
            width="100">
        </el-table-column>
        <el-table-column
            prop="operator_name"
            label="操作人"
            width="200">
        </el-table-column>
        <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
    </el-table>
</template>
<script>
import _ from 'lodash'
export default {
    data() {
        return {
            tableData: [],
            allGoodsData: [],
            searchObj: {
                goods_ids: []
            }
        }
    },
    props: {
        activeName: String
    },

    watch: {
        activeName(value) {
            if (value === 'second') {
                this.getList()
            }
        }
    },

    mounted() {
        this.getList().then(data => {
            this.allGoodsData = data.goods_list
        })
    },

    methods: {
        getTableList(page) {
            return this.getList(page)
        },

        getList(page = 0) {
            return this.$fetch.get({
                url: '/warehouse/stockoutin/record',
                params: {
                    page,
                    ..._.mapValues(this.searchObj, obj => obj.join('|') || undefined)
                }
            }).then(data => {
                // console.log(data)
                if (page === 0) {
                    this.tableData = data.stock_outin_record_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.stock_outin_record_list)
                }
                // this.tableData = data.stock_outin_record_list
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取出入库记录失败')
            })
        }
    }
}
</script>
<style lang="scss" scoped>

</style>
