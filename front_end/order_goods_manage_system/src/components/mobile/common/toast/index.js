import Vue from 'vue'
import toast from './toast'

const Component = Vue.extend(toast)

class Toast {
    constructor() {
        this.component = new Component().$mount()
        document.body.appendChild(this.component.$el)
        this.messageQueen = []
        this.interval = null
    }

    show(text) {
        this.messageQueen.push(text)
        this.loop()
    }

    loop() {
        this.component.$data.showToast = true
        this.component.setText(this.messageQueen[0])
        if (this.interval) {
            clearInterval(this.interval)
        }
        this.interval = setInterval(() => {
            let message = this.messageQueen.shift()
            if (message) {
                this.component.setText(message)
            } else {
                clearInterval(this.interval)
                this.component.$data.showToast = false
            }
        }, 1500)
    }
}

export default {
    install: function(VueConstructor) {
        VueConstructor.prototype.$myToast = new Toast()
    }
}
