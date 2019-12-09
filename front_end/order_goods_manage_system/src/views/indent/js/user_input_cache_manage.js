import MyStorage from '@/assets/js/storage'

class UserInputCache extends MyStorage {
    constructor() {
        super(localStorage, 'indent_user_input_data_cache')
        // Example = {
        //     demandOrderId: 1, // 订货单id
        //     cacheData: {}, // 用户之前输入的数据，为了存储容量考虑，一次只存储一个意向单数据
        //     updateTime: '31412312313123' // 毫秒，用于判断数据是否新鲜
        // }
    }

    setData(demandOrderId, data) {
        let storageData = this.getStorage()
        storageData.demandOrderId = demandOrderId
        storageData.cacheData = data
        storageData.updateTime = Date.now()
        this.setStorage(storageData)
    }

    getData(demandOrderId, time) {
        let storageData = this.getStorage()
        if (demandOrderId !== storageData.demandOrderId) {
            return false
        } else if (new Date(time).getTime() > +storageData.updateTime) {
            return false
        } else {
            return storageData.cacheData
        }
    }
}

export default new UserInputCache()
