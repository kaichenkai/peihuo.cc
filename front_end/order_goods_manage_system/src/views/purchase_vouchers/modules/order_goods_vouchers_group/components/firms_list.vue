<template>
<transition name="slide-fade-y">
    <div class="firms-container" @click.stop ref="firmsContainer" v-show="isShowFirmsContainer">
        <div class="nav-bar">
            <div :class="{'active': !isShowAllFirms}" @click="isShowAllFirms = false">指定供货商列表</div>
            <div :class="{'active': isShowAllFirms}" @click="isShowAllFirms = true">所有供货商列表</div>
        </div>
        <div class="goods-firms-container" v-show="!isShowAllFirms">
            <p v-if="isGoodsHaveNoFirms" class="no-firms-hint">该商品未设置供货商，可从系统所有供货商中选择</p>
            <ul v-else>
                <li v-for="item in goodsFirmList" :key="item.id">
                    <div class="remark" v-if="item.recommend_remarks && item.isShowRemark">
                        {{item.recommend_remarks}}
                    </div>
                    <p @click="chooseTheFirm(item)" @mouseleave="item.isShowRemark = false" @mouseenter="item.isShowRemark = true" :class="{check: choosedList.includes(item.id)}">
                        <span class="name-info">
                            <span class="recommend" v-if="item.recommend">推荐</span>
                            <span class="name">{{item.name}}</span>
                        </span>
                        <span class="phone-number">{{item.phone}}</span>
                        <span  v-if="!isGoodsHaveNoFirms" class="purchase-times">采购{{item.purchase_times}}次</span>
                        <img src="~@/assets/images/a2.png" v-if="choosedList.includes(item.id)" alt="">
                    </p>
                </li>
            </ul>
        </div>
        <div class="all-firms-container" v-show="isShowAllFirms">
            <div class="search-box">
                <el-input
                placeholder="请输入供货商姓名/手机号码搜索"
                v-model="search"
                clearable>
                </el-input>
            </div>
            <ul>
                <li v-for="item in showAllFirmList" :key="item.id">
                    <p @click="chooseTheFirm(item)" :class="{check: choosedList.includes(item.id)}">
                        <span class="name-info">
                            <span class="recommend" v-if="item.recommend">推荐</span>
                            <span class="name">{{item.name}}</span>
                        </span>
                        <span class="phone-number">{{item.phone}}</span>
                        <!-- <span  v-if="!isGoodsHaveNoFirms" class="purchase-times">采购{{item.purchase_times}}次</span> -->
                        <img src="~@/assets/images/a2.png" v-if="choosedList.includes(item.id)" alt="">
                    </p>
                    <!-- <p class="remark" v-if="item.remarks">备注：{{item.remarks}}</p> -->
                </li>
            </ul>
        </div>
    </div>
</transition>
</template>

<script>
export default {
    data() {
        return {
            isShowFirmsContainer: false,
            goodsFirmList: [],
            choosedList: [],
            choosedFirm: {},
            AllfirmList: [],
            showAllFirmList: [],
            isGoodsHaveNoFirms: false,
            isShowAllFirms: false,
            search: ''
        }
    },

    props: {
        goodsData: {}
    },

    watch: {
        search: function(newVal) {
            if (newVal) {
                this.showAllFirmList = this.AllfirmList.filter(value => {
                    if (value.phone.indexOf(newVal) !== -1 || value.name.indexOf(newVal) !== -1) {
                        return true
                    } else {
                        return false
                    }
                })
            } else {
                this.showAllFirmList = this.AllfirmList
            }
        }
    },

    created() {
        // this.getFirmsList()
        this.getAllfirmsList()
    },

    methods: {
        open(obj) {
            this.isShowFirmsContainer = true
            this.choosedList = obj.choosedList
            this.callback = obj.callback || function() {}

            this.getFirmsListByGoodsId().then(data => {
                if (data.firm_list.length === 0) {
                    // this.goodsFirmList = this.AllfirmList
                    this.isGoodsHaveNoFirms = true
                } else {
                    this.isGoodsHaveNoFirms = false
                }
            })
        },

        close() {
            this.isShowFirmsContainer = false
        },

        getFirmsListByGoodsId() {
            return this.$fetch.get({
                url: this.goodsData.goods_id + '/firm/list',
                params: {
                    page: 0,
                    limit: 10000
                }
            }).then(data => {
                this.goodsFirmList = data.firm_list.map(value => {
                    value.isShowRemark = false
                    return value
                })
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取供货商失败')
            })
        },

        getAllfirmsList() {
            this.$fetch.get({
                url: '/station/firm/list',
                params: {
                    page: 0,
                    limit: 10000
                }
            }).then(data => {
                this.showAllFirmList = this.AllfirmList = data.firm_list
            }).catch(e => {
                this.openMessage(0, e || '获取供货商失败')
            })
        },

        chooseTheFirm(item) {
            if (this.choosedList.includes(item.id)) {
                return this.openMessage(2, '该供应商已在采购列表数据中')
            }
            this.choosedFirm = item
            this.callback(item)
            this.isShowFirmsContainer = false
        }
    }
}
</script>

<style lang="scss" scoped>
.firms-container {
    position: absolute;
    left: 10px;
    width: 660px;
    height: 340px;
    background: #fff;
    border: 1px solid #DDDDDD;
    overflow: auto;

    .nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0 auto;
        margin-top: 15px;
        margin-bottom: 15px;
        width: 270px;
        height: 40px;
        background: #F9F9F9;
        border: 1px solid #F2F2F2;
        border-radius: 20px;
        user-select: none;

        > div {
            margin-left: 4px;
            margin-right: 4px;
            height: 32px;
            width: 129px;
            border-radius: 16px;
            text-align: center;
            line-height: 32px;
            background: #f9f9f9;
            font-size: 14px;
            color: #333333;
            cursor: pointer;
        }

        .active {
            background: #00968822;
            color: #009688;
        }
    }

    .no-firms-hint {
        margin: 15px 0;
        margin-top: 60px;
        padding-left: 10px;
        font-size: 14px;
        color: #666;
        text-align: center;
    }

    ul {
        height: 200px;
        overflow: auto;
    }

    li {
        position: relative;
        height: 30px;
        margin: 10px;

        > .remark {
            position: absolute;
            top: -28px;
            padding: 4px 10px;
            background: #fff;
            font-size: 12px;
            // height: 15px;
            color: #333333;
            z-index: 1;
            box-shadow: 0 2px 4px 0 rgba(0,0,0,0.21);
            border-radius: 4px;

            &:before {
                content: '';
                position: absolute;
                left: 50%;
                margin-left: -5px;
                bottom: -5px;
                height: 10px;
                width: 10px;
                transform: rotate(45deg);
                background: #fff;
            }
        }

        p {
            display: inline-flex;
            justify-content: space-between;
            vertical-align: middle;

            &:nth-of-type(1) {
                position: relative;
                padding: 5px 5px 5px 9px;
                width: 100%;
                background: #F9F9F9;
                border-radius: 4px;
                font-size: 14px;
                color: #333333;
                cursor: pointer;
                overflow: hidden;

                img {
                    position: absolute;
                    right: 0;
                    bottom: 0;
                    height: 18px;
                }
            }
        }

        .check {
            background: #00968822 !important;
        }

        .name-info {
            display: inline-block;
            vertical-align: middle;
            width: 380px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;

            .recommend {
                display: inline-block;
                width: 39px;
                height: 16px;
                margin-right: 5px;
                background: #FF7C56;
                border-radius: 8px;
                font-size: 12px;
                color: #FFFFFF;
                text-align: center;
                line-height: 16px;
            }

            .name {
                font-size: 14px;
                color: #333333;
                white-space: nowrap;
            }
        }

        .phone-number {
            display: inline-block;
            width: 92px;
            margin-right: 10px;
            font-size: 14px;
            color: #333333;
        }

        .purchase-times {
            white-space: nowrap;
            text-overflow: ellipsis;
            width: 88px;
            display: inline-block;
            vertical-align: middle;
            overflow: hidden;
        }
    }

    .all-firms-container {
        .search-box {
            padding: 0 15px;
            margin-bottom: 10px;

            /deep/ .el-input__inner  {
                // margin-left: 15px;
                border-radius: 20px;
            }
        }
    }
}

.slide-fade-y-enter-active {
    transition: all .5s ease;
}
.slide-fade-y-leave-active {
    transition: all .5s ease;
}
.slide-fade-y-enter, .slide-fade-y-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
    transform: translateY(-20px);
    opacity: 0;
}

.slide-fade-y-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
    transform: translateY(20px);
    opacity: 0;
}
</style>
