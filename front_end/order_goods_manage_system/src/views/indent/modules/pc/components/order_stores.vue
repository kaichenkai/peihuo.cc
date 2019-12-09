<template>
<el-dialog
    :title="'今日已订货(' + orderStoreList.length + ')'"
    :visible.sync="dialogVisible"
    width="600px">
    <el-table
      :data="orderStoreList"
      height="400px"
      style="width: 100%">
       <el-table-column
        type="index"
        width="50">
        </el-table-column>
      <el-table-column
        prop="date"
        label="订货人"
        width="180">
        <template slot-scope="scope">
            <img class="avatar" :src="scope.row.headimgurl" alt=""><span>{{scope.row.creator}}</span>
        </template>
      </el-table-column>
      <el-table-column
        prop="shop"
        label="店铺"
        width="180">
      </el-table-column>
      <el-table-column
        prop="create_time"
        label="提交时间">
      </el-table-column>
    </el-table>

</el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false
        }
    },

    props: {
        orderStoreList: Array
    },

    methods: {
        open() {
            this.dialogVisible = true
        }
    }
}
</script>

<style lang="scss" scoped>
.avatar {
    display: inline-block;
    vertical-align: middle;
    margin-right: 4px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #D8D8D8;
}
</style>
