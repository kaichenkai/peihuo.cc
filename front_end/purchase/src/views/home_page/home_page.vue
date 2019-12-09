<template>
    <div class="home_page">
        <template v-if="show1">
            <div class="header">
                {{currentstation_info.name}}
            </div>
            <div class="title">
                采购单({{caigouBillNum}})
            </div>
            <div class="table">
                <table>
                    <colgroup>
                        <col width="32%/">
                        <col width="18%">
                        <col width="20%">
                        <col width="23%">
                        <col width="7%">
                    </colgroup>
                    <thead>
                        <tr>
                            <td>完成时间</td>
                            <td>货品数</td>
                            <td>总件数</td>
                            <td>总支出/元</td>
                            <td>&nbsp;</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr @click="caigouBillDetail(item)" v-for="(item,index) in purchase_order_list" :key="index">
                            <td v-if="item.subtotal===0" class="wait_tobuy">待采购</td>
                            <td v-else>{{item.date}}</td>
                            <td>{{item.goods_num}}</td>
                            <td>{{item.total_amount}}</td>
                            <td>{{item.subtotal}}</td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>
        <person-center v-show="!show1" :login_info='login_info' :currentstation_info='currentstation_info'></person-center>
        <div class="nav">
            <ul>
                <li class="caigou" @click="tab" :class="{active:show1}">
                    <p></p>
                    采购
                </li>
                <li class="center" @click="show1=false" :class="{active:!show1}">
                    <p></p>
                    个人中心
                </li>
            </ul>
        </div>
    </div>
</template>
<script>
import personCenter from '../user_info/person_center.vue'
export default {
    data() {
        return {
            purchase_order_list: [],
            show1: this.$route.params.index === undefined,
            login_info: {},
            currentstation_info: {}
        }
    },
    created() {
        this.$fetch.get({
            url: '/login',
            params: {}
        }).then(data => {
            this.login_info = data.user
        })
        this.$fetch.get({
            url: '/currentstation',
            params: {}
        }).then(data => {
            this.currentstation_info = data.data
        })
        this.$fetch.get({
            url: 'purchase/order/list',
            params: {

            }
        }).then(data => {
            this.purchase_order_list = data.purchase_order_list
        })
    },
    methods: {
        tab() {
            this.show1 = true
            window.localStorage.removeItem('index')
        },
        caigouBillDetail(item) {
            this.$router.push({ name: 'caigou', params: { item: item } })
        }
    },
    components: {
        personCenter
    },
    computed: {
        caigouBillNum() {
            return this.purchase_order_list.length
        }
    }
}
</script>
<style lang="scss" scoped>
    .home_page{
        width:100%;
        height: 100%;
        background-color: #fff;
        .header{
            height: 50px;
            line-height: 50px;
            font-size: 18px;
            color:#333;
            text-align: center;
            border-bottom: 1px solid #dedede;
            box-shadow: 0 1px 2px 0 #e4e4e4;
            // background: url('~@/assets/images/chain.png')  no-repeat 18% center/60px;
        }
        .title{
            padding: 10px 0 5px 10px;
            font-size: 14px;
            color:#333;
            font-weight: bold;
        }
        .table{
            max-height: calc(100% - 125px);
            table{
                width: 100%;
                thead{
                    tr{
                        line-height: 40px;
                        td{
                            font-size:12px;
                            color:#999;
                            &:nth-of-type(1){
                                padding-left: 10px;
                            }
                        }
                    }
                }
                tbody{
                    tr{
                        line-height: 40px;
                        td{
                            font-size:12px;
                            color:#333;
                            &.wait_tobuy{
                                color:#009688;
                                font-weight: bold;
                            }
                            &:nth-of-type(1){
                                padding-left: 10px;
                            }
                            &:nth-last-of-type(1){
                                background: url('~@/assets/images/arr_right.png') no-repeat center/8px;
                            }
                            &:nth-last-of-type(2){
                                color: #ff7c56;
                                font-weight: bold;
                            }
                        }
                        &:nth-of-type(2n-1){
                            background: rgba(239,242,244,.5);
                        }
                    }
                }
            }
        }
        .nav{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            box-shadow: 0 -1px 2px 0 #D4D4D4;
            ul{
                overflow: hidden;
                li{
                    position: relative;
                    float: left;
                    width: 50%;
                    height: 50px;
                    padding-top: 4px;
                    font-size: 12px;
                    color:#333;
                    text-align: center;
                    p{
                        width: 24px;
                        height: 24px;
                        margin: 0 auto;
                        margin-bottom: 4px;
                    }
                    &.active{
                        color:#009688;
                        font-weight: bold;
                        background: -webkit-linear-gradient(top,rgba(0,150,136,.15) 18%,rgba(0,150,136,0) 100%);
                    }
                    &.caigou{
                        p{
                            background: url('~@/assets/images/i_data.png') no-repeat 0 -0/24px;
                        }
                        &.active{
                            p{
                                background: url('~@/assets/images/i_data.png') no-repeat 0 -26px/24px;
                            }
                        }
                    }
                    &.center{
                        p{
                            background: url('~@/assets/images/i_profile.png') no-repeat 0 -0/24px;
                        }
                        &.active{
                            p{
                                background: url('~@/assets/images/i_profile.png') no-repeat 0 -26px/24px;
                            }
                        }
                    }
                }
            }
        }
    }
</style>
