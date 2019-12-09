<template>
    <div class="edit-quantity-bg" v-show="showDialog" @click="showDialog = false">
        <div class="container" @click.stop>
            <div class="item-container">
                <h2>数据录入</h2>
                <img @click="showDialog = false" class="close" src="~@/assets/images/a11.png" alt="">
                <i class="line"></i>
                <p class="name">{{goodsData.goods_name}}</p>
                <p class="remark">{{goodsData._remarks}}</p>
                <div class="input-container">
                    <div class="input-item" :class="{'active': focus == 0}" @click="focus = 0">
                        <span>分店库存</span>
                        <span>{{goodsData.current_storage}}</span>
                    </div>
                    <div class="input-item" style="margin-left:19px" :class="{'active': focus == 1}" @click="focus = 1">
                        <span>订货量</span>
                        <span>{{goodsData.demand_amount}}</span>
                    </div>
                </div>
            </div>
            <div id="keyboardContainer"></div>
        </div>
    </div>
</template>

<script>
import MiniKeyBoard from '@/assets/js/keyboard.min.js'
import userInputCache from '../../../js/user_input_cache_manage'

export default {
    data() {
        return {
            showDialog: false,
            focus: 0,
            inputList: ['current_storage', 'demand_amount'],
            goodsData: {}
        }
    },

    mounted() {
        this.keyboard = new MiniKeyBoard({
            container: 'keyboardContainer'
        })

        this.keyboard.on('keydown', code => {
            this.keyDown(code)
        })

        this.initKeyDownEvent()
    },

    methods: {
        open(obj) {
            this.showDialog = true
            this.goodsData = obj.data
            this.allGoods = obj.allGoods
            this.demandOrderId = obj.demandOrderId
            this.callback = obj.callback || function() {}
        },

        initKeyDownEvent() {
            const strategy = [
                [/[0-9]/, (code) => {
                    const testDot = /(\.)+/
                    this.goodsData[this.inputList[this.focus]] = this.goodsData[this.inputList[this.focus]] + code

                    if (!testDot.test(this.goodsData[this.inputList[this.focus]])) {
                        this.goodsData[this.inputList[this.focus]] = +this.goodsData[this.inputList[this.focus]]
                    }
                }],

                [/(dot)/, () => {
                    const testDot = /(\.)+/
                    if (!testDot.test(this.goodsData[this.inputList[this.focus]])) {
                        this.goodsData[this.inputList[this.focus]] += '.'
                    }
                }],

                [/(del)/, () => {
                    let str = this.goodsData[this.inputList[this.focus]] + ''
                    str = str.substr(0, str.length - 1)
                    if (str.length > 0) {
                        this.goodsData[this.inputList[this.focus]] = str
                    } else {
                        this.goodsData[this.inputList[this.focus]] = 0
                    }
                }],

                [/(next)$/, () => {
                    this.focus = (this.focus + 1) % 2
                }],

                [/(nextGoods)$/, () => {
                    let nowIndex = this.allGoods.findIndex(goods => goods.goods_id === this.goodsData.goods_id)
                    if (nowIndex !== this.allGoods.length - 1) {
                        this.focus = 0
                        this.goodsData = this.allGoods[++nowIndex]
                    } else {
                        this.$myToast.show('已经是最后一个商品了')
                    }
                }],

                [/(confirm)/, () => {
                    // this.callback({
                    //     current_storage: this.goodsData.current_storage,
                    //     demand_amount: this.goodsData.demand_amount
                    // })
                    this.showDialog = false
                    this.focus = 0
                }]
            ]
            this.strategyMap = new Map(strategy)
        },

        keyDown(code) {
            this.strategyMap.forEach((fn, strategy) => {
                if (strategy.test(code)) {
                    fn(code)
                    this.cacheUserInput()
                }
            })
        },

        cacheUserInput() {
            userInputCache.setData(this.demandOrderId, this.allGoods.map(value => {
                let obj = {}
                obj.remarks = value.remarks
                obj.current_storage = value.current_storage
                obj.demand_amount = value.demand_amount
                obj.wish_order_goods_id = value.wish_order_goods_id

                return obj
            }))
        }
    }
}
</script>

<style lang="scss" scoped>
.edit-quantity-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, .5);
    z-index: 1000;
    // transform: translateZ(3px);

    .container {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 410px;
        background: #fff;
        border-radius: 6px 6px 0 0;

        .close {
            position: absolute;
            top: 8px;
            right: 11px;
            width: 24px;
            height: 24px;
        }

        .item-container {
            margin: 12px 10px 0 10px;

            h2 {
                font-size: 16px;
                color: #009688;
            }

            .line {
                display: block;
                margin: 8px 0 10px 0px;
                height: 2px;
                background: #009688;

            }

            .name {
                margin-bottom: 11px;
                font-size: 16px;
                color: #333333;
            }

            .remark {
                margin-bottom: 20px;
                font-size: 14px;
                color: #FF6666;
                line-height: 16px;
            }

            .input-container {
                display: flex;
                justify-content: space-between;
                max-width: 414px;
            }

            .input-item {
                display: flex;
                // flex: 1;
                flex-direction: column;
                padding: 6px;
                width: 168px;
                overflow: hidden;
                height: 60px;
                background: #EFF2F4;
                // box-shadow: inset 0 1px 1px 0 rgba(212,212,212,0.50);
                border-radius: 10px;
                border: 2px solid #EFF2F4;

                span:nth-of-type(1) {
                    align-self: flex-start;
                    font-size: 12px;
                    color: #666666;
                    text-align: left;
                    line-height: 16px;
                }

                span:nth-of-type(2) {
                    margin-top: 8px;
                    align-self: flex-end;
                    font-size: 20px;
                    line-height: 28px;
                    color: #333333;
                }
            }

            .active {
                border: 2px solid #009688;

                span:nth-of-type(1) {
                    color: #009688;
                }
            }
        }

        #keyboardContainer {
            position: absolute;
            bottom: 0;
        }
    }
}
</style>
