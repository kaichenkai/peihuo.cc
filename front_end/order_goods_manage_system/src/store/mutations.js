import TYPE from './mutations_type'

function init() {
    if (!JSON.parse(localStorage.getItem('tableHeader'))) {
        localStorage.setItem('tableHeader', JSON.stringify({
            orderGroupStoresTable: [1, 2, 3, 4],
            orderGroupStoreDetailTable: [1, 2]
        }))
    }
}

init()

export default {
    [TYPE.SET_DEMAND_ORDER_UPDATE_STATUS](store, obj) {
        store.demandOrderUpDateStatus = obj
    },

    [TYPE.SET_STATION_INFO](store, obj) {
        store.stationInfo = obj
    },

    [TYPE.SET_USER_INFO](store, obj) {
        store.userInfo = obj
    },

    [TYPE.SET_USER_PRIVILEGES_INFO](store, obj) {
        // console.log(obj)
        store.userPrivilege.isSuperAdmin = !!obj.super_admin_status
        if (obj.admin_status) {
            store.userPrivilege.admin = obj.admin_permissions
        }

        if (obj.purchaser_status) {
            store.userPrivilege.purchaser = obj.purchaser_permissions
        }
    },

    [TYPE.SET_CURRENT_SHOP](store, shop) {
        store.currentShop = shop
    },

    [TYPE.SET_SHOP_LIST](store, shopList) {
        store.shopList = shopList
    },

    [TYPE.SET_STATION_CONFIG](store, data = {}) {
        store.stationConfig = data
    },

    [TYPE.SET_TABLE_HEADER](store, { table, columnsSetting }) {
        // console.log(table, columnsSetting)
        const tableHeader = JSON.parse(localStorage.getItem('tableHeader'))
        tableHeader[table] = tableHeader[table] || []
        tableHeader[table] = columnsSetting
        store.tableHeader = tableHeader
        localStorage.setItem('tableHeader', JSON.stringify(tableHeader))
    }
}
