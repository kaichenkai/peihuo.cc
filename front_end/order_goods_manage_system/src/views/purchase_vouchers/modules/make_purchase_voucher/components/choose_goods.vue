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
                <el-tab-pane v-loading="isLoading" label="商品选择列表" name="first" style="height: 380px;overflow-y: auto;">
                    <div class="tool" v-if="form.search">
                        <span @click="form.search = ''" class="back"><img src="~@/assets/images/a1.png" alt="">返回</span>
                        <span class="search-detail">所有商品中搜到<span>{{form.search}}</span>共{{goodsList.length}}个商品</span>
                    </div>
                    <div>
                        <span  :class="{'choosed': ischoosedGoodsHave(item), 'removed': item.isRemoved}" @click="checkItem(item)" class="item" v-for="(item, index) in unChoosedGoodsList" :key="index">{{item.name}}
                            <img v-if="ischoosedGoodsHave(item)" src="~@/assets/images/a2.png" alt="">
                        </span>
                        <div v-if="unChoosedGoodsList.length == 0" class="has-no-more">
                            <img src="~@/assets/images/a17.png" alt="">
                            <p>暂无待选择商品～</p>
                        </div>
                    </div>
                    <div v-if="form.search && !isLoading" class="choosed-container">
                        <div v-for="(goodsList, index) in cacheData.choosedList" :key="index" v-if="goodsList.length > 0">
                            <p v-if="index == 0 && goodsList.some(goods => isGoodsListHave(goods))">正常订货：</p>
                            <p v-if="index == 1 && goodsList.some(goods => isGoodsListHave(goods))">可能缺货：</p>
                            <p v-if="index == 2 && goodsList.some(goods => isGoodsListHave(goods))">暂时无货：</p>
                            <div>
                                <span class='item choosed' v-if="isGoodsListHave(item)" v-for="(item) in goodsList" style="border:none;opacity: .7" :key="item.goods_id">{{item.goods_name || item.name}}
                                    <img src="~@/assets/images/a2.png" alt="">
                                </span>
                            </div>
                        </div>
                    </div>
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
    </el-dialog>
</template>

<script>
/**
 * 业务逻辑：打开商品选择时需要判断服务器返回的商品是否已经被选择，如果选择了，那么就不需要将选中的商品展示了
 * 其次，进行搜索时，如果搜索到的商品有选中的商品，那么需要将选中的商品展示在下方，但是是不可点击状态
 * 再者，如果在意向单页面如果将选中的商品移出意向单后，那么下次选择商品，则需要将移出的商品标记并且放置在列表最前面
 * 选中的商品以及意向单移出的商品都通过open函数传入进来，并且存储在cacheData中
 */
const _ = require('lodash')
export default {
    data() {
        return {
            isLoading: false,
            dialogVisible: false,
            activeName: 'first',
            choosedList: [],
            cacheData: {},
            goodsList: [],
            unChoosedGoodsList: [],
            form: {
                search: ''
            }
        }
    },

    watch: {
        'form.search'(val) {
            this.isLoading = true
            this.debounceSearch()
        }
    },

    created() {
        this.debounceSearch = _.debounce(this.getGoodsList, 500)
    },

    methods: {
        handleClose() {
            this.cancel()
        },
        /**
         * choosedList {Array} goodsList
         */
        open(obj = { choosedList: [] }) {
            this.cacheData = obj
            this.dialogVisible = true
            this.callback = obj.callback || function() {}
            this.getGoodsList()
        },

        getGoodsList() {
            this.isLoading = true
            return this.$fetch.get({
                url: `/station/goods/list`,
                params: {
                    ...this.form,
                    page: 0,
                    limit: 1000
                }
            }).then(data => {
                // console.log(data)
                this.goodsList = data.goods_list
                this.setUnChoosedGoodsList()
            }).catch(e => {
                console.error('获取商品列表失败')
            }).finally(() => {
                this.isLoading = false
            })
        },

        setUnChoosedGoodsList() {
            let unChoosedGoodsList = this.goodsList.filter(value => { // 将没有选择的商品筛选出来
                for (let i in this.cacheData.choosedList) {
                    for (let j = 0; j < this.cacheData.choosedList[i].length; j++) {
                        if (this.cacheData.choosedList[i][j].goods_id === value.id) {
                            return false
                        }
                    }
                }
                return true
            }).map(value => { // 将移出意向单的商品添加标志位
                if (this.cacheData.removedList.includes(value.id)) {
                    value.isRemoved = true
                }
                return value
            }).sort((a, b) => { // 将移出意向单的商品放在列表最前方
                if (a.isRemoved) {
                    return -1
                } else {
                    return 1
                }
            })

            this.$set(this, 'unChoosedGoodsList', unChoosedGoodsList)
            console.log(this.unChoosedGoodsList)
        },

        isGoodsListHave(goods) {
            return this.goodsList.some(_goods => _goods.id === goods.id || _goods.id === goods.goods_id)
        },

        ischoosedGoodsHave(goods) {
            return this.choosedList.some(_goods => _goods.id === goods.id)
        },

        checkItem(goods) {
            // console.log(this.choosedList)
            if (this.ischoosedGoodsHave(goods)) {
                this.choosedList.splice(this.choosedList.findIndex(_goods => _goods.id === goods.id), 1)
            } else {
                this.choosedList.push(goods)
            }
        },

        comfirmChoosed() {
            this.$emit('choosed', this.choosedList)
            this.callback({
                ...this.cacheData,
                goods: this.choosedList
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
.choose-goods-container {
    .header {
        position: relative;

        .el-tabs__nav {
            .el-tabs__item {
                font-size: 14px;
            }
        }

        .tool {
            margin-top: 15px;
            font-size: 14px;
            color: #333333;

            .back {
                color: #999999;
                cursor: pointer;
            }
            img {
                vertical-align: middle;
                margin-right: 5px;
                width: 18px;
                height: 18px;
            }

            .search-detail {
                margin-left: 14px;
                color: #333333;

                span {
                    color: #009688;
                }
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

    .choosed-container {
        > div {
            margin-top: 15px;
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

    .removed {
        background: rgba(0,150,136,0.20);
        border: 1px solid rgba(0,150,136,0.20);
    }

    .has-no-more {
        text-align: center;
        margin-top: 120px;
        margin-bottom: 60px;
    }
}

</style>
