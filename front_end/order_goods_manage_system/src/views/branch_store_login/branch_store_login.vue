<template>
    <div class="login-container">
        <img class="hidden-xs header-img" src="https://static.ls.senguo.cc/static/official/img/head_logo_active.png?v=b0f9bbe641bde586e1405dfc11f6a604" alt="">
        <div class="login-form">
            <h2>【{{storeName}}】采购意向单</h2>
            <div class="login-type" v-if="isPc">
                <div :class="{'login-type-choosed': loginType === 'wx'}" @click="loginType='wx'">微信扫码</div><div :class="{'login-type-choosed': loginType === 'phone'}" @click="loginType='phone'">手机号</div>
            </div>
            <div v-show="loginType=='phone'">
                <label class="input-container">
                    <input type="number" v-removeMouseWheelEvent v-model="phone" placeholder="手机号码">
                    <div class="line"></div>
                </label>
                <label class="input-container">
                    <input type="number" v-removeMouseWheelEvent v-model="code" @keyup.enter="login" placeholder="验证码">
                    <span class="code-btn" @click="getCode">{{text}}</span>
                    <div class="line"></div>
                </label>
                <button class="submit" @click="login">确认</button>
                <p class="tip">请先验证手机号，确认店铺订货人身份</p>
            </div>
            <div v-show="loginType=='wx'">
                <canvas ref="canvas"></canvas>
                <p class="wx-login-info">使用微信扫码关注公众号「森果商户通」即可登录</p>
            </div>
            <img class="hidden-sm img-bottom" src="~@/assets/images/a10.png" alt="">
        </div>
        <bind ref="bind"></bind>
    </div>
</template>

<script>
import BTime from 'best-calendar'
import Bind from '@/components/bind/bind'
import { getQueryString, isPC, isWX, replaceQueryString } from '@/utils'
const qrcode = require('qrcode')
export default {
    data() {
        return {
            text: '获取验证码',
            phone: '',
            code: '',
            lock: false,
            storeName: '',
            loginType: isPC() ? 'wx' : 'phone',
            isPc: isPC()
        }
    },

    created() {
        this.redirectURL = this.$route.query.redirect
        this.storeName = this.$route.query.storeName || getQueryString(this.redirectURL, 'storeName')
        if (this.isPc) {
            this.getQrImage()
            this.timer = setInterval(() => {
                this.checkLogin()
            }, 1000)
        } else if (isWX()) {
            this.wxBrowserLogin()
        }
    },

    beforeDestroy() {
        clearInterval(this.timer)
    },

    methods: {
        wxBrowserLogin() {
            let code = getQueryString(window.location.href, 'code')
            if (!code) {
                window.location.href = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx554875345d7cbba4&response_type=code&scope=snsapi_userinfo&state=onfuckweixin&redirect_uri=${escape(`https://ph.senguo.cc/admin/#/branchStoreLogin?redirect=${this.redirectURL}`)}#wechat_redirect`
            } else {
                this.$fetch.post({
                    url: '/login/wxauth',
                    params: {
                        code: code
                    }
                }).then(data => {
                    if (!data.phone_bind) {
                        this.$refs.bind.open({
                            type: 'phone',
                            success: () => {
                                location.href = replaceQueryString('code', '')
                            }
                        })
                    } else {
                        this.jump()
                    }
                }).catch(e => {
                    console.log(e)
                    this.$myToast.show('微信登陆失败')
                })
            }
        },

        getQrImage() {
            this.$fetch.get({
                url: '/wxticket',
                params: {
                    action: 'login'
                }
            }).then(data => {
                console.log(data)
                this.$nextTick(() => {
                    qrcode.toCanvas(this.$refs.canvas, data.ticket_url, (e) => {
                        if (e) {
                            console.log(e)
                            this.openMessage(0, '生成二维码失败')
                        }
                    })
                })
                this.scene_id = data.scene_id
            }).catch(e => {
                console.log(e)
                this.openMessage(0, '获取二维码登陆图片失败,' + e)
            })
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
                    action: 'login',
                    phone: this.phone
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
                                this.jump()
                            }
                        })
                    } else {
                        this.jump()
                    }
                }
            })
        },

        login() {
            let singleTest = this.$Validator.single
            if (!singleTest('isPhone', this.phone)) {
                return this.openMessage(2, '请先输入电话号码')
            }
            this.$fetch.post({
                url: '/login',
                params: {
                    action: 'phone',
                    phone: this.phone,
                    code: this.code
                }
            }).then(data => {
                if (isPC() && !data.wx_bind) {
                    this.$refs.bind.open({
                        type: 'wx',
                        action: 'bind',
                        success: () => {
                            this.jump()
                        }
                    })
                } else {
                    this.jump()
                }
            })
        },

        jump() {
            if (this.redirectURL) {
                this.$router.push({
                    path: this.redirectURL
                })
            } else {
                this.openMessage(0, '没有可跳转的订货单')
            }
        }
    },

    components: {
        Bind
    }
}
</script>

<style lang="scss" scoped>
@import '~@/assets/style/_include-media.scss';

.login-container {
    height: 100%;
    background: rgba(0,150,136,0.05);

    @include media("<tablet") {
        .hidden-xs {
            display: none;
        }
    }

    @include media(">=tablet") {
        .hidden-sm {
            display: none;
        }
    }

    .header-img {
        position: absolute;
        top: 25px;
        left: 25px;
        width: 100px;
        height: 40px;
    }

    .login-form {
        // max-width: 465px;
        // min-width: 320px;
        height: 390px;
        background: #FFFFFF;
        box-shadow: 0 0 16px 0 rgba(0,0,0,0.10);
        border-radius: 8px;
    }

    h2 {
        margin-top: 25px;
        margin-bottom: 40px;
        font-size: 20px;
        color: #333333;
        text-align: center;
    }

    .login-type {
        display: flex;
        margin: 0 auto;
        margin-bottom: 16px;
        font-size: 14px;
        color: #333333;
        user-select: none;
        cursor: pointer;

        >div {
            flex: 1;
            height: 40px;
            line-height: 40px;
            text-align: center;
            border-bottom: 1px solid #EDEDED;
        }
    }

    .login-type-choosed {
        color: #009688;
        border-bottom: 1px solid #009688 !important;
    }

    .wx-login-info {
        text-align: center;
        color: #666;
        margin: 30px 0 10px;
        font-size: 12px;
    }

    canvas {
        display: block;
        margin: 0 auto;
        width: 250px;
        height: 250px;
    }

    .input-container {
        position: relative;
        display: block;
        margin: 0 auto;
        padding: 0 10px;
        height: 40px;
        width: 345px;
        // border-bottom: 1px #EDEDED  solid;

        // &:focus {
        //     border-bottom: 1px #EDEDED solid;
        // }

        & + .input-container {
            margin-top: 16px;
        }

        input::-webkit-outer-spin-button,
        input::-webkit-inner-spin-button {
            -webkit-appearance: none;
        }

        input[type="number"]{
            -moz-appearance: textfield;
        }

        input {
            display: block;
            width: 100%;
            height: 100%;
            border: none;
            outline: none;
            font-size: 14px;
            color: #333333;
            line-height: 40px;

            &:focus {
                border: none !important;
                & + .code-btn {
                    color: #009688;
                }
                & ~ .line {
                    background: #009688;
                }
            }
        }

        .line {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background:  #EDEDED;
        }

        .code-btn {
            position: absolute;
            top: 0;
            right: 10px;
            height: 40px;
            font-size: 14px;
            color: #999999;
            line-height: 40px;
        }
    }

    .submit {
        display: block;
        margin: 0 auto;
        height: 45px;
        width: 345px;
        margin-top: 45px;
        background: #009688;
        border-radius: 4px;
        font-size: 18px;
        color: #FFFFFF;
        outline: none;
        border: none;

        &:active {
            transform: scale(.95);
        }
    }

    .tip {
        margin-top: 20px;
        text-align: center;
        font-size: 14px;
        color: #999999;
    }

    @include media(">=phone", "<tablet") {
        .login-form {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            border-radius: 0;
        }

        h2 {
            margin-top: 35px;
        }

        .login-type {
            width: 90%;
        }

        .input-container {
            width: 90%;
            input::-webkit-outer-spin-button,
            input::-webkit-inner-spin-button {
                -webkit-appearance: none;
            }

            input[type="number"]{
                -moz-appearance: textfield;
            }
        }

        .submit {
            width: 90%;
        }

        .tip {
            margin-top: 25px;
            padding-left: 5%;
            text-align: left;
        }

        .img-bottom {
            position: absolute;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 70px;
            height: 30px;
        }
    }

    @include media(">=tablet") {

        .login-type  {
            width: 345px;
        }

        canvas {
            display: block;
            margin: 0 auto;
            width: 150px;
            height: 150px;
        }

        .login-form {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate3d(-50%, -50%, 0);
            width: 465px;
        }
    }

}

</style>
