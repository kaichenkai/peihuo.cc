<template>
    <el-dialog
        class="choose-goods-container"
        title="选择商品"
        :visible.sync="dialogVisible"
        :before-close="handleClose"
        width="800px">
        <div>
            <div class="header">
                <el-tabs v-model="activeName">
                    <el-tab-pane label="商品选择列表" name="first" style="max-height: 420px;overflow-y: auto;">
                        <span :class="{'choosed': ischoosedGoodsHave(item)}" @click="checkItem(item)" class="item" v-for="(item, index) in goodsList" :key="index">{{item.name}}
                            <img v-if="ischoosedGoodsHave(item)" src="~@/assets/images/a2.png" alt="">
                        </span>
                    </el-tab-pane>
                </el-tabs>
                <el-input
                class="search"
                placeholder="请输入商品名/首字母"
                v-model="form.search"
                clearable>
                </el-input>
            </div>
        </div>
        <span slot="footer" class="dialog-footer">
            <button @click="comfirmChoosed" class="btn confirm">确认</button><button @click="cancel" class="btn cancel">取消</button>
        </span>
        <el-dialog
            title="新增出库"
            :visible.sync="dialogVisible_1"
            append-to-body
            width="380px">
            <el-form :inline="true" :model="form" style="height:40px;" ref="form" label-width="60">
                <el-form-item label="出库量：">
                    <el-input v-model.trim="form.num" placeholder="输入出库量" @keyup.enter.native="confirm" type="number" style="width:275px;"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <button class="btn confirm" @click="confirm">确认新增</button>
                <button class="btn cancel" @click="cancel_1">取消</button>
            </span>
        </el-dialog>
    </el-dialog>
</template>

<script>
var _ = require('lodash')
export default {
    data() {
        return {
            dialogVisible: false,
            dialogVisible_1: false,
            activeName: 'first',
            choosedList: [],
            goodsList: [],
            form: {
                search: '',
                num: ''
            }
        }
    },

    watch: {
        'form.search'(val) {
            this.debouncedGetAnswer()
        }
    },

    created() {
        this.debouncedGetAnswer = _.debounce(this.searchGoods, 300)
    },

    methods: {
        confirm() {
            if (this.form.num > 0) {
                this.$fetch.post({
                    url: `/warehouse/stockout`,
                    params: {
                        goods_id: this.choosedList[0].id,
                        amount: this.form.num
                    }
                }).then(data => {
                    this.openMessage(1, '新增成功')
                    this.dialogVisible = false
                    this.dialogVisible_1 = false
                    this.$emit('addStockOut')
                }).catch(erro => {
                    this.openMessage(0, erro)
                })
            } else {
                this.openMessage(0, '请输入正确的出库量')
            }
        },
        handleClose() {
            this.cancel()
        },
        searchGoods() {
            this.getGoodsList(this.form.search)
        },

        /**
         * choosedList {Array} id List
         */
        open(obj = {}) {
            this.dialogVisible = true
            this.callback = obj.callback || function() {}
            this.getGoodsList()
        },

        getGoodsList(str = '') {
            return this.$fetch.get({
                url: `/station/goods/list?search=${str}&page=0&limit=1000`
            }).then(data => {
                // console.log(data)
                this.goodsList = data.goods_list
            }).catch(e => {
                console.error('获取商品列表失败')
            })
        },

        ischoosedGoodsHave(goods) {
            return this.choosedList.some(_goods => _goods.id === goods.id)
        },

        checkItem(goods) {
            this.choosedList = [goods]
        },

        comfirmChoosed() {
            this.dialogVisible_1 = true
            this.form.num = ''
        },

        cancel() {
            this.form.search = ''
            this.dialogVisible = false
        },

        cancel_1() {
            this.dialogVisible_1 = false
        }
    }
}
</script>

<style lang="scss" scoped>
.choose-goods-container {
    .header {
        position: relative;

        .el-tabs__nav {
            .el-tabs__item {
                font-size: 14px;
            }
        }
    }

    .search {
        position: absolute;
        right: 10px;
        top: 0px;
        width: 300px;
        height: 32px;

        /deep/ .el-input__inner {
            border-radius: 0;
            height: 100%;

            &:focus {
                border-color: #009688;
                outline: 0;
            }
        }
    }

    .item {
        position: relative;
        display: inline-block;
        padding: 10px;
        margin-top: 10px;
        margin-right: 10px;
        background: #F0F0F0;
        border-radius: 4px;
        font-size: 14px;
        line-height: 22px;
        color: #333333;
        overflow: hidden;
        border: 1px solid #F0F0F0;
        cursor: pointer;

        img {
            position: absolute;
            right: 0;
            bottom: 0;
        }
    }

    .choosed {
        background: rgba(0,150,136,0.20);
        border: 1px solid #009688;
    }
}
/deep/ .el-form .el-form-item__label{
    line-height: 40px!important;
}

</style>
