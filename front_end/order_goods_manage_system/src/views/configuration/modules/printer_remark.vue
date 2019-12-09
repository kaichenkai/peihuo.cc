<template>
    <el-dialog
        title="备注名称"
        :visible.sync="dialogVisible"
        width="380px">
        <el-form :inline="true" label-position="top" class="inline" :model="print_data" style="height:40px;" ref="form">
            <el-form-item label="" style="width:350px;padding-left:10px;font-size:16px">
                <el-input @keydown.native.enter="confirm" v-model="print_data.remarks" placeholder=""></el-input>
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
            dialogVisible: false
        }
    },

    props: {
        print_data: {
            default() {
                return {}
            },
            type: Object
        }
    },

    methods: {
        open() {
            this.dialogVisible = true
        },

        confirm() {
            if (this.print_data.remarks.length > 0) {
                this.$fetch.put({
                    url: `/printer/${this.print_data.id}`,
                    params: this.print_data
                }).then(data => {
                    this.openMessage(1, '修改备注名称成功')
                    this.dialogVisible = false
                    this.$emit('finishRemark')
                })
            } else {
                this.openMessage(0, '请输入备注名称')
            }
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
