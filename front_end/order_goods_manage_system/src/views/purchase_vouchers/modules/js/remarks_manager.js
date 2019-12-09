class RemarksManage {
    constructor() {
        let storage = JSON.parse(localStorage.getItem('remarks'))
        if (!storage) {
            localStorage.setItem('remarks', JSON.stringify([]))
        }
    }

    setRemark(text) {
        let storage = JSON.parse(localStorage.getItem('remarks'))
        if (storage.find(obj => obj.value === text)) {
            storage.map(obj => {
                if (obj.value === text) {
                    obj.count++
                }
                return obj
            })
        } else {
            text && storage.push({
                value: text,
                count: 1
            })
        }

        localStorage.setItem('remarks', JSON.stringify(storage))
    }

    getRemarksLimit(limit = 3) {
        const remarks = JSON.parse(localStorage.getItem('remarks'))
        return remarks.sort((a, b) => {
            return b.count - a.count
        }).slice(0, limit)
    }
}

export default new RemarksManage()
