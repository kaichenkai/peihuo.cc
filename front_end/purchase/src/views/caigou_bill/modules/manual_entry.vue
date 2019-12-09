<template>
    <translucent-box @closeBox='closeBox'>
        <div class="up">
            <div class="caigou">{{caigou_good_name}}
                <!-- <p @click="$emit('close');clearData()"></p> -->
                <p class="pay_type" :class="'pay'+pay_type.id" @click="$emit('payType')">{{pay_type.name}}</p>
            </div>
            <div class="supplier">
                <div class="choose_supplier" @click="$emit('chooseSupplier')">{{supplier_item.name}}</div>
                <!-- <div class="pay_type" @click="$emit('payType')">{{pay_type.name}}
                    <p>支付方式 :</p>
                </div> -->
            </div>
            <div class="data_area">
                <ul>
                    <li style="width:29%;" :class="{focus:focus===0}" @click="focusLi(0)">
                        <p>件数</p>
                        <p>
                            <span>{{input_data[0].value}}</span>
                            <span>件</span>
                        </p>
                    </li>
                    <li style="width:29%;" :class="{focus:focus===1}" @click="focusLi(1)">
                        <p>单价</p>
                        <p>
                            <span>{{input_data[1].value}}</span>
                            <span>{{input_data.active?'元/件':'元/斤'}}</span>
                        </p>
                    </li>
                    <li style="width:38%;" :class="{focus:focus===2}" @click="focusLi(2)">
                        <p>小计</p>
                        <p>
                            <span>{{input_data[2].value}}</span>
                            <span>元</span>
                        </p>
                    </li>
                    <div style="width:29%;" class="caigou_unit">
                        <p>采购单位</p>
                        <div @click="input_data.active=!input_data.active">
                            <span :class="{active:input_data.active}">件</span>
                            <span :class="{active:!input_data.active}">斤</span>
                        </div>
                    </div>
                    <li style="width:29%" :class="{focus:focus===3}" @click="focusLi(3)">
                        <p>重量</p>
                        <p>
                            <span>{{input_data[3].value}}</span>
                            <span>斤</span>
                        </p>
                    </li>
                    <li style="width:18%" :class="{focus:focus===4}" @click="focusLi(4)">
                        <p>行费</p>
                        <p>
                            <span>{{input_data[4].value}}</span>
                            <span>元/件</span>
                        </p>
                    </li>
                    <li style="width:18%;" :class="{focus:focus===5}" @click="focusLi(5)">
                        <p>押金</p>
                        <p>
                            <span>{{input_data[5].value}}</span>
                            <span>元/件</span>
                        </p>
                    </li>
                </ul>
            </div>
        </div>
        <div class="down">
            <table>
                <colgroup>
                    <col width="25%/">
                    <col width="25%">
                    <col width="25%">
                    <col width="25%">
                </colgroup>
                <tr>
                    <td @click="clickNum('1')">1</td>
                    <td @click="clickNum('2')">2</td>
                    <td @click="clickNum('3')">3</td>
                    <td rowspan="2" class="next_item" style="background-color: #CCEAE7;border-color: #CCEAE7;color: #009688;font-size: 24px;" @click="nextItme">下一项</td>
                </tr>
                <tr>
                    <td @click="clickNum('4')">4</td>
                    <td @click="clickNum('5')">5</td>
                    <td @click="clickNum('6')">6</td>
                </tr>
                <tr>
                    <td @click="clickNum('7')">7</td>
                    <td @click="clickNum('8')">8</td>
                    <td @click="clickNum('9')">9</td>
                    <td rowspan="2" class="finish" :class="{canSubmit:numCanSubmit&&canEditOrAdd}" @click="finishCaigouEntry">完成</td>
                </tr>
                <tr>
                    <td @click="clickNum('0')">0</td>
                    <td @click="clickNum('.')">.</td>
                    <td @click="clickNum('')" style="text-align:center;"><img src="~@/assets/images/delete.png" alt="" class="delete"></td>
                </tr>
            </table>
        </div>
    </translucent-box>
</template>
<script>
import translucentBox from './translucent_box.vue'
export default {
    data() {
        return {
            focus: 0,
            numCanSubmit: false
        }
    },
    watch: {
        input_data: {
            handler() {
                let value0 = Number(this.input_data[0].value)
                let value1 = Number(this.input_data[1].value)
                let value3 = Number(this.input_data[3].value)
                let value4 = Number(this.input_data[4].value)
                let value5 = Number(this.input_data[5].value)
                if (this.input_data.active) {
                    let value = this.mostSaveTwoDecimal((value0 * value1 + value0 * (value4 + value5)).toFixed(2))
                    this.input_data[2].value = value === 0 ? '' : value
                } else {
                    let value = this.mostSaveTwoDecimal((value3 * value1 + value0 * (value4 + value5)).toFixed(2))
                    this.input_data[2].value = value === 0 ? '' : value
                }
                if (this.input_data[0].value === '' || this.input_data[0].value === '0') {
                    this.numCanSubmit = false
                } else if (this.input_data[1].value === '' || this.input_data[1].value === '0') {
                    this.numCanSubmit = false
                } else if (!this.input_data.active) {
                    if (this.input_data[3].value === '' || this.input_data[3].value === '0') {
                        this.numCanSubmit = false
                    } else {
                        this.numCanSubmit = true
                    }
                } else {
                    this.numCanSubmit = true
                }
            },
            deep: true
        }
    },
    props: {
        is_one_good_many_supplier: {
            default: false,
            type: Boolean
        },
        supplier_item: {
            default() {
                return {}
            },
            type: Object
        },
        pay_type: {
            default() {
                return {}
            },
            type: Object
        },
        good_item: {
            default() {
                return {}
            },
            type: Object
        },
        caigou_good_name: {
            default: '',
            type: String
        },
        firm_id_list: {
            default() {
                return []
            },
            type: Array
        },
        input_data: {
            default() {
                return {}
            },
            type: Object
        },
        canEditOrAdd: {
            default: true,
            type: Boolean
        }
    },
    methods: {
        closeBox() {
            this.$emit('close')
            this.clearData()
        },
        clearData() {
            for (let i = 0; i < 6; i++) {
                this.input_data[i].value = ''
            }
            this.input_data.active = true
            this.focus = 0
        },
        mostSaveTwoDecimal(num) {
            num = String(num)
            var size = num.length
            if (num.charAt(size - 1) === '0') {
                num = num.slice(0, -1)
                size = num.length
                if (num.charAt(size - 1) === '0') {
                    num = num.slice(0, -2)
                }
            }
            return Number(num)
        },
        finishCaigouEntry() {
            if (!this.supplier_item.id) {
                return this.$alert('请选择供货商')
            } else if (!this.canEditOrAdd) {
                return this.$alert(`你已经采购过该供货商的${this.caigou_good_name}了,请选择其他供货商`)
            } else if (this.input_data[0].value === '' || this.input_data[0].value === '0') {
                return this.$alert('请输入件数')
            } else if (this.input_data[1].value === '' || this.input_data[1].value === '0') {
                return this.$alert('请输入单价')
            } else if (!this.input_data.active) {
                if (this.input_data[3].value === '' || this.input_data[3].value === '0') {
                    return this.$alert('请输入重量')
                }
            }
            this.$fetch.put({
                url: `/purchase/order/goods/${this.good_item.id}`,
                params: {
                    action: this.is_one_good_many_supplier ? 'again_entering' : 'manually_entering',
                    firm_id: this.supplier_item.id,
                    actual_amount: Number(this.input_data[0].value),
                    subtotal: Number(this.input_data[2].value),
                    payment: this.pay_type.id,
                    price: Number(this.input_data[1].value),
                    actual_unit: this.input_data.active ? 0 : 1,
                    actual_weight: Number(this.input_data[3].value),
                    fee: Number(this.input_data[4].value),
                    deposit: Number(this.input_data[5].value)
                }
            }).then(data => {
                this.clearData()
                this.$emit('finishCaigouEntry')
            }).catch(erro => {
                this.$alert(erro)
            })
        },
        focusLi(num) {
            if (this.focus !== num) {
                this.focus = num
                this.input_data[this.focus].first_time = false
            }
        },
        nextItme() {
            this.input_data[this.focus].first_time = false
            this.focus++
            this.focus = this.focus % 6
        },
        clickNum(num) {
            var bol = this.input_data[this.focus].first_time // 是不是第一次输入
            var value = this.input_data[this.focus].value + '' // 当前聚焦的输入框的值
            if (num === '') { // 删除键
                if (bol) {
                    this.input_data[this.focus].value = value.slice(0, -1) // 删除最后一位
                } else {
                    this.input_data[this.focus].value = '' // 清空
                }
            } else if (num === '.') { // 小数点键
                if (bol) {
                    if (value.length !== 0 && value.indexOf('.') === -1 && value.length < 5) { // 小数点不能出现在第一位也不能重复
                        this.input_data[this.focus].value = this.input_data[this.focus].value + '.'
                    }
                }
            } else {
                if (bol) {
                    if (value.length < 5 && value.split("").reverse().join("").indexOf('.') < 2) { // 小数点的后面最多只有2位小数
                        // if (num === '0' && value.length === 0) { // 0不能出现在第一位
                        //     return
                        // }
                        this.input_data[this.focus].value = this.input_data[this.focus].value + num
                    }
                } else {
                    // if (num === '0') { // 0不能出现在第一位
                    //     return
                    // }
                    this.input_data[this.focus].value = num
                    this.input_data[this.focus].first_time = true
                }
            }
        }
    },
    components: {
        translucentBox
    }
}
</script>

<style lang="scss" scoped>
    .up{
        padding: 0 10px;
        .caigou{
            position: relative;
            line-height: 40px;
            color: #009688;
            font-size: 17px;
            font-weight: bold;
            border-bottom: 2px solid #009688;
            overflow: hidden;
            // p{
            //     position: absolute;
            //     top: 0;
            //     right: 0;
            //     width: 42px;
            //     height: 42px;
            //     background: url('~@/assets/images/close.png') center/24px no-repeat;
            // }
            .pay_type{
                height: 100%;
                float: right;
                padding-left: 40px;
                padding-right: 12px;
                text-align: right;
                font-weight: normal;
                font-size: 16px;
                color: #666;
                &.pay0{
                    background: url('~@/assets/images/cash_pay.png') no-repeat 10px center/24px 24px,url("~@/assets/images/arr_right.png") no-repeat right center/10px;
                }
                &.pay1{
                    background: url('~@/assets/images/card_pay.png') no-repeat 10px center/24px 24px,url("~@/assets/images/arr_right.png") no-repeat right center/10px;
                }
                &.pay2{
                    background: url('~@/assets/images/wx_pay1.png') no-repeat 10px center/24px 24px,url("~@/assets/images/arr_right.png") no-repeat right center/10px;
                }
                &.pay3{
                    background: url('~@/assets/images/ali_pay1.png') no-repeat 10px center/24px 24px,url("~@/assets/images/arr_right.png") no-repeat right center/10px;
                }
                &.pay4{
                    background: url('~@/assets/images/credit_pay.png') no-repeat 10px center/24px 24px,url("~@/assets/images/arr_right.png") no-repeat right center/10px;
                }
                &.pay5{
                    background: url('~@/assets/images/other_pay.png') no-repeat 10px center/24px 24px,url("~@/assets/images/arr_right.png") no-repeat right center/10px;
                }
            }
        }
        .supplier{
            overflow: hidden;
            .choose_supplier{
                float: left;
                margin: 20px 0;
                padding: 0 10px 0 36px;
                background: url('~@/assets/images/edit.png') 10px center/20px no-repeat;
                width: 168px;
                height: 40px;
                line-height: 40px;
                color: #009688;
                font-size: 20px;
                border: 1px solid #009688;
                border-radius: 6px;
                white-space:nowrap;
                overflow: hidden;
                text-overflow:ellipsis;
            }
            .pay_type{
                position: relative;
                float: right;
                margin: 20px 0;
                width: 168px;
                height: 40px;
                line-height: 40px;
                color: #000;
                font-size: 16px;
                border: 1px solid #666;
                border-radius: 6px;
                text-align: center;
                p{
                    position: absolute;
                    top: 3px;
                    left: 6px;
                    width: 34px;
                    line-height: 16px;
                    font-size: 12px;
                    color:#999;
                    text-align: left;
                }
            }
        }
        .data_area{
            ul{
                overflow: hidden;
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                li{
                    float: left;
                    height: 60px;
                    border-radius: 10px;
                    // margin-right: 8px;
                    overflow: hidden;
                    p{
                        line-height: 24px;
                        font-size: 14px;
                        color: #999;
                        &:nth-of-type(2){
                            text-align: right;
                            white-space:nowrap;
                            span{
                                &:nth-of-type(1){
                                    margin-right: 4px;
                                    color: #333;
                                    font-size: 20px;
                                }
                            }
                        }
                    }
                    &:nth-of-type(1),&:nth-of-type(2),&:nth-of-type(3){
                        background: #EFF2F4;
                        box-shadow: inset 0 1px 1px 0 rgba(212,212,212,.5);
                        padding: 4px;
                        margin-bottom: 8px;
                    }
                    &:nth-of-type(4),&:nth-of-type(5),&:nth-of-type(6){
                        border: 2px solid #EFF2F4;
                        padding: 2px;
                    }
                    &.focus{
                        border: 2px solid #009688;
                        padding: 2px;
                        p:nth-of-type(1){
                            color:#009688;
                        }
                    }
                }
                .caigou_unit{
                    float: left;
                    height: 60px;
                    // margin-right: 8px;
                    p{
                        line-height: 24px;
                        font-size: 14px;
                        color: #333;
                    }
                    div{
                        display: inline-block;
                        background: #EFF2F4;
                        width: 100%;
                        max-width: 100px;
                        height: 36px;
                        line-height: 36px;
                        border-radius: 10px;
                        span{
                            display: inline-block;
                            color: #999;
                            width: 50%;
                            height: 100%;
                            border-radius: 10px;
                            text-align: center;
                            font-size: 16px;
                            &.active{
                                background: #009688;
                                color: #fff;
                            }
                        }
                    }
                }
            }
        }
    }
    .down{
        margin-top: 20px;
        table{
            box-shadow: inset 0 1px 1px 0 rgba(180,180,180,.8);
            width: 100%;
            background-color: #F7F8F9;
            tr{
                td{
                    border: 1px solid #fff;
                    color: #333;
                    text-align: center;
                    font-size: 30px;
                    border-collapse: collapse;
                    height: 52px;
                    vertical-align: middle;
                    user-select: none;
                    .delete{
                        position: relative;
                        top:6px;
                    }
                    .next_item{
                        background-color: #CCEAE7;
                        border-color: #CCEAE7;
                        color: #009688;
                        font-size: 24px;
                    }
                    &.finish{
                        background: #ccc;
                        color: #fff;
                        border-color: transparent;
                        &.canSubmit{
                            background: #009688;
                            border-color: #009688;
                        }
                    }
                }
            }
        }
    }
</style>
