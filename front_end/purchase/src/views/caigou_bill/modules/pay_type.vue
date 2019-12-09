<template>
    <translucent-box @closeBox="$emit('closeAll')">
        <div class="up">
            <div class="caigou">货品付款方式
                <!-- <p @click="$emit('closeAll')"></p> -->
            </div>
            <div class="add_supplier">
                <p @click="$emit('close')">返回</p>
            </div>
            <div class="list">
                <ul>
                    <li v-for="(item,index) in data_list" :key="index" :class="[item.class,{active:index===active}]" @click="active=index">{{item.name}}</li>
                </ul>
            </div>
            <div class="btn_sure" @click="surePayType">确认</div>
        </div>
    </translucent-box>
</template>
<script>
import translucentBox from './translucent_box.vue'
export default {
    data() {
        return {
            active: 0,
            data_list: [
                { class: 'debt', name: '赊账', id: 4 },
                { class: 'cash', name: '现金', id: 0 },
                { class: 'card', name: '银行卡', id: 1 },
                { class: 'weixin', name: '微信', id: 2 },
                { class: 'zhifubao', name: '支付宝', id: 3 },
                { class: 'other', name: '其它', id: 5 }
            ]
        }
    },
    methods: {
        surePayType() {
            this.$emit('surePayType', this.data_list[this.active])
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
            font-size: 16px;
            border-bottom: 2px solid #009688;
            p{
                position: absolute;
                top: 0;
                right: 0;
                width: 42px;
                height: 42px;
                background: url('~@/assets/images/close.png') center/24px no-repeat;
            }
        }
        .add_supplier{
            overflow: hidden;
            p{
                line-height: 56px;
                &:nth-of-type(1){
                    float: left;
                    color: #333;
                    font-size: 16px;
                    padding-left: 22px;
                    background: url('~@/assets/images/back.png') left center/16px no-repeat;
                }
            }
        }
        .list{
            ul{
                overflow: hidden;
                margin-top: 8px;
                li{
                    width: 48%;
                    text-align: center;
                    border: 1px solid #9F9F9F;
                    height: 52px;
                    line-height: 50px;
                    border-radius: 26px;
                    font-size: 16px;
                    margin-bottom: 20px;
                    &:nth-of-type(odd){
                        float: left;
                    }
                    &:nth-of-type(even){
                        float: right;
                    }
                    &.active{
                        border: 2px solid #00A093;
                        color: #00A093;
                        font-weight: 700;
                    }
                    &.debt{
                        background: url('~@/assets/images/credit_pay.png') no-repeat 10px center/24px;
                        &.active{
                            background: rgba(0,160,147,.19) url('~@/assets/images/credit_pay.png') no-repeat 10px center/24px;
                        }
                    }
                    &.cash{
                        background: url('~@/assets/images/cash_pay.png') no-repeat 10px center/24px;
                        &.active{
                            background: rgba(0,160,147,.19) url('~@/assets/images/cash_pay.png') no-repeat 10px center/24px;
                        }
                    }
                    &.weixin{
                        background: url('~@/assets/images/wx_pay1.png') no-repeat 10px center/24px;
                        &.active{
                            background: rgba(0,160,147,.19) url('~@/assets/images/wx_pay1.png') no-repeat 10px center/24px;
                        }
                    }
                    &.card{
                        background: url('~@/assets/images/card_pay.png') no-repeat 10px center/24px;
                        &.active{
                            background: rgba(0,160,147,.19) url('~@/assets/images/card_pay.png') no-repeat 10px center/24px;
                        }
                    }
                    &.zhifubao{
                        background: url('~@/assets/images/ali_pay1.png') no-repeat 10px center/24px;
                        &.active{
                            background: rgba(0,160,147,.19) url('~@/assets/images/ali_pay1.png') no-repeat 10px center/24px;
                        }
                    }
                    &.other{
                        background: url('~@/assets/images/other_pay.png') no-repeat 10px center/24px;
                        &.active{
                            background: rgba(0,160,147,.19) url('~@/assets/images/other_pay.png') no-repeat 10px center/24px;
                        }
                    }
                }
            }
        }
        .btn_sure{
            position: absolute;
            bottom: 20px;
            left: 10px;
            width: calc(100% - 20px);
            height: 50px;
            line-height: 50px;
            background: #009688;
            box-shadow: 0 2px 5px 0 rgba(0,150,136,.6);
            color: #fff;
            font-size: 20px;
            text-align: center;
            border-radius: 5px;
        }
    }
</style>
