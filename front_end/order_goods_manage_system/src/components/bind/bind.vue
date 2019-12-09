<template>
    <div class="bg" v-if="showBind">
        <div class="bind-wx" v-if="actionForWx">
            <canvas ref="canvas"></canvas>
            <!-- <p @click="jump">跳过</p> -->
            <p>请扫码关注森果商户通</p>
        </div>
        <div v-else class="bind-phone wrap-usernum-login">
            <p>您没有绑定手机号，请先绑定手机号</p>
            <div class="right-list">
                <div class="wrap-usernum-login ltab_box">
                    <div class="username login-input">
                        <input type="text" v-model="phoneNumber" placeholder="手机号" id="phone" autocomplete="off">
                        <input type="hidden"></div>
                    <div class="pwd login-input wrap_pw">
                        <input type="text" v-model="code" placeholder="输入短信验证码" id="code" autocomplete="off">
                        <a @click="getBindMessage" href="javascript:;" class="get-code get_code" data-action="login">{{text}}</a></div>
                    <div class="login-btn">
                        <button @click="bindPhone" type="button" id="phoneLogin">绑定</button></div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import BTime from 'best-calendar'
const qrcode = require('qrcode')
export default {
    data() {
        return {
            showBind: false,
            actionForWx: true,
            text: '获取验证码',
            phoneNumber: '',
            code: ''
        }
    },

    created() {
        this.lock = false
    },

    beforeDestroy() {
        clearInterval(this.timer)
    },

    methods: {
        open(obj) {
            // obj = {
            //     success // 执行成功的回调函数
            //     type // 需要执行的类型如微信（wx）,手机（phone）
            //     action // 需要执行的动作，如绑定（bind）登陆（login）
            // }
            this.showBind = true
            this.actionForWx = obj.type === 'wx'
            this.action = obj.action || '' // login or bind
            this.success = obj.success || function() {}

            if (this.actionForWx) {
                if (this.action === 'bind') {
                    this.getQrImage('bind').then(() => {
                        this.timer = setInterval(() => {
                            this.checkBind()
                        }, 1000)
                    })
                } else if (this.action === 'login') {
                    this.getQrImage('login').then(() => {
                        this.timer = setInterval(() => {
                            this.checkLogin()
                        }, 1000)
                    })
                }
            }
        },

        getQrImage(type) {
            if (this.timer) {
                clearInterval(this.timer)
            }
            return this.$fetch.get({
                url: '/wxticket',
                params: {
                    action: type
                }
            }).then(data => {
                console.log(data)
                this.createQrCode(data.ticket_url)
                this.scene_id = data.scene_id
            }).catch(e => {
                this.openMessage(0, e || '获取二维码登陆图片失败')
            })
        },

        createQrCode(text) {
            qrcode.toCanvas(this.$refs.canvas, text, (e) => {
                if (e) {
                    this.openMessage(0, '生成二维码失败')
                }
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
                    this.openMessage(1, '登陆成功')
                    this.showBind = false
                    clearTimeout(this.timer)
                    this.success()
                }
            })
        },

        checkBind() {
            this.$fetch.post({
                url: '/bind',
                params: {
                    action: 'wx',
                    scene_id: this.scene_id
                }
            }).then(data => {
                if (data.done) {
                    this.openMessage(1, '绑定成功')
                    this.showBind = false
                    clearTimeout(this.timer)
                    this.success()
                }
            })
        },

        getBindMessage() {
            let singleTest = this.$Validator.single
            if (!singleTest('isPhone', this.phoneNumber)) {
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
                    action: 'bind',
                    phone: this.phoneNumber
                }
            }).then(data => {
                this.lock = true
                console.log(data)
            }).catch(e => {
                this.openMessage(0, e || '获取登陆验证码失败')
                countDown.stop(true)
            })
        },

        bindPhone() {
            let singleTest = this.$Validator.single
            if (!singleTest('isPhone', this.phoneNumber)) {
                return this.openMessage(2, '请先输入电话号码')
            }
            this.$fetch.post({
                url: '/bind',
                params: {
                    action: 'phone',
                    phone: this.phoneNumber,
                    code: this.code
                }
            }).then(data => {
                this.openMessage(1, '绑定成功')
                this.showBind = false
                this.success()
            }).catch(e => {
                console.log(e)
                this.openMessage(0, e || '绑定失败')
            })
        }

        // jump() {
        //     this.$fetch.post({
        //         url: '/login/wxtest'
        //     }).then(() => {
        //         this.$router.push('/main')
        //     }).catch(e => {
        //         this.$router.push('/main')
        //     })
        // }
    }
}
</script>

<style lang="scss" scoped>
a {
    text-decoration: none;
}

button {
    outline: none;
}

.bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, .6) !important;
    z-index: 1000;

    .bind-wx {
        padding: 14px;
        position: absolute;
        top: 30%;
        left: 50%;
        transform: translate3d(-50%, -50%, 0);
        background: #fff;

        img {
            display: block;
            width: 200px;
            height: 200px;
        }

        p {
            text-align: center;
        }
    }

    .bind-phone {
        padding: 30px;
        position: absolute;
        top: 30%;
        left: 50%;
        transform: translate3d(-50%, -50%, 0);
        background: #fff;

        label {
            display: block;
        }
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
                border: 1px #999 solid;
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

        .login-btn {
            width: 300px;
            text-align: center;
            margin: 30px 0 10px 0;
            cursor: pointer;

            &:active {
                transform: scale(.9);
            }

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
</style>
