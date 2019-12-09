<template>
    <div>
        <el-dialog
            title="结款"
            :visible.sync="dialogVisible"
            height='560px'
            width="580px">
            <p class="p1">
                <span class="ib">结算金额：</span>
                <span class="num">{{total_money}}</span>
                <span class="yuan">元</span>
            </p>
            <p class="p2"><span class="ib">供货商：</span>{{firmNameList}}</p>
            <el-form label-position="right" label-width="80px" :model="form" size="medium">
                <el-form-item label="姓名：" class="required">
                    <el-input v-model="form.agent_name" placeholder="请输入结算人姓名"></el-input>
                </el-form-item>
                <el-form-item label="手机号：" class="required">
                    <el-input v-model="form.agent_phone" style="width:306px;" placeholder="请输入结算人手机号"></el-input><el-checkbox v-model="form.send_sms" style="margin-left:15px;">发送短信通知</el-checkbox>
                </el-form-item>
                <el-form-item label="结算账号：">
                    <div class="paytype">
                        <!-- <template v-for="(item,index) in firm_list"> -->
                            <!-- <div class="firm_name" :key="index+'a'" v-show="firm_list.length>1">{{item.firm_name}}</div> -->
                            <div v-for="(item_1,index_1) in paytype_list" :key="index_1" class="radio"><my-radio v-model="form.payment_account_id" :label='item_1.id'>{{paymentStr(item_1)}}</my-radio></div>
                        <!-- </template> -->
                        <div class="radio"><my-radio v-model="form.payment_account_id" name='cash' :label='0'>现金</my-radio></div>
                    </div>
                    <div class="addpayment">
                        <span @click="beforeAdd">+添加支付账号</span>
                        <div class="whichfirm" v-show="show_1">
                            <ul>
                                <li>选择添加到哪个供货商</li>
                                <li v-for="(item,index) in firm_list" :key="index" @click="addPayment(item)">{{item.firm_name}}</li>
                            </ul>
                        </div>
                    </div>
                </el-form-item>
                <el-form-item label="备注：">
                    <el-input v-model="form.remarks" placeholder="结款备注"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <button class="btn confirm" @click="confirm" :class="{canclick:canclick}" style="width: 550px;height: 46px;font-size: 18px;background: #DDDDDD;color: #999999;border-radius: 2px;cursor: not-allowed;">结算完成</button>
            </span>
        </el-dialog>
        <add-payment-account ref="addPaymentAccount" @saveSuccess='saveSuccess'></add-payment-account>
    </div>
</template>
<script>
import addPaymentAccount from '@/views/suppliers/modules/add_payment_account.vue'
export default {
    data() {
        return {
            dialogVisible: false,
            form: {
                agent_name: '',
                agent_phone: '',
                remarks: '',
                payment_account_id: 0, // 没有支付账号的时候默认用现金支付
                send_sms: true // 是否发送短信
            },
            firm_list: [],
            total_money: 0,
            paytype_list: [],
            show_1: false
        }
    },

    computed: {
        firmNameList() { // 所有供货商姓名和金额拼成的字符串
            let arr = []
            this.firm_list.forEach(ele => {
                arr.push(`${ele.firm_name}：${ele.sun_money}元`)
            })
            return arr.join(' | ')
        },
        canclick() { // 姓名和手机号符合要求才可以点击结算完成
            return this.$Validator.single('isEmpty', this.form.agent_name) && this.$Validator.single('isEmpty', this.form.agent_phone) && this.$Validator.single('isPhone', this.form.agent_phone)
        }
    },

    watch: {
        paytype_list(val) { // 增加完支付账号之后默认选择第一个支付账号
            if (val.length > 0) {
                this.form.payment_account_id = val[0].id
            }
        }
    },

    methods: {
        saveSuccess() { // 添加支付账号成功
            this.getAccounts()
        },
        paymentStr(payment) { // 支付方式字符串
            let str = ''
            str = payment.account_type === 1 ? `支付宝-${payment.account_name}-${payment.account_num}` : `${payment.account_name}-${payment.account_num}-${payment.bank_name}`
            if (this.firm_list.length > 1) { // 供货商超过一个就在支付账号前面加上供货商名字
                str = payment.firm_name + '-' + str
            }
            return str
        },
        beforeAdd() { // 添加支付账号按钮
            this.firm_list.length > 1 ? this.show_1 = !this.show_1 : this.addPayment(this.firm_list[0])
        },
        validator() { // 验证姓名和手机号的格式
            let validator = new this.$Validator()

            validator.add('isEmpty', this.form.agent_name, '请输入结算人姓名')
            validator.add('isEmpty', this.form.agent_phone, '请输入结算人手机号')
            validator.add('isPhone', this.form.agent_phone, '请输入正确的手机号')

            return validator.start()
        },
        addPayment(firm) { // 打开添加支付账号弹框
            // this.dialogVisible = false
            this.$refs.addPaymentAccount.open({
                name: firm.firm_name,
                id: firm.firm_id
            })
        },
        confirm() { // 完成结算按钮
            this.validator().then(() => {
                this.$fetch.post({
                    url: '/firmsettlementorder',
                    params: {
                        ...this.form,
                        vouchers: this.vouchers.reduce((last, next) => {
                            return [...last, {
                                id: next.settlement_voucher_id,
                                amount: next.amount,
                                price: next.price,
                                total_money: next.total_money
                            }]
                        }, []),
                        total_money_sum: this.total_money
                    }
                }).then(() => {
                    this.openMessage(1, '结算成功')
                    this.dialogVisible = false
                    this.$emit('finishScavenging')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        open(arr, totalMoney, vouchers) { // 打开结算弹框,参数:1供货商列表2结算总金额3结算列表
            this.show_1 = false
            this.total_money = totalMoney
            this.firm_list = arr
            this.paytype_list = []
            this.vouchers = vouchers
            let _arr = []
            arr.forEach(element => {
                _arr.push(element.firm_id)
            })
            this.firm_ids = _arr.join('|')
            this.getAccounts()
            this.dialogVisible = true
            this.form = { // 清空数据
                agent_name: '',
                agent_phone: '',
                remarks: '',
                payment_account_id: 0,
                send_sms: true
            }
        },
        getAccounts() { // 查询供货商的支付账号
            this.$fetch.get({
                url: `/firm/paymentaccounts`,
                params: {
                    firm_ids: this.firm_ids
                }
            }).then(data => {
                this.paytype_list = data.accounts
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    },

    components: {
        addPaymentAccount
    }
}
</script>
<style lang="scss" scoped>
    p{
        padding-bottom: 10px;
        .ib{
            display: inline-block;
            width: 80px;
            font-size: 16px;
            color: #333333;
            text-align: right;
        }
        .num{
            font-size: 22px;
            color: #FF7C56;
        }
        .yuan{
            font-size: 14px;
            color: #999999;
        }
        &.p2{
            border-bottom: 1px solid #F2F2F2;
            font-size: 14px;
            color: #333333;
            margin-bottom: 25px;
            .ib{
                font-size: 14px;
                color: #333333;
            }
        }
    }
    .paytype{
        background: #F9F9F9;
        width: 430px;
        max-height: 156px;
        overflow-y: auto;
        padding-left: 10px;
        padding-bottom: 10px;
        .firm_name{
            height: 30px;
            font-size: 14px;
            color: #333333;
            font-weight: bold;
        }
        .radio{
            height: 30px;
        }
    }
    .addpayment{
        position: relative;
        width: 102px;
        height: 40px;
        line-height: 40px;
        // &:hover .whichfirm{
        //     display: block;
        // }
        span{
            font-size: 14px;
            color: rgba(107,164,239,0.95);
            cursor: pointer;
        }
        .whichfirm{
            // display: none;
            position: absolute;
            width:267px;
            z-index: 2;
            top: -14px;
            left: 105px;
            background: #fff;
            box-shadow: 0 0 12px 3px rgba(0,0,0,0.15);
            &::after{
                position: absolute;
                content: '';
                width: 0;
                height: 0;
                border: 6px solid transparent;
                top: 25px;
                left: -12px;
                border-right-color: #fff;
            }
            ul{
                li{
                    height: 30px;
                    line-height: 30px;
                    padding-left: 10px;
                    font-size: 14px;
                    color: #666666;
                    &:nth-of-type(2n){
                        background: #F5F7FA;
                    }
                    &:nth-of-type(1){
                        height: 36px;
                        line-height: 36px;
                        color: #333333;
                        cursor: normal;
                    }
                }
                li+li{
                    cursor: pointer;
                }
            }
        }
    }
    /deep/ .el-form-item{
        margin-bottom: 0!important;
    }
    /deep/ .el-form-item--small.el-form-item{
        margin-bottom: 0;
    }
    .canclick{
        background: #009688!important;
        color:#fff!important;
        cursor: pointer!important;
    }
    .required:nth-of-type(1):after{
        top: 10px;
        left: 24px;
    }
    .required:nth-of-type(2):after{
        top: 10px;
        left: 10px;
    }
</style>
