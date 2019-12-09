<template>
    <el-dialog
        title="库存修改"
        :visible.sync="dialogVisible"
        width="380px">
        <!-- <search></search> -->
        <p>{{goodsData.name}}</p>
        <el-form :inline="true" label-position="top" :model="form" ref="form">
            <el-form-item label="" style="width:350px;font-size:16px">
                <el-input type="number" v-removeMouseWheelEvent v-selectTextOnFocus v-model.trim="goodsData.stock" placeholder="请填写库存" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="" style="width:350px;font-size:16px" prop=''>
                <el-input v-model="form.remarks" placeholder="填写备注" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">保存</button>
            <button class="btn cancel" @click="close">取消</button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            form: {
                stock: '',
                remarks: ''
            },
            goodsData: {}
        }
    },

    methods: {
        open(obj) {
            this.id = obj.data.id
            this.callback = obj.callback || function() {}
            this.dialogVisible = true
            this.goodsData = JSON.parse(JSON.stringify(obj.data))
        },

        confirm() {
            this.form.stock = this.goodsData.stock
            if (String(this.goodsData.stock).length === 0) {
                return this.openMessage(0, '请输入库存')
            } else if (isNaN(this.goodsData.stock)) {
                return this.openMessage(0, '库存必须是数字')
            }
            this.$fetch.put({
                url: '/warehouse/stock/' + this.id,
                params: this.form
            }).then(data => {
                this.dialogVisible = false
                this.openMessage(1, '修改成功')
                this.callback(this.goodsData.stock)
                this.close()
            }).catch(e => {
                this.openMessage(0, '修改失败,' + e)
            })
        },

        close() {
            this.dialogVisible = false
            this.form = {
                stock: '',
                remarks: ''
            }
        }
    }
}
</script>

<style lang="scss" scoped>
p {
    margin-bottom: 10px;
    color: #333;
    font-weight: bold;
}
.inline {
    .el-form-item{
        margin-bottom: 20px;
    }
}
</style>
