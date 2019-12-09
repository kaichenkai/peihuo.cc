<template>
    <div>
        <el-table
            :data="staff_list"
            :height="tableHeight"
            v-scrollLoad="scrollLoad"
            v-loading="tableLoading"
            style="width: 100%">
            <el-table-column
                label="头像"
                width="160">
                <template slot-scope="scope">
                    <img :src="scope.row.avatar" alt="" width="25" height="25" style="border-radius: 50%;">
                </template>
            </el-table-column>
            <el-table-column
                prop="name"
                label="姓名"
                width="200">
            </el-table-column>
            <el-table-column
                prop="phone"
                label="手机号"
                width="150">
            </el-table-column>
            <el-table-column
                label="角色"
                width="">
                <template slot-scope="scope">
                    <span class="role" v-show='scope.row.admin_status'>管理员</span>
                    <span class="role" v-show='scope.row.purchaser_status'>采购员<span class="buy-record" @click="openCaigouRecord(scope.row)">采购记录</span></span>
                    <span class="no-role" v-show='!scope.row.admin_status&&!scope.row.purchaser_status'>暂无员工角色</span>
                </template>
            </el-table-column>
            <el-table-column
                label="操作"
                width="150">
                <template slot-scope="scope">
                    <el-button @click="openCaigouRecord(scope.row)" type="text">员工详情</el-button>
                    <el-button @click="$emit('editEmployee',scope.row.staff_id)" type="text">编辑</el-button>
                </template>
            </el-table-column>
            <p slot="append" style="text-align:center;padding: 10px" v-if="!isTableDataHasMore">没有更多了</p>
        </el-table>
        <search-box :styleData='styleData' @searchData='searchData'></search-box>
    </div>
</template>
<script>
import searchBox from '@/components/common/search.vue'
export default {
    data() {
        return {
            styleData: {
                top: -64,
                placeholder: '输入员工姓名/手机号'
            },
            staff_list: [
            ],
            search_str: ''
        }
    },

    created() {
        this.queryData()
    },

    methods: {
        dataChanged() {
            this.queryData()
        },
        openCaigouRecord(item) {
            this.$router.push({
                path: '/main/employees/caigourecord',
                query: {
                    item: JSON.stringify(item)
                }
            })
        },
        searchData(str) {
            this.search_str = str
            this.queryData(str)
        },
        getTableList(page) {
            return this.queryData(this.search_str, page)
        },
        queryData(str = '', page = 0) {
            return this.$fetch.get({
                url: `/stafflist`,
                params: {
                    search: str,
                    page: page
                }
            }).then(data => {
                if (page === 0) {
                    this.staff_list = data.staff_list
                    this.initScrollTable(data.has_more)
                } else {
                    this.staff_list = this.staff_list.concat(data.staff_list)
                }
                return data
            }).catch(e => {
                this.openMessage(0, e || '获取员工列表数据失败')
            })
        }
    },

    components: {
        searchBox
    }
}
</script>

<style lang="scss" scoped>
    span.role{
        display: inline-block;
        margin-right: 10px;
        padding:0 5px;
        border: 1px solid #666666;
        border-radius: 2px;
        span.buy-record{
            margin-left: 10px;
            color: rgba(107,164,239,0.95);
            cursor: pointer;
        }
    }
    span.no-role{
        color:#999;
    }
    /deep/ .el-button + .el-button {
        margin-left: 10px;
    }
</style>
