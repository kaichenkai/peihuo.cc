<template>
    <div class="login">
        <div class="title">
            <p class="img">
                <img src="~@/assets/images/logo_white.png" alt="">
            </p>
            <p class="text">采购配货系统登录</p>
        </div>
        <div class="form">
            <ul>
                <li :class="{active:active}" @click="active=true">
                    <p>手机号</p>
                    <input type="text" placeholder="输入手机号" v-model.trim="form.phone">
                </li>
                <li :class="{active:!active}" @click="active=false">
                    <p>验证码</p>
                    <span :class="{sended:sended}" @click="sendYanzhengMa">{{text}}</span>
                    <input type="text" placeholder="输入验证码" v-model.trim="form.code">
                </li>
            </ul>
            <div class="btn_login_sure" :class="{forbid:forbid}" @click="login">确认</div>
        </div>
    </div>
</template>
<script>
export default {
    data() {
        return {
            active: true,
            forbid: true,
            form: {
                action: 'phone',
                phone: '',
                code: ''
            },
            sended: false,
            text: '发送',
            timer: ''
        }
    },
    watch: {
        'form.code'(val) {
            if (val.length > 0) {
                this.forbid = false
            } else {
                this.forbid = true
            }
        },
        sended(val) {
            if (!val) {
                this.text = '发送'
                clearInterval(this.timer)
            }
        }
    },
    methods: {
        sendYanzhengMa() {
            if (this.sended) {
                return
            }
            this.$fetch.get({
                url: '/common/logincode',
                params: {
                    action: 'login',
                    phone: this.form.phone
                }
            }).then(data => {
                this.sended = true
                console.log(data)
                let count = 60
                this.text = `(${count})秒`
                this.timer = setInterval(() => {
                    count--
                    this.text = `(${count})秒`
                    if (count === 0) {
                        this.sended = false
                    }
                }, 1000)
            }).catch(e => {
                this.sended = false
                this.$alert(`获取登陆验证码失败,${e}`)
            })
        },
        login() {
            if (this.forbid) {
                return false
            }
            this.$fetch.post({
                url: '/login',
                params: this.form
            }).then(data => {
                this.$router.push('/home')
            }).catch(erro => {
                this.$alert(erro)
            })
        }
    }
}
</script>

<style lang="scss" scoped>
    .login{
        .title{
            width:100%;
            height: 220px;
            padding-top: 40px;
            background: -webkit-linear-gradient(to right,#009688 0,#58d0a6 100%);
            .img{
                text-align: center;
            }
            .text{
                margin-top: 44px;
                font-size: 26px;
                color: #fff;
                text-align: center;
            }
        }
        .form{
            position: relative;
            top: -40px;
            ul{
                border-radius: 4px;
                box-shadow: 0 1px 2px 1px #e7e7e7;
                background-color: #fff;
                li{
                    border-bottom: 1px solid #ddd;
                    padding: 6px 10px;
                    overflow: hidden;
                    &.active{
                        background-color: #d9f0ed;
                        p{
                            color: #009688;
                        }
                    }
                    p{
                        display: inline-block;
                        line-height: 40px;
                        color: #666;
                        font-size: 20px;
                    }
                    input{
                        float: right;
                        height: 40px;
                        // width: 140px;
                        max-width: calc(100% - 80px);
                        max-width: calc(100% - 130px);
                        text-align: right;
                        font-size: 20px;
                        color: #333;
                        padding: 0 6px;
                        background-color: transparent;
                        outline: none;
                        border:none;
                    }
                    span{
                        float: right;
                        color: #009688;
                        border: 1px solid #009688;
                        background-color: #fff;
                        vertical-align: middle;
                        width: 48px;
                        font-size: 14px;
                        text-align: center;
                        height: 36px;
                        line-height: 36px;
                        border-radius: 4px;
                        margin-left: 10px;
                        &.sended{
                            color: #666;
                            border-color: #666;
                        }
                    }
                }
            }
            .btn_login_sure{
                margin: 26px auto;
                width: 96%;
                font-size: 20px;
                height: 50px;
                line-height: 50px;
                text-align: center;
                border-radius: 25px;
                background: -webkit-linear-gradient(to right,#009688 0,#58d0a6 100%);
                color: #fff;
                &.forbid{
                    background: #ccc;
                }
            }
        }
    }
</style>
