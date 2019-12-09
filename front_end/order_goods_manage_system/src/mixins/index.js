export default {
    install: function(Vue) {
        Vue.mixin({
            data() {
                return {
                    tableHeight: window.innerHeight - 200,
                    tableLoading: false,
                    page: 0,
                    isTableDataHasMore: true
                }
            },
            methods: {
                initScrollTable(isTableDataHasMore = true) {
                    this.page = 0
                    this.isTableDataHasMore = isTableDataHasMore
                },

                // 用于监听表格滚动，以及加载数据
                scrollLoad() {
                    if (this.tableLoading) {
                        return
                    }

                    this.tableLoading = true
                    // 执行获取数据函数
                    if (this.isTableDataHasMore && this.getTableList) {
                        this.getTableList(++this.page).then(data => {
                            this.isTableDataHasMore = data.has_more
                            return data
                        }).finally(() => {
                            this.tableLoading = false
                        })
                    } else {
                        this.tableLoading = false
                    }
                },

                openMessage(code, message) {
                    let type
                    switch (code) {
                        case 0: type = 'error'; break
                        case 1: type = 'success'; break
                        case 2: type = 'info'; break
                        default: break
                    }
                    this.$message({
                        type,
                        message,
                        showClose: true
                    })
                },

                openNotify(code, message) {
                    let type, typeText
                    switch (code) {
                        case 0: type = 'error'; typeText = '失败'; break
                        case 1: type = 'success'; typeText = '成功'; break
                        case 2: type = 'info'; typeText = '提示'; break
                        default: break
                    }
                    this.$notify({
                        title: typeText,
                        message: message,
                        type: type
                    })
                },

                clearObject(obj) { // 清空(不是删除)一个对象的所有属性
                    for (var key in obj) {
                        obj[key] = ''
                    }
                },

                cloneObject(obj) { // 深克隆一个对象
                    return JSON.parse(JSON.stringify(obj))
                }
            }
        })
    }
}
