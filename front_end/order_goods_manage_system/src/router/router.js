import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import GoodsLibrarys from '@/views/goods_librarys/goods_librarys'
import Suppliers from '@/views/suppliers/suppliers'
// =============== 对账中心 =============== //
import ReconcileCenter from '@/views/reconcile_center/index'
import ReconcileCenterMain from '@/views/reconcile_center/reconcile_center'
import ReconcileCenterPurchaseDetail from '@/views/reconcile_center/modules/expenses_reconcile/goods_purchase_detail'
import ReconcileCenterScavengingKnot from '@/views/reconcile_center/modules/suppliers_settle_accounts/scavenging_knot'
import BillDetail from '@/views/reconcile_center/modules/branch_reconciliation/bill_detail'
import settlementDetail from '@/views/reconcile_center/modules/suppliers_settle_accounts/settlement_detail'
// ======================================= //
import PurchaseCenter from '@/views/purchase_vouchers'
// import PurchaseVouchers from '@/views/purchase_vouchers/modules/purchase_vouchers'
import MakePurchaseVouchers from '@/views/purchase_vouchers/modules/make_purchase_voucher/make_purchase_voucher'
import OrderGoodsVouchersGroup from '@/views/purchase_vouchers/modules/order_goods_vouchers_group/order_goods_vouchers_group'
import Warehouse from '@/views/warehouse/warehouse'
import Shops from '@/views/shops/shops'
import Employees from '@/views/employees/index'
import EmployeesList from '@/views/employees/employees'
import CaigouRecord from '@/views/employees/modules/caigou_record'
import Configuration from '@/views/configuration/configuration'
import Login from '@/views/login/login'
import Main from '@/views/main/main'
import CreateTransferStation from '@/views/create_transfer_station/create_transfer_station'
import Indent from '@/views/indent/indent'
import BranchStoreLogin from '@/views/branch_store_login/branch_store_login'
import MakeQuotedPriceVoucher from '@/views/purchase_vouchers/modules/quoted_price_voucher/make_quoted_price_voucher'
import viewQuotedPriceVoucher from '@/views/purchase_vouchers/modules/quoted_price_voucher/view_quoted_price_voucher'
import PrivilegeValidator from '@/views/privilege/privilege'

Vue.use(Router)

const router = new Router({
    linkActiveClass: 'active',
    routes: [{
        path: '/',
        redirect: '/login'
    }, {
        path: '/login',
        component: Login
    }, {
        path: '/createTransferStation',
        component: CreateTransferStation
    }, {
        path: '/indent', // 订货单
        component: Indent
    }, {
        path: '/viewQuotedPriceVoucher',
        component: viewQuotedPriceVoucher
    }, {
        path: '/branchStoreLogin',
        component: BranchStoreLogin
    }, {
        path: '/main',
        component: Main,
        children: [{
            path: '',
            redirect: 'privilegeValidator'
        },
        {
            path: 'privilegeValidator',
            component: PrivilegeValidator
        }, {
            path: 'goodsLibrarys',
            component: GoodsLibrarys,
            meta: {
                role: 'admin',
                privilegeId: 3
            }
        }, {
            path: 'suppliers',
            component: Suppliers,
            meta: {
                role: 'admin',
                privilegeId: 5
            }
        }, {
            path: 'reconcileCenter',
            component: ReconcileCenter,
            meta: {
                role: 'admin',
                privilegeId: 1
            },
            children: [{
                path: '',
                redirect: 'main'
            }, {
                path: 'main',
                component: ReconcileCenterMain
            }, {
                path: 'purchaseDetail',
                component: ReconcileCenterPurchaseDetail
            }, {
                path: 'fendianDetail',
                component: BillDetail
            }, {
                path: 'supplierJiekuanDetail',
                component: settlementDetail
            }, {
                path: 'scavengingKnot',
                component: ReconcileCenterScavengingKnot
            }]
        }, {
            path: 'purchaseCenter',
            component: PurchaseCenter,
            meta: {
                role: 'admin',
                privilegeId: 2
            },
            children: [{
                path: '',
                redirect: 'edit'
            },
            // {
            //     path: 'purchaseVouchers',
            //     component: PurchaseVouchers
            // },
            {
                path: 'edit',
                component: MakePurchaseVouchers
            }, {
                path: 'orderGoodsVouchersGroup',
                component: OrderGoodsVouchersGroup
            }, {
                path: 'makeQuotedPriceVoucher',
                component: MakeQuotedPriceVoucher
            }]
        }, {
            path: 'warehouse',
            component: Warehouse,
            meta: {
                role: 'admin',
                privilegeId: 4
            }
        }, {
            path: 'shops',
            component: Shops,
            meta: {
                role: 'admin',
                privilegeId: 6
            }
        }, {
            path: 'employees',
            component: Employees,
            meta: {
                role: 'admin',
                privilegeId: 7
            },
            children: [{
                path: '',
                redirect: 'list'
            }, {
                path: 'list',
                component: EmployeesList
            }, {
                path: 'caigourecord',
                component: CaigouRecord
            }]
        }, {
            path: 'configuration',
            component: Configuration,
            meta: {
                role: 'admin',
                privilegeId: 8
            }
        }]
    }]
})

function isCanUseThisModule(to, from, next) {
    return to.matched.every(record => {
        if (record.meta.role) {
            return store.getters.canIUse(record.meta.role, record.meta.privilegeId)
        } else {
            return true
        }
    })
}

router.beforeEach((to, from, next) => {
    if (isCanUseThisModule(to, from, next)) {
        next()
    } else {
        next({
            path: '/main/privilegeValidator',
            query: {
                redirect: to.fullPath
            },
            replace: true
        })
    }
})

export default router
