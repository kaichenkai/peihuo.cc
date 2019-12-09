<template>
    <div>

    </div>
</template>
<script>
import { mapGetters } from 'vuex'
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
        ...mapGetters(['canIUse'])
    },

    created() {
        this.redirectUrl = this.$route.query.redirect
        this.$store.dispatch('getUserPrivileges').then(data => {
            if (data.admin_status) {
                let order = [2, 1, 3, 4, 5, 6, 7, 8]
                data.admin_permissions = data.admin_permissions
                    .reduce((prev, now, index, arr) => {
                        let head = order.shift()
                        if (arr.includes(head)) {
                            prev.push(head)
                        }
                        return prev
                    }, [])
                for (let i = 0; i < data.admin_permissions.length; i++) {
                    if (this.canIUse('admin', data.admin_permissions[i])) {
                        let linkHref = this.routerList.find(value => value.privilegeId === +data.admin_permissions[i]).linkHref
                        // console.log(linkHref)
                        if (this.redirectUrl) {
                            if (this.redirectUrl.indexOf(linkHref) !== -1) {
                                this.$router.replace({
                                    path: this.redirectUrl
                                })
                                break
                            }
                        } else {
                            this.$router.replace({
                                path: linkHref
                            })
                            break
                        }
                    }
                }
            } else {
                this.$router.push('/login')
            }
        })
    }
}
</script>
<style lang="scss" scoped>
</style>
