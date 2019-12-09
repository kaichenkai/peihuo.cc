<template>
    <div style="height: 100%; position: relative">
        <h2>采购订货</h2>
        <el-radio-group v-model="modul" style="margin: 10px 0;">
            <el-radio-button label="wishOrder">采购意向单</el-radio-button>
            <el-radio-button label="orderGroup">订货汇总单</el-radio-button>
        </el-radio-group>
        <div class="router-container">
            <router-view></router-view>
        </div>
    </div>
</template>

<script>
//
export default {
    data() {
        return {
            modul: 'wishOrder'
        }
    },

    watch: {
        modul: function(newVal) {
            switch (newVal) {
                case 'wishOrder':
                    this.$router.replace({
                        path: '/main/purchaseCenter/edit',
                        query: {
                            module: newVal
                        }
                    }); break
                case 'orderGroup':
                    this.$router.replace({
                        path: '/main/purchaseCenter/orderGoodsVouchersGroup',
                        query: {
                            module: newVal
                        }
                    }); break
            }
        },
        $route: function(newVal) {
            if (!newVal.query.module) {
                this.modul = 'wishOrder'
            }
        }
    },

    created() {
        this.modul = this.$route.query.module || 'wishOrder'
    }
}
</script>

<style lang="scss" scoped>
.router-container {
    position: absolute;
    top: 70px;
    bottom: 0px;
    left: 0;
    right: 0;
}
</style>
