<template>
    <div class="person_center">
        <div class="header">
            <p class="photo"><img :src="login_info.avatar" alt=""></p>
            <p class="name"><span @click="toPersonCenter">{{login_info.nickname || login_info.realname}}</span></p>
            <p class="phone">手机号&nbsp;&nbsp;{{login_info.phone}}</p>
        </div>
        <div class="list">
            <ul>
                <li>{{currentstation_info.name}}</li>
                <li @click="aboutSenguo">关于森果</li>
            </ul>
        </div>
    </div>
</template>
<script>
export default {
    props: {
        login_info: {
            default() {
                return {}
            },
            type: Object
        },
        currentstation_info: {
            default() {
                return {}
            },
            type: Object
        }
    },
    methods: {
        aboutSenguo() {
            location.href = 'https://i.senguo.cc/msadmin/about?type=pf'
        },
        toPersonCenter() {
            this.$router.push({ name: 'person', params: { login_info: this.login_info } })
        }
    }
}
</script>

<style lang="scss" scoped>
    .person_center{
        width: 100%;
        height: 100%;
        padding: 0 20px;
        background: url('~@/assets/images/green_circle.png') no-repeat -120px -112px/270px,url('~@/assets/images/org_circle.png') no-repeat 143% -80px/180px;
        .header{
            padding-top: 30px;
            padding-bottom: 35px;
            border-bottom: 1px solid #ddd;
            .photo{
                height: 50px;
                text-align: center;
                img{
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                }
            }
            .name{
                margin-top: 12px;
                text-align: center;
                span{
                    padding-right: 12px;
                    font-size: 20px;
                    color: #333;
                    letter-spacing: .3px;
                    background: url('~@/assets/images/arr_right.png') right center/8px no-repeat;
                }
            }
            .phone{
                margin-top: 10px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
        }
        .list{
            ul{
                li{
                    border-bottom: 1px solid #ddd;
                    height: 80px;
                    line-height: 80px;
                    font-size: 16px;
                    color: #333;
                    letter-spacing: .3px;
                    &:nth-of-type(1){
                        // background: url('~@/assets/images/chain.png') no-repeat right center/50px;
                    }
                    &:nth-of-type(2){
                        background: url('~@/assets/images/arr_right.png') no-repeat right center/10px;
                    }
                }
            }
        }
    }
</style>
