<template>
    <div class="settlement_detail" v-show="show">
        <div class="tool-container"><img src="~@/assets/images/a1.png" alt="" @click="back"><span @click="back">对账中心/供货商结款</span><span>/</span><span class="now">结算详情</span></div>
        <div class="line"></div>
        <div class="middle">
            <div class="left">
                <p style="margin-top: 6px;"><span>结算金额：{{item.total_money}}</span></p>
                <p style="margin-top: 12px;">供货商：{{firm_str}}</p>
            </div>
            <div class="line"></div>
            <div class="right">
                <p style="margin-top: 8px;">结算时间：{{item.create_time}} <span>操作人：{{item.creator_name}}</span></p>
                <p style="margin-top: 12px;">结算人：{{item.agent_name+' '+item.agent_phone}} <span>结算账号：{{item.payment_account.firm_name}}-{{item.payment_account.account_name}}-{{item.payment_account.account_num}}-{{item.payment_account.bank_name}}</span><span>结算备注：{{item.remarks}}</span></p>
            </div>
        </div>
        <el-table
            :data="tableData"
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
            label="待结算单号"
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
                    {{scope.row.settled_amount}}
                    <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.settled_amount===scope.row.amount?'':scope.row.amount}}</span>
                </template>
            </el-table-column>
            <el-table-column
            width="100"
            label="采购价">
                <template slot-scope="scope">
                    {{scope.row.settled_price}}
                    <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{scope.row.settled_price===scope.row.price?'':scope.row.price}}</span>
                </template>
            </el-table-column>
            <el-table-column
            width="130"
            label="应结金额">
                <template slot-scope="scope">
                    {{mostSaveTwoDecimal((scope.row.settled_price*scope.row.settled_amount).toFixed(2))}}
                    <span style="text-decoration: line-through;font-size: 12px;color: #999999;">{{modi_total(scope.row)}}</span>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>
<script>
export default {
    data() {
        return {
            tableData: [],
            show: true,
            item: {
                firms: [],
                payment_account: {}
            }
        }
    },

    computed: {
        firm_str() { // 所有供货商姓名和金额组成的字符串
            let arr = []
            for (let item of this.item.firms) {
                arr.push(`${item.name}(${item.settled_money})`)
            }
            return arr.join('；')
        }
    },

    created() {
        this.show = true
        this.queryData(this.$route.query.id)
    },

    methods: {
        back() {
            this.$router.back(-1)
        },
        modi_total(item) { // 单价和数量有一个改了,金额就改了
            if (item.settled_amount !== item.amount || item.settled_price !== item.price) {
                return item.total_money
            } else {
                return ''
            }
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
        queryData(id) {
            this.$fetch.get({ // 查询该结算单的信息
                url: `/firmsettlementorder/${id}`
            }).then(data => {
                this.item = data.order_info
            }).catch(e => {
                this.openMessage(0, e)
            })
            this.$fetch.get({ // 查询已结算列表
                url: '/firmsettlementvouchers',
                params: {
                    order_id: id,
                    status: 1 // 0:待结算1:已结算
                }
            }).then(data => {
                this.tableData = data.order_list
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    }
}
</script>
<style lang="scss" scoped>
    .settlement_detail{
        // position: absolute;
        // width: 100%;
        // height: calc(100% + 103px);
        // top: -102px;
        // z-index: 11;
        // background: #fff;
        .tool-container {
            font-family: PingFangSC-Regular;
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
        >.line{
            width: 100%;
            height: 1px;
            background: #d8d8d8;
            margin: 10px 0;
        }
        .middle{
            width: 100%;
            height: 80px;
            padding: 10px;
            background: #F9F9F9;
            div{
                display: inline-block;
                font-size: 14px;
                color: #333333;
                vertical-align: text-top;
                &.left{
                    span{
                        font-size: 16px;
                        color: #333333;
                        font-weight: bold;
                    }
                }
                &.line{
                    width: 1px;
                    height: 100%;
                    margin: 0 15px;
                    background: #DDDDDD;
                }
                &.right{
                    span{
                        margin-left: 25px;
                    }
                }
            }
        }
    }
</style>
