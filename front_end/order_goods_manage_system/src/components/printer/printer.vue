<template>
    <el-dialog
    class="print-container"
    :title="title"
    :lock-scroll="false"
    :visible.sync="dialogVisible"
    :modal-append-to-body="false"
    width="595px">
    <div class="left-container"><slot></slot></div><div class="right-container">
        <p>{{title}}：</p>
        <el-select v-model="choosedPrinter" class="select">
            <el-option v-for="(item, key) in printerList" :value="item.id" :label="item.remarks" :key="key"></el-option>
        </el-select>
        <button class="confirm" @click="confirm">确认</button>
    </div>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            printerList: [],
            choosedPrinter: ''
        }
    },
    props: {
        title: String
    },

    created() {
        this.getPrinterList()
    },

    methods: {
        open(data) {
            this.dialogVisible = true
            this.callback = data.callback || function() {}
        },

        getPrinterList() {
            this.$fetch.get({
                url: '/printers'
            }).then(data => {
                this.printerList = data.printer_list
            }).catch(e => {
                this.openMessage(0, '获取打印机列表失败,' + e)
            })
        },

        confirm() {
            if (!this.choosedPrinter) {
                return this.openMessage(2, '请选择打印机')
            }
            this.dialogVisible = false
            this.callback(this.choosedPrinter)
        }
    }
}
</script>

<style lang="scss" scoped>
/deep/ .el-dialog__header {
    display: none;
}

/deep/ .el-dialog .el-dialog__body {
    padding: 0 !important;
}

.left-container, .right-container {
    display: inline-block;
    vertical-align: top;
    height: 100%;
    max-height: 395px;
}

.print-container {
    overflow: hidden;
}

.left-container {
    width: 410px;
    padding: 20px;
    overflow: auto;
}

.right-container {
    position: relative;
    padding: 15px 5px 17px 5px;
    width: 185px;
    background: #F7F7F7;
    min-height: 395px;

    .select {
        padding: 5px 0;
        /deep/ .el-input__inner {
            border-radius: 0px;
            height: 30px;
        }

        /deep/ .el-select__caret {
            line-height: 30px;
        }
    }

    .confirm {
        position: absolute;
        bottom: 17px;
        left: 50%;
        transform: translateX(-50%);
        width: 165px;
        height: 35px;
        background: #009688;
        border-radius: 2px;
        font-size: 14px;
        color: #FFFFFF;

        &:active {
            transform: scale(.95) translateX(-50%);
        }
    }
}
</style>
