
import MyRadio from './radio/index.js'
import MyWarning from './warning/index'
import TableDataFilter from './table_data_filter'
import Sort from './sort'
// import MySelect from './select'

let components = { MyRadio, MyWarning, TableDataFilter, Sort }

export default {
    install: function(Vue) {
        for (let i in components) {
            components[i].install(Vue)
        }
    }
}
