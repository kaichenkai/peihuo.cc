<template>
<div class="bg">
<div class="max-container">
    <input type="hidden" value="Pm0tzHLClI6iHqxdkCbwlSwHWZycbQoRFQwdqEI_:4TysosM_wuFDuOBsk1--3FjPnww=:eyJkZWFkbGluZSI6MTU0MDE4MzM2Niwic2NvcGUiOiJzaG9waW1nIn0=" id="token">
    <div class="register-container">
        <div class="register-top">
            <img :src="avatar" class="re-img" alt="头像">
            <p>{{userName}}</p>
        </div>
        <div class="register-content mt10">
            <div class="regis-row">
                <input type="text" v-model="name" class="long-ipt shop_name" placeholder="中转站名"></div>
            <div class="regis-row group">
                <span class="wrap-ipt-span fl  p0">
                    <el-select class="long-ipt province  p0" v-model="province" @change="provinceChange" placeholder="请选择">
                        <el-option
                        v-for="(value, key) in provinces"
                        :key="key"
                        :label="value.name"
                        :value="key">
                        </el-option>
                    </el-select>
                </span>
                <span class="wrap-ipt-span fr p0">
                    <el-select class="long-ipt province  p0" v-model="city_code" placeholder="请选择">
                        <el-option
                        v-for="(value, key) in citys"
                        :key="key"
                        :label="value.name"
                        :value="key">
                        </el-option>
                    </el-select>
                </span>
            </div>
            <div class="regis-row">
                <input type="text" v-model="address" class="long-ipt shop_address address" placeholder="详细地址" data-code="420100"></div>
            <div class="regis-row">
            </div>
            <div class="regis-row">
                <input type="text" v-model="phone" class="long-ipt shop_address" id="phone" placeholder="输入手机号"></div>
            <div class="regis-row">
                <input type="text" class="long-ipt" v-model="code" placeholder="输入验证码" id="code">
                <a @click="getCode" class="get-code get_code" data-action="shop_register">{{text}}</a></div>
            <p class="c999 f12 mt10">此手机号将会和该微信帐号锁定登录</p>
            <a href="javascript:;" @click="submit" class="register-btn register mt10">申请注册</a></div>
    </div>
</div>
<bind ref="bind"></bind>
</div>
</template>

<script>
import BTime from 'best-calendar'
import Bind from '@/components/bind/bind'
import { citys as provinces } from '@/config/citys'
export default {
    data() {
        return {
            userName: '',
            avatar: '',
            provinces,
            citys: {},
            province: '',
            city_code: '',
            name: '',
            address: '',
            phone: '',
            code: '',
            text: '获取验证码'
        }
    },

    created() {
        this.checkLoginAndWxBind()
    },

    methods: {
        checkLoginAndWxBind() {
            this.$fetch.get({
                url: 'login'
            }).then(data => {
                console.log(data)
                if (!data.user) {
                    this.$refs.bind.open({
                        type: 'wx',
                        action: 'login',
                        success: () => {
                            this.checkLoginAndWxBind()
                        }
                    })
                } else if (!data.user.wx_unionid) {
                    // 绑定微信
                    this.$refs.bind.open({
                        type: 'wx',
                        action: 'bind',
                        success: () => {
                            this.checkLoginAndWxBind()
                        }
                    })
                } else {
                    this.phone = data.user.phone
                    this.avatar = data.user.avatar
                    this.userName = data.user.realname || data.user.nickname
                }
            }).catch(e => {
                this.openMessage(0, e || '获取用户信息失败')
            })
        },

        provinceChange(value) {
            this.city = ''
            if (this.provinces[value].city) {
                this.citys = this.provinces[value].city
            } else {
                this.citys = {
                    [value]: this.provinces[value]
                }
            }
        },

        getCode() {
            let singleTest = this.$Validator.single
            if (!singleTest('isPhone', this.phone)) {
                return this.openMessage(2, '请先输入电话号码')
            }
            if (this.lock) return
            let countDown = new BTime.CountDown(60000, 0)

            countDown.on('timing', time => {
                this.text = time.second + 's'
            })

            countDown.on('timend', () => {
                this.lock = false
                this.text = '获取验证码'
            })

            this.$fetch.get({
                url: '/common/logincode',
                params: {
                    action: 'station_register',
                    phone: this.phone
                }
            }).then(data => {
                this.lock = true
                console.log(data)
            }).catch(e => {
                countDown.stop(true)
                this.openMessage(0, e || '获取登陆验证码失败')
            })
        },

        submit() {
            this.validator().then(() => {
                this.$fetch.post({
                    url: '/station',
                    params: {
                        city_code: this.city_code,
                        name: this.name,
                        address: this.address,
                        phone: this.phone,
                        code: this.code
                    }
                }).then(data => {
                    this.openMessage(1, '创建成功')
                    this.$router.push('/login')
                }).catch(e => {
                    this.openMessage(0, e || '创建失败')
                })
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        validator() {
            let vd = new this.$Validator()

            vd.add('isEmpty', this.name, '请输入中转站名称')
            vd.add('isEmpty', this.city_code, '请选择城市')
            vd.add('isEmpty', this.address, '请输入详细地址')
            vd.add('isEmpty', this.phone, '请输入电话号码')
            vd.add('isPhone', this.phone, '请输入正确的电话号码')
            vd.add('isEmpty', this.code, '请输入验证码')

            return vd.start()
        }
    },

    components: {
        Bind
    }
}
</script>
<style lang="scss" scoped>
.bg {
    background: #fff;
    height: 100%;
    font-size: 12px;

    a {
        text-decoration: none;
    }
}

.max-container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    padding: 0 10px;

    .register-top {
        background-color: #fff;
        padding: 30px 0 20px 0;
        text-align: center;

        .re-img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-bottom: 8px;
        }

        .register-top p {
            text-align: center;
            font-size: 16px;
        }
    }

    .register-content {
        .regis-row {
            position: relative;
            margin-bottom: 10px;

            .long-ipt {
                width: 100%;
                height: 40px;
                padding: 0 6px;
                border-top: 1px solid #ddd;
                background-color: #f0f4f0;
                border-radius: 4px;
                outline: 0;
                border: 1px solid #eee;
            }

            .address-span {
                display: inline-block;
                padding-right: 10px!important;
                line-height: 38px;
                white-space: nowrap;
                overflow: hidden;
            }

            .long-ipt:focus {
                background-color: #fff;
                border: 2px solid #47b8a0!important;
            }

            .wrap-ipt-span {
                width: 49%;
                position: relative;
                z-index: 1;
            }

            .fl {
                float: left;
            }

            .fr {
                float: right;
            }

            .get-code {
                position: absolute;
                right: 1px;
                top: 1px;
                background-color: #47b8a0;
                color: #fff;
                width: 70px;
                text-align: center;
                height: 38px;
                line-height: 38px;
            }
        }

        .btn>.caret, p {
            clear: both;
            margin: 0;
            word-break: break-all;
            text-align: left;
        }

        .group {
            clear: both;
        }

        .group:after, .group:before {
            content: '';
            display: block;
            line-height: 0;
            height: 0;
            font-size: 0;
            clear: both;
        }
    }

    .register-btn {
        display: block;
        height: 40px;
        line-height: 40px;
        color: #fff;
        background-color: #47b8a0;
        border-radius: 20px;
        text-align: center;
    }
}

div:after {
    display: table;
    content: "";
}

.mt10 {
    margin-top: 10px;
}

.p0 {
    padding: 0 !important;
    padding-right: 0 !important;
}
</style>
