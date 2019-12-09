<template>
    <el-dialog
    class="fees-list-container"
    :title="title + '详情'"
    :visible.sync="dialogVisible"
    width="600px">
    <div>
        <span>{{title + '合计：'}}{{fee_sum}}</span>
    </div>
    <el-table
        class="tabel"
        :data="tableData"
        v-loading="tableLoading"
        v-scrollLoad="scrollLoad"
        border
        height="400px"
        style="width: 100%">
        <el-table-column
        prop="date"
        label="时间"
        width="180">
        </el-table-column>
        <el-table-column
        prop="creator_name"
        label="操作人"
        width="80">
        </el-table-column>
        <el-table-column
        prop="money"
        label="金额/元">
        </el-table-column>
        <el-table-column
        prop="remarks"
        label="备注">
        </el-table-column>
        <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
    </el-table>
    <!-- <div class="table-bottom">
        <el-button @click="addOne" style="padding-left: 10px" type="text">+添加支出</el-button>
    </div> -->
    <!-- <span slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="isUpload" class="btn confirm" @click="confirm">确认</el-button>
        <button @click="cancel" class="btn cancel">取消</button>
    </span> -->
    </el-dialog>
</template>

<script>
import { formatDate } from '@/utils'
export default {
    data() {
        return {
            title: '',
            dialogVisible: false,
            tableData: [],
            fee_sum: 0
        }
    },

    methods: {
        open(data) {
            this.title = data.title
            this.data = data.data
            this.type = data.type
            this.dateType = data.dateType
            this.getTableList()
            this.dialogVisible = true
        },

        getTableList(page = 0) {
            return this.$fetch.get({
                url: '/fees',
                params: {
                    types: [this.type],
                    from_date: this.getFormDate(),
                    before_date: this.getBeforeDate(),
                    page: page,
                    scope: this.dateType
                }
            }).then(data => {
                this.fee_sum = data.fee_sum
                if (page === 0) {
                    this.tableData = data.fees
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.fees)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        getFormDate() {
            let date = new Date(this.data.date.replace(/-/g, '/'))
            switch (this.dateType) {
                case 0: date = new Date(date); break
                case 1: date = new Date(date.setDate(1)); break
                case 2:
                    date = new Date(date.setDate(1))
                    date = new Date(date.setMonth(0)); break
                default:
                    this.openMessage(0, '日期类型错误')
            }

            return formatDate(new Date(date), 'yyyy-MM-dd')
        },

        getBeforeDate() {
            // debugger
            let date = new Date(this.data.date.replace(/-/g, '/'))
            switch (this.dateType) {
                case 0: date = date.setDate(date.getDate() + 1); break
                case 1:
                    date = new Date(date.setDate(1))
                    date = date.setMonth(date.getMonth() + 1); break
                case 2:
                    date = new Date(date.setDate(1))
                    date = new Date(date.setMonth(0))
                    date = date.setFullYear(date.getFullYear() + 1); break
                default:
                    this.openMessage(0, '日期类型错误')
            }

            return formatDate(new Date(date), 'yyyy-MM-dd')
        },

        cancel() {
            this.close()
        },

        close() {
            this.initScrollTable()
            this.tableData = []
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
.fees-list-container {

}
</style>
