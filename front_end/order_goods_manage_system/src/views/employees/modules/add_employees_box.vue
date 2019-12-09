<template>
    <el-dialog
        title="添加员工"
        :visible.sync="dialogVisible"
        width="400px">
        <!-- <search></search> -->
        <el-form :inline="true" :rules="rules" label-position="top" class="inline" :model="form" ref="form">
            <el-form-item label="输入手机号/个人ID" style="width:350px;padding-left:10px;font-size:16px" prop='phone'>
                <el-input v-model="form.phone" placeholder="" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">下一步</button>
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
                phone: ''
            },
            rules: {
                phone: [{ required: true, message: '请输入手机号或个人ID', trigger: 'blur' }]
            }
        }
    },

    methods: {
        open() {
            this.dialogVisible = true
        },

        confirm() {
            this.$refs['form'].validate((valid) => {
                if (valid) {
                    this.$fetch.get({
                        url: `/accountsearch/${this.form.phone}`,
                        params: {}
                    }).then(data => {
                        if (data.account_data.id) {
                            this.dialogVisible = false
                            this.$emit('nextStep', data.account_data)
                        } else {
                            this.openMessage(0, '该用户不存在')
                        }
                    }).catch(e => {
                        this.openMessage(0, e || '查找用户失败')
                    })
                } else {
                    return false
                }
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
.inline {
    .el-form-item{
        margin-bottom: 20px;
    }
}
</style>
