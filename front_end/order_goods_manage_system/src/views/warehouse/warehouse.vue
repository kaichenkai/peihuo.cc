<template>
    <div class="warehouse">
        <div style="line-height:30px;margin-bottom:10px;">仓库</div>
        <el-tabs v-model="activeName">
            <el-tab-pane label="出库清单" name="first">
                <outgoing-list :activeName="activeName"></outgoing-list>
            </el-tab-pane>
            <el-tab-pane label="出入库记录" name="second">
                <in-out-record :activeName="activeName" ref="inOutRecord"></in-out-record>
            </el-tab-pane>
            <el-tab-pane label="仓库库存" name="third">
                <warehouse-stock :activeName="activeName" @modiStock='modiStock'></warehouse-stock>
            </el-tab-pane>
            <el-tab-pane label="库存修改记录" name="fourth">
                <stock-modify-history :activeName="activeName" @modiStock='modiStock'></stock-modify-history>
            </el-tab-pane>
        </el-tabs>
        <search-box v-selectTextOnFocus :styleData='styleData' @searchData="searchStockInorder"></search-box>
        <stock-in-bill ref="stockInBill" :stock_in_detail='stock_in_detail' @stockinSuccess='stockinSuccess'></stock-in-bill>
        <printer ref="printer" title="打印待结算单" class="printer">
            <h2 style="font-size: 18px; color: #000">仓库待结算单</h2>
            <p style="margin: 10px 0;">分车单号：{{stock_in_detail.order_no}}</p>
            <p style="margin: 10px 0;">货品名：{{stock_in_detail.goods_name}}</p>
            <p style="margin: 10px 0;">入库数量：{{stock_in_detail.actual_stock_in_amount}}</p>
            <p style="margin: 10px 0;">已配货：{{stock_in_detail.allocated_amount - stock_in_detail.stock_in_amount}}</p>
            <p style="margin: 10px 0;">待结算量：{{stock_in_detail.allocated_amount - stock_in_detail.stock_in_amount + stock_in_detail.actual_stock_in_amount}}</p>
        </printer>
    </div>
</template>

<script>
import Printer from '@/components/printer/printer'
import searchBox from '@/components/common/search.vue'
import inOutRecord from './modules/in_out_record.vue'
import warehouseStock from './modules/warehouse_stock.vue'
import outgoingList from './modules/outgoing_list.vue'
import stockInBill from './modules/stock_in_bill.vue'
import StockModifyHistory from './modules/stock_modify_history'
export default {
    data() {
        return {
            styleData: {
                placeholder: '输入分车单号'
            },
            activeName: 'first',
            stock_in_detail: {},
            willprintGoodsVoucher: {}
        }
    },

    methods: {
        stockinSuccess() {
            this.$refs.inOutRecord.getList()
        },
        handleClick(tab, event) {
            // console.log(tab, event, this.activeName)
        },

        modiStock() {},

        async searchStockInorder(value) {
            if (value.length > 0) {
                this.stock_in_detail = await this.getStockInOrderDetail(value)
                if (this.stock_in_detail.allocation_status === 0) {
                    this.$refs.stockInBill.open({
                        callback: async() => {
                            this.stock_in_detail = await this.getStockInOrderDetail(value)
                            print.call(this)
                        }
                    })
                } else {
                    print.call(this)
                }
            } else {
                // this.openMessage(2, '请输入分车单号')
            }

            function print() {
                this.$refs.printer.open({
                    callback: (printerId) => {
                        this.$fetch.post({
                            url: '/firmsettlementvoucher',
                            params: {
                                allocation_order_id: this.stock_in_detail.allocation_order_id,
                                printer_id: printerId
                            }
                        }).then(() => {
                            this.search = ''
                            this.openMessage(1, '打印成功')
                        }).catch(e => {
                            this.openMessage(0, e || '打印失败')
                        })
                    }
                })
            }
        },

        getStockInOrderDetail(id) {
            return this.$fetch.get({
                url: `/ordersearch/${id}`
            }).then(data => {
                if (![5, 6].includes(data.data.order_type)) {
                    this.openMessage(0, '无效的分车单号')
                } else {
                    return data.data
                }
            }).catch(erro => {
                this.openMessage(0, erro)
            })
        }
    },

    components: {
        searchBox,
        inOutRecord,
        warehouseStock,
        outgoingList,
        stockInBill,
        StockModifyHistory,
        Printer
    }
}
</script>

<style>
    .warehouse{
        position: relative;
    }
</style>
