const strategies = {
    isEmpty: function(value, errorMsg) {
        if (value === '' || value === null || value === undefined || value === 0) {
            return errorMsg
        }
    },

    isNumber: function(value, errorMsg) { // 判断是数字
        let testRuls = /\d+/
        if (!testRuls.test(value)) {
            return errorMsg
        }
    },

    isPhone: function(value, errorMsg) {
        let test = /^(1){1}\d{10}$/
        if (!test.test(value)) {
            return errorMsg
        }
    },

    price: function(value, errorMsg) {
        let test = /^\d+[.]?\d{0,2}$/
        if (!test.test(value)) {
            return errorMsg
        }
    },

    haveBlank: function(value, errorMsg) { // 判断是否有空格
        let testBlank = /\s+/
        if (testBlank.test(value)) {
            return errorMsg
        }
    },

    password: function(value, errorMsg) {
        let testPassword = /^[A-Za-z0-9]{6,}$/
        if (!testPassword.test(value)) {
            return errorMsg
        }
    },

    isLengthLessThan4: function(value, errorMsg) {
        let testPassword = /^[A-Za-z0-9\u4e00-\u9fa5]{1,4}$/
        if (!testPassword.test(value)) {
            return errorMsg
        }
    }
}

class Validator {
    constructor() {
        this.validators = []
    }

    add(type, value, errorMsg) {
        this.validators.push(function() {
            return strategies[type](value, errorMsg)
        })
    }

    start() {
        return new Promise((resolve, reject) => {
            this.validators.forEach(fn => {
                let result = fn()

                if (result) {
                    reject(result)
                }
            })
            resolve()
        })
    }

    static single(type, value, message = '验证失败') {
        if (strategies[type](value, message)) {
            return false
        } else {
            return true
        }
    }
}

export default {
    install(Vue, option) {
        Vue.prototype.$Validator = Validator
    }
}
