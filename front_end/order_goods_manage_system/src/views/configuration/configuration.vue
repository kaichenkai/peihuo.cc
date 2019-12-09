<template>
    <div class="configuration">
        <div>设置</div>
        <el-tabs v-model="activeName">
            <el-tab-pane label="基础设置" name="first">
                <p class="brand-name">
                    <span class="name">品牌名称：</span>
                    <span>{{stationInfo.name}}</span>
                    <span class="modify" @click="$refs.nameModi.open()">更改</span>
                </p>
                <template>
                    <div class="distribution-mode">
                        <p class="title">采购数据录入方式设置：</p>
                        <div>
                            <my-radio class="radio" v-model="purchaseType" :label="0">通过采购助手</my-radio>
                            <p class="desc">在完成意向单的汇总后，系统会通过『采购助手』小程序给采购员发送待采购货品清单，采购员通过小程序录入采购数据。</p>
                        </div>
                        <div>
                            <my-radio class="radio" v-model="purchaseType" :label="1">后台直接录入</my-radio>
                            <p class="desc">由后台的操作人员直接在汇总单录入采购数据。</p>
                        </div>
                    </div>
                </template>
                <name-modi ref="nameModi" :stationInfo='cloneObject(stationInfo)' @editStationName='editStationName'></name-modi>
            </el-tab-pane>
            <el-tab-pane label="打印机设置" name="second">
                <div class="print_set">
                    <p>已连接的打印机：{{print_list.length}}台<span @click="$refs.addPrinterBox.open()">+添加打印机</span></p>
                    <el-table
                        :data="print_list"
                        style="width: 100%">
                        <el-table-column
                            prop="remarks"
                            label="备注名称"
                            width="120">
                        </el-table-column>
                        <el-table-column
                            prop="printer_num"
                            label="终端号"
                            width="">
                        </el-table-column>
                        <el-table-column
                            prop="printer_key"
                            label="密钥"
                            width="">
                        </el-table-column>
                        <el-table-column
                            label="操作"
                            width="190">
                            <template slot-scope="scope">
                                <el-button @click="printTest(scope.row)" type="text" >打印测试</el-button>
                                <el-button @click="printerRemark(scope.row)" type="text" >备注名称</el-button>
                                <el-button style="color: #f55" @click="deletePrinter(scope.row,$event)" type="text" >删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                    <add-printer-box ref="addPrinterBox" @finishAddPrinter='queryData'></add-printer-box>
                    <printer-remark ref="printerRemark" :print_data='cloneObject(print_data)' @finishRemark='queryData'></printer-remark>
                </div>
                <div class="single_good_set">
                    <span>单品配货打印机：</span>
                    <el-select v-model="choosedPrinter" class="select" size="medium">
                        <el-option v-for="(item, key) in print_list" :value="item.id" :label="item.remarks" :key="key"></el-option>
                    </el-select>
                    <span style="margin-left:30px;">设置打印份数：</span>
                    <el-input v-selectTextOnFocus size='medium' v-model="print_num" placeholder="请输入内容" style="width:217px;" v-removeMouseWheelEvent type="number"></el-input>
                    <el-button @click="save" style="background-color: #009688;color:#fff;padding: 10px 30px;margin-left:30px;">保存</el-button>
                </div>
                <div class="settlement_set">
                    <span style="padding-left: 28px;">结算打印机：</span>
                    <el-select v-model="choosedSettlementPrinter" class="select" size="medium">
                        <el-option v-for="(item, key) in print_list" :value="item.id" :label="item.remarks" :key="key"></el-option>
                    </el-select>
                    <el-checkbox-group
                        v-model="checkList" style="display:inline-block;margin-left: 30px;">
                        <el-checkbox label="kuaiji" style="color: #000;">会计联</el-checkbox>
                        <el-checkbox label="kehu" style="color: #000;">客户联</el-checkbox>
                    </el-checkbox-group>
                    <el-button @click="save1" style="background-color: #009688;color:#fff;padding: 10px 30px;margin-left:171px;">保存</el-button>
                </div>
            </el-tab-pane>
        </el-tabs>

    </div>
</template>

<script>
import nameModi from './modules/name_modi.vue'
import addPrinterBox from './modules/add_printer_box.vue'
import printerRemark from './modules/printer_remark.vue'
import { mapState } from 'vuex'
export default {
    data() {
        return {
            purchaseType: -1,
            activeName: 'first',
            print_list: [],
            print_data: {},
            choosedPrinter: '',
            choosedSettlementPrinter: '',
            print_num: '',
            print_id: '',
            settlement_printer_id: '',
            print_settlement_key: '',
            checkList: []
        }
    },

    watch: {
        activeName(val) {
            if (val === 'first') {
                this.queryData()
            } else {
                this.getConfig()
            }
        },

        purchaseType(newVal) {
            this.$fetch.put({
                url: '/config',
                params: {
                    action: 'purchase_type',
                    new_type: newVal
                }
            }).then(data => {
                // this.openMessage(1, '切换成功')
            }).catch(e => {
                this.openMessage(0, e || '切换失败')
            })
        }
    },

    computed: {
        ...mapState(['stationInfo'])
    },

    created() {
        this.queryData()
        this.getConfig()
    },

    methods: {
        getConfig() {
            let _this = this
            _this.$fetch.get({
                url: 'config'
            }).then(data => {
                let _data = data.config
                if (_data.print_accountant_receipt) {
                    !_this.checkList.includes('kuaiji') && _this.checkList.push('kuaiji')
                } else {
                    _this.checkList.includes('kuaiji') && _this.checkList.splice(_this.checkList.findIndex(item => item === 'kuaiji'), 1)
                }
                if (_data.print_customer_receipt) {
                    !_this.checkList.includes('kehu') && _this.checkList.push('kehu')
                } else {
                    _this.checkList.includes('kehu') && _this.checkList.splice(_this.checkList.findIndex(item => item === 'kehu'), 1)
                }
                _this.print_num = _data.allocation_print_copies
                _this.print_id = _data.allocation_printer_id
                _this.settlement_printer_id = _data.settlement_printer_id
                _this.print_list.forEach(item => {
                    if (item.id === _this.print_id) {
                        _this.choosedPrinter = _this.printer_key = item.remarks
                    }
                    if (item.id === _this.settlement_printer_id) {
                        _this.choosedSettlementPrinter = _this.print_settlement_key = item.remarks
                    }
                })
                this.purchaseType = _data.purchase_type
            }).catch(e => {
                _this.openMessage(0, e)
            })
        },
        save() {
            if (this.choosedPrinter === '') {
                return this.openMessage(0, '请选择打印机')
            } else if (this.print_num === '') {
                return this.openMessage(0, '请输入打印份数')
            } else if (this.print_num <= 0) {
                return this.openMessage(0, '打印份数不能为0或负值')
            } else {
                this.$fetch.put({
                    url: '/config',
                    params: {
                        action: "allocation_printer",
                        printer_id: this.choosedPrinter === this.printer_key ? this.print_id : this.choosedPrinter,
                        copies: this.print_num
                    }
                }).then(() => {
                    this.openMessage(1, '保存成功')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }
        },
        save1() {
            if (this.choosedSettlementPrinter === '') {
                return this.openMessage(0, '请选择打印机')
            } else {
                this.$fetch.put({
                    url: '/config',
                    params: {
                        action: "settlement_printer",
                        printer_id: this.choosedSettlementPrinter === this.print_settlement_key ? this.settlement_printer_id : this.choosedSettlementPrinter,
                        print_accountant_receipt: this.checkList.includes('kuaiji'),
                        print_customer_receipt: this.checkList.includes('kehu')
                    }
                }).then(() => {
                    this.openMessage(1, '保存成功')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }
        },
        printTest(item) {
            this.$fetch.post({
                url: '/print/test',
                params: {
                    printer_id: item.id
                }
            }).catch(erro => {
                this.openMessage(0, erro)
            })
        },
        editStationName() {
            this.getStationInfo()
        },
        getStationInfo() {
            return this.$fetch.get({
                url: '/currentstation'
            }).then(data => {
                this.$store.commit('SET_STATION_INFO', data.data)
            }).catch(e => {
                this.openMessage(0, '获取中转站信息失败,' + e)
            })
        },

        deletePrinter(item, e) {
            this.$myWarning({
                message: '确定要删除该打印机吗？'
            }).then(() => {
                this.$fetch.delete({
                    url: `/printer/${item.id}`,
                    params: {}
                }).then(data => {
                    this.openMessage(1, '删除打印机成功')
                    this.queryData()
                }).catch(e => {
                    this.openMessage(0, e)
                })
            })
        },
        printerRemark(item) {
            this.print_data = item
            this.$refs.printerRemark.open()
        },
        queryData() {
            return this.$fetch.get({
                url: '/printers'
            }).then(data => {
                this.print_list = data.printer_list
            }).catch(e => {
                this.openMessage(0, e || '获取打印机列表数据失败')
            })
        }
    },

    components: {
        nameModi,
        addPrinterBox,
        printerRemark
    }
}
</script>

<style lang="scss" scoped>
    .configuration{
        .brand-name{
            width: 785px;
            height: 40px;
            margin-top: 20px;
            margin-bottom: 10px;
            line-height: 40px;
            border: 1px solid #F2F2F2;
            padding-left: 15px;
            span{
                font-size: 14px;
                color:#333;
                &.name{
                    color:#000;
                    font-weight: bold;
                }
                &.modify{
                    margin-left: 10px;
                    color: rgba(107,164,239,0.95);
                    cursor: pointer;
                }
                &.fr{
                    float: right;
                    margin-right: 15px;
                }
            }

        }
        .distribution-mode{
            width: 785px;
            // height: 90px;
            padding: 10px 15px;
            border: 1px solid #F2F2F2;
            .title{
                line-height: 30px;
                font-size: 14px;
                color:#333;
                font-weight: bold;
            }

            div {
                margin-bottom: 20px;
                .radio {
                    font-size: 14px;
                    color: #333333;
                }

                .desc {
                    margin-top: 6px;
                    padding-left: 28px;
                    font-size: 14px;
                    color: #666666;
                }
            }
        }
        .print_set{
            > p{
                padding: 20px 0 0 5px;
                font-size: 14px;
                span{
                    margin-left: 30px;
                    color: rgba(107, 164, 239, 0.95);
                    cursor: pointer;
                }
            }
        }
        .single_good_set,.settlement_set{
            margin-top: 20px;
            padding-left: 5px;
            font-size: 14px;
        }
    }
</style>
