<template>
    <div class="caigou_bill">
        <div class="header">
            <p @click="$router.push('/home')"></p>
            {{billDate}}采购单
        </div>
        <div class="table">
            <table>
                <colgroup>
                    <col width="7%">
                    <col width="22%">
                    <col width="18%">
                    <col width="18%">
                    <col width="18%">
                    <col width="17%">
                </colgroup>
                <thead>
                    <tr>
                        <td></td>
                        <td>货品名</td>
                        <td>订货</td>
                        <td>实采</td>
                        <td>小计/元</td>
                        <td>商户</td>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="(item, index) in data_list.goods_list">
                        <template v-for="(item1,index1) in item.goods_info_list">
                            <tr @click="caigouBillTr(item1,item.name,item.goods_info_list)" :key="index+''+index1" :class="{odd:index % 2 === 0}">
                                <td style="color:#ccc">{{index1>0?'':getIndex()}}</td>
                                <td>{{index1>0?'':item.name}}</td>
                                <td>{{index1>0?'':item1.estimated_amount}}</td>
                                <template v-if="item1.actual_amount===0">
                                    <td colspan="3" class="manual_entry">
                                        <span @click.stop="manualEntry(item1,item.name)">手工录入</span>
                                    </td>
                                </template>
                                <template v-else>
                                    <td>{{item1.actual_amount}}</td>
                                    <td>{{item1.subtotal}}</td>
                                    <td>
                                        <span class="merchant">{{item1.firm_name}}</span>
                                    </td>
                                </template>
                            </tr>
                        </template>
                    </template>
                </tbody>
            </table>
        </div>
        <div class="footer">
            <ul>
                <li style="width:45%">
                    <p style="color:#000;font-weight: bold;margin-bottom:3px;font-size:14px">{{data_list.order_actual_amount}}</p>
                    <p>总件数</p>
                </li>
                <li style="width:55%">
                    <p style="color:#ff7c56;font-weight: bold;margin-bottom:3px;font-size:14px">￥{{data_list.order_subtotal}}</p>
                    <p>总支出</p>
                </li>
            </ul>
        </div>
        <add-goods-box v-show="show2" @edit='edit' @close='close2' @oneGoodManySupplier='oneGoodManySupplier'></add-goods-box>
        <manual-entry ref="manualEntry" v-show="show1" @close='close1' @chooseSupplier='chooseSupplier' @payType='payType' @finishCaigouEntry='queryData' v-bind="manual_entry_data"></manual-entry>
        <supplier-entry v-show="show3" @addNewSupplier='addNewSupplier' @close='close3' @closeAll='closeAll' @perpotyChange='perpotyChange' @finishEntry='finishEntry' :history_firm_list='history_firm_list'></supplier-entry>
        <pay-type v-show="show4" @close='close4' @closeAll='closeAll' @surePayType='surePayType' ref="payType"></pay-type>
        <add-new-supplier v-show="show5" @close='close5' @finishEntry='finishEntry' @closeAll='closeAll' v-bind="manual_entry_data"></add-new-supplier>
    </div>
</template>
<script>
import addGoodsBox from './modules/add_goods_box.vue'
import manualEntry from './modules/manual_entry.vue'
import supplierEntry from './modules/supplier_entry.vue'
import payType from './modules/pay_type.vue'
import addNewSupplier from './modules/add_new_supplier.vue'
let trIndex = 1
export default {
    data() {
        return {
            show1: false, // 手动录入弹框
            show2: false, // 添加货品弹框
            show3: false, // 选择供货商弹框
            show4: false, // 选择支付方式弹框
            show5: false, // 新增供货商弹框
            data_list: {},
            data_item: {},
            history_firm_list: [],
            supplier_item_before: {},
            manual_entry_data: {
                supplier_item: {
                    name: '选择供货商'
                },
                pay_type: {
                    name: '赊账',
                    id: 4
                },
                good_item: {},
                is_one_good_many_supplier: false,
                caigou_good_name: '',
                firm_id_list: [],
                input_data: {
                    0: { first_time: true, value: '' }, // 件数
                    1: { first_time: true, value: '' }, // 单价
                    2: { first_time: true, value: '' }, // 小计
                    3: { first_time: true, value: '' }, // 重量
                    4: { first_time: true, value: '' }, // 行费
                    5: { first_time: true, value: '' }, // 押金
                    active: true // 单位:斤或者件
                },
                canEditOrAdd: true
            }
        }
    },
    beforeUpdate() {
        trIndex = 1
    },
    computed: {
        billDate() {
            let str = this.data_list.date + ""
            let arr = str.split('-')
            return arr[1] + arr[2]
        }
    },
    methods: {
        getIndex() {
            return trIndex++
        },
        addNewSupplier() {
            this.show3 = false
            this.show5 = true
        },
        edit() {
            this.manual_entry_data.is_one_good_many_supplier = false
            this.manual_entry_data.canEditOrAdd = true
            this.manual_entry_data.input_data = {
                0: { first_time: false, value: this.manual_entry_data.good_item.actual_amount || '' }, // 件数
                1: { first_time: false, value: this.manual_entry_data.good_item.price || '' }, // 单价
                2: { first_time: false, value: this.manual_entry_data.good_item.subtotal || '' }, // 小计
                3: { first_time: false, value: this.manual_entry_data.good_item.actual_weight || '' }, // 重量
                4: { first_time: false, value: this.manual_entry_data.good_item.fee || '' }, // 行费
                5: { first_time: false, value: this.manual_entry_data.good_item.deposit || '' }, // 押金
                active: this.manual_entry_data.good_item.actual_unit === 0 // 单位:斤或者件
            }
            this.manual_entry_data.supplier_item = {
                name: this.manual_entry_data.good_item.firm_name,
                id: this.manual_entry_data.good_item.firm_id
            }
            let typeStr = ''
            let payTypeActive = 0
            switch (this.manual_entry_data.good_item.payment) {
            case 0:
                typeStr = '现金'
                payTypeActive = 1
                break
            case 1:
                typeStr = '银行卡'
                payTypeActive = 2
                break
            case 2:
                typeStr = '微信'
                payTypeActive = 3
                break
            case 3:
                typeStr = '支付宝'
                payTypeActive = 4
                break
            case 4:
                typeStr = '赊账'
                payTypeActive = 0
                break
            case 5:
                typeStr = '其它'
                payTypeActive = 5
                break
            default:
                break
            }
            this.manual_entry_data.pay_type = {
                name: typeStr,
                id: this.manual_entry_data.good_item.payment
            }
            this.$refs.payType.active = payTypeActive
            this.show2 = false
            this.show1 = true
        },
        oneGoodManySupplier() {
            this.manual_entry_data.canEditOrAdd = false
            this.manual_entry_data.is_one_good_many_supplier = true
            this.manual_entry_data.input_data = {
                0: { first_time: true, value: '' }, // 件数
                1: { first_time: true, value: '' }, // 单价
                2: { first_time: true, value: '' }, // 小计
                3: { first_time: true, value: '' }, // 重量
                4: { first_time: true, value: '' }, // 行费
                5: { first_time: true, value: '' }, // 押金
                active: true // 单位:斤或者件
            }
            this.manual_entry_data.supplier_item = {
                name: '选择供货商'
            }
            this.manual_entry_data.pay_type = {
                name: '赊账',
                id: 4
            }
            this.$refs.payType.active = 0
            this.show2 = false
            this.show1 = true
        },
        caigouBillTr(item, key, value) {
            this.supplier_item_before = item
            this.manual_entry_data.good_item = item
            this.manual_entry_data.caigou_good_name = key
            this.manual_entry_data.firm_id_list = []
            value.forEach(element => {
                this.manual_entry_data.firm_id_list.push(element.firm_id)
            })
            this.show2 = true
        },
        queryData() {
            this.closeAll()
            this.$fetch.get({
                url: `/purchase/order/${this.$route.params.item.id}`,
                params: {
                    action: 'get_purchase_goods_list'
                }
            }).then(data => {
                this.data_list = data
            })
        },
        manualEntry(item, key) {
            this.manual_entry_data.caigou_good_name = key
            this.manual_entry_data.good_item = item
            this.oneGoodManySupplier()
            this.manual_entry_data.is_one_good_many_supplier = false
        },
        surePayType(payType) {
            this.manual_entry_data.pay_type = payType
            this.close4()
        },
        finishEntry(supplierItem) {
            if (this.manual_entry_data.is_one_good_many_supplier) {
                if (this.manual_entry_data.firm_id_list.includes(supplierItem.id)) {
                    this.manual_entry_data.canEditOrAdd = false
                } else {
                    this.manual_entry_data.canEditOrAdd = true
                }
            } else {
                if (supplierItem.id !== this.supplier_item_before.firm_id && this.manual_entry_data.firm_id_list.includes(supplierItem.id)) {
                    this.manual_entry_data.canEditOrAdd = false
                } else {
                    this.manual_entry_data.canEditOrAdd = true
                }
            }
            this.manual_entry_data.supplier_item = supplierItem
            this.close3()
            this.show5 = false
        },
        close1() {
            this.show1 = false
            this.manual_entry_data.supplier_item = {
                name: '选择供货商'
            }
            this.manual_entry_data.pay_type = {
                name: '赊账',
                id: 4
            }
            this.$refs.manualEntry.clearData()
        },
        close2() {
            this.show2 = false
        },
        close3() {
            this.show3 = false
            this.show1 = true
        },
        close4() {
            this.show4 = false
            this.show1 = true
        },
        close5() {
            this.show3 = true
            this.show5 = false
        },
        closeAll() {
            this.show1 = false
            this.show3 = false
            this.show4 = false
            this.show5 = false
            this.manual_entry_data.supplier_item = {
                name: '选择供货商'
            }
            this.manual_entry_data.pay_type = {
                name: '赊账',
                id: 4
            }
            this.$refs.manualEntry.clearData()
        },
        chooseSupplier() {
            this.$fetch.get({
                url: `/purchase/order/goods/${this.manual_entry_data.good_item.id}`,
                params: {
                    action: 'get_history_firms'
                }
            }).then(data => {
                this.history_firm_list = data.firm_list
                this.show3 = true
                this.show1 = false
            })
        },
        payType() {
            this.show4 = true
            this.show1 = false
        },
        perpotyChange(val) {
            this.$fetch.get({
                // url: `/${this.manual_entry_data.good_item.goods_id}/firm/list`,
                url: `/firm/list`,
                params: {
                    search: val
                }
            }).then(data => {
                this.history_firm_list = data.firm_list
            }).catch(erro => {
                this.$alert(erro)
            })
        }
    },
    components: {
        addGoodsBox,
        manualEntry,
        supplierEntry,
        payType,
        addNewSupplier
    },
    mounted() {
        this.queryData()
    }
}
</script>

<style lang="scss" scoped>
    .caigou_bill{
        height: 100%;
        background-color: #fff;
        .header{
            position: relative;
            height: 50px;
            line-height: 50px;
            font-size: 18px;
            color:#333;
            text-align: center;
            border-bottom: 1px solid #dedede;
            box-shadow: 0 1px 2px 0 #e4e4e4;
            p{
                position: absolute;
                left: 0;
                top: 0;
                width: 34px;
                height: 100%;
                background: url('~@/assets/images/back.png') no-repeat right center/16px;
            }
        }
        .table{
            max-height: calc(100% - 100px);
            overflow-y: auto;
            table{
                width: 100%;
                thead{
                    tr{
                        line-height: 40px;
                        td{
                            font-size:12px;
                            color:#999;
                            &:nth-of-type(1){
                                padding-left: 10px;
                            }
                        }
                    }
                }
                tbody{
                    tr{
                        line-height: 40px;
                        td{
                            font-size:12px;
                            color:#333;
                            &:nth-of-type(1){
                                padding-left: 10px;
                            }
                            &:nth-of-type(2){
                                max-width: 70px;
                                color:#000;
                                font-weight: bold;
                                white-space:nowrap;
                                overflow: hidden;
                                text-overflow:ellipsis;
                            }
                            &:nth-last-of-type(1){
                                padding-right: 5px;
                            }
                            .merchant{
                                position: relative;
                                top:6px;
                                display: inline-block;
                                height: 20px;
                                line-height: 20px;
                                font-size: 10px;
                                padding: 0 4px;
                                border-radius: 4px;
                                background-color: #eee;
                                color: #9f9f9f;
                                max-width: 62px;
                                white-space:nowrap;
                                overflow: hidden;
                                text-overflow:ellipsis;
                            }
                            &.manual_entry{
                                span{
                                    display: inline-block;
                                    width: 160px;
                                    height: 30px;
                                    line-height: 28px;
                                    color: #009688;
                                    border: 1px solid #009688;
                                    border-radius: 15px;
                                    font-size: 14px;
                                    text-align: center;
                                }
                            }
                        }
                        &.odd{
                            background: rgba(239,242,244,.5);
                        }
                    }
                }
            }
        }
        .footer{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #fff;
            box-shadow: 0 -1px 2px 0 #D4D4D4;
            ul{
                overflow: hidden;
                height: 50px;
                padding-left: 10px;
                padding-top: 10px;
                li{
                    float: left;
                    height: 50px;
                    font-size: 12px;
                    color:#999;
                }
            }
        }
    }
</style>
