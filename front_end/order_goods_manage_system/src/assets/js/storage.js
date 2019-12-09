class MyStorage {
    /**
     * @param storage 存储的类型
     * @param storageName 存储的 key name
     */
    constructor(storage, storageName) {
        if (storage !== localStorage && storage !== sessionStorage) {
            return console.error('storage.js: 传入了错误的storage类型') // eslint-disable-line no-console
        }

        if (!storageName) {
            return console.error('storage.js: 需要传入 storageName')
        }

        this.storage = storage
        this.storageName = storageName
    }

    init() {
        let storageData = this.storage.getItem(this.storageName)
        if (!storageData) {
            this.storage.setItem(this.storageName, JSON.stringify({}))
        } else {
            try {
                JSON.parse(storageData)
            } catch (e) {
                this.storage.setItem(this.storageName, JSON.stringify({}))
            }
        }
    }

    setStorage(data) {
        this.init()
        try { // 用于判断存储空间是否爆满
            this.storage.setItem(this.storageName, JSON.stringify(data))
        } catch (e) {
            this.storage.clear()
        }
    }

    getStorage() {
        this.init()
        return JSON.parse(this.storage.getItem(this.storageName))
    }
}

export default MyStorage
