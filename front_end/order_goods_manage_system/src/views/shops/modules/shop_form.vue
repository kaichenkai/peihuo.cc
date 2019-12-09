<template>
    <el-dialog
        :title="mode==='create'?'添加店铺':'编辑店铺'"
        :visible.sync="dialogVisible"
        width="750px">
        <p class="delete_shop" v-show="mode==='update'" @click="deleteShop">删除店铺</p>
        <el-form label-position="top" label-width="80px" :model="form">
            <el-form :inline="true" label-position="top" class="inline">
                <span style="color:#ff6666">*</span>
                <el-form-item label="店铺简称">
                    <el-input v-selectTextOnFocus v-model="form.abbreviation" placeholder="最多四个字" @keyup.enter.native="confirm"></el-input>
                </el-form-item>
                <el-form-item label="店铺全称" style="padding-left: 10px">
                    <el-input v-selectTextOnFocus v-model="form.name" placeholder="请填写店铺名称" @keyup.enter.native="confirm"></el-input>
                </el-form-item>
            </el-form>

            <el-form-item label="店铺地址">
                <el-input v-selectTextOnFocus v-model="form.address" placeholder="请填写店铺地址" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <div class="inline">
            <table>
                <h2>订货人1</h2>
                <tr>
                    <td><span style="color:#ff6666">*</span>姓名</td>
                    <td><el-input v-selectTextOnFocus type="text" v-model="form.contacts[0].name" @keyup.enter.native="confirm"></el-input></td>
                </tr>
                <tr>
                    <td><span style="color:#ff6666">*</span>手机号</td>
                    <td><el-input v-selectTextOnFocus type="text" v-model="form.contacts[0].phone" @keyup.enter.native="confirm"></el-input></td>
                </tr>
            </table>
            <table>
                <h2>订货人2</h2>
                <tr>
                    <td>姓名</td>
                    <td><el-input v-selectTextOnFocus type="text" v-model="form.contacts[1].name" @keyup.enter.native="confirm"></el-input></td>
                </tr>
                <tr>
                    <td>手机号</td>
                    <td><el-input v-selectTextOnFocus type="text" v-model="form.contacts[1].phone" @keyup.enter.native="confirm"></el-input></td>
                </tr>
            </table>
            </div>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">确认</button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            mode: 'create',
            form: {
                abbreviation: '',
                name: '',
                address: '',
                contacts: [{
                    name: '',
                    phone: ''
                }, {
                    name: '',
                    phone: ''
                }]
            }
        }
    },

    methods: {
        open(obj = {}) {
            this.dialogVisible = true
            this.callback = obj.callback || function() {}
            if (obj.mode === 'create') {
                this.mode = 'create'
                this.form = {
                    abbreviation: '',
                    name: '',
                    address: '',
                    contacts: [{
                        name: '',
                        phone: ''
                    }, {
                        name: '',
                        phone: ''
                    }]
                }
            } else if (obj.mode === 'update') {
                this.mode = 'update'
                this.form = obj.form
            }
        },

        cancel() {
            this.dialogVisible = false
        },

        confirm() {
            this.validator().then(() => {
                if (this.mode === 'create') {
                    this.create()
                } else {
                    this.update()
                }
            }).catch(erro => {
                console.log(erro)
                this.openMessage(2, erro)
            })
        },

        removeEmptyContact(form) {
            let obj = JSON.parse(JSON.stringify(form))
            obj.contacts = obj.contacts.reduce((last, next) => {
                if (!next.name || !next.phone) {
                    return last
                } else {
                    return [...last, next]
                }
            }, [])
            return obj
        },

        create() {
            this.$fetch.post({
                url: '/shop',
                params: this.removeEmptyContact(this.form)
            }).then(data => {
                this.openMessage(1, '创建成功')
                this.dialogVisible = false
                this.callback()
            }).catch(e => {
                console.log(e)
                this.openMessage(0, e)
            })
        },

        update() {
            this.$fetch.put({
                url: `/shop/${this.form.id}`,
                params: this.removeEmptyContact(this.form)
            }).then(data => {
                this.openMessage(1, '修改成功')
                this.dialogVisible = false
                this.callback()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        deleteShop() {
            this.$myWarning({
                message: '是否确认删除'
            }).then(() => {
                this.$fetch.delete({
                    url: `/shop/${this.form.id}`,
                    params: {}
                }).then(data => {
                    this.dialogVisible = false
                    this.$emit('dataChanged')
                    this.openMessage(1, '删除成功')
                }).catch(e => {
                    this.openMessage(0, e)
                })
            }).catch(() => {})
        },

        validator() {
            let validator = new this.$Validator()
            validator.add('isEmpty', this.form.abbreviation, '请输入店铺简称')
            // validator.add('isEmpty', this.form.name, '请输入店铺全称')
            // validator.add('isEmpty', this.form.address, '请输入店铺地址')
            this.form.contacts.forEach((value, index) => {
                if (value.name || value.phone) {
                    validator.add('isEmpty', this.form.contacts[index].name.trim(), '请输入订货人姓名')
                    validator.add('isEmpty', this.form.contacts[index].phone, '请输入订货人电话')
                    validator.add('isPhone', this.form.contacts[index].phone, '请输入正确的订货人电话')
                }
            })

            return validator.start()
        },

        close() {
            this.dialogVisible = false
            this.callback()
        }
    }
}
</script>

<style lang="scss" scoped>
.inline {
    display: flex;

    >div {
        flex: 1;
    }
}

/deep/ .el-form-item__label {
    font-size: 14px !important;
    color: #666666 !important;
    margin-bottom: 10px !important;
}

table {

    &:nth-of-type(2) {
        margin-left: 20px;
    }

    h2 {
        font-size: 14px;
        color: #666666;
        margin-bottom: 10px;
    }

    tr > td {
        // height: 40px;
        border: 1px #ddd solid;
        &:nth-of-type(1) {
            width: 65px;
            // height: 40px;
            line-height: 40px;
            background: #F9F9F9;
            // border-color: #DDDDDD;
            // border-top: 1px solid #DDDDDD;
            // border-left: 1px solid #DDDDDD;
            font-size: 14px;
            color: #666666;
            text-align: center;
        }

        &:nth-of-type(2) {
            width: 285px;
            // height: 100%;
            // line-height: 38px;
            background: #F9F9F9;
            // border-color: #DDDDDD;
            // border-top: 1px solid #DDDDDD;
            // border-left: 1px solid #DDDDDD;
            font-size: 14px;
            color: #666666;
            text-align: center;
            overflow: hidden;

            /deep/ input {
                width: 100%;
                height: 40px;
                border: none;
                outline: none;
            }
        }
    }
}

.inline-input {
    display: flex;
    align-items: center;
    height: 40px;
    // margin-top: 10px;

    span {
        width: 65px;
        // height: 40px;
        background: #F9F9F9;
        // border-color: #DDDDDD;
        border-top: 1px solid #DDDDDD;
        border-left: 1px solid #DDDDDD;
        font-size: 14px;
        color: #666666;
        text-align: center;
    }

    div {
        border-top: 1px solid #DDDDDD;
        border-right: 1px solid #DDDDDD;
        border-left: 1px solid #DDDDDD;
        display: inline-block;

         .el-input__inner {
            border: none;
        }
    }
}

.delete_shop{
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
</style>
