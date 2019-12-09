<template>
    <el-dialog
        title="名称更改"
        :visible.sync="dialogVisible"
        width="380px">
        <el-form :inline="true" label-position="top" class="inline" :model="stationInfo" style="height:40px;" ref="form">
            <el-form-item label="" style="width:350px;padding-left:10px;font-size:16px">
                <el-input v-model.trim="stationInfo.name" placeholder="" @keyup.enter.native="confirm"></el-input>
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
        stationInfo: {
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
            if (this.stationInfo.name.length > 0) {
                this.$fetch.put({
                    url: `/station/${this.stationInfo.id}`,
                    params: {
                        name: this.stationInfo.name
                    }
                }).then(data => {
                    this.openMessage(1, '修改成功')
                    this.dialogVisible = false
                    this.$emit('editStationName')
                }).catch(erro => {
                    this.openMessage(0, erro)
                })
            } else {
                this.openMessage(0, '请输入名称')
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
