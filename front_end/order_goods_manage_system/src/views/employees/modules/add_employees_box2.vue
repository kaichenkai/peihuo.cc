<template>
    <el-dialog
        :title="title"
        :visible.sync="dialogVisible"
        width="925px"
        height='500px'>
        <p class="delete_Employee" v-show="mode==='update'" @click="deleteEmployee">删除员工</p>
        <div class="add_employees_second_step">
            <div class="left">
                <p class="title">
                    基本信息
                </p>
                <ul>
                    <li class="head_portrait"><span>头&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;像：</span><img :src="account_data.avatar||form.avatar" alt=""></li>
                    <li><span>昵&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;称：</span><span class="name">{{account_data.name||form.name||form.nickname}}</span></li>
                    <li><span>手&nbsp;&nbsp;机&nbsp;号：</span>{{account_data.phone||form.phone}}</li>
                    <li class="realname"><span>真实姓名：</span>
                        <el-input v-model="form.realname" placeholder="填写" size="small"></el-input>
                    </li>
                    <li class="position"><span>员工职位：</span>
                        <el-input v-model="form.position" placeholder="填写" size="small"></el-input>
                    </li>
                    <li><span>员工生日：</span>
                        <el-date-picker
                            v-model="form.birthday"
                            type="date"
                            placeholder=""
                            format='yyyy-MM-dd'
                            :clearable="false"
                            size="small">
                        </el-date-picker>
                    </li>
                    <li><span>入职日期：</span>
                        <el-date-picker
                            v-model="form.date_onboarding"
                            type="date"
                            placeholder=""
                            format='yyyy-MM-dd'
                            :clearable="false"
                            size="small">
                        </el-date-picker>
                    </li>
                    <li><span class="remark">备&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;注：</span>
                        <el-input v-model="form.remarks" placeholder="填写" size="small" type="textarea"></el-input>
                    </li>
                </ul>
            </div>
            <div class="right">
                <div class="role">
                    <ul>
                        <li :class="{active:role==1}" @click="role=1">管理员</li>
                        <li :class="{active:role==2}" @click="role=2">采购员</li>
                    </ul>
                </div>
                <div class="power">
                    <div class="manager">
                        <p>
                            <span>管理员</span>
                            <el-switch
                                v-model="form.admin_status"
                                :active-value="1"
                                active-color="#009688"
                                inactive-color="#ddd">
                            </el-switch>
                            <el-checkbox :indeterminate="isIndeterminateAdmin" v-model="checkAllAdminPrivilege" :disabled="form.admin_status == 0">全选</el-checkbox>
                        </p>
                        <el-checkbox-group
                            class="checkbox-group"
                            v-model="form.admin_permissions">
                            <el-checkbox v-for="privilege in administratorPrivileges" :label="privilege.id" :key="privilege.id" :disabled="form.admin_status == 0">{{privilege.name}}</el-checkbox>
                        </el-checkbox-group>
                    </div>
                    <div class="buyer">
                        <p>
                            <span>采购员</span>
                            <el-switch
                                :active-value="1"
                                v-model="form.purchaser_status"
                                active-color="#009688"
                                inactive-color="#ddd">
                            </el-switch>
                            <el-checkbox :indeterminate="isIndeterminatePurchaser" v-model="checkAllPurchaserPrivilege" :disabled="form.purchaser_status == 0">全选</el-checkbox>
                        </p>
                        <el-checkbox-group
                            class="checkbox-group"
                            v-model="form.purchaser_permissions">
                            <el-checkbox v-for="privilege in purchaserPrivileges" :label="privilege.id" :key="privilege.id" :disabled="form.purchaser_status == 0">{{privilege.name}}</el-checkbox>
                        </el-checkbox-group>
                    </div>
                </div>
            </div>
        </div>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">确认</button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>

<script>
// import checkAll from '@/components/common/check_all.vue'
import { dateFormat } from '@/utils'
export default {
    data() {
        return {
            dialogVisible: false,
            mode: 'create',
            role: 1,
            checkAllAdminPrivilege: '',
            checkAllPurchaserPrivilege: '',
            isIndeterminateAdmin: true,
            isIndeterminatePurchaser: true,
            administratorPrivileges: [{
                name: '对账中心',
                id: 1
            }, {
                name: '采购订货',
                id: 2
            }, {
                name: '商品库',
                id: 3
            }, {
                name: '仓库',
                id: 4
            }, {
                name: '供货商',
                id: 5
            }, {
                name: '店铺',
                id: 6
            }, {
                name: '员工',
                id: 7
            }, {
                name: '设置',
                id: 8
            }, {
                name: '查看汇总单里的货品采购价',
                id: 9
            }, {
                name: '查看仓库采购均价和采购成本',
                id: 10
            }],
            purchaserPrivileges: [{
                name: '接受分店订货请求',
                id: 1
            }, {
                name: '查看全局采购汇总',
                id: 2
            }, {
                name: '新建采购单',
                id: 3
            }, {
                name: '查看货品采购价',
                id: 4
            }],
            form: {
                realname: '',
                position: '',
                birthday: '',
                date_onboarding: '',
                remarks: '',
                admin_status: 1,
                purchaser_status: 1,
                admin_permissions: [],
                purchaser_permissions: []
            },
            account_data: {
                name: '',
                avatar: '',
                phone: ''
            }
        }
    },

    computed: {
        title() {
            if (this.mode === 'create') {
                return '添加员工'
            } else {
                return '编辑员工'
            }
        }
    },

    watch: {
        'form.admin_status': function(newVal) {
            if (!newVal) {
                this.checkAllAdminPrivilege = false
            }
        },

        'form.purchaser_status': function(newVal) {
            if (!newVal) {
                this.checkAllPurchaserPrivilege = false
            }
        },

        checkAllAdminPrivilege: function(newVal) {
            if (newVal) {
                this.form.admin_permissions = this.administratorPrivileges.map(value => value.id)
            } else {
                this.form.admin_permissions = []
            }
        },

        checkAllPurchaserPrivilege: function(newVal) {
            if (newVal) {
                this.form.purchaser_permissions = this.purchaserPrivileges.map(value => value.id)
            } else {
                this.form.purchaser_permissions = []
            }
        },

        'form.admin_permissions': function(newVal) {
            if (newVal.length === 0) {
                this.checkAllAdminPrivilege = false
                this.isIndeterminateAdmin = false
            } else if (this.administratorPrivileges.every(value => newVal.includes(value.id))) {
                this.checkAllAdminPrivilege = true
                this.isIndeterminateAdmin = false
            } else {
                this.isIndeterminateAdmin = true
            }
        },

        'form.purchaser_permissions': function(newVal) {
            if (newVal.length === 0) {
                this.checkAllPurchaserPrivilege = false
                this.isIndeterminatePurchaser = false
            } else if (this.purchaserPrivileges.every(value => newVal.includes(value.id))) {
                this.checkAllPurchaserPrivilege = true
                this.isIndeterminatePurchaser = false
            } else {
                this.isIndeterminatePurchaser = true
            }
        }
    },

    methods: {
        open(obj) {
            this.mode = obj.mode
            this.cacheData = obj
            this.dialogVisible = true
            if (this.mode === 'create') {
                this.form = {
                    account_id: obj.data.id,
                    realname: '',
                    position: '',
                    birthday: '',
                    date_onboarding: '',
                    remarks: '',
                    admin_status: 0,
                    purchaser_status: 0,
                    admin_permissions: [],
                    purchaser_permissions: []
                }
                this.account_data = obj.data
            } else {
                this.form = obj.data
            }
        },

        confirm() {
            this.form.birthday = dateFormat(this.form.birthday, 'yyyy-MM-dd')
            this.form.date_onboarding = dateFormat(this.form.date_onboarding, 'yyyy-MM-dd')
            if (this.mode === 'create') {
                this.create()
            } else {
                this.update()
            }
        },

        create() {
            this.$fetch.post({
                url: `/staff`,
                params: this.form
            }).then(data => {
                this.dialogVisible = false
                this.openMessage(1, '添加员工成功')
                this.$emit('dataChanged')
            }).catch(erro => {
                this.openMessage(0, erro)
            })
        },

        update() {
            this.$fetch.put({
                url: `/staff/${this.form.staff_id}`,
                params: this.form
            }).then(data => {
                this.dialogVisible = false
                this.openMessage(1, '编辑员工成功')
                this.$store.dispatch('getUserPrivileges')
                this.$emit('dataChanged')
            }).catch(error => {
                this.openMessage(0, error)
            })
        },

        deleteEmployee() {
            this.$myWarning({
                message: '确定要删除吗？'
            }).then(data => {
                this.$fetch.delete({
                    url: `/staff/${this.form.staff_id}`
                }).then(data => {
                    this.openMessage(1, '删除成功')
                    this.dialogVisible = false
                    this.$emit('dataChanged')
                })
            }).catch(e => {

            })
        },

        cancel() {
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
.delete_Employee{
    position: absolute;
    top:12px;
    left:103px;
    width: 94px;
    height: 26px;
    line-height: 26px;
    border: 1px solid #FF6666;
    border-radius: 13px;
    font-size: 14px;
    color: #FF6666;
    text-align: center;
    cursor: pointer;
}
.add_employees_second_step{
    overflow: hidden;
    height: 400px;
    .left{
        float: left;
        width: 220px;
        p{
            margin-bottom: 10px;
            font-size: 16px;
            color: #333333;
            font-weight: bold;
        }
        ul{
            li{
                font-size: 16px;
                color: #333333;
                height: 30px;
                line-height: 30px;
                margin-bottom: 5px;

                span:nth-of-type(1) {
                    display: inline-block;
                    width: 80px;
                }

                &.head_portrait{
                    height: 40px;
                    line-height: 40px;
                    img{
                        height: 40px;
                        width: 40px;
                        border-radius: 50%;
                    }
                }

                .name {
                    display: inline-block;
                    max-width: 110px;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                }

                span{
                    vertical-align: top;
                }
                &.position,&.remark,&.realname{
                    /deep/ .el-input--small .el-input__inner{
                        padding:5px;
                    }
                }
            }
        }
    }
    .right{
        float: right;
        width: 668px;
        height: 375px;
        border: 1px solid #DDDDDD;
        .role{
            float: left;
            width: 78px;
            height: 100%;
            background: #F9F9F9;
            ul{
                li{
                    width: 100%;
                    height: 40px;
                    line-height: 40px;
                    text-align: center;
                    font-size: 16px;
                    color: #333333;
                    &.active{
                        border-left: 2px solid #009688;
                        background-color: #fff;
                    }
                }
            }
        }
        .power{
            float: right;
            width: calc(100% - 78px);
            height: 100%;
            padding-top: 10px;
            padding-left: 8px;
            .manager,.buyer{
                p{
                    > * {
                        display: inline-block;
                        vertical-align: middle;
                    }
                    line-height: 30px;
                    >span{
                        font-size: 16px;
                        color: #009688;
                        margin-right: 7px;
                    }
                    >label{
                        // position: relative;
                        // top:4px;
                        margin-left: 21px;
                    }

                    .check-all {
                        margin-left: 15px;
                    }
                }
            }
            .manager{
                margin-bottom: 20px;
            }
            .buyer{
                /deep/ .el-checkbox{
                    margin-right: 30px;
                }
            }
        }
    }
}
/deep/ .el-input,.el-date-editor.el-input,.el-textarea{
    width: 140px;
}
/deep/ .el-input--small .el-input__inner{
    height: 30px;
    line-height: 30px;
    border-radius: 0;
}
/deep/ .el-textarea__inner{
    border-radius: 0;
    padding:5px;
    height: 60px;
}
// /deep/ .el-checkbox__inner{
//     width: 20px;
//     height: 20px;
// }
/deep/ .el-checkbox__label{
    font-size: 16px;
    color:#333;
}
/deep/ .el-checkbox__input.is-checked+.el-checkbox__label{
    color:#333;
}
/deep/ .el-checkbox+.el-checkbox{
    margin-left: 0;
}
.checkbox-group {
    /deep/ .el-checkbox{
        min-width: 116px;
        margin-top: 14px;
    }
}

</style>
