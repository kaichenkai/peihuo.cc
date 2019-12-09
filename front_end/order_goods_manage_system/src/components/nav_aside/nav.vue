<template>
    <div class="nav-container">
        <ul>
            <router-link tag="li"
            v-if="canIUse('admin', router.privilegeId)"
            :to="{path: router.linkHref}"
            v-for="(router, index) in routerList"
            :key="index">
                {{router.name}}
                <span class="pop" v-if="router.name=='采购订货' && demandOrderUpDateStatus.total > 0">{{demandOrderUpDateStatus.total}}</span>
            </router-link>
        </ul>
    </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
export default {
    data() {
        return {
            routerList: [{
                linkHref: '/main/purchaseCenter',
                name: '采购订货',
                privilegeId: 2
            }, {
                linkHref: '/main/reconcileCenter',
                name: '对账中心',
                privilegeId: 1
            }, {
                linkHref: '/main/goodsLibrarys',
                name: '商品库',
                privilegeId: 3
            }, {
                linkHref: '/main/warehouse',
                name: '仓库',
                privilegeId: 4
            }, {
                linkHref: '/main/suppliers',
                name: '供货商',
                privilegeId: 5
            }, {
                linkHref: '/main/shops',
                name: '店铺',
                privilegeId: 6
            }, {
                linkHref: '/main/employees',
                name: '员工',
                privilegeId: 7
            }, {
                linkHref: '/main/configuration',
                name: '设置',
                privilegeId: 8
            }]
        }
    },

    computed: {
        ...mapState(['demandOrderUpDateStatus']),
        ...mapGetters(['canIUse'])
    }
}
</script>

<style lang="scss" scoped>
.nav-container {
    padding: 0 10px 10px 10px;
    width: 100%;
    // height: 410px;

    ul {
        padding-bottom: 10px;
        width: 130px;
        background: #fff;
        overflow: hidden;
        user-select: none;

        li {
            position: relative;
            margin: 0 auto;
            margin-top: 10px;
            height: 40px;
            width: 110px;
            text-align: center;
            line-height: 40px;
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
            cursor: pointer;

            &:hover {
                background: #009688a3;
                border-radius: 100px;
                color: #fff;
            }

            .pop {
                position: absolute;
                top: -5px;
                right: 0;
                padding: 3px;
                border-radius: 10px;
                background: #ff6666;
                color: #fff;
                min-width: 20px;
                height: 20px;
                line-height: 14px;
                font-size: 12px;
            }
        }

        .active {
            background: #009688 !important;
            border-radius: 100px;
            color: #fff;
        }
    }
}
</style>
