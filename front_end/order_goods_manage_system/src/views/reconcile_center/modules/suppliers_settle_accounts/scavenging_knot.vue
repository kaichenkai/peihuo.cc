<template>
    <div class="scavenging_knot">
        <bread-crumb :titles="['对账中心 / 供货商结款', '扫码结款']"></bread-crumb>
        <!-- <div class="tool-container"><img src="~@/assets/images/a1.png" alt="" @click="$emit('back')"><span @click="$emit('back')">对账中心/供货商结款</span><span>/</span><span class="now">扫码结款</span></div> -->
        <div class="knot" :style="{height:height+'px'}">
            <p class="search"><span @click="openWaitToSettlement">待结算({{wait_settlement-tableData.length}})</span><input placeholder="输入待结算单号" v-model="input" @keyup.enter="queryData"></p>
            <div class="table">
                <el-table
                    :data="tableData"
                    :max-height="height-141"
                    style="width: 100%;">
                    <el-table-column
                    type="index"
                    label="序号"
                    width="50">
                    </el-table-column>
                    <el-table-column
                    prop="create_time"
                    label="开票时间"
                    width="100">
                    </el-table-column>
                    <el-table-column
                    prop="order_no"
                    label="预结算单号"
                    width="160">
                    </el-table-column>
                    <el-table-column
                    prop="goods_name"
                    label="商品名">
                    </el-table-column>
                    <el-table-column
                    prop="firm_name"
                    width="140"
                    label="供货商">
                    </el-table-column>
                    <el-table-column
                    prop="remarks"
                    width="140"
                    label=备注>
                    </el-table-column>
                    <el-table-column
                    width="70"
                    label="件数">
                    <template slot-scope="scope">
                        {{scope.row.amount}}
                        <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.modi_amount}}</span>
                    </template>
                    </el-table-column>
                    <el-table-column
                    width="100"
                    label="采购价">
                    <template slot-scope="scope">
                        {{scope.row.price}}
                        <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.modi_price}}</span>
                    </template>
                    </el-table-column>
                    <el-table-column
                    width="130"
                    label="应结金额">
                    <template slot-scope="scope">
                        {{scope.row.total_money}}
                        <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.modi_total}}</span>
                    </template>
                    </el-table-column>
                    <el-table-column
                    prop="address"
                    width="120"
                    label="操作">
                        <template slot-scope="scope">
                            <el-button type="text" @click="updateData(scope.row)">修改数据</el-button>
                            <el-button type="text" @click="deleteData(scope.row,$event)" style="color: #FF6666;">移除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
            <div class="bottom">
                结算金额(元)：<span>{{money.toFixed(2)}}</span>
                <div class="button" :class="{canclick:tableData.length>0}" @click="settlement">结算</div>
            </div>
        </div>
        <wait-to-settlement ref="waitToSettlement" @addSettlement='addSettlement' :data_list='tableData'></wait-to-settlement>
        <el-dialog
            title="修改数据"
            :visible.sync="dialogVisible"
            height='228px'
            width="515px">
            <el-form label-position="right" label-width="80px" :model="form">
                <el-form-item label="结算单价：">
                    <el-input v-model="form.modi_price" type='number'></el-input>
                </el-form-item>
                <el-form-item label="应结件数：">
                    <el-input v-model="form.modi_amount" type='number'></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <button class="btn confirm" @click="confirm">确认</button>
                <button class="btn cancel" @click="cancel">取消</button>
            </span>
        </el-dialog>
        <scavenging ref="scavenging" @finishScavenging='finishScavenging'></scavenging>
    </div>
</template>
<script>
import waitToSettlement from './wait_to_settlement.vue'
import scavenging from './scavenging.vue'
import { getTheMostNitemInArray } from '@/utils'
import BreadCrumb from '@/components/modules_top_tools/bread_crumb'
export default {
    data() {
        return {
            tableData: [],
            input: '', // 搜索框的值
            dialogVisible: false,
            form: { // 修改数据弹框的单价和数量
                modi_price: '',
                modi_amount: ''
            },
            height: window.innerHeight - 124,
            wait_settlement: 0 // 待结算单数量
        }
    },

    computed: {
        money() { // 计算结算的总金额
            let _money = 0
            this.tableData.forEach(element => {
                _money += element.total_money
            })
            return this.mostSaveTwoDecimal(_money.toFixed(2)) // 保留两位小数
        }
    },

    created() {
        this.getWaitSettlement()
        if (this.$route.query.orderNo) {
            this.input = this.$route.query.orderNo
            this.queryData()
        }
    },

    mounted() {
        window.addEventListener('resize', this.setTableHeight)
    },

    beforeDestroy() {
        window.removeEventListener('resize', this.setTableHeight)
    },

    methods: {
        setTableHeight() {
            this.height = window.innerHeight - 104
        },

        getWaitSettlement() { // 查询待结算单
            this.$fetch.get({
                url: '/firmsettlementvouchers',
                params: {
                    status: 0
                }
            }).then(data => {
                this.wait_settlement = data.data_count
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        finishScavenging() { // 完成结算按钮
            this.tableData = []
            this.getWaitSettlement()
        },
        settlement() { // 结算按钮
            if (this.tableData.length === 0) {
                return
            }
            let firmList = getTheMostNitemInArray(this.tableData, 'firm_id', this.tableData.length) // 统计结算列表中有几种供货商
            let arr = [] // 存储所有供货商名字的数组
            firmList.forEach(ele => { // 分别计算每个供货商的结算金额
                ele.sun_money = 0
                arr.push(`【${ele.firm_name}】`)
                this.tableData.forEach(element => {
                    if (ele.firm_id === element.firm_id) {
                        ele.sun_money += element.total_money
                        ele.sun_money = this.mostSaveTwoDecimal(ele.sun_money.toFixed(2))
                    }
                })
            })
            if (firmList.length > 1) {
                this.$myWarning({
                    message: `您选择了${arr.join('、')}共${firmList.length}个供货商的单据进行结算，确认继续吗？`
                }).then(() => {
                    this.$refs.scavenging.open(firmList, this.money, this.tableData)
                }).catch(e => {

                })
            } else {
                this.$refs.scavenging.open(firmList, this.money, this.tableData)
            }
        },
        confirm() {
            if (this.form.modi_price <= 0 || this.form.modi_amount <= 0) {
                return this.openMessage(0, '请输入正确的数值')
            }
            if (this.item.modi_price === undefined) { // 修改前的单价,数量,金额
                this.$set(this.item, 'modi_price', this.item.price)
                this.$set(this.item, 'modi_amount', this.item.amount)
                this.$set(this.item, 'modi_total', this.item.total_money)
            } else {
                this.item.modi_price = this.item.price
                this.item.modi_amount = this.item.amount
                this.item.total_money = this.item.total_money
            }
            this.item.amount = this.mostSaveTwoDecimal(Number(this.form.modi_amount).toFixed(2)) // 修改后的单价,数量,金额
            this.item.price = this.mostSaveTwoDecimal(Number(this.form.modi_price).toFixed(2))
            this.item.total_money = this.mostSaveTwoDecimal(Number(this.form.modi_amount * this.form.modi_price).toFixed(2))
            this.cancel()
        },
        mostSaveTwoDecimal(num) { // 最多保留两位小数且最后一位小数不会是0(参数的小数部分也不能超过两位)
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
        cancel() {
            this.dialogVisible = false
        },
        updateData(item) { // 修改数据按钮
            this.form.modi_price = item.price
            this.form.modi_amount = item.amount
            this.form.total_money = item.total_money
            this.item = item
            this.dialogVisible = true
        },
        deleteData(item, e) { // 移除按钮
            if (e.screenX === 0) { // 阻止回车事件
                this.tableData.splice(this.tableData.indexOf(item), 1)
            } else {
                this.$myWarning({
                    title: '移除',
                    message: `确认将【${item.goods_name}】移除结算单吗？`
                }).then(() => {
                    this.tableData.splice(this.tableData.indexOf(item), 1)
                    // this.$refs.waitToSettlement.queryData()
                }).catch(e => {})
            }
        },
        addSettlement(item) { // 加入结算按钮
            this._input = item.order_no
            this.queryData()
        },
        queryData() { // 将待结算单加入结算
            let that = this
            that.$fetch.get({
                url: `/ordersearch/${that.input || that._input}`
            }).then(data => {
                that._input = '' // 中间变量:防止点击加入结算的时候,搜索框内容发生变化
                let _data = data.data
                let bol = false
                that.tableData.forEach(element => {
                    let ele = element
                    if (ele.order_no === _data.order_no) {
                        bol = true
                    }
                })
                if (!bol) {
                    that.tableData.push(_data)
                } else {
                    this.openMessage(2, '该单已加入结算')
                }
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        openWaitToSettlement() { // 待结算按钮
            this.$refs.waitToSettlement.open()
        }
    },

    components: {
        waitToSettlement,
        scavenging,
        BreadCrumb
    }
}
</script>
<style lang="scss" scoped>
    .scavenging_knot{
        background-color: #f8f8f8;
        .tool-container {
            font-size: 16px;
            color: #999999;
            letter-spacing: 0;
            line-height: 30px;
            user-select: none;
            background-color: #fff;
            img {
                margin-right: 5px;
                cursor: pointer;
            }

            span {
                padding: 2px;
                &:nth-of-type(1){
                    cursor: pointer;
                }
            }

            > * {
                display: inline-block;
                vertical-align: middle;
            }

            .now {
                color: #151515;
            }
        }
        .knot{
            position: relative;
            padding: 0 10px;
            background: #f8f8f8;
            .search{
                position: relative;
                line-height: 70px;
                text-align: center;
                span{
                    position: absolute;
                    left: 0px;
                    font-size: 18px;
                    color: #009688;
                    cursor: pointer;
                }
                input{
                    width: 370px;
                    height: 40px;
                    border: 1px solid #DDDDDD;
                    border-radius: 20px;
                    outline: none;
                    text-indent: 18px;
                }
            }
            .table{
                height: calc(100% - 139px);
                overflow-y: auto;
                background: #fff;
                border: 1px solid #F2F2F2;
            }
            .bottom{
                position: absolute;
                left: 10px;
                bottom: 0;
                width: calc(100% - 20px);
                height: 70px;
                line-height: 70px;
                text-align: right;
                box-shadow: 0 -4px 6px 0 rgba(0,0,0,0.04);
                overflow: hidden;
                background-color: #fff;
                .button{
                    float: right;
                    margin-left: 20px;
                    width: 130px;
                    height: 70px;
                    line-height: 70px;
                    text-align: center;
                    background: #DDDDDD;
                    border-radius: 4px;
                    font-size: 20px;
                    color: #999999;
                    cursor: not-allowed;
                    &.canclick{
                        background-color: #009688;
                        color:#fff;
                        cursor: pointer;
                    }
                }
                span{
                    font-size: 20px;
                    color: #ff6666;
                }
            }
        }
    }
    /deep/ .el-table{
        margin-top: 0;
    }
    /deep/ .el-table th{
        background-color: #fff;
        border:none;
    }
    /deep/ .el-form-item{
        margin-bottom: 5px;
    }
    /deep/ .el-form .el-form-item__label{
        line-height: 40px;
    }
    /deep/ .el-table__header-wrapper{
        box-shadow: 0 4px 4px 0 rgba(0,0,0,0.06);
        position: relative;
        z-index: 2;
    }
</style>
