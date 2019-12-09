<template>
    <!-- <div> -->
        <el-container style="height: 100%">
            <el-header height="60px">
                <page-header></page-header>
            </el-header>
            <el-container class="layout-container">
                <el-aside width="auto">
                    <nav-aside></nav-aside>
                </el-aside>
                <el-main class="layout-main">
                    <router-view/>
                </el-main>
            </el-container>
        </el-container>
    <!-- </div> -->
</template>
<script>
import PageHeader from '@/components/header/header'
import NavAside from '@/components/nav_aside/nav'
import statusSignal from '@/assets/js/status_signal' // 不要删除
export default {
    data() {
        return {
        }
    },

    created() {
        statusSignal.startCheck()
        this.$store.dispatch('init')
    },

    beforeDestroy() {
        statusSignal.clearCheck()
    },

    components: {
        PageHeader,
        NavAside
    }
}
</script>
<style lang="scss" scoped>
.el-header {
    padding: 0 !important;
}
.el-main {
    padding: 0;
    margin-right: 10px;
}
#app {
    height: 100%;
}
.layout-container {
    padding-top: 10px;
}
.layout-main {
    padding: 10px !important;
    background: #fff;
}
</style>
