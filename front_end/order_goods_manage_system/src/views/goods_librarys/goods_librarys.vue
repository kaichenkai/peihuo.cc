<template>
    <div class="goods-library-container">
        <title-and-tools :config="titleToolConfig"></title-and-tools>
        <search-box :styleData='styleData' @searchData='searchData'></search-box>
        <el-table
            :data="tableData"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
            prop="serial_number"
            label="商品序列号"
            width="100">
            </el-table-column>
            <el-table-column
            prop="name"
            label="商品名称"
            sortable
            width="">
            </el-table-column>
            <el-table-column
            prop="code"
            label="商品编码"
            width="150">
            </el-table-column>
            <el-table-column
            prop="firm_amount"
            width="150"
            label="供货商">
            <template slot-scope="scope">
                <el-button type="text" style="color: #009688" @click="viewFirm(scope.row)">{{scope.row.firm_amount || 0}}</el-button>
                <el-button type="text" @click="addFirm(scope.row)">+添加</el-button>
            </template>
            </el-table-column>
            <el-table-column
            min-width="150">
            <template slot="header" slot-scope="scope">
                推荐供货商
                <el-tooltip class="item" effect="dark" placement="bottom">
                    <div slot="content">设置推荐供<br/>货商后，订<br/>货选择供货<br/>商时，系统<br/>将置顶提<br/>醒。</div>
                    <i class="el-icon-question"></i>
                </el-tooltip>
            </template>
            <template slot-scope="scope">
                {{recommendFirm(scope.row.recommend_firm)}}
                <el-button type="text" @click="chooseRecommendFirms(scope.row)">选择</el-button>
            </template>
            </el-table-column>
            <el-table-column
            prop="address"
            width="140"
            label="操作">
            <template slot-scope="scope">
                <el-button type="text" @click="deleteGoods(scope.row,$event)" style="color: #FF6666;">删除</el-button>
                <el-button type="text" @click="updateGoods(scope.row)">修改</el-button>
            </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <goods-form ref="goodsForm"></goods-form>
        <firm-list ref="firmList"></firm-list>
        <choose-suppliers ref="chooseSuppliers"></choose-suppliers>
        <choose-recommend-supplier ref="chooseRecommendSupplier" @operateSuccess='operateSuccess'></choose-recommend-supplier>
    </div>
</template>

<script>
import titleAndTools from '@/components/modules_top_tools/title_&_tools.vue'
import GoodsForm from './modules/goods_form'
import FirmList from './modules/view_firm_list'
import ChooseSuppliers from '@/components/choose_suppliers/choose_suppliers'
import chooseRecommendSupplier from './modules/choose_recommend_supplier.vue'
import searchBox from '@/components/common/search.vue'
export default {
    data() {
        return {
            isShowDialog: true,
            styleData: {
                top: -3,
                placeholder: '输入商品名'
            },
            searchStr: '',
            tableData: [],
            titleToolConfig: {
                title: '商品库',
                tools: [{
                    name: '+添加商品',
                    callback: this.addGoods
                }]
            }
        }
    },

    created() {
        this.getGoodsList()
    },

    methods: {
        recommendFirm(arr) {
            let str = ''
            for (let item of arr) {
                str = str + item.name + '   '
            }
            return str
        },

        operateSuccess() {
            this.getGoodsList()
        },

        searchData(str) {
            this.searchStr = str
            this.getGoodsList()
        },

        getTableList(page) {
            return this.getGoodsList(page)
        },

        getGoodsList(page = 0) {
            this.tableLoading = true
            return this.$fetch.get({
                url: '/station/goods/list',
                params: {
                    page: page,
                    search: this.searchStr
                }
            }).then(data => {
                // console.log(data)
                if (page === 0) {
                    this.tableData = data.goods_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.goods_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取商品列表失败')
                console.error('获取商品列表失败')
            }).finally(() => {
                this.tableLoading = false
            })
        },

        chooseRecommendFirms(item) {
            this.$refs.chooseRecommendSupplier.open(item)
        },

        addGoods() {
            this.$refs.goodsForm.open({
                mode: 'create',
                callback: () => this.getGoodsList()
            })
        },

        updateGoods(goods) {
            this.$refs.goodsForm.open({
                mode: 'update',
                data: goods,
                callback: () => this.getGoodsList()
            })
        },

        deleteGoods(goods, e) {
            this.$myWarning({
                message: '确定要删除吗？'
            }).then(() => {
                this.$fetch.delete({
                    url: '/station/goods/' + goods.id
                }).then(data => {
                    this.openMessage(1, '删除成功')
                    this.getGoodsList()
                }).catch(e => {
                    this.openMessage(0, e || '删除失败')
                })
            }).catch(e => {})
        },

        viewFirm(data) {
            this.$refs.firmList.open(data)
        },

        addFirm(goods) {
            this.$fetch.get({
                url: `/${goods.id}/firm/list`
            }).then(data => {
                this.$refs.chooseSuppliers.open({
                    choosedList: data.firm_list.map(value => value.id),
                    callback: (data) => {
                        console.log(data.suppliers)
                        this.updateSuppliers(goods, data.suppliers)
                    }
                })
            }).catch(e => {
                this.openMessage(0, '获取供应商数据失败,' + e)
            })
        },

        updateSuppliers(goods, suppliers) {
            this.$fetch.put({
                url: '/station/goods/' + goods.id,
                params: {
                    action: 'update_firm',
                    firm_id_list: suppliers.map(value => value.id)
                }
            }).then(data => {
                this.openMessage(1, '更新供应商成功')
                this.getGoodsList()
            }).catch(e => {
                this.openMessage(0, '更新供应商失败,' + e)
            })
        }
    },

    components: {
        titleAndTools,
        GoodsForm,
        FirmList,
        ChooseSuppliers,
        chooseRecommendSupplier,
        searchBox
    }
}
</script>

<style lang="scss" scoped>
.goods-library-container {
    position: relative;
}
</style>
