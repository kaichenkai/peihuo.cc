class OrderStatusManager {
    constructor() {
        let storage = localStorage.getItem('OrdersStatus')

        if (!storage) {
            localStorage.setItem('OrdersStatus', JSON.stringify({}))
        }
        this.storage = null
    }

    setOrderStatus(id, status) {
        this.storage = JSON.parse(localStorage.getItem('OrdersStatus'))
        this.storage[id] = status
        localStorage.setItem('OrdersStatus', JSON.stringify(this.storage))
    }

    getOrderStatus(id) {
        let storage = this.storage || JSON.parse(localStorage.getItem('OrdersStatus'))
        return storage[id]
    }
}

export default new OrderStatusManager()
