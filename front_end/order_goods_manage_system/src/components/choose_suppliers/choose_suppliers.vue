<template>
    <el-dialog
    class="choose-suppliers-container"
    title="选择供货商"
    :visible.sync="dialogVisible"
    :before-close="handleClose"
    width="750px">
    <div>
        <div class="header">
            <el-tabs v-model="activeName">
                <el-tab-pane label="已选供货商" name="second" style="max-height: 420px;overflow-y: auto;">
                    <span class="item choosed" v-for="(item, index) in [...choosedList]" :key="index">
                        <p>{{item.name}}</p>
                        <p>{{item.phone||'暂无电话'}}</p>
                        <img src="~@/assets/images/a2.png" alt="">
                    </span>
                </el-tab-pane>
                <el-tab-pane label="供货商选择列表" name="first" style="max-height: 420px;overflow-y: auto;">
                    <span :class="{'choosed': isChoosedSuppliersHave(item)}" @click="checkItem(item)" class="item" v-for="(item, index) in suppliersList" :key="index">
                        <p>{{item.name}}</p>
                        <p>{{item.phone||'暂无电话'}}</p>
                        <img v-if="isChoosedSuppliersHave(item)" src="~@/assets/images/a2.png" alt="">
                    </span>
                </el-tab-pane>
            </el-tabs>
            <el-input
            class="search"
            placeholder="请输入供货商姓名/手机号"
            v-model="form.search"
            clearable>
            </el-input>
        </div>
    </div>
    <span slot="footer" class="dialog-footer">
        <button @click="comfirmChoosed" class="btn confirm">确认</button><button @click="cancel" class="btn cancel">取消</button>
    </span>
    </el-dialog>
</template>

<script>
var _ = require('lodash')
export default {
    data() {
        return {
            dialogVisible: false,
            activeName: 'first',
            choosedList: [],
            suppliersList: [],
            form: {
                search: ''
            }
        }
    },

    created() {
        this.debouncedGetAnswer = _.debounce(this.searchSupplier, 300)
    },

    watch: {
        'form.search'(val) {
            this.debouncedGetAnswer()
        }
    },

    methods: {
        handleClose() {
            this.cancel()
        },
        searchSupplier() {
            this.getSuppliersList(this.form.search)
        },
        open(obj = { choosedList: [] }) {
            this.cacheData = obj
            this.dialogVisible = true
            this.callback = obj.callback || function() {}
            this.getSuppliersList().then(() => {
                if (!obj.choosedList) return
                this.choosedList = this.suppliersList.filter(value => obj.choosedList.includes(value.id))
            })
        },

        getSuppliersList(str = '') {
            return this.$fetch.get({
                url: `/station/firm/list?search=${str}&page=0&limit=1000`
            }).then(data => {
                // console.log(data)
                this.suppliersList = data.firm_list
            }).catch(e => {
                console.error('获取供应商列表失败')
            })
        },

        isChoosedSuppliersHave(supplier) {
            return this.choosedList.some(_supplier => _supplier.id === supplier.id)
        },

        checkItem(supplier) {
            console.log(this.choosedList)
            if (this.isChoosedSuppliersHave(supplier)) {
                this.choosedList.splice(this.choosedList.findIndex(_supplier => _supplier.id === supplier.id), 1)
            } else {
                this.choosedList.push(supplier)
            }
        },

        comfirmChoosed() {
            this.$emit('choosed', this.choosedList)
            this.callback({
                ...this.cacheData,
                suppliers: this.choosedList
            })
            this.choosedList = []
            this.cancel()
        },

        cancel() {
            this.form.search = ''
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
.choose-suppliers-container {
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

        /deep/ input {
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
        padding-left: 10px;
        padding-top: 2px;
        width: 160px;
        height: 50px;
        margin-top: 10px;
        margin-right: 10px;
        background: #F0F0F0;
        border-radius: 4px;
        font-size: 14px;
        line-height: 22px;
        color: #333333;
        overflow: hidden;
        p:nth-of-type(1){
            font-weight: bold;
        }
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

</style>
