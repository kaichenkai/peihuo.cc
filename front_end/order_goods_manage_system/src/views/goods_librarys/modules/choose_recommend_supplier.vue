<template>
    <el-dialog
        title="选择供货商"
        :visible.sync="dialogVisible"
        width="375px">
        <div style="max-height:282px;overflow-y:auto;">
            <el-checkbox-group v-model="checkList">
                <div class="clear_both" v-for="(item,index) in firm_list" :key="index">
                    <div class="left"><el-checkbox :label="item.id">{{item.name}}</el-checkbox></div>
                    <div class="right">
                        <!-- <div class="up">{{item.name}}</div> -->
                        <div class="down" v-show="showRemark(item.id)"><span>备注：</span><input type="text" v-model="item.remarks"></div>
                    </div>
                </div>
            </el-checkbox-group>
        </div>
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
            checked: '',
            checkList: [],
            firm_list: []
        }
    },

    methods: {
        showRemark(id) {
            return this.checkList.includes(id)
        },
        getFirmList() {
            this.$fetch.get({
                url: '/station/firm/list',
                params: {
                    limit: 1000
                }
            }).then(data => {
                this.firm_list = data.firm_list
                for (let item of this.good_item.recommend_firm) {
                    for (let item1 of this.firm_list) {
                        if (item.id === item1.id) {
                            item1.remarks = item.recommend_remarks
                        }
                    }
                }
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        open(obj) {
            this.dialogVisible = true
            this.good_item = obj
            this.checkList = []
            for (let item of obj.recommend_firm) {
                this.checkList.push(item.id)
            }
            this.getFirmList()
        },
        cancel() {
            this.dialogVisible = false
        },
        confirm() {
            let firmList = this.firm_list.filter(ele => {
                return this.checkList.includes(ele.id)
            })
            firmList.map(ele => {
                ele.firm_id = ele.id
            })
            this.$fetch.put({
                url: `/station/goods/${this.good_item.id}`,
                params: {
                    action: 'set_recommend_firm',
                    firm_list: firmList
                }
            }).then(() => {
                this.openMessage(1, '添加成功')
                this.cancel()
                this.$emit('operateSuccess')
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    }
}
</script>
<style lang="scss" scoped>
    .clear_both{
        overflow: hidden;
        margin-bottom: 15px;
        .left{
            float: left;
        }
        .right{
            float: right;
            width: 310px;
            .up{
                height: 20px;
                line-height: 20px;
                font-size: 14px;
                color: #333333;
            }
            .down{
                position: relative;
                height: 38px;
                margin-top: 5px;
                padding-left: 8px;
                line-height: 38px;
                font-size: 14px;
                color: #333333;
                background: #F9F9F9;
                span{
                    font-size: 14px;
                    color: #999999;
                }
                input{
                    height: 28px;
                    outline: none;
                    border: none!important;
                    background-color: #f9f9f9;
                }
                &::after{
                    position: absolute;
                    content: '';
                    width: 0;
                    height: 0;
                    top: -10px;
                    left: 11px;
                    border: 5px solid transparent;
                    border-bottom-color: #f9f9f9;
                }
            }
        }
    }
    /deep/ .el-dialog .el-dialog__footer{
        box-shadow: 0 -4px 6px 0 rgba(0, 0, 0, 0.04);
    }
    /deep/ .el-checkbox__label{
        display: inline-block;
        width: 310px;
    }
    /deep/ .el-tooltip__popper.is-dark{
        font-size: 14px;
    }
</style>
