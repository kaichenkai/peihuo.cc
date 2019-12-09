<template>
    <el-table
        :data="operate_list"
        :height="tableHeight"
        v-scrollLoad="scrollLoad"
        v-loading="tableLoading"
        style="width: 100%">
        <el-table-column
            prop="datetime"
            label="时间"
            width="100">
        </el-table-column>
        <el-table-column
            prop="creator_name"
            label="操作人"
            width="200">
        </el-table-column>
        <el-table-column
            prop="operation_object"
            label="员工"
            width="200">
        </el-table-column>
        <el-table-column
            prop="detail"
            label="操作详情"
            width="">
        </el-table-column>
    </el-table>
</template>
<script>
export default {
    data() {
        return {
            operate_list: []
        }
    },

    created() {
        this.queryOperateData()
    },

    methods: {
        getTableList(page) {
            return this.queryOperateData(page)
        },
        queryOperateData(page = 0) {
            return this.$fetch.get({
                url: `/staff/operation/record`,
                params: {
                    page: page
                }
            }).then(data => {
                if (page === 0) {
                    this.operate_list = data.operation_record_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.operate_list = this.operate_list.concat(data.operation_record_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取操作记录失败')
            })
        }
    }
}
</script>
