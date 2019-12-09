<template>
    <div class="search" :style="[{top:styleData.top+'px'},{right:styleData.right+'px'}]">
        <input type="text" :placeholder="styleData.placeholder" v-model="value" @keyup.enter="searchData">
        <span @click="searchData">
            搜索
        </span>
        <i @click="clear" v-show="value" class="el-icon el-icon-circle-close"></i>
    </div>
</template>
<script>
export default {
    data() {
        return {
            value: ''
        }
    },
    props: {
        styleData: {
            default() {
                return {
                    top: 30,
                    right: 0,
                    placeholder: '请输入'
                }
            },
            type: Object
        }
    },
    methods: {
        searchData() {
            this.$emit('searchData', this.value)
        },

        clear() {
            this.value = ''
            this.searchData()
        }
    }
}
</script>

<style lang="scss" scoped>
    .search{
        position: absolute;
        z-index: 2;
        top:30px;
        right: 0px;
        width: 250px;
        border: 1px solid #DDDDDD;
        border-radius: 4px;

        input{
            margin-right: 6px;
            width: 170px;
            height: 40px;
            background: #FFFFFF;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            color: #999999;
            text-indent: 10px;
            outline: none;

            &:focus {
                border: none !important;
            }
        }
        span{
            position: absolute;
            top:11px;
            right:11px;
            padding-left: 11px;
            height: 20px;
            line-height: 20px;
            font-size: 14px;
            color: #009688;
            border-left: 1px solid #ddd;
            cursor: pointer;
        }

        .el-icon-circle-close {
            color: #999999;
            cursor: pointer;
        }
    }
</style>
