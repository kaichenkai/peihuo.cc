<template>
    <el-dialog
        :title="title"
        :visible.sync="dialogVisible"
        append-to-body
        width="445px">
        <el-form label-position="right" label-width="50px" :model="form" ref="form" size="small">
            <el-form-item label="类型：">
                <el-input v-selectTextOnFocus v-model="form.type" placeholder="请输入类型" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="金额：">
                <el-input type="number" v-selectTextOnFocus v-model="form.money" placeholder="请输入金额" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="备注：">
                <el-input v-selectTextOnFocus v-model="form.remarks" placeholder="请输入备注" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
        </el-form>
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
            form: {
                type: '',
                money: '',
                remarks: ''
            },
            dialogVisible: false,
            shop_id: '',
            mode: ''
        }
    },

    computed: {
        title() {
            return this.mode === 'add' ? '添加支出' : '修改支出'
        }
    },

    methods: {
        confirm() {
            this.$fetch[this.mode === 'add' ? 'post' : 'put']({
                url: `/shoppayout${this.mode === 'edit' ? "/" + this.id : ''}`,
                params: {
                    shop_id: this.shop_id,
                    ...this.form,
                    date: this.date
                }
            }).then(() => {
                this.openMessage(1, this.mode === 'add' ? '添加成功' : '修改成功')
                this.$emit('finishAdd')
                this.cancel()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        cancel() {
            this.dialogVisible = false
        },
        open(item, obj) {
            this.dialogVisible = true
            if (obj) {
                this.mode = 'edit'
                this.id = obj.id
                this.form = obj
            } else {
                this.mode = 'add'
                this.date = item.date
                this.shop_id = item.shop_id
                this.form = {
                    type: '',
                    money: '',
                    remarks: ''
                }
            }
        }
    }
}
</script>
<style lang="scss" scoped>
    /deep/ .el-form .el-form-item__label{
        line-height: 31px;
        font-size: 14px;
        color: #333333;
    }
</style>
