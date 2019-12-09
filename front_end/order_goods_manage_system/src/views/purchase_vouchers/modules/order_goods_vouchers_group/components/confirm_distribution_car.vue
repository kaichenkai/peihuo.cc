<template>
    <el-dialog
    class="print-container"
    :lock-scroll="false"
    :visible.sync="dialogVisible"
    :modal-append-to-body="false"
    width="595px">
    <div class="left-container">
        <h1 v-if="!isDistributionCar">确认分车完成并打印待结算单</h1>
        <h1 v-else>打印待结算单</h1>
        <p><span>货品名称:</span>{{goodsData.goods_name}}</p>
        <p><span>供货商:</span>{{goodsData.firm_name}}</p>
        <p><span>实配数量:</span>{{goodsData.allocated_amount}}</p>
        <p>
            <span>备注:</span><input v-model="remarks" type="text"/>
        </p>
        <div class="btn-group">
            <button class="btn confirm" v-if="!isDistributionCar" @click="confirmDistributionCar">确认并打印</button>
            <button class="btn confirm" v-else @click="print">打印</button>
            <button class="btn cancel" @click="dialogVisible = false">取消</button>
        </div>
    </div><div class="right-container" ref="outerContainer">
        <div class="inner-cotnainer" ref="innerContainer">
            <table class="header" ref="header">
                <tr>
                    <th>店铺</th>
                    <th>已配货</th>
                </tr>
            </table>
            <table class="content">
                <tr v-for="item in goodsData.allocation_list" :key="item.id">
                    <td>{{item.shop_name}}</td>
                    <td>{{item.allocated_amount}}</td>
                </tr>
            </table>
        </div>
    </div>
    </el-dialog>
</template>

<script>
import StickyListHeaders from 'sticky-list-headers'
export default {
    data() {
        return {
            dialogVisible: false,
            isDistributionCar: false,
            goodsData: {},
            remarks: ''
        }
    },
    mounted() {
        document.addEventListener('keydown', this.keydown)
    },

    beforeDestroy() {
        document.removeEventListener('keydown', this.keydown)
    },

    methods: {
        open(obj = {}) {
            this.dialogVisible = true
            this.catchedData = obj
            this.goodsData = obj.data
            this.callback = obj.callback || function() {}
            this.isDistributionCar = obj.isDistributionCar
            // this.getAllocationorder()
            this.$nextTick(function() {
                new StickyListHeaders({
                    outerContainer: this.$refs.outerContainer,
                    innerContainer: this.$refs.innerContainer,
                    headers: [this.$refs.header]
                })
            })
        },

        keydown(e) {
            if (!this.dialogVisible || e.keyCode !== 13) return
            if (this.isDistributionCar) {
                this.print()
            } else {
                this.confirmDistributionCar()
            }
        },

        confirmDistributionCar() {
            this.$fetch.put({
                url: '/allocationorder/' + this.catchedData.data.allocation_order_id,
                params: {
                    action: 'confirm'
                }
            }).then(() => {
                this.openMessage(1, '分车成功')
                this.print()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        // getAllocationorder(data) {
        //     return this.$fetch.get({
        //         url: '/allocationorder/' + this.catchedData.data.allocation_order_id
        //     }).then(data => {
        //         this.table

        //         return data
        //     }).catch(e => {
        //         this.openMessage(0, e || '获取采购详情失败')
        //     })
        // },

        print() {
            this.$fetch.post({
                url: '/firmsettlementvoucher',
                params: {
                    allocation_order_id: this.catchedData.data.allocation_order_id,
                    remarks: this.remarks
                }
            }).then(() => {
                this.callback()
                this.dialogVisible = false
                this.remarks = ''
                this.openMessage(1, '打印成功')
            }).catch(e => {
                this.openMessage(0, e || '打印失败')
            })
        }
    }
}
</script>

<style lang="scss" scoped>
/deep/ .el-dialog__header {
    display: none;
}

/deep/ .el-dialog .el-dialog__body {
    padding: 0 !important;
}

.left-container, .right-container {
    display: inline-block;
    vertical-align: top;
    height: 100%;
    max-height: 395px;
}

.left-container {
    width: 410px;
    padding: 20px;
    overflow: auto;

    h1 {
        font-size: 20px;
        color: #333333;
    }

    p {
        margin: 10px 0;
        font-size: 14px;
        color: #333333;

        span {
            display: inline-block;
            width: 70px;
        }

        input {
            width: 300px;
            height: 30px;
            background: #FFFFFF;
            border: 1px solid #DDDDDD;
        }
    }

    .btn-group {
        margin-top: 170px;
        text-align: center;
        .btn {
            display: inline-block;
            width: 90px;
            height: 36px;
            border-radius: 2px;
        }

        .confirm {
            background: #009688;
            font-size: 14px;
            color: #FFFFFF;
        }

        .cancel {
            margin-left: 20px;
            background: #E7E7E7;
            border: 1px solid #CCCCCC;
            font-size: 14px;
            color: #666666;
        }
    }
}

.right-container {
    position: relative;
    width: 185px;
    background: #F7F7F7;
    min-height: 395px;

    .inner-cotnainer {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        overflow: auto;
        @mixin tableStyle {
            td,th {
                background: #F7F7F7;
                text-align: center;
                height: 40px;
                line-height: 40px;
            }

            td:nth-of-type(1), th:nth-of-type(1) {
                width: 100px;
            }

            td:nth-of-type(2), th:nth-of-type(2) {
                // width: 100px;
            }
        }

        .header {
            height: 40px;
            line-height: 40px;
            font-size: 14px;
            color: #333333;
            box-shadow: 0 4px 4px 0 rgba(0,0,0,0.05);
        }

        .content {
            font-size: 14px;
            color: #333333;
        }

        table {
            @include tableStyle;
            width: 100%;
        }
    }
}
</style>
