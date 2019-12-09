export const orderStatus = [{
    name: '待采购/待出库',
    id: 0
}, {
    name: '待确认收货',
    id: 1
}, {
    name: '待分车',
    id: 2
}, {
    name: '已分车',
    id: 3
}, {
    name: '已送货到店',
    id: 4
}]

/**
 *
 * @param {Number} id 状态id
 * @param {Number} type 采购（1）或者出库（2）
 */
export function getOrderStatusById(id, type) {
    let status = orderStatus.filter(value => value.id === +id)
    if (status.length > 0) {
        if (+id === 0) {
            return status[0].name.split('/')[type - 1]
        } else {
            return status[0].name
        }
    }
}
