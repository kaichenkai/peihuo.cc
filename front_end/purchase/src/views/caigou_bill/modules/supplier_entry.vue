<template>
    <translucent-box @closeBox='close'>
        <div class="up">
            <div class="caigou">采购商户录入
                <!-- <p @click="close"></p> -->
                <p class="add_new_supplier" @click="$emit('addNewSupplier')">+添加新供货商</p>
            </div>
            <div class="add_supplier">
                <p @click="back">返回</p>
                <!-- <p @click="show1=!show1">{{show1?'+添加新供货商':'取消'}}</p> -->
            </div>
            <div class="input">
                <input type="text" placeholder="输入采购商户名称" v-model="input_supplier_name">
            </div>
            <div class="suppliers">
                <ul>
                    <!-- <li v-for="(item,index) in history_firm_list" :key="index" @click="input_supplier_name=item.name">{{item.name}}</li> -->
                    <li v-for="(item,index) in history_firm_list" :key="index" @click="finishEntry(item,index)">
                        <span>{{item.name}}</span><span>{{item.phone}}</span>
                        <!-- <i :class="{checked:checked===index}"></i> -->
                    </li>
                </ul>
            </div>
            <!-- <template v-else>
                <div class="new_supplier">
                    <p><span>*</span>供货商名称<input type="text" placeholder="输入名称" v-model="form.name"></p>
                    <p>联系电话<input type="text" placeholder="输入手机号码" v-model="form.phone"></p>
                </div>
            </template> -->
            <!-- <div class="btn_sure" @click="finishEntry">完成录入</div> -->
        </div>
    </translucent-box>
</template>
<script>
import translucentBox from './translucent_box.vue'
var _ = require('lodash')
export default {
    data() {
        return {
            input_supplier_name: '',
            show1: true,
            form: {
                name: '',
                phone: ''
            },
            checked: -1
        }
    },
    components: {
        translucentBox
    },
    created() {
        this.debouncedGetAnswer = _.debounce(this.searchSupplier, 300)
    },
    watch: {
        input_supplier_name(val) {
            this.debouncedGetAnswer()
        }
    },
    props: {
        history_firm_list: {
            default() {
                return []
            },
            type: Array
        }
    },
    methods: {
        close() {
            this.$emit('closeAll')
            this.show1 = true
            this.input_supplier_name = ''
        },
        back() {
            this.$emit('close')
            this.show1 = true
            this.input_supplier_name = ''
        },
        searchSupplier() {
            this.$emit('perpotyChange', this.input_supplier_name)
        },
        finishEntry(item, index) {
            this.checked = index
            this.input_supplier_name = ''
            this.$emit('finishEntry', item)
            this.checked = -1
        }
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
            // p{
            //     position: absolute;
            //     top: 0;
            //     right: 0;
            //     width: 42px;
            //     height: 42px;
            //     background: url('~@/assets/images/close.png') center/24px no-repeat;
            // }
            .add_new_supplier{
                height: 100%;
                float: right;
                padding-right: 12px;
                text-align: right;
                font-weight: normal;
                font-size: 16px;
                color: #666;
                background: url("~@/assets/images/arr_right.png") no-repeat right center/10px;
            }
        }
        .add_supplier{
            overflow: hidden;
            p{
                line-height: 56px;
                &:nth-of-type(1){
                    float: left;
                    color: #333;
                    font-size: 13px;
                    padding-left: 22px;
                    background: url('~@/assets/images/back.png') left center/16px no-repeat;
                }
                &:nth-of-type(2){
                    float: right;
                    padding-right: 15px;
                    color: #009688;
                    font-size: 16px;
                    font-weight: bold;
                }
            }
        }
        .input{
            input{
                box-sizing: border-box;
                height: 50px;
                border: 2px solid #ddd;
                font-size: 16px;
                background-color: #EFF2F4;
                padding: 0 14px;
                width: 100%;
                border-radius: 25px;
                outline: none;
                &:focus{
                    border-color: #009688;
                    outline: none;
                }
            }
        }
        .suppliers{
            max-height: 330px;
            overflow-y: auto;
            ul{
                overflow: hidden;
                // li{
                //     float: left;
                //     padding: 0 6px;
                //     margin: 0 6px 6px 0;
                //     min-width: 50px;
                //     text-align: center;
                //     height: 30px;
                //     line-height: 30px;
                //     background: rgba(0,150,136,.18);
                //     border-radius: 3px;
                //     color: #009688;
                // }
                li{
                    height: 40px;
                    line-height: 40px;
                    border-bottom: 1px solid #EFF2F4;
                    overflow: hidden;
                    span{
                        display: inline-block;
                        &:nth-of-type(1){
                            margin-right: 8px;
                            max-width: 200px;
                            font-size: 16px;
                            color: #333333;
                            white-space:nowrap;
                            overflow:hidden;
                            text-overflow:ellipsis;
                        }
                        &:nth-of-type(2){
                            position: relative;
                            top:-15px;
                            font-size: 12px;
                            color: #9F9F9F;
                        }
                    }
                    i{
                        float: right;
                        width: 20px;
                        height: 40px;
                        margin-right: 10px;
                        background: url('~@/assets/images/check_btn.png') no-repeat -23px center/42px;
                        &.checked{
                            background: url('~@/assets/images/check_btn.png') no-repeat 0 center/42px;
                        }
                    }
                }
            }
        }
        .new_supplier{
            p{
                margin-top: 10px;
                line-height: 50px;
                overflow: hidden;
                font-size: 14px;
                color: #333;
                span{
                        color: #f66;
                }
                input{
                    float: right;
                    height: 50px;
                    border: 2px solid #ddd;
                    font-size: 16px;
                    background-color: #EFF2F4;
                    padding: 0 14px;
                    border-radius: 40px;
                    width: 60%;
                    &:focus{
                        border-color: #009688;
                        outline: none;
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
