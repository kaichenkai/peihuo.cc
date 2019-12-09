<template>
<div class="container box_sty txt-center">
    <div class="page-login group">
        <div class="left-img fl">
            <router-link tag="div" to="/createTransferStation">
                <button class="logo-txt">注册中转站</button>
            </router-link>
            <img class="logo-img" src="https://static.pf.senguo.cc/static/login/img/bg_img.png?v=a7fe14fd397819d44b4fa981c3b8796c" alt=""></div>
        <div class="right-list">
            <p class="label">账号登录</p>
            <div class="login-type-tab login_type_tab">
                <a @click="isUseWxLogin = true" :class="{'active': isUseWxLogin}" class="item login-by-wx" href="javascript:;">微信扫码登录</a>
                <!-- <a class="item login-by-phone" href="javascript:;">帐号密码登录</a> -->
                <a @click="isUseWxLogin = false" :class="{'active': !isUseWxLogin}" class="item login-by-phone" href="javascript:;">手机号登录</a></div>
            <div v-show="isUseWxLogin" class="wrap-wx-login ltab_box">
                <div class="login-qrcode-box">
                    <div class="wrap-login-qrcode" title="" id="code2">
                        <canvas ref="canvas" width="160" height="160"></canvas>
                    </div>
                    <div class="wrap-qrcode-outtime" v-if="isQrCodeExpired">
                        <div style="margin-top: 50px;">二维码已失效</div>
                        <a @click="getQrImage" class="btn-refresh-qrcode btn_refresh_qrcode" href="javascript:;">刷新</a>
                    </div>
                </div>
                <div class="wx-login-info">使用微信扫码关注公众号「森果商户通」即可登录</div>
            </div>
            <div v-show="!isUseWxLogin"  class="wrap-usernum-login ltab_box">
                <div class="username login-input">
                    <input type="text" v-model="phoneNumber" placeholder="手机号" id="phone" autocomplete="off">
                    <input type="hidden"></div>
                <div class="pwd login-input wrap_pw">
                    <input type="text" v-model="code"  @keydown.enter="login" placeholder="输入短信验证码" id="code" autocomplete="off">
                    <a ref="getCode" @click="getLoginMessage" href="javascript:;" class="get-code get_code" data-action="login">{{text}}</a></div>
                <div class="login-btn">
                    <button @click="login" type="button" id="phoneLogin">登录</button></div>
            </div>
        </div>
    </div>
    <bind ref="bind"></bind>
</div>
</template>

<script>
import Bind from '@/components/bind/bind'
import BTime from 'best-calendar'
const qrcode = require('qrcode')
export default {
    data() {
        return {
            isUseWxLogin: true,
            phoneNumber: '',
            code: '',
            isQrCodeExpired: false,
            text: '获取验证码'
        }
    },

    created() {
        this.getQrImage()

        this.timer = setInterval(() => {
            this.checkLogin()
        }, 1000)
    },

    beforeDestroy() {
        clearInterval(this.timer)
    },

    methods: {
        getQrImage() {
            this.$fetch.get({
                url: '/wxticket',
                params: {
                    action: 'login'
                }
            }).then(data => {
                this.isQrCodeExpired = false
                this.scene_id = data.scene_id
                qrcode.toCanvas(this.$refs.canvas, data.ticket_url, (e) => {
                    if (e) {
                        console.log(e)
                        this.openMessage(0, '生成二维码失败')
                    }

                    // 10分钟后提示二维码过期刷新
                    let countDown = new BTime.CountDown(1000 * 60 * 10, 0)
                    countDown.on('timend', () => {
                        this.isQrCodeExpired = true
                    })
                })
            }).catch(e => {
                console.log(e)
                this.openMessage(0, '获取二维码登陆图片失败,' + e)
            })
        },

        getLoginMessage() {
            let singleTest = this.$Validator.single
            if (!singleTest('isPhone', this.phoneNumber)) {
                return this.openMessage(2, '请先输入正确的电话号码')
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
                    action: 'login',
                    phone: this.phoneNumber
                }
            }).then(data => {
                this.lock = true
                console.log(data)
            }).catch(e => {
                countDown.stop(true)
                this.openMessage(0, '获取登陆验证码失败,' + e)
            })
        },

        checkLogin() {
            this.$fetch.post({
                url: '/login',
                params: {
                    action: 'wx',
                    scene_id: this.scene_id
                }
            }).then(data => {
                if (data.done) {
                    if (!data.phone_bind) {
                        this.$refs.bind.open({
                            type: 'phone',
                            success: () => {
                                this.loginSuccess()
                            }
                        })
                    } else {
                        this.loginSuccess()
                    }
                }
            })
        },

        login() {
            let singleTest = this.$Validator.single
            if (!singleTest('isPhone', this.phoneNumber)) {
                return this.openMessage(2, '请先输入正确的电话号码')
            }
            this.$fetch.post({
                url: '/login',
                params: {
                    action: 'phone',
                    phone: this.phoneNumber,
                    code: this.code
                }
            }).then(data => {
                if (!data.wx_bind) {
                    this.$refs.bind.open({
                        type: 'wx',
                        action: 'bind',
                        success: () => {
                            this.loginSuccess()
                        }
                    })
                } else {
                    this.loginSuccess()
                }
            }).catch(e => {
                this.openMessage(0, e || '登陆失败')
            })
        },

        loginSuccess() {
            // this.$store.dispatch('getUserPrivileges').then(data => {
            this.$router.push({
                path: '/main'
            })
            // })
        }
    },

    components: {
        Bind
    }
}
</script>

<style lang="scss" scoped>
.container {
    padding: 0;
    z-index: 2;

    .page-login {
        margin: 130px auto 0 auto;
        display: inline-block;
        box-shadow: 0 0 10px rgba(0,0,0,.3);
        background: -webkit-linear-gradient(to bottom,#c6efe1 0,#c8e6ee 100%);
        background: linear-gradient(to bottom,#c6efe1 0,#c8e6ee 100%);
        position: relative;
        width: 640px;

        .logo-img {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 220px;
        }

        .logo-txt {
            display: block;
            margin: 0 auto;
            width: 120px;
            height: 30px;
            line-height: 30px;
            margin-top: 20px;
            font-size: 18px;
            border: 1px #000 solid;
            user-select: none;
            background: transparent;
        }

        .left-img {
            height: 350px;
            width: 250px;
            position: relative;
            overflow: hidden;
        }

        .right-list {
            padding: 38px 20px;
            width: 340px;
            border-radius: 0 4px 4px 0;
            position: absolute;
            top: -15px;
            right: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,.3);

            .label {
                text-align: center;
                font-size: 24px;
            }

            .login-type-tab {
                font-size: 14px;
                text-align: center;
                margin-top: 12px;
                height: 32px;
                line-height: 32px;

                .item {
                    display: inline-block;
                    width: 88px;
                    margin: 0 4px;
                    position: relative;
                    color: #333;
                    border-bottom: 2px solid transparent;
                    transition: color .2s ease 0s;
                }

                .active {
                    border-bottom: 2px solid #58d0a6;
                }
            }

            .wrap-wx-login {
                margin-top: 20px;
                text-align: center;

                .login-qrcode-box {
                    position: relative;
                    width: 160px;
                    height: 160px;
                    margin: 0 auto;

                    .wrap-login-qrcode {
                        width: 160px;
                        height: 160px;
                        background-color: #ecf1ef;
                    }
                }
            }

            .wrap-qrcode-outtime {
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,.4);
                font-size: 14px;
                text-align: center;
                color: #fff;
            }

            .btn-refresh-qrcode {
                margin-top: 6px;
                display: inline-block;
                color: #fff;
                line-height: 34px;
                width: 64px;
                background: #58d0a6;
                border-radius: 4px;
                font-size: 16px;
            }

            .wrap-usernum-login {
                margin-top: 30px;
            }
        }

        .wx-login-info {
            text-align: center;
            color: #666;
            margin: 30px 0 10px;
            font-size: 12px;
        }

        .wrap-usernum-login {
            margin-top: 30px;

            .login-input {
                height: 50px;
                width: 300px;
                margin-top: 14px;
                position: relative;

                input {
                    height: 50px;
                    width: 300px;
                    font-size: 14px;
                    text-indent: 10px;
                    border-radius: 2px;
                }
            }
            .get-code {
                position: absolute;
                right: 1px;
                top: 1px;
                background-color: #47b8a0;
                color: #fff;
                text-align: center;
                height: 48px;
                line-height: 48px;
                width: 100px;
            }
        }

        .login-btn {
            width: 300px;
            text-align: center;
            margin: 30px 0 10px 0;
            cursor: pointer;

            button {
                border: none;
                width: 100%;
                height: 50px;
                font-size: 18px;
                line-height: 50px;
                background-color: #47b8a0;
                color: #fff;
                border-radius: 40px;
                box-shadow: 0 4px 10px rgba(0,0,0,.2);
            }
        }
    }
}

input {
    border: 1px solid #eee;
    outline: 0;
    -webkit-appearance: none;
}

button {
    outline: none;
    cursor: pointer;
}

a {
    text-decoration: none;
}

.fl {
    float: left;
}

.box_sty {
    width: 100%;
    min-width: 320px;
    max-width: 800px;
    margin: 0 auto;
    max-width: 1000px!important;
}

.txt-center {
    text-align: center;
}
</style>
