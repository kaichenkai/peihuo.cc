<template>
    <div class="employees">
        <title-and-tools :config="titleToolConfig"></title-and-tools>
        <el-tabs v-model="activeName" @tab-click="handleClick">
            <el-tab-pane label="员工列表" name="first">
                <employee-list @editEmployee='editEmployee' ref="employeeList"></employee-list>
            </el-tab-pane>
            <el-tab-pane label="操作记录" name="second">
                <operate-list ref="operateList"></operate-list>
            </el-tab-pane>
        </el-tabs>
        <add-employees-box ref="addEmployeesBox" @nextStep='nextStep'></add-employees-box>
        <add-employees-box2 ref="addEmployeesBox2" @dataChanged="$refs.employeeList.queryData()" @addEditEmployee='$refs.employeeList.queryData()'></add-employees-box2>
    </div>
</template>

<script>
import titleAndTools from '@/components/modules_top_tools/title_&_tools.vue'
import employeeList from './modules/employee_list.vue'
import operateList from './modules/operate_list.vue'
import addEmployeesBox from './modules/add_employees_box.vue'
import addEmployeesBox2 from './modules/add_employees_box2.vue'
export default {
    data() {
        return {
            titleToolConfig: {
                title: '员工',
                tools: [{
                    name: '+添加员工',
                    callback: this.addEmployeesBox
                }]
            },
            activeName: 'first',
            account_data: {}
        }
    },

    watch: {
        activeName: {
            handler(val) {
                if (val === 'first') {
                    this.$refs.employeeList.queryData()
                } else {
                    this.$refs.operateList.queryOperateData()
                }
            }
        }
    },

    methods: {
        handleClick() {

        },
        addEmployeesBox() {
            this.$refs.addEmployeesBox.open()
        },
        editEmployee(staffid) {
            this.$fetch.get({
                url: `/staff/${staffid}`,
                params: {
                    action: 'staff_info'
                }
            }).then(data => {
                this.$refs.addEmployeesBox2.open({
                    mode: 'update',
                    data: data.staff_data,
                    callback: () => this.$refs.employeeList.queryData()
                })
            })
        },

        nextStep(accountData) {
            this.$refs.addEmployeesBox2.open({
                mode: 'create',
                data: accountData,
                callback: () => this.$refs.employeeList.queryData()
            })
        }
    },

    components: {
        titleAndTools,
        addEmployeesBox,
        addEmployeesBox2,
        employeeList,
        operateList
    }
}
</script>

<style lang="scss" scoped>
    .employees{
        position: relative;
    }
    /deep/ .el-tabs__content{
        overflow: inherit;
    }
</style>
