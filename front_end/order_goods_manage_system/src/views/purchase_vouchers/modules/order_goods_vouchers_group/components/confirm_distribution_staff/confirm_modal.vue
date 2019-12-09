<template>
    <el-dialog
    title="配货确认提示"
    :visible.sync="dialogVisible"
    :append-to-body="true"
    width="500px">
    <div>
        <p><span class="item-name">货品名：</span><span>{{goodsData.goods_name}}</span></p>
        <p><span class="item-name">供货商：</span><span>{{goodsData.firm_name}}</span></p>
        <p>
            <span class="item-name">已实配：</span><span>{{goodsData.allocated_amount - stockAmount}}</span>
            <span class="item-name" :class="{'diabled': stockAmount === 0}">到货量：{{goodsData.allocated_amount}}</span>
            <span class="item-name" :class="{'diabled': stockAmount === 0}">仓库待入库：{{stockAmount}}</span>
        </p>
        <p><span class="item-name" v-if="remarks">备注：</span><span>{{remarks}}</span></p>
    </div>
    <span slot="footer" class="dialog-footer">
        <el-button type="primary" v-if="!isDistributionCar" @click="comfirm">货已配完，打印待结算单</el-button>
        <el-button type="primary" v-else @click="comfirm">打印待结算单</el-button>
        <el-button :disabled="stockAmount === 0" :type="stockAmount !== 0 ? 'primary' : ''" @click="uploadRemarks">货未配完</el-button>
    </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            isDistributionCar: false,
            goodsData: {
                allocation_list: []
            },
            remarks: ''
        }
    },

    computed: {
        stockAmount: function() {
            const stockData = this.goodsData.allocation_list.find(value => value.destination === 1)
            return (stockData && stockData.allocated_amount) || 0
        }
    },

    methods: {
        open({ data, callback, isDistributionCar, remarks, allocationOrderId }) {
            console.log(data)
            this.goodsData = data
            this.isDistributionCar = isDistributionCar
            this.callback = callback || function() {}
            this.remarks = remarks
            this.allocationOrderId = allocationOrderId
            this.dialogVisible = true
        },

        comfirm() {
            this.dialogVisible = false
            if (!this.isDistributionCar) {
                this.confirmDistributionCar()
            } else {
                this.print()
            }
            // this.callback()
        },

        uploadRemarks() {
            this.$fetch.put({
                url: '/allocationorder/' + this.allocationOrderId,
                params: {
                    action: 'update_remarks',
                    remarks: this.remarks
                }
            }).then(() => {
                this.dialogVisible = false
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        confirmDistributionCar() {
            this.$fetch.put({
                url: '/allocationorder/' + this.allocationOrderId,
                params: {
                    action: 'confirm',
                    remarks: this.remarks
                }
            }).then(() => {
                this.openMessage(1, '分车成功')
                this.print()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        print() {
            this.$fetch.post({
                url: '/firmsettlementvoucher',
                params: {
                    allocation_order_id: this.allocationOrderId,
                    remarks: this.remarks
                }
            }).then(() => {
                this.callback()
                this.openMessage(1, '打印成功')
            }).catch(e => {
                this.openMessage(0, e || '打印失败')
            })
        }
    }
}
</script>

<style lang="scss" scoped>
p {
    color: #333;
    margin-top: 10px;

    .item-name {
        margin-right: 10px;
    }

    .item-name + span {
        margin-right: 10px;
    }

    .diabled {
        color: #999;
    }
}
</style>
