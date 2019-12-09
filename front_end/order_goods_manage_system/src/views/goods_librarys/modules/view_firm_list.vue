<template>
<el-dialog
    :title="'【'+goodsData.name+'】的供货商列表'"
    :visible.sync="dialogVisible"
    width="60%">
    <el-table
        :data="tableData"
        height="500"
        style="width: 100%">
        <el-table-column
        type="index"
        label="序号"
        width="140">
        </el-table-column>
        <el-table-column
        prop="name"
        label="供货商姓名"
        width="150">
        </el-table-column>
        <el-table-column
        prop="phone"
        label="联系电话">
        </el-table-column>
        <el-table-column
        prop="purchase_times"
        label="采购次数"
        width="100">
        </el-table-column>
    </el-table>
    <!-- <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
    </span> -->
</el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            tableData: [],
            goodsData: {}
        }
    },

    methods: {
        open(data) {
            this.dialogVisible = true
            this.goodsData = data
            this.getList()
        },

        getList() {
            this.$fetch.get({
                url: `/${this.goodsData.id}/firm/list`
            }).then(data => {
                console.log(data)
                this.tableData = data.firm_list
            }).catch(e => {
                this.openMessage(0, '获取供应商数据失败,' + e)
            })
        }
    }
}
</script>

<style>

</style>
