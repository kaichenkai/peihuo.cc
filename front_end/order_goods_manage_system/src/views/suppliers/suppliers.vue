<template>
    <div class="suppliers">
        <title-and-tools :config="titleToolConfig"></title-and-tools>
        <el-tabs v-model="activeName">
            <el-tab-pane label="供货商列表" name="first">
                <supplier-list ref="supplierList" @openGoodsList='openGoodsList' @chooseGoods='chooseGoods' @editSupplier='editSupplier'></supplier-list>
            </el-tab-pane>
            <el-tab-pane label="操作记录" name="second">
                <operate-list ref="operateList"></operate-list>
            </el-tab-pane>
        </el-tabs>

        <add-supplier-box ref="add_Supplier"></add-supplier-box>
        <goods-list ref="goodsList"></goods-list>
        <choose-goods ref="chooseGoods" @choosed='choosed'></choose-goods>
    </div>
</template>

<script>
import titleAndTools from '@/components/modules_top_tools/title_&_tools.vue'
import addSupplierBox from './modules/add_supplier.vue'
import goodsList from './modules/goods_list.vue'
import supplierList from './modules/supplier_list.vue'
import operateList from './modules/operate_list.vue'
import chooseGoods from '@/components/choose_goods/choose_goods.vue'
export default {
    data() {
        return {
            titleToolConfig: {
                title: '供货商',
                tools: [{
                    name: '+添加供货商',
                    callback: this.addSupplier
                }]
            },
            activeName: 'first',
            firm_data: {}
        }
    },

    watch: {
        activeName: {
            handler(val) {
                this.$nextTick(() => {
                    if (val === 'first') {
                        this.$refs.supplierList.queryData()
                    } else {
                        this.$refs.operateList.queryOperateData()
                    }
                })
            },
            immediate: true
        }
    },

    methods: {
        addSupplier() {
            this.$refs.add_Supplier.open({
                if_add_supplier: true,
                data: {},
                callback: () => this.$refs.supplierList.queryData()
            })
        },

        chooseGoods(obj) {
            this.firm_data = obj
            this.$refs.chooseGoods.open({
                choosedList: obj.goods_ids
            })
        },

        editSupplier(info) {
            this.$refs.add_Supplier.open({
                if_add_supplier: false,
                data: this.cloneObject(info),
                callback: () => this.$refs.supplierList.queryData()
            })
        },

        addEditSupplier() {
            this.$refs.supplierList.queryData()
        },

        choosed(arr) {
            var goodsIdList = arr.map(element => {
                return element.id
            })

            this.$fetch.put({
                url: `/firm/${this.firm_data.id}`,
                params: {
                    firm_id: this.firm_data.id,
                    action: 'update_goods',
                    goods_id_list: goodsIdList
                }
            }).then(data => {
                this.openMessage(1, '更新商品成功')
                this.$refs.supplierList.queryData()
            }).catch(e => {
                this.openMessage(0, e || '更新商品失败')
            })
        },

        openGoodsList(obj) {
            this.$fetch.get({
                url: `/${obj.id}/goods/list`,
                params: {}
            }).then(data => {
                this.$refs.goodsList.open({
                    data: data.goods_list,
                    supplier_name: obj.name
                })
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    },

    components: {
        titleAndTools,
        addSupplierBox,
        goodsList,
        chooseGoods,
        supplierList,
        operateList
    }
}
</script>

<style lang="scss" scoped>
    .suppliers{
        position: relative;
    }
    /deep/ .el-tabs__content{
        overflow: inherit;
    }
</style>
