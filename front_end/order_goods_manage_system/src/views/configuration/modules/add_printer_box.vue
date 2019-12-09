<template>
    <el-dialog
        title="添加打印机"
        :visible.sync="dialogVisible"
        :before-close="handleClose"
        width="380px">
        <el-form :inline="true" label-position="top" class="inline" :model="form" ref="form">
            <el-form-item label="终端号" style="width:350px" class="required">
                <el-input v-model="form.printer_num" placeholder="输入终端号" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="终端密钥" style="width:350px">
                <el-input v-model="form.printer_key" placeholder="输入终端密钥" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="备注" style="width:350px" class="required">
                <el-input v-model="form.remarks" placeholder="输入备注" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">保存</button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            form: {
                printer_num: '',
                printer_key: '',
                remarks: ''
            }
        }
    },

    methods: {
        handleClose() {
            this.cancel()
        },
        validator() {
            let validator = new this.$Validator()

            validator.add('isEmpty', this.form.printer_num, '请输入终端号')
            validator.add('isEmpty', this.form.remarks, '请输入备注')

            return validator.start()
        },
        open() {
            this.dialogVisible = true
        },

        confirm() {
            this.validator().then(() => {
                this.$fetch.post({
                    url: '/printer',
                    params: this.form
                }).then(data => {
                    this.openMessage(1, '添加打印机成功')
                    this.form = {
                        printer_num: '',
                        printer_key: '',
                        remarks: ''
                    }
                    this.cancel()
                    this.$emit('finishAddPrinter')
                }).catch(erro => {
                    this.openMessage(2, erro)
                })
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        cancel() {
            this.dialogVisible = false
            this.form = {
                printer_num: '',
                printer_key: '',
                remarks: ''
            }
        }
    },
    
    components: {
    }
}
</script>

<style lang="scss" scoped>
.inline {
    .el-form-item{
        margin-bottom: 20px;
    }
}
</style>
