<template>
    <div id="app">
        <router-view></router-view>
        <!-- <el-container style="height: 100%">
            <el-header height="60px">
                <page-header></page-header>
            </el-header>
            <el-container class="container">
                <el-aside width="auto">
                    <nav-aside></nav-aside>
                </el-aside>
                <el-main class="main">
                    <router-view/>
                </el-main>
            </el-container>
        </el-container> -->
    </div>
</template>
<script>
// import PageHeader from '@/components/header/header'
// import NavAside from '@/components/nav_aside/nav'
export default {
    // components: {
    //     PageHeader,
    //     NavAside
    // }
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
.container {
    padding-top: 10px;
}
.main {
    padding: 10px !important;
    background: #fff;
}
</style>
