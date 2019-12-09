<template>
    <el-dialog
        :title="'【'+supplier_name+'】的货品列表'"
        :visible.sync="dialogVisible"
        width="520px">
        <el-table
            :data="goods_list"
            border
            height="520"
            style="width: 100%">
            <el-table-column
                type="index"
                label="序号"
                width="50">
            </el-table-column>
            <el-table-column
                prop="name"
                label="货品名称"
                width="320">
            </el-table-column>
            <el-table-column
                prop="purchase_times"
                label="采购次数"
                width="">
            </el-table-column>
        </el-table>
    </el-dialog>
</template>

<script>
import search from './search.vue'
export default {
    data() {
        return {
            dialogVisible: false,
            goods_list: [],
            supplier_name: ''
        }
    },
    methods: {
        open(obj) {
            this.goods_list = obj.data
            this.supplier_name = obj.supplier_name
            this.dialogVisible = true
        }
    },
    components: {
        search
    }
}
</script>

<style lang="scss" scoped>
.inline {
}
</style>
