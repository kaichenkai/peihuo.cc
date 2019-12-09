<template>
    <div class="header-container">
        <ul>
            <li class="logo">
                <img src="https://static.ls.senguo.cc/static/official/img/head_logo_active.png?v=b0f9bbe641bde586e1405dfc11f6a604" alt="">
            </li>
            <li class="dinghuo">
                采购配货系统
            </li>
            <li class="exit" @click="logout">
                退出
            </li>
            <li class="user">
                <dl>
                    <dt>
                        <img :src="userData.avatar" alt="">
                    </dt>
                    <dd>{{userData.nickname}}</dd>
                    <dd>{{userData.phone}}</dd>
                </dl>
            </li>
            <stations-select></stations-select>
        </ul>
    </div>
</template>

<script>
import StationsSelect from './stations_select'
export default {
    data() {
        return {
            userData: {},
            stationInfo: {}
        }
    },

    created() {
        this.getUserInfo()
        this.getStationInfo()
    },

    methods: {
        logout() {
            this.$fetch.delete({
                url: '/login'
            }).then(() => {
                this.$router.replace('/login')
                this.openMessage(1, '登出成功')
            }).catch(e => {
                this.openMessage(0, '登出失败, ' + e)
            })
        },

        getUserInfo() {
            return this.$fetch.get({
                url: '/login'
            }).then(data => {
                this.userData = data.user
                this.$store.commit('SET_USER_INFO', this.userData)
            }).catch(e => {
                this.openMessage(0, '获取用户信息失败,' + e)
            })
        },

        getStationInfo() {
            return this.$fetch.get({
                url: '/currentstation'
            }).then(data => {
                this.stationInfo = data.data
                this.$store.commit('SET_STATION_INFO', this.stationInfo)
            }).catch(e => {
                this.openMessage(0, '获取中转站信息失败,' + e)
            })
        }
    },

    components: {
        StationsSelect
    }
}
</script>

<style lang="scss" scoped>
.header-container {
    width: 100%;
    height: 60px;
    line-height: 60px;
    box-shadow: 0 4px 4px 0 rgba(0,0,0,0.10);
    background: #fff;
    user-select: none;

    ul{
        font-size: 24px;
        color: #333333;
        text-align: center;
        // overflow: hidden;
        li{
            &.logo{
                float: left;
                padding:8px 20px 0 30px;
            }
            &.dinghuo{
                float: left;
                line-height: 32px;
                margin-top: 14px;
                text-indent: 20px;
                font-size: 24px;
                color: #333333;
                border-left: 1px solid #d8d8d8;
            }
            &.user{
                float: right;
                padding-top: 10px;
                margin-right: 35px;
                dl{
                    width: 140px;
                    overflow: hidden;
                    font-size: 14px;
                    color: #333333;
                    dt{
                        float: left;
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background-color: #ccc;
                        overflow: hidden;
                        img {
                            width: 100%;
                            height: 100%;
                        }
                    }
                    dd{
                        float: right;
                        width: 91px;
                        line-height: 20px;
                        text-align: left;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                }
            }
            &.exit{
                float: right;
                margin-right: 50px;
                font-size: 14px;
                color: #333333;
                cursor: pointer;
            }
        }
    }
}
</style>
