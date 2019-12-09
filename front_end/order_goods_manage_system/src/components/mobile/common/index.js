import MyMWarning from './warning/index.js'
import Toast from './toast/index'
// import MySelect from './select'

let components = { MyMWarning, Toast }

export default {
    install: function(Vue) {
        for (let i in components) {
            components[i].install(Vue)
        }
    }
}
