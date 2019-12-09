import Vue from 'vue'
import LoadingComponent from './loading'

const Component = Vue.extend(LoadingComponent)

class Loading {
    constructor() {
        this.requestCount = 0
        this.component = new Component().$mount()
        document.body.appendChild(this.component.$el)
    }

    show(text, obj = {}) {
        if (this.requestCount > 0) {
            this.component.setText(text)
        } else {
            this.component.show(text)
        }
        this.requestCount++
    }

    close() {
        this.requestCount--
        if (this.requestCount === 0) {
            this.component.close()
        }
    }
}

export default {
    install: function(VueConstrucor) {
        VueConstrucor.myLoading = new Loading()
        VueConstrucor.prototype.myLoading = new Loading()
    }
}
