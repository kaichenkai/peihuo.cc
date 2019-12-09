<template>
    <div class="person_info">
        <div class="header">
            <p @click="returnToHome"></p>
            个人信息
        </div>
        <div class="basic_info">
            <ul>
                <li>头像<img :src="$route.params.login_info.avatar" alt=""></li>
                <li>昵称<span>{{$route.params.login_info.nickname}}</span></li>
                <li>真实姓名<span>{{$route.params.login_info.realname}}</span></li>
                <li>性别<span>{{$route.params.login_info.sex?'女':'男'}}</span></li>
                <li style="border-bottom:none;">出生日期<span>{{$route.params.login_info.birthday}}</span></li>
            </ul>
        </div>
        <div class="other_info">
            <ul>
                <li>森果ID<span>{{$route.params.login_info.id}}</span></li>
                <li style="border-bottom:none">手机号绑定<span>{{$route.params.login_info.phone}}</span></li>
                <!-- <li style="border-bottom:none">密码管理<span></span></li> -->
            </ul>
        </div>
        <div class="exit" @click="exit">退出登录</div>
    </div>
</template>
<script>
export default {
    methods: {
        exit() {
            this.$fetch.delete({
                url: '/login'
            }).then(data => {
                this.$router.push('/login')
            })
        },
        returnToHome() {
            this.$router.push({ name: 'home', params: { index: 1 } })
        }
    }
}
</script>

<style lang="scss" scoped>
    .person_info{
        .header{
            position: relative;
            height: 50px;
            line-height: 50px;
            font-size: 18px;
            color:#333;
            text-align: center;
            border-bottom: 1px solid #dedede;
            box-shadow: 0 1px 2px 0 #e4e4e4;
            background-color: #fff;
            p{
                position: absolute;
                left: 0;
                top: 0;
                width: 34px;
                height: 100%;
                background: url('~@/assets/images/back.png') no-repeat right center/16px;
            }
        }
        .basic_info,.other_info{
            padding: 0 10px;
            background-color: #fff;
            box-shadow: 0 1px 2px 0 #e4e4e4;
            li{
                font-size: 16px;
                height: 60px;
                line-height: 60px;
                border-bottom: 1px solid #ddd;
                padding-right: 14px;
                span{
                    float: right;
                    color:#999;
                }
                img{
                    position: relative;
                    top: 4px;
                    float: right;
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                }
            }
        }
        .other_info{
            margin-top: 10px;
            // li:nth-last-of-type(1){
            //     background: url('~@/assets/images/arr_right.png') right center/8px no-repeat;
            // }
        }
        .exit{
            margin-top: 20px;
            height: 60px;
            line-height: 60px;
            box-shadow: 0 0 6px 0 #e4e4e4;
            background-color: #fff;
            text-align: center;
            color: #f66;
            font-size: 16px;
        }
    }
</style>
