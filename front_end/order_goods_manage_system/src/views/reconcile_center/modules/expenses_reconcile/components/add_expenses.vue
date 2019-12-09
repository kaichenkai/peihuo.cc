<template>
    <el-dialog
    class="add-expenses-container"
    title="+添加费用"
    :visible.sync="dialogVisible"
    width="600px">
    <div>
        <span>费用发生日期：</span>
        <el-date-picker
            v-model="form.date"
            :editable='false'
            :clearable='false'
            type="date"
            size="small"
            value-format="yyyy-MM-dd"
            placeholder="选择日期">
        </el-date-picker>
    </div>
    <el-table
        class="tabel"
        :data="tableData"
        border
        style="width: 100%">
        <el-table-column
        prop="date"
        label="费用类型"
        width="180">
        <template slot-scope="scope">
            <el-select v-model="scope.row.type" placeholder="请选择">
                <el-option
                v-for="item in types"
                :key="item.value"
                :label="item.label"
                :value="item.value">
                </el-option>
            </el-select>
        </template>
        </el-table-column>
        <el-table-column
        prop="name"
        label="金额/元"
        width="80">
        <template slot-scope="scope">
            <input class="input-text" v-model="scope.row.money" type="number" v-removeMouseWheelEvent min="0" placeholder="必填">
        </template>
        </el-table-column>
        <el-table-column
        prop="address"
        label="备注">
        <template slot-scope="scope">
            <input class="input-text" v-model="scope.row.remarks" type="text" placeholder="选填">
        </template>
        </el-table-column>
        <el-table-column>
            <template slot-scope="scope">
                <el-button @click="deleteOne(scope.row)" style="color: #ff5555;padding-left: 10px" type="text">删除</el-button>
            </template>
        </el-table-column>
    </el-table>
    <div class="table-bottom">
        <el-button @click="addOne" style="padding-left: 10px" type="text">+添加支出</el-button>
    </div>
    <span slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="isUpload" class="btn confirm" @click="confirm">确认</el-button>
        <button @click="cancel" class="btn cancel">取消</button>
    </span>
    </el-dialog>
</template>

<script>
import { formatDate } from '@/utils'
export default {
    data() {
        return {
            dialogVisible: false,
            form: {
                date: formatDate(new Date(), 'yyyy-MM-dd')
            },
            tableData: [],
            types: [{
                value: 1,
                label: '运杂费'
            }, {
                value: 2,
                label: '日常杂费'
            }],
            isUpload: false
        }
    },

    methods: {
        open(data) {
            this.callback = data.callback
            this.dialogVisible = true
        },

        addOne() {
            this.tableData.push({
                type: 1,
                money: 0,
                remarks: '',
                _createTime: Date.now()
            })
        },

        deleteOne(data) {
            this.tableData.splice(this.tableData.findIndex(value => value._createTime === data._createTime), 1)
        },

        confirm() {
            this.validator().then(() => {
                this.isUpload = true
                this.$fetch.post({
                    url: '/fee',
                    params: {
                        ...this.form,
                        fee_list: this.tableData
                    }
                }).then(data => {
                    this.callback()
                    this.openMessage(1, '添加成功')
                    this.close()
                }).catch(e => {
                    this.openMessage(0, e || '添加失败')
                }).finally(() => {
                    this.isUpload = false
                })
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        validator() {
            const validator = new this.$Validator()
            validator.add('isEmpty', this.form.date, '请选择日期')
            this.tableData.forEach(value => {
                validator.add('isEmpty', value.money, '请输入金额')
            })

            return validator.start()
        },

        cancel() {
            this.close()
        },

        close() {
            this.tableData = []
            this.form.date = ''
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
.add-expenses-container {
    /deep/ .el-date-editor.el-input{
        margin-top: 8px;
        width: 150px;
        .el-input__inner{
            height: 30px;
            line-height: 30px;
            border-radius: 15px;
            font-size: 16px;
            color: #333333;
        }
    }
    /deep/ .el-picker-panel {
        position: absolute;
        z-index: 2;
    }

    .tabel {
        /deep/ .el-table--border th:first-child .cell, .el-table--border td:first-child .cell {
            padding: 0;
        }

        /deep/ .el-table__row .cell {
            padding: 0;
            /deep/ .el-input__inner {
                border: none;
            }
        }

        .input-text {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 10px;
            border: none;
        }
    }

    .table-bottom {
        border: 1px solid #ebeef5;
        border-top: none;
    }
}
</style>
