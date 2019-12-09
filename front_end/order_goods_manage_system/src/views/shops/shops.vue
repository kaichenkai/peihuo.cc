<template>
    <div>
        <title-and-tools :config="titleToolsConfig"></title-and-tools>
        <el-table
            :data="tableData"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
            prop="serial_number"
            label="店铺序列号"
            width="100">
            </el-table-column>
            <el-table-column
            prop="name"
            label="店铺名称">
            </el-table-column>
            <el-table-column
            prop="abbreviation"
            label="店铺简称"
            width="150">
            </el-table-column>
            <el-table-column
            prop="address"
            width="140"
            label="店铺地址">
            </el-table-column>
            <el-table-column
            width="300"
            label="订货人信息">
            <template slot-scope="scope">
                <!-- {{JSON.stringify(scope.row)}} -->
                <ul>
                    <li class="contact" v-for="(item, index) in scope.row.contacts" :key="index">
                        <span class="img"><img v-if="item.avatar" :src="item.avatar"/></span>
                        <span>{{item.name}}</span>
                        /
                        <span>{{item.phone}}</span>
                        <!-- <span><el-button type="text">添加</el-button></span> -->
                    </li>
                </ul>
            </template>
            </el-table-column>
            <el-table-column
            width="140"
            label="操作">
            <template slot-scope="scope">
                <!-- <el-button type="text" style="color: #FF6666;">删除</el-button> -->
                <el-button type="text" @click="editShop(scope.row)">编辑</el-button>
            </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <shop-form ref="shopForm" @dataChanged="getShopList"></shop-form>
    </div>
</template>

<script>
import titleAndTools from '@/components/modules_top_tools/title_&_tools.vue'
import ShopForm from './modules/shop_form'
export default {
    data() {
        return {
            radio: 1,
            titleToolsConfig: {
                title: '店铺管理',
                tools: [{
                    name: '+添加店铺',
                    callback: this.addShop
                }]
            },
            tableData: []
        }
    },

    created() {
        this.getShopList()
    },

    methods: {
        editShop(item) {
            item.contacts[0] || (item.contacts[0] = {})
            item.contacts[1] || (item.contacts[1] = {})
            this.$refs.shopForm.open({
                mode: 'update',
                form: this.cloneObject(item),
                callback: () => this.getShopList()
            })
        },
        getTableList(page) {
            return this.getShopList(page)
        },
        getShopList(page = 0) {
            return this.$fetch.get({
                url: '/shops',
                params: {
                    page: page
                }
            }).then(data => {
                if (page === 0) {
                    this.tableData = data.shop_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.tableData = this.tableData.concat(data.shop_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取店铺列表失败')
            })
        },
        addShop() {
            this.$refs.shopForm.open({
                mode: 'create',
                callback: () => {
                    this.getShopList()
                }
            })
        }
    },

    components: {
        titleAndTools,
        ShopForm
    }
}
</script>

<style lang="scss" scoped>
.contact {
    display: flex;
    align-items: center;
    margin: 5px 0;
    .img {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        overflow: hidden;
        background: #c9c9c9;

        img {
            width: 100%;
            height: 100%;
        }
    }

    > * {
        margin: 0 4px;
    }
}
</style>
