<template>
    <transition name="slide-fade">
        <div class="caigou_detail" @click="close" v-if="show_1">
            <div class="content" @click.stop>
                <div class="top">
                    汇总详情
                    <i class="el-icon-close" @click="close"></i>
                </div>
                <div class="middle">
                    <div class="good_or_firm_name" :class="[{good_name:active===3},{firm_name:active===4}]" v-if="active===3||active===4">
                        <span>{{item.firm_name||item.goods_name}}</span>
                    </div>
                    <div class="datetime" :class="{flr:active===3||active===4}">
                        日期：
                        <el-date-picker
                            v-model="start_date"
                            :type="active===1?'date':'month'"
                            size="small"
                            :clearable="true"
                            :editable="true"
                            value-format="yyyy-MM-dd"
                            placeholder="选择日期">
                        </el-date-picker>
                    </div>

                </div>
                <!-- 日汇总详情 -->
                <el-table v-if="active===1"
                    :key="1"
                    :data="tableData"
                    max-height="760"
                    :row-class-name="getRowClass"
                    style="width: 100%"
                >
                    <el-table-column
                        type="index"
                        label="序号"
                        width="50">
                        <template slot-scope="scope">
                            {{scope.$index === 0?'累计':scope.$index}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="goods_name"
                        label="货品名"
                        width="">
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="采购件数"
                        width="80">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        label="商户"
                        width="150">
                        <template slot-scope="scope">
                            {{manyFirmName(scope.row.firm_purchase_record)}}
                        </template>
                    </el-table-column>
                    <el-table-column type="expand"
                        width="50">
                        <template slot-scope="scope">
                            <div class="expand_tr">
                                <p v-for="(item,index) in scope.row.firm_purchase_record" :key="index">
                                    <span></span>
                                    <span></span>
                                    <span>{{item.actual_amount}}</span>
                                    <span>{{item.subtotal}}</span>
                                    <span>{{item.firm_name}}</span>
                                </p>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
                <!-- 月汇总详情 -->
                <el-table v-else-if="active===2"
                    :key="2"
                    :data="tableData"
                    :row-class-name="getRowClass"
                    max-height="760"
                    style="width: 100%"
                >
                    <el-table-column
                        type="index"
                        label="序号"
                        width="50">
                        <template slot-scope="scope">
                            {{scope.$index === 0?'累计':scope.$index}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="goods_name"
                        label="货品名"
                        width="">
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="采购件数"
                        width="80">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        label="商户"
                        width="150">
                        <template slot-scope="scope">
                            {{manyFirmName(scope.row.firm_purchase_record)}}
                        </template>
                    </el-table-column>
                    <el-table-column type="expand"
                        width="50">
                        <template slot-scope="scope">
                            <div class="expand_tr">
                                <p v-for="(item,index) in scope.row.firm_purchase_record" :key="index">
                                    <span></span>
                                    <span></span>
                                    <span>{{item.actual_amount}}</span>
                                    <span>{{item.subtotal}}</span>
                                    <span>{{item.firm_name}}</span>
                                </p>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
                <!-- 货品汇总详情 -->
                <el-table v-else-if="active===3"
                    :key="3"
                    :data="tableData"
                    max-height="760"
                    style="width: 100%"
                >
                    <el-table-column
                        type="index"
                        label="序号"
                        width="50">
                        <template slot-scope="scope">
                            {{scope.$index === 0?'累计':scope.$index}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="date"
                        label="采购时间"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        label="供货商"
                        width="">
                        <template slot-scope="scope">
                            {{scope.row.firm_name_list?scope.row.firm_name_list.join('、'):''}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="采购件数"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="price"
                        label="单价/元"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="100">
                    </el-table-column>
                </el-table>
                <!-- 供货商汇总详情 -->
                <el-table v-else
                    :key="4"
                    :data="tableData"
                    max-height="760"
                    style="width: 100%"
                >
                    <el-table-column
                        type="index"
                        label="序号"
                        width="50">
                        <template slot-scope="scope">
                            {{scope.$index === 0?'累计':scope.$index}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        prop="goods_name"
                        label="货品名"
                        width="">
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="采购件数"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="累计金额"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="price"
                        label="均价/元"
                        width="100">
                    </el-table-column>
                </el-table>
            </div>
        </div>
    </transition>
</template>
<script>
export default {
    data() {
        return {
            show_1: false,
            tableData: [],
            params: {
                status: 0, // 0待结算1已结算
                order_by: '',
                desc: false,
                keyword: ''
            },
            start_date: '',
            active: 0,
            item: {},
            employee_info: {}
        }
    },

    computed: {
        end_date() {
            let date = this.start_date
            let yearStr = date.substr(0, 4)
            let monthStr = date.substr(5, 2)
            let year = Number(yearStr)
            let month = Number(monthStr)
            if (month < 9) {
                month++
                monthStr = 0 + '' + month
            } else if (month < 12) {
                month++
                monthStr = month + ''
            } else if (month === 12) {
                year++
                yearStr = year + ''
                monthStr = '01'
            }
            return yearStr + '-' + monthStr + '-01'
        },
        action() {
            let action = ''
            switch (this.active) {
                case 1:
                    action = 'day_summary_detail'
                    break
                case 2:
                    action = 'month_summary_detail'
                    break
                case 3:
                    action = 'goods_summary_detail'
                    break
                case 4:
                    action = 'firm_summary_detail'
                    break
            }
            return action
        }
    },

    watch: {
        params: {
            handler() {
                // this.debouncedGetAnswer()
            },
            deep: true
        },
        start_date() {
            this.queryData()
        }
    },

    methods: {
        getRowClass(row) {
            if (row.row.firm_purchase_record && row.row.firm_purchase_record.length > 1) {
                return ''
            } else {
                return 'no_expand'
            }
        },
        manyFirmName(arr) {
            if (arr) {
                if (arr.length > 1) {
                    return '多供货商'
                } else {
                    return arr[0].firm_name
                }
            } else {
                return ''
            }
        },
        open(item, active, employeeInfo, time) {
            this.show_1 = true
            this.active = active
            this.employee_info = employeeInfo
            this.item = item
            this.start_date = time
            this.queryData()
        },
        close() {
            this.show_1 = false
        },
        queryData(page = 0) { // 查询待结算列表
            let that = this
            that.$fetch.get({
                url: `/staff/${this.employee_info.staff_id}`,
                params: {
                    action: this.action,
                    limit: 1000,
                    date: this.start_date,
                    start_date: this.start_date,
                    end_date: this.end_date,
                    page,
                    goods_id: this.item.goods_id,
                    firm_id: this.item.firm_id
                }
            }).then(data => {
                let obj = {
                    goods_amount: (data.day_summary_data ? data.day_summary_data.total_actual_amount : '') || (data.month_summary_data ? data.month_summary_data.total_actual_amount : '') || (data.goods_summary_data ? data.goods_summary_data.total_actual_amount : '') || (data.firm_summay_data ? data.firm_summay_data.total_actual_amount : ''),
                    goods_subtotal: (data.day_summary_data ? data.day_summary_data.total_spending : '') || (data.month_summary_data ? data.month_summary_data.total_spending : '') || (data.goods_summary_data ? data.goods_summary_data.total_spending : '') || (data.firm_summay_data ? data.firm_summay_data.total_spending : '')
                }
                that.tableData = data.purchase_goods_data_list
                this.tableData.length && this.tableData.splice(0, 0, obj)
            }).catch(e => {
                that.openMessage(0, e)
            })
        }
    }
}
</script>
<style lang="scss" scoped>
    .caigou_detail{
        position: fixed;
        top: 0;
        right: 0;
        z-index: 2;
        width: 100%;
        height: 100%;
        background: transparent;
        .content{
            position: absolute;
            top: 0;
            right: 0;
            width: 680px;
            height: 100%;
            background: #FFFFFF;
            box-shadow: -10px 0 10px 0 rgba(0,0,0,0.05);
            .top{
                width: 100%;
                height: 56px;
                line-height: 56px;
                padding-left: 10px;
                font-size: 20px;
                color: #333333;
                background: #F9F9F9;
                i{
                    float: right;
                    margin-right: 15px;
                    margin-top: 17px;
                    cursor: pointer;
                }
            }
            .middle{
                padding-top: 7px;
                padding-left: 15px;
                overflow: hidden;
                .good_or_firm_name{
                    padding-left:47px;
                    float: left;
                    height: 30px;
                    line-height: 30px;
                    margin-top: 13px;
                    &.good_name{
                        background: url('~@/assets/images/good.png') no-repeat left center/30px;
                    }
                    &.firm_name{
                        background: url('~@/assets/images/shop.png') no-repeat left center/30px;
                    }
                    span{
                        font-size: 18px;
                        color: #333333;
                    }
                }
                .datetime{
                    height: 50px;
                    margin-right: 14px;
                    &.flr{
                        float:right;
                    }
                }
            }
            .search{
                padding: 15px;
            }
        }
    }
    /deep/ .el-date-editor.el-input{
        margin-top: 8px;
        width: 150px;
        .el-input__inner{
            margin-top: 6px;
            height: 30px;
            line-height: 30px;
            border-radius: 15px;
            font-size: 16px;
            color: #333333;
        }
    }
    /deep/ .expand_tr{
        background-color: #f8f8f8;
        span{
            display: inline-block;
            height: 40px;
            line-height: 40px;
            padding-left: 11px;
            vertical-align: top;
            &:nth-of-type(1){
                width: 50px;
            }
            &:nth-of-type(2){
                width: 250px;
            }
            &:nth-of-type(3){
                width: 80px;
            }
            &:nth-of-type(4){
                width: 100px;
            }
        }
    }
    .slide-fade-enter-active,.slide-fade-leave-active {
        transition: all .5s ease;
    }
    .slide-fade-enter, .slide-fade-leave-to
    /* .slide-fade-leave-active for below version 2.1.8 */ {
        transform: translateX(680px);
        opacity: 0;
    }
    /deep/ .el-table__expanded-cell[class*=cell]{
        padding: 0;
    }
    /deep/ .el-icon-arrow-right:before{
        content: '\E60E'
    }
    /deep/ .el-table__expand-icon > .el-icon{
        left: 29%;
        top: 24%;
        font-size: 22px;
    }
    /deep/ .no_expand .el-table__expand-icon{
        display: none;
    }
    /deep/ .el-table__row:nth-of-type(1) td{
        color: #333;
        font-weight: bold;
    }
    /deep/ .el-table:before{
        height: 0;
    }
    /deep/ .el-input__prefix{
        top: 2px;
    }
    /deep/ .el-input__suffix{
        top: 2px;
    }
</style>
