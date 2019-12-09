<template>
    <div class="table-data-filter">
        <div class="header-select" ref="headerHandler">
            <span>{{title}}<span v-if="choosed.length > 0">({{choosed.length}})</span></span><i class="el-icon el-icon-caret-bottom"></i>
            <input type="text" @click="handlerClick" @blur="handlerBlur" ref="input">
        </div>
        <transition name="height-fade">
            <div class="search-container" v-if="isShowSearch" ref="searchHandler" @click="searchClick">
                <div class="check-all">
                    <el-checkbox :disabled="disableCheckAll" v-model="checkAll" :indeterminate="isIndeterminate">{{allString}}</el-checkbox>
                </div>
                <i class="line"></i>
                <div class="center">
                    <div class="search">
                        <input type="text" v-if="items.length > 8" @click.stop ref="search" v-model="search" @focus="inputFocus" @blur="inputBlur" placeholder="请输入搜索内容" />
                        <i v-if="search" @click="search = ''" class="el-icon el-icon-circle-close"></i>
                    </div>
                    <!-- <input type="text"> -->
                    <el-checkbox-group style="display: block" v-model="choosed">
                        <div>
                            <p v-for="(item) in listItem" :key="item[itemKeyCode]">
                                <el-checkbox :label="item[itemKeyCode]">{{item[itemKeyName]}}</el-checkbox>
                                <span class="arrow arrow-animate"  @click.stop="showThisOne(item)">
                                    <img src="~@/assets/images/a20.png" alt="">
                                    <img src="~@/assets/images/a20.png" alt="">
                                    <img src="~@/assets/images/a20.png" alt="">
                                </span>
                            </p>
                        </div>
                    </el-checkbox-group>
                </div>
                <div class="btn-wrapper">
                    <i class="line"></i>
                    <button class="btn confirm" @click.stop="confirm">确认</button>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
export default {
    data() {
        return {
            isFouce: false,
            isShowSearch: false,
            checkAll: false,
            disableCheckAll: false,
            isIndeterminate: true,
            search: '',
            listItem: []
        }
    },

    props: {
        title: String, // 表头默认文字
        allString: { // 选择所有默认文字
            default: '选择所有',
            type: String
        },
        itemKeyName: { // 多选框后面的名字
            default: 'name',
            type: String
        },
        itemKeyCode: { // 根据这个字段得到筛选后的id数组
            default: 'id',
            type: String
        },
        items: { // 多选框列表
            default: () => [],
            type: Array
        },
        value: { // 用于 v-model绑定值
            default: () => [],
            type: Array
        }
    },

    computed: {
        choosed: {
            get() {
                return this.value
            },

            set(value) {
                this.$emit('input', value)
            }
        }
    },

    watch: {
        isFouce(newVal) {
            if (newVal) {
                this.isShowSearch = true
            } else {
                this.isShowSearch = false
            }
        },

        search(newVal) {
            if (newVal.length > 0) {
                this.checkAll = false
                this.disableCheckAll = true
            } else {
                this.disableCheckAll = false
            }

            this.listItem = this.items.filter(value => {
                if (value[this.itemKeyName].indexOf(newVal) !== -1) {
                    value.isHover = false
                    return value
                }
            })
        },

        items(newVal) {
            this.listItem = newVal.map(value => {
                value.isHover = false
                return value
            })
            this.checkAll = true
        },

        choosed(newVal) {
            if (newVal.length === 0) {
                this.checkAll = false
                this.isIndeterminate = false
            } else if (this.items.every(value => newVal.includes(value[this.itemKeyCode]))) {
                this.checkAll = true
                this.isIndeterminate = false
            } else {
                this.isIndeterminate = true
            }
        },

        checkAll(newVal) {
            if (newVal) {
                this.choosed = this.items.map(value => value[this.itemKeyCode])
            } else {
                this.choosed = []
            }
        }
    },

    beforeDestroy() {
        clearInterval(this.timer)
    },

    /**
     * 大致的实现逻辑：
     * 1:因为饿了么表头的默认属性是overflow:hidden，所以无法使用绝对定位使下拉框出现在页面中
     * 所以通过点击表头时，计算表头的坐标，将下拉框fixed到一个固定在屏幕上的位置
     * 同时使用定时器轮询表头的位置是否改变，如果改变则隐藏下拉框。
     *
     * 2: 利用input的focus以及blur事件，检测是否应该显示以及关闭下拉框
     */
    methods: {
        /**
         * 点击表头后
         */
        handlerClick() {
            if (!this.isFouce) {
                this.isFouce = true
                let headerRect = this.$refs.headerHandler.getBoundingClientRect()
                this.$nextTick(function() {
                    this.$refs.searchHandler.style.top = headerRect.top + 38 + 'px'
                    this.$refs.searchHandler.style.left = headerRect.left + 'px'
                })
                this.timer = setInterval(() => {
                    let nowPositon = this.$refs.headerHandler.getBoundingClientRect()
                    if (headerRect.top !== nowPositon.top || headerRect.left !== nowPositon.left) {
                        this.isShowSearch = false
                        clearInterval(this.timer)
                        this.$refs.input.blur()
                    }
                }, 100)
            } else {
                this.isFouce = false
                this.$refs.input.blur()
            }
        },

        searchClick() {
            clearTimeout(this.handlerCloseTimer)
            this.isFouce = true
            this.$refs.input.focus()
        },

        handlerBlur() {
            this.handlerCloseTimer = setTimeout(() => {
                this.isFouce = false
                clearInterval(this.timer)
            }, 200)
        },

        inputFocus() {
            clearTimeout(this.handlerCloseTimer)
        },

        inputBlur() {
            this.handlerCloseTimer = setTimeout(() => {
                this.isFouce = false
                clearInterval(this.timer)
            }, 200)
        },

        showThisOne(item) {
            this.choosed = [item[this.itemKeyCode]]
            this.close()
            this.$emit('confirm')
        },

        close() {
            this.isFouce = false
        },

        confirm() {
            this.$emit('confirm')
        }
    }
}
</script>

<style lang="scss" scoped>
.table-data-filter {
    position: relative;
    display: inline-grid;
    padding: 0;
    margin: 0;
    width: 100%;

    div {
        padding: 0;
    }

    .header-select {
        position: relative;
        height: 28px;
        line-height: 28px;
        width: 100%;
        background: #fff;
        font-size: 14px;
        padding: 0 10px;
        color: #333333;

        input {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            opacity: 0;
            cursor: pointer;
        }

        i {
            float: right;
            line-height: 28px;
        }
    }

    .search-container {
        position: fixed;
        top: 50px;
        width: 230px;
        height: 380px;
        padding: 0px !important;
        background: #fff;
        z-index: 1;
        box-shadow: 0 0 10px 0 rgba(0,0,0,0.15);

        .check-all {
            display: block;
            padding: 0 10px;
            height: 40px;

            /deep/ .el-checkbox {
                .el-checkbox__label {
                    font-weight: bold;
                    color: #333;
                }
            }
        }

        .line {
            display: block;
            height: 1px;
            background: #E7E7E7;
        }

        .center {
            position: absolute;
            top: 40px;
            bottom: 50px;
            left: 0;
            right: 0;
            overflow-y: auto;

            .search {
                position: relative;
                display: block;
                margin-top: 6px;

                input {
                    display: block;
                    margin: 0 auto;
                    padding: 0 30px 0 10px;
                    width: 96%;
                    height: 30px;
                    border: 1px solid #999999;
                    border-radius: 3px;
                    font-size: 14px;
                    color: #999999;
                }

                i {
                    position: absolute;
                    top: 50%;
                    right: 10px;
                    transform: translateY(-50%);
                    cursor: pointer;
                }
            }

            /deep/ .el-checkbox {
                display: inline-block;
                width: 180px;
                margin: 8px 0px 8px 10px;
                line-height: 24px;
                span {
                    display: inline-block;
                    vertical-align: top;
                    white-space: pre-line;
                }
                .el-checkbox__label {
                    width: 160px;
                    color: #333;
                }
            }

            .arrow {
                display: inline-block;
                margin-left: 6px;
                cursor: pointer;

                img {
                    display: inline-block;
                    width: 8px;
                }
            }

            .arrow-animate {
                @for $i from 1 through 3 {
                    img:nth-of-type(#{$i}) {
                        animation: twinkle#{$i} 1s infinite;
                        animation-delay: .2s * $i;
                    }

                    @keyframes twinkle#{$i} {
                        0% {
                            opacity: 0;
                        }

                        50% {
                            opacity: 1;
                        }

                        100% {
                            opacity: 0;
                        }
                    }
                }
            }
        }

        .btn-wrapper {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 0;
            height: 50px;
            text-align: center;
        }

        .confirm {
            display: inline-block;
            margin-top: 10px;
            width: 180px;
            height: 30px;
            background: #009688;
            border-radius: 3px;
            color: #fff;
            font-size: 14px;
        }
    }

    .height-fade-enter-active {
        transition: all .3s ease;
    }
    .height-fade-leave-active {
        transition: all .3s ease;
    }
    .height-fade-enter, .height-fade-leave-to
    /* .slide-fade-leave-active for below version 2.1.8 */ {
        height: 30%;
        opacity: 0;
    }
}
</style>
