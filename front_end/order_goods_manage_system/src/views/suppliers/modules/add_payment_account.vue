<template>
    <el-dialog
        title="供货商支付账号"
        :visible.sync="dialogVisible"
        height='430px'
        width="445px">
        <p class="supplier_name"><span>供货商：</span>{{firm_dict.name}}</p>
        <p class="account_type"><span>账号类型：</span><my-radio v-model="account_type" label='1'>支付宝</my-radio><my-radio v-model="account_type" label='3'>对私转账</my-radio><my-radio v-model="account_type" label='2'>对公转账</my-radio></p>
        <el-form label-position="right" label-width="97px" size="small">
            <template v-if="account_type==='1'">
                <el-form-item label="支付宝账号：">
                    <el-input v-selectTextOnFocus v-model="pay_type_1.account_num" placeholder="输入支付宝账号"></el-input>
                </el-form-item>
                <el-form-item label="账户姓名：">
                    <el-input v-selectTextOnFocus v-model="pay_type_1.account_name" placeholder="输入账户姓名"></el-input>
                </el-form-item>
            </template>
            <template v-if="account_type==='3'">
                <el-form-item label="开户银行：">
                    <el-select v-model="pay_type_3.bank_no" placeholder="选择银行" style="width:318px;" @change="showBranchBanks">
                        <el-option
                        v-for="item in bank_list"
                        :key="item.no"
                        :label="item.name"
                        :value="item.no">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="账户姓名：">
                    <el-input v-selectTextOnFocus v-model="pay_type_3.account_name" placeholder="输入公司全称"></el-input>
                </el-form-item>
                <el-form-item label="银行卡号：">
                    <el-input v-selectTextOnFocus v-model="pay_type_3.account_num" placeholder="输入银行卡号"></el-input>
                </el-form-item>
                <el-form-item label="开户地区：">
                    <el-select v-model="pay_type_3.bank_province_code" placeholder="选择省份" style="width:153px;" @change="provinceChange">
                        <el-option
                        v-for="item in province_list"
                        :key="item.province_code"
                        :label="item.province_text"
                        :value="item.province_code">
                        </el-option>
                    </el-select>
                    <el-select v-model="pay_type_3.bank_city_code" placeholder="选择城市" style="width:153px;float: right;" @change="showBranchBanks">
                        <el-option
                        v-for="item in city_list_3"
                        :key="item.city_code"
                        :label="item.city_text"
                        :value="item.city_code">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="开户行全称：">
                    <el-select v-model="pay_type_3.branch_bank_no" placeholder="选择开户支行" style="width:318px;">
                        <el-option
                        v-for="item in branch_bank_list_3"
                        :key="item.bank_no"
                        :label="item.bank_name"
                        :value="item.bank_no">
                        </el-option>
                    </el-select>
                </el-form-item>
            </template>
            <template v-if="account_type==='2'">
                <el-form-item label="开户银行：">
                    <el-select v-model="pay_type_2.bank_no" placeholder="选择银行" style="width:318px;" @change="showBranchBanks">
                        <el-option
                        v-for="item in bank_list"
                        :key="item.no"
                        :label="item.name"
                        :value="item.no">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="公司全称：">
                    <el-input v-selectTextOnFocus v-model="pay_type_2.account_name" placeholder="输入账户姓名"></el-input>
                </el-form-item>
                <el-form-item label="银行卡号：">
                    <el-input v-selectTextOnFocus v-model="pay_type_2.account_num" placeholder="输入银行卡号"></el-input>
                </el-form-item>
                <el-form-item label="开户地区：">
                    <el-select v-model="pay_type_2.bank_province_code" placeholder="选择省份" style="width:153px;" @change="provinceChange">
                        <el-option
                        v-for="item in province_list"
                        :key="item.province_code"
                        :label="item.province_text"
                        :value="item.province_code">
                        </el-option>
                    </el-select>
                    <el-select v-model="pay_type_2.bank_city_code" placeholder="选择城市" style="width:153px;float: right;" @change="showBranchBanks">
                        <el-option
                        v-for="item in city_list_2"
                        :key="item.city_code"
                        :label="item.city_text"
                        :value="item.city_code">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="开户行全称：">
                    <el-select v-model="pay_type_2.branch_bank_no" placeholder="选择开户支行" style="width:318px;">
                        <el-option
                        v-for="item in branch_bank_list_2"
                        :key="item.bank_no"
                        :label="item.bank_name"
                        :value="item.bank_no">
                        </el-option>
                    </el-select>
                </el-form-item>
            </template>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">确认</button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>
<script>
export default {
    data() {
        return {
            dialogVisible: false,
            pay_type_1: {
                account_name: '',
                account_num: ''
            },
            pay_type_3: {
                account_name: '',
                account_num: '',
                bank_no: '',
                branch_bank_no: '',
                bank_province_code: '',
                bank_city_code: ''
            },
            pay_type_2: {
                account_name: '',
                account_num: '',
                bank_no: '',
                branch_bank_no: '',
                bank_province_code: '',
                bank_city_code: ''
            },
            account_type: '1',
            firm_dict: {},
            bank_list: [],
            province_list: [],
            city_list_2: [],
            city_list_3: [],
            branch_bank_list_2: [],
            branch_bank_list_3: []
        }
    },

    created() {
        this.getProvinceList()
        this.getBankList()
    },

    methods: {
        showBranchBanks(bol) {
            if (bol !== true) { // 新增模式
                this['pay_type_' + this.account_type].branch_bank_no = '' //  开户银行或者城市改变的时候,开户支行列表要发生变化(清空)
            }
            let bankCityCode = this['pay_type_' + this.account_type].bank_city_code
            let bankNo = this['pay_type_' + this.account_type].bank_no
            if (bankNo === '') {
                return this.openMessage(2, '请先选择开户银行')
            }
            this.$fetch.get({
                url: '/branchbanks',
                params: {
                    city_code: bankCityCode,
                    bank_no: bankNo
                }
            }).then(data => {
                this['branch_bank_list_' + this.account_type] = data.banks
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        provinceChange(province, bol) {
            if (bol !== true) {
                this['pay_type_' + this.account_type].bank_city_code = ''
                this['pay_type_' + this.account_type].branch_bank_no = ''
                this[`branch_bank_list_${this.account_type}`] = []
            }
            this.$fetch.get({
                url: '/bankareas',
                params: {
                    query_type: 'cities',
                    parent_code: province
                }
            }).then(data => {
                this['city_list_' + this.account_type] = data.data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        getProvinceList() {
            this.$fetch.get({
                url: '/bankareas',
                params: {
                    query_type: 'provinces'
                }
            }).then(data => {
                this.province_list = data.data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        getBankList() {
            this.$fetch.get({
                url: '/banks'
            }).then(data => {
                this.bank_list = data.banks
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        open(obj, payment) {
            this.dialogVisible = true
            this.clearObject(this.pay_type_1) // 每次进来先清空数据
            this.clearObject(this.pay_type_2)
            this.clearObject(this.pay_type_3)
            this.city_list_2 = []
            this.city_list_3 = []
            this.branch_bank_list_2 = []
            this.branch_bank_list_3 = []
            this.firm_dict = obj

            if (payment) {
                this.mode = 'edit'
                this.account_type = String(payment.account_type) // 1支付宝2对公转账3对私转账
                this['pay_type_' + this.account_type] = payment // 赋值
                if (this.account_type !== '1') { // 非支付宝账号
                    this.showBranchBanks(true) // 初始化开户支行列表
                    this.provinceChange(this['pay_type_' + this.account_type].bank_province_code, true) // 初始化城市列表
                }
            } else { // 新增
                this.mode = 'add'
            }
        },

        confirm() { // 确认按钮
            this.$fetch[this.mode === 'add' ? 'post' : 'put']({
                url: this.mode === 'add' ? `/firm/${this.firm_dict.id}/paymentaccount` : `/firm/${this.firm_dict.id}/paymentaccount/${this['pay_type_' + this.account_type].id}`,
                params: {
                    account_type: Number(this.account_type),
                    account_name: this['pay_type_' + this.account_type].account_name.trim(),
                    account_num: this['pay_type_' + this.account_type].account_num.trim(),
                    branch_bank_no: this['pay_type_' + this.account_type].branch_bank_no || '' // 支付宝没有开户支行
                }
            }).then(data => {
                this.openMessage(1, '保存成功')
                this.$emit('saveSuccess')
                this.cancel()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        cancel() {
            this.dialogVisible = false
        }
    }
}
</script>
<style lang="scss" scoped>
    .supplier_name,.account_type{
        line-height: 30px;
        span{
            display: inline-block;
            width: 97px;
            font-size: 14px;
            color: #333333;
            text-align: right;
        }
    }
    .account_type{
        margin-bottom: 8px;
        label+label{
            margin-left: 20px;
        }
    }
    /deep/ .el-form .el-form-item__label{
        line-height: 31px;
        font-size: 14px;
        color: #333333;
    }
    /deep/ .el-form-item--small.el-form-item{
        margin-bottom: 0px;
    }
</style>
