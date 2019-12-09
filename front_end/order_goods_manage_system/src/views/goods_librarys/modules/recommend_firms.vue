<template>
    <el-dialog
    title="选择供货商"
    :visible.sync="dialogVisible"
    width="375px">
    <div class="firm-container">

    </div>
    <span slot="footer" class="dialog-footer">
        <button class="btn comfirm" @click="dialogVisible = false">确 定</button>
        <button class="btn cancel" @click="dialogVisible = false">取 消</button>
    </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: true,
            firmList: []
        }
    },

    created() {
        this.getFirmList()
    },

    methods: {
        getFirmList() {
            this.$fetch.get({
                url: '/station/firm/list?page=0&limit=1000'
            }).then(data => {
                this.firmList = data.firm_list
            }).catch(e => {
                this.openMessage(0, e || '获取供货商列表失败')
            })
        }
    }
}
</script>

<style lang="scss" scoped>
.firm-container {
    height: 300px;
    overflow-y: auto;
}
</style>
