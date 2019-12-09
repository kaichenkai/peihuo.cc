<template>
    <div class="caigou_record" v-if="show_1">
        <div class="tool-container"><img src="~@/assets/images/a1.png" alt="" @click="cancel"><span @click="cancel">员工管理</span><span>/</span><span class="now">员工详情</span></div>
        <div class="top" v-if="show_2">
            <img :src="employee_info.avatar" alt="">
            <span class="name">{{employee_info.name}}</span>
            <span class="power" v-show="employee_info.admin_status">管理员</span>
            <span class="power" v-show="employee_info.purchaser_status">采购员</span>
            <div class="open" @click="show_2=false">展开</div>
        </div>
        <div class="zhankai" v-else>
            <div class="left">
                <dl>
                    <dt><img :src="employee_info.avatar" alt=""></dt>
                    <dd>{{employee_info.name}}</dd>
                    <dd>
                        <span class="power" v-show="employee_info.admin_status">管理员</span>
                        <span class="power" v-show="employee_info.purchaser_status">采购员</span>
                    </dd>
                </dl>
            </div>
            <div class="center">
                <div class="up">
                    <p><span>{{employee_info.name||employee_info.nickname||'未设置'}}</span><span>{{employee_info.position||'未设置'}}</span></p>
                    <p><span>昵称</span><span>员工职位</span></p>
                </div>
                <div class="down">
                    <p><span>{{employee_info.phone||'未设置'}}</span><span>{{employee_info.date_onboarding||'未设置'}}</span><span>{{employee_info.birthday||'未设置'}}</span><span class="remark">{{employee_info.remarks||'未设置'}}</span></p>
                    <p><span>手机号</span><span>入职日期</span><span>员工生日</span><span class="remark">备注</span></p>
                </div>
            </div>
            <div class="right">
                <button @click="editEmployee">编辑信息</button>
                <button class="delete" @click="deleteEmployee">删除</button>
            </div>
            <div class="retract" @click="show_2=true">收起</div>
        </div>
        <div class="record">
            <div class="role">
                <ul>
                    <li class="active">采购记录</li>
                </ul>
            </div>
            <div class="huizong">
                <div class="tab">
                    <span :class="{active:active===1}" @click="active=1">日汇总</span>
                    <span :class="{active:active===2}" @click="active=2">月汇总</span>
                    <span :class="{active:active===3}" @click="active=3">按货品汇总</span>
                    <span :class="{active:active===4}" @click="active=4">按供货商汇总</span>
                </div>
                <template v-if="active===3">
                    日期：
                    <el-date-picker
                        v-model="record_date_good"
                        type="month"
                        size="small"
                        :clearable="true"
                        :editable="true"
                        value-format="yyyy-MM-dd"
                        placeholder="选择日期">
                    </el-date-picker>
                </template>
                <template v-if="active===4">
                    日期：
                    <el-date-picker
                        v-model="record_date_firm"
                        type="month"
                        size="small"
                        :clearable="true"
                        :editable="true"
                        value-format="yyyy-MM-dd"
                        placeholder="选择日期">
                    </el-date-picker>
                </template>
                <el-table v-if="active===1"
                    :key="1"
                    :data="tableData"
                    :height="tableHeight-160"
                    v-scrollLoad="scrollLoad"
                    v-loading="tableLoading"
                    style="width: 100%"
                >
                    <el-table-column
                        prop="date"
                        label="采购时间"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="goods_num"
                        label="货品数"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="总件数"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="">
                    </el-table-column>
                    <el-table-column
                        label=""
                        width="50">
                        <template slot-scope="scope">
                            <p style="font-size: 22px;color: #979797;cursor: pointer;" @click="seeDetail(scope.row)"><i class="el-icon-arrow-right"></i></p>
                        </template>
                    </el-table-column>
                    <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
                </el-table>
                <el-table v-else-if="active===2"
                    :key="2"
                    :data="tableData"
                    :height="tableHeight-160"
                    v-scrollLoad="scrollLoad"
                    v-loading="tableLoading"
                    style="width: 100%"
                >
                    <el-table-column
                        prop="year"
                        label="采购时间"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="goods_num"
                        label="货品数"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="总件数"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="">
                    </el-table-column>
                    <el-table-column
                        label=""
                        width="50">
                        <template slot-scope="scope">
                            <p style="font-size: 22px;color: #979797;cursor: pointer;" @click="seeDetail(scope.row)"><i class="el-icon-arrow-right"></i></p>
                        </template>
                    </el-table-column>
                    <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
                </el-table>
                <el-table v-else-if="active===3"
                    :key="3"
                    :data="tableData"
                    :height="tableHeight-160"
                    v-scrollLoad="scrollLoad"
                    v-loading="tableLoading"
                    style="width: 100%"
                >
                    <el-table-column
                        prop="goods_name"
                        label="货品名"
                        width="">
                    </el-table-column>
                    <el-table-column
                        prop="purchase_count"
                        label="次数"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="goods_amount"
                        label="件数"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        label="商户"
                        width="">
                        <template slot-scope="scope">
                            {{scope.row.firm_name_list?scope.row.firm_name_list.join('、'):''}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        label=""
                        width="50">
                        <template slot-scope="scope">
                            <p style="font-size: 22px;color: #979797;cursor: pointer;" @click="seeDetail(scope.row)"><i class="el-icon-arrow-right"></i></p>
                        </template>
                    </el-table-column>
                    <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
                </el-table>
                <el-table v-else
                    :key="4"
                    :data="tableData"
                    :height="tableHeight-160"
                    v-scrollLoad="scrollLoad"
                    v-loading="tableLoading"
                    style="width: 100%"
                >
                    <el-table-column
                        prop="firm_name"
                        label="商户"
                        width="250">
                    </el-table-column>
                    <el-table-column
                        prop="purchase_count"
                        label="次数"
                        width="80">
                    </el-table-column>
                    <el-table-column
                        prop="goods_subtotal"
                        label="总支出/元"
                        width="100">
                    </el-table-column>
                    <el-table-column
                        label="采购货品"
                        width="">
                        <template slot-scope="scope">
                            {{scope.row.goods_name_list?scope.row.goods_name_list.join('、'):''}}
                        </template>
                    </el-table-column>
                    <el-table-column
                        label=""
                        width="50">
                        <template slot-scope="scope">
                            <p style="font-size: 22px;color: #979797;cursor: pointer;" @click="seeDetail(scope.row)"><i class="el-icon-arrow-right"></i></p>
                        </template>
                    </el-table-column>
                    <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
                </el-table>
            </div>
        </div>
        <caigou-detail ref="caigouDetail"></caigou-detail>
        <add-employees-box2 ref="addEmployeesBox2"></add-employees-box2>
    </div>
</template>
<script>
import { formatDate } from '@/utils'
import caigouDetail from './caigou_detail.vue'
import addEmployeesBox2 from './add_employees_box2.vue'
export default {
    data() {
        return {
            show_1: true,
            show_2: true,
            employee_info: {},
            record_date_good: formatDate(new Date(), 'yyyy-MM-dd'),
            record_date_firm: formatDate(new Date(), 'yyyy-MM-dd'),
            tableData: [],
            active: 1
        }
    },

    watch: {
        active() {
            this.queryData()
        },
        record_date_good() {
            this.queryData()
        },
        record_date_firm() {
            this.queryData()
        }
    },

    computed: {
        action() {
            let action = ''
            switch (this.active) {
                case 1:
                    action = 'day_summary_record'
                    break
                case 2:
                    action = 'month_summary_record'
                    break
                case 3:
                    action = 'with_goods_summary'
                    break
                case 4:
                    action = 'with_firm_summary'
                    break
            }
            return action
        },
        start_date() {
            let date = ''
            switch (this.active) {
                case 1:
                case 2:
                    date = ''
                    break
                case 3:
                    date = this.record_date_good
                    break
                case 4:
                    date = this.record_date_firm
                    break
            }
            return date.substr(0, 8) + '01'
        },
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
        }

    },

    created() {
        this.show_2 = true
        this.active = 1
        this.employee_info = JSON.parse(this.$route.query.item)
        this.queryData()
        this.getEmployeeInfo(this.employee_info.staff_id)
    },

    methods: {
        gettime(obj) {
            let time = ''
            switch (this.active) {
                case 1:
                case 2:
                    time = obj.date || obj.year + '-01'
                    break
                case 3:
                    time = this.record_date_good.substr(0, 8) + '01'
                    break
                case 4:
                    time = this.record_date_firm.substr(0, 8) + '01'
                    break
            }
            return time
        },
        seeDetail(row) {
            this.$refs.caigouDetail.open(row, this.active, this.employee_info, this.gettime(row))
        },
        getTableList(page) {
            return this.queryData(page)
        },
        queryData(page = 0) {
            return this.$fetch.get({
                url: `/staff/${this.employee_info.staff_id}`,
                params: {
                    action: this.action,
                    page,
                    limit: this.active === 2 ? '' : 20,
                    start_date: this.start_date,
                    end_date: this.end_date
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.purchase_goods_data_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.purchase_goods_data_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e)
            })
        },
        editEmployee() {
            this.$fetch.get({
                url: `/staff/${this.employee_info.staff_id}`,
                params: {
                    action: 'staff_info'
                }
            }).then(data => {
                this.$refs.addEmployeesBox2.open({
                    mode: 'update',
                    data: data.staff_data
                })
            })
        },
        deleteEmployee(e) {
            this.$myWarning({
                message: '确定要删除吗？'
            }).then(data => {
                this.$fetch.delete({
                    url: `/staff/${this.employee_info.staff_id}`
                }).then(data => {
                    this.openMessage(1, '删除成功')
                    this.$router.back(-1)
                })
            }).catch(e => {

            })
        },
        getEmployeeInfo(id) {
            this.$fetch.get({
                url: `/staff/${id}`,
                params: {
                    action: 'staff_info'
                }
            }).then(data => {
                this.employee_info = data.staff_data
            })
        },
        cancel() {
            this.$router.back(-1)
        }
    },

    components: {
        caigouDetail,
        addEmployeesBox2
    }
}
</script>
<style lang="scss" scoped>
    .caigou_record{
        // position: absolute;
        // top: -103px;
        // z-index: 11;
        // width: 100%;
        // height: calc(100% + 105px);
        // background-color: #fff;
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
        .top{
            padding: 10px;
            line-height: 25px;
            background: #f5f8f7;
            img{
                height: 30px;
                width: 30px;
                margin-right: 10px;
                border-radius: 50%;
                vertical-align: top;
            }
            .name{
                font-size: 24px;
                color: #333;
                margin-right: 10px;
                vertical-align: top;
            }
        }
        .power{
            display: inline-block;
            width: 62px;
            height: 26px;
            line-height: 26px;
            margin-right: 8px;
            border-radius: 2px;
            border: 1px solid #666;
            font-size: 14px;
            color: #666;
            text-align: center;
        }
        .open,.retract{
            float: right;
            width: 50px;
            height: 26px;
            line-height: 26px;
            font-size: 14px;
            color: rgba(107,164,239,0.95);
            background: url('~@/assets/images/down.png') no-repeat right center;
            cursor: pointer;
        }
        .zhankai{
            padding: 10px;
            background: #f5f8f7;
            >div{
                display: inline-block;
                vertical-align: top;
                &.left{
                    width: 250px;
                    padding: 2px;
                    border-right: 1px solid #d8d8d8;
                    dl{
                        overflow: hidden;
                        dt{
                            width: 80px;
                            height: 80px;
                            float: left;
                            img{
                                width: 100%;
                                height: 100%;
                                border-radius: 50%;
                            }
                        }
                        dd{
                            float: right;
                            width: 150px;
                            &:nth-of-type(1){
                                padding-top: 12px;
                                padding-bottom: 12px;
                                font-size: 18px;
                                color: #333333;
                            }
                        }
                    }
                }
                &.center{
                    width: 488px;
                    padding-left: 20px;
                    border-right: 1px solid #d8d8d8;
                    .up{
                        margin-bottom: 4px;
                    }
                    p{
                        span{
                            display: inline-block;
                            width: 120px;
                            line-height: 20px;
                            font-size: 14px;
                            color: #333333;
                            vertical-align: top;
                            &.remark{
                                width: 95px;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                            }
                        }
                        &:nth-of-type(2){
                            span{
                                color:#999;
                            }
                        }
                    }
                }
                &.right{
                    margin-left: 20px;
                    line-height: 84px;
                    button{
                        width: 80px;
                        height: 30px;
                        line-height: 28px;
                        border: 1px solid #979797;
                        outline: none;
                        background: #fff;
                        text-align: center;
                        color: #333;
                        margin-right: 12px;
                        &.delete{
                            color: #f66;
                        }
                    }
                }
                &.retract{
                    background: url('~@/assets/images/up.png') no-repeat right center;
                }
            }
        }
        .record{
            height: 690px;
            margin-top: 15px;
            border: 1px solid #f2f2f2;
            .role{
                float: left;
                width: 100px;
                height: 100%;
                background: #F9F9F9;
                ul{
                    li{
                        width: 100%;
                        height: 40px;
                        line-height: 40px;
                        text-align: center;
                        font-size: 16px;
                        color: #333333;
                        &.active{
                            border-left: 2px solid #009688;
                            background-color: #fff;
                        }
                    }
                }
            }
            .huizong{
                float: right;
                width: calc(100% - 100px);
                height: 100%;
                padding: 15px;
                .tab{
                    span{
                        display: inline-block;
                        width: 100px;
                        height: 26px;
                        margin-right: 14px;
                        line-height: 24px;
                        border: 1px solid #999999;
                        border-radius: 13px;
                        font-size: 14px;
                        color: #333333;
                        text-align: center;
                        &.active{
                            background: rgba(0, 150, 136, 0.1);
                            border: 1px solid transparent;
                            color: #009688;
                        }
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
            /deep/ .el-input__prefix{
                top: 2px;
            }
            /deep/ .el-input__suffix{
                top: 2px;
            }
        }
    }
</style>
