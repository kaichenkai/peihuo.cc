<template>
    <el-table
        :data="tableData"
        :height="tableHeight"
        v-scrollLoad="scrollLoad"
        v-loading="tableLoading"
        style="width: 100%">
        <el-table-column
            prop="create_time"
            label="时间"
            width="100">
        </el-table-column>
        <el-table-column
            prop="goods_name"
            label="商品名称"
            width="150">
        </el-table-column>
        <el-table-column
            prop="goods_code"
            label="商品条码"
            width="200">
        </el-table-column>
        <el-table-column
            prop="creator_name"
            label="操作人"
            width="200">
        </el-table-column>
        <el-table-column
            prop="operation_detail"
            label="操作详情"
            width="">
        </el-table-column>
        <el-table-column
            prop="remarks"
            label="备注"
            width="200">
        </el-table-column>
        <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
    </el-table>
</template>

<script>
export default {
    data() {
        return {
            tableData: []
        }
    },

    props: {
        activeName: String
    },

    watch: {
        activeName(value) {
            if (value === 'fourth') {
                this.getList()
            }
        }
    },

    methods: {
        getTableList(page) {
            return this.getList(page)
        },
        getList(page = 0) {
            return this.$fetch.get({
                url: '/warehouse/stock/operation/record',
                params: {
                    page
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.operation_record_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.operation_record_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取出入库历史记录失败')
            })
        }
    }
}
</script>

<style>

</style>
