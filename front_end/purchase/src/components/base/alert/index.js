import Vue from 'vue'
import Alert from './alert.vue'

const MessageBox = Vue.extend(Alert)

Alert.install = function(options, type) {
    if (options === undefined || options === null) {
        options = {
            content: ''
        }
    } else if (typeof options === 'string' || typeof options === 'number') {
        options = {
            content: options
        }
        if (type !== undefined && options != null) {
            options.type = type
        }
    }

    let instance = new MessageBox({
        data: options
    }).$mount()

    document.body.appendChild(instance.$el)

    Vue.nextTick(() => {
        instance.visible = true
    })
}

export default Alert
