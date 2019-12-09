<template>
    <div>
        <el-radio-group v-model="radio3" style="margin-bottom: 10px">
            <el-radio-button label="按日"></el-radio-button>
            <el-radio-button label="按月"></el-radio-button>
            <el-radio-button label="按年"></el-radio-button>
        </el-radio-group>
        <el-table
            :data="tableData"
            style="width: 100%">
            <el-table-column
            prop="date"
            label="序号"
            width="100">
            </el-table-column>
            <el-table-column
            prop="date"
            label="日期"
            width="100">
            </el-table-column>
            <el-table-column
            prop="name"
            label="现金"
            width="100">
            </el-table-column>
            <el-table-column
            prop="province"
            label="微信"
            width="100">
            </el-table-column>
            <el-table-column
            prop="city"
            label="支付宝">
            </el-table-column>
            <el-table-column
            prop="address"
            label="银行卡">
            </el-table-column>
            <el-table-column
            prop="address"
            label="支票">
            </el-table-column>
            <el-table-column
            prop="address"
            label="收款累计">
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
export default {
    data() {
        return {
            tableData: [],
            radio3: '按日'
        }
    }
}
</script>

<style>

</style>
