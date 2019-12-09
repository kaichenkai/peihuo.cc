let canUploadFilesUsers = []
if (process.env.NODE_ENV === 'development') {
    canUploadFilesUsers = [7]
} else if (process.env.NODE_ENV === 'production') {
    canUploadFilesUsers = [1, 14]
}

export default {
    demandOrderUpDateStatus: {}, // 小红点更新数据
    stationInfo: {}, // 中转站信息
    userInfo: {}, // 登陆的用户信息
    userPrivilege: {
        isSuperAdmin: false,
        admin: [],
        purchaser: []
    }, // 用户权限信息
    currentShop: {}, // 当前订货单页面登陆的门店
    shopList: [], // 订货单门店列表
    stationConfig: {}, // 中转站设置信息
    canUploadFilesUsers: canUploadFilesUsers,
    tableHeader: {}
}
