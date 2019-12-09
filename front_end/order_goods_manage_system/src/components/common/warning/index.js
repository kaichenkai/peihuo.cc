import Vue from 'vue'
import WarningComponent from './warning'

const Component = Vue.extend(WarningComponent)

class Warning {
    constructor(obj) {
        this.component = new Component({
            propsData: obj
        }).$mount()
        document.body.appendChild(this.component.$el)
        this.component.open()

        return new Promise((resolve, reject) => {
            this.component.$watch('state', (newVal) => {
                if (newVal) {
                    resolve()
                } else {
                    reject()
                }
            })
        }).finally(() => {
            this.component.$destroy()
            // document.body.removeChild(this.component.$el)
        })
    }
}

export default {
    install: VueConstructor => {
        VueConstructor.prototype.$myWarning = function(obj) {
            return new Warning(obj)
        }
    }
}
