<template>
    <translucent-box @closeBox="$emit('closeAll')">
        <div class="up">
            <div class="caigou">添加新供货商
            </div>
            <div class="add_supplier">
                <p @click="$emit('close')">返回</p>
            </div>
            <div class="new_supplier">
                <p><span>*</span>供货商名称<input type="text" placeholder="输入名称" v-model="form.name"></p>
                <p>联系电话<input type="text" placeholder="输入手机号码" v-model="form.phone"></p>
            </div>
            <div class="btn_sure" @click="sureAddSupplier">确认</div>
        </div>
    </translucent-box>
</template>
<script>
import translucentBox from './translucent_box.vue'
export default {
    data() {
        return {
            form: {
                name: '',
                phone: ''
            }
        }
    },
    props: {
        good_item: {
            default() {
                return {}
            },
            type: Object
        }
    },
    components: {
        translucentBox
    },
    methods: {
        sureAddSupplier() {
            if (!this.form.name) {
                return this.$alert('请输入供货商名称')
            }
            this.$fetch.post({
                url: '/firm',
                params: this.form
            }).then(data => {
                this.addSupplierToGood(data.firm_dict)
            }).catch(erro => {
                this.$alert(erro)
            })
        },
        addSupplierToGood(firm) {
            this.$fetch.put({
                url: `/goods/${this.good_item.goods_id}`,
                params: {
                    action: 'add_firm',
                    firm_id: firm.id
                }
            }).then(data => {
                this.$emit('finishEntry', firm)
                this.form = {
                    name: '',
                    phone: ''
                }
            }).catch(erro => {
                this.$alert(erro)
            })
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
