<template>
    <div class="quoted_price_voucher">
        <h2>{{date && date.replace(/-/g, '-')}}采购报价单</h2>
        <el-table
        border
        :data="tableData"
        stripe
        style="width: 100%">
        <el-table-column
        prop="name"
        label="商品名"
        width="180">
        </el-table-column>
        <!-- <el-table-column
        prop="tag"
        v-if="isPC"
        label="标签"
        width="180">
        <template slot-scope="scope">
            <span v-if="scope.row.tag" class="tag">{{scope.row.tag}}</span>
        </template>
        </el-table-column> -->
        <el-table-column
        prop="remarks"
        v-if="isPC"
        label="意向单说明">
        </el-table-column>
        <el-table-column
        v-if="isPC"
        prop="yesterday_price"
        label="昨日报价">
        </el-table-column>
        <el-table-column
        v-if="isPC"
        prop="purchase_price"
        label="进货价">
        </el-table-column>
        <el-table-column
        label="今日报价">
        <template slot-scope="scope">
            <input class="input" :disabled="!isCanEdit" min="0" type="number" v-removeMouseWheelEvent v-model.number="scope.row.today_price">
        </template>
        </el-table-column>
    </el-table>
    <div v-if="mode == 'edit'">
        <div class="button-group" v-if="status == 1">
            <button @click="save" class="btn share">保存草稿</button>
            <button class="btn confirm" @click="confirm">制作完成</button>
        </div>
        <div class="button-group" v-else>
            <button class="btn share" @click="share">分享</button>
        </div>
    </div>
    <share ref="share"></share>
    </div>
</template>

<script>
import Share from '@/components/share/share'
import domain from '@/config/domain'
import { isPC } from '@/utils'
export default {
    data() {
        return {
            tableData: [],
            status: 0,
            date: '',
            isPC: isPC()
        }
    },

    props: {
        mode: {
            default: 'edit',
            type: String
        }
    },

    computed: {
        isCanEdit() {
            return +this.status !== 2 && this.mode === 'edit'
        }
    },

    created() {
        this.wishOrderId = this.$route.query.wishOrderId
        this.date = this.$route.query.date
        this.getQuotationPriceList()
    },

    methods: {
        getQuotationPriceList() {
            this.$fetch.get({
                url: '/quotation/order/' + this.wishOrderId,
                params: {
                    action: 'get_purchase_quotation'
                }
            }).then(data => {
                this.tableData = data.wish_goods_list
                this.status = data.status
            }).catch(e => {
                this.openMessage(0, '获取报价单失败')
            })
        },

        share() {
            this.$refs.share.open(domain + '/#/viewQuotedPriceVoucher?wishOrderId=' + this.wishOrderId + '&date=' + this.date)
        },

        save() {
            this.uploadData('save_draft').then(data => {
                this.openMessage(1, '保存成功')
                this.getQuotationPriceList()
            }).catch(e => {
                this.openMessage(0, '保存失败')
            })
        },

        confirm() {
            this.uploadData('completed').then(data => {
                this.openMessage(1, '保存成功')
                this.getQuotationPriceList()
            }).catch(e => {
                this.openMessage(0, '保存失败')
            })
        },

        uploadData(action) {
            return this.$fetch.put({
                url: '/quotation/order/' + this.wishOrderId,
                params: {
                    action: action,
                    goods_today_price: this.tableData.reduce((last, next) => {
                        // if (next.today_price) {
                        last[next.id] = next.today_price
                        // }
                        return last
                    }, {})
                }
            })
        }
    },

    components: {
        Share
    }
}
</script>

<style lang="scss" scoped>
.quoted_price_voucher{
    position: relative;
h2 {
    margin-top: 25px;
    margin-bottom: 20px;
    font-size: 20px;
    color: #333333;
    letter-spacing: 0;
    text-align: center;
}
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
}
input[type="number"]{
    -moz-appearance: textfield;
}

.input {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 0 10px;
    height: 100%;
    width: 100%;
    border: none;
    outline: none;
    appearance: none;
    font-size: 14px;
}

.button-group {
    position: absolute;
    top: -230px;
    right: 0;
    margin-top: 208px;
    text-align: center;
    height: 67px;
    line-height: 67px;
}

.btn {
    box-sizing: border-box;
    padding: 4px 20px;
    font-size: 16px;
    border-radius: 2px;
    outline: none;
    border: none;
    line-height: initial;
    user-select: none;

    &:active {
        transform: scale(.9);
    }
}

.confirm {
    margin-left: 20px;
    background: #009688;
    border: 1px solid #009688;
    color: #fff;
}

.share {
    color: #009688;
    border: 1px solid #009688;
    border-radius: 2px;
}

.tag {
    padding: 2px 8px;
    // display: inline-block;
    border-radius: 2px;
    font-size: 12px;
    color: #F88B30;
    border: 1px #F88B30 solid;
}

.remarks {
    padding: 0 10px;
    width: 100%;
    /* height: 25px; */
    font-size: 14px;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    border: none;
}
}
</style>
