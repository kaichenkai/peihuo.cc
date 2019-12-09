<template>
    <div>
        <el-dialog
            :title="if_add_supplier?'添加供货商':'编辑供货商'"
            :visible.sync="dialogVisible"
            width="750px">
            <p class="delete_supplier" v-show="!if_add_supplier" @click="deleteSupplier">删除供货商</p>
            <el-form :inline="true" label-position="top" class="inline" :model="form" ref="form">
                <el-form-item label="供货商姓名" style="width:350px" class="required">
                    <el-input v-selectTextOnFocus v-model="form.name" placeholder="输入供货商姓名" @keyup.enter.native="confirm"></el-input>
                </el-form-item>
                <el-form-item label="供货商联系电话" style="width:350px;margin-left:10px;margin-right:0" class="required">
                    <el-input v-selectTextOnFocus v-model="form.phone" placeholder="输入供货商联系电话" @keyup.enter.native="confirm"></el-input>
                </el-form-item>
                <el-form-item label="备注" style="width:350px">
                    <el-input v-selectTextOnFocus v-model="form.remarks" placeholder="输入备注" @keyup.enter.native="confirm"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <button class="btn confirm" @click="confirm">确认</button>
                <button class="btn cancel" @click="cancel">取消</button>
            </span>
        </el-dialog>
        <add-supplier-success ref="addSupplierSuccess"></add-supplier-success>
    </div>
</template>

<script>
import addSupplierSuccess from './add_supplier_success.vue'
export default {
    data() {
        return {
            dialogVisible: false,
            form: {
                name: '',
                phone: '',
                remarks: ''
            },
            if_add_supplier: true
        }
    },
    methods: {
        open(obj) {
            this.if_add_supplier = obj.if_add_supplier
            this.callback = obj.callback || function() {}
            if (obj.data) {
                this.form = JSON.parse(JSON.stringify(obj.data))
            } else {
                this.form = {
                    name: '',
                    phone: '',
                    remarks: ''
                }
            }
            this.dialogVisible = true
        },

        confirm() {
            this.validator().then(() => {
                if (this.if_add_supplier) {
                    this.addSupplier()
                } else {
                    this.editSupplier()
                }
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        cancel() {
            this.dialogVisible = false
        },

        addSupplier() {
            this.$fetch.post({
                url: '/firm',
                params: this.form
            }).then(data => {
                this.cancel()
                this.$refs.addSupplierSuccess.open(data.firm_dict)
                this.callback()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        editSupplier() {
            this.$fetch.put({
                url: `/firm/${this.form.id}`,
                params: {
                    action: 'edit_firminfo',
                    ...this.form
                }

            }).then(data => {
                this.openMessage(1, '编辑供货商成功')
                this.cancel()
                this.callback()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        deleteSupplier() {
            this.$myWarning({
                message: '确定要删除吗？'
            }).then(() => {
                this.$fetch.delete({
                    url: `/firm/${this.form.id}`,
                    params: this.form
                }).then(data => {
                    this.cancel()
                    this.callback()
                    this.openMessage(1, '删除供货商成功')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(e => {})
        },

        validator() {
            let validator = new this.$Validator()

            validator.add('isEmpty', this.form.name, '请输入供货商姓名')
            // validator.add('isPhone', this.form.phone, '请输入正确的电话号码')

            return validator.start()
        }
    },
    components: {
        addSupplierSuccess
    }
}
</script>

<style lang="scss" scoped>
.delete_supplier{
    position: absolute;
    top:12px;
    left:103px;
    width: 94px;
    height: 26px;
    line-height: 26px;
    border: 1px solid #FF6666;
    border-radius: 13px;
    font-size: 14px;
    color: #FF6666;
    text-align: center;
    cursor: pointer;
}
</style>
