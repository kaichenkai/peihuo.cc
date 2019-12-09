<template>
    <el-dialog
        title="出库详情"
        :visible.sync="dialogVisible"
        width="400px">
        <p><span>货品名称：</span>{{stockOutData.goods_name}}</p>
        <p style="margin-bottom: 10px;"><span>出库数量：</span>{{stockOutData.amount}}</p>
        <p style="margin-bottom: 10px;"><span>实际出货量：</span><input v-selectTextOnFocus v-removeMouseWheelEvent v-model="actualyAmount" type="number" min="0" /></p>
        <el-checkbox v-model="checked" style="color:#333">打印出库单</el-checkbox>
        <el-select v-model="choosedPrinter" class="select">
            <el-option v-for="(item, key) in printerList" :value="item.id" :label="item.remarks" :key="key"></el-option>
        </el-select>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">确认</button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            checked: true,
            printerList: [],
            choosedPrinter: '',
            actualyAmount: '',
            stockOutData: {}
        }
    },

    created() {
        this.getPrinterList()
    },

    methods: {
        getPrinterList() {
            this.$fetch.get({
                url: '/printers'
            }).then(data => {
                this.printerList = data.printer_list
                if (data.printer_list.length > 0) {
                    this.choosedPrinter = data.printer_list[0].id
                }
            }).catch(e => {
                this.openMessage(0, e || '获取打印机列表失败')
            })
        },
        open(obj = {}) {
            this.dialogVisible = true
            this.callback = obj.callback
            this.stockOutData = JSON.parse(JSON.stringify(obj.data))
            this.actualyAmount = this.stockOutData.amount
        },

        async confirm() {
            if (+this.actualyAmount !== +this.stockOutData.amount) {
                await this.modifyStockOutAmout().then(data => {
                    this.stockOut()
                })
            } else {
                this.stockOut()
            }

            if (this.checked) {
                this.print()
            }
        },

        modifyStockOutAmout() {
            return this.$fetch.put({
                url: '/warehouse/stockout/' + this.stockOutData.id,
                params: {
                    action: "modify_stock_out_amount",
                    amount: this.actualyAmount
                }
            }).catch(e => {
                this.openMessage(0, e || '修改出库量失败')
            })
        },

        print() {
            this.$fetch.post({
                url: `/print/stockout`,
                params: {
                    'record_id': this.stockOutData.id,
                    'printer_id': this.choosedPrinter
                }
            }).then(data => {
                this.openMessage(1, '打印成功')
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        stockOut() {
            this.$fetch.put({
                url: '/warehouse/stockout/' + this.stockOutData.id,
                params: {
                    action: 'stockout_affirm'
                }
            }).then(data => {
                this.openMessage(1, '出库成功')
                this.dialogVisible = false
                this.callback()
            }).catch(e => {
                this.openMessage(0, '出库失败')
            })
        },

        cancel() {
            this.dialogVisible = false
        }
    },
    components: {
    }
}
</script>

<style lang="scss" scoped>
p{
    line-height: 32px;
    color:#000;

    span {
        display: inline-block;
        width: 110px;
    }

    input {
        padding: 0 10px;
        width: 194px;
        height: 32px;
    }
}

/deep/ .el-checkbox__input.is-checked + .el-checkbox__label{
    color: #333;
}

.select {
    padding: 5px 0;
    margin-left: 10px;
    /deep/ .el-input__inner {
        border-radius: 0px;
        height: 30px;
    }

    /deep/ .el-select__caret {
        line-height: 30px;
    }
}
</style>
