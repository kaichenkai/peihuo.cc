export default {
    install: function(Vue) {
        Vue.directive('selectTextOnFocus', {
            bind: function(el, binding) {
                function bindDom(el) {
                    if (el.tagName !== 'INPUT') {
                        [...el.children].forEach(dom => {
                            bindDom(dom)
                        })
                    } else {
                        el.onfocus = function() {
                            el.select()
                        }
                        return true
                    }
                }

                bindDom(el)
            }
        })

        Vue.directive('removeMouseWheelEvent', {
            bind: function(el, binding) {
                el.onmousewheel = function(e) {
                    e.preventDefault()
                }
            }
        })

        Vue.directive('scrollLoad', {
            bind: function(el, binding) {
                const scrollWrap = el.querySelector('.el-table__body-wrapper')
                scrollWrap.onscroll = function() {
                    let sign = 100
                    const scrollDistance = this.scrollHeight - this.scrollTop - this.clientHeight
                    if (scrollDistance <= sign) {
                        binding.value()
                    }
                }
            },
            unbind: function(el) {
                const scrollWrap = el.querySelector('.el-table__body-wrapper')
                scrollWrap.onscroll = ''
            }
        })
    }
}
