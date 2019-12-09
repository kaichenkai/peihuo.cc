<template>
    <div class="station-container" v-if="shopList.length > 1">
        <slot></slot>
        <input @focus="isFocus = true" readonly @blur="isFocus = false" type="text">
        <transition name="slide-fade">
            <ul v-show="isFocus">
                <li v-for="shop in shopList" :key="shop.id" @click="chooseShop(shop)">{{shop.abbreviation}}</li>
            </ul>
        </transition>
    </div>
</template>

<script>
import { mapState } from 'vuex'
import MIXIN_GET_INFO from '../mixin/get_info'
export default {
    data() {
        return {
            isFocus: false
        }
    },

    mixins: [MIXIN_GET_INFO],

    computed: {
        ...mapState(['currentShop', 'shopList'])
    },

    methods: {
        chooseShop(shop) {
            if (shop.id === this.currentShop.id) {
                return
            }
            this.$emit('beforeShopChang')
            this.$fetch.put({
                url: '/currentshop',
                params: {
                    shop_id: shop.id
                }
            }).then(data => {
                this.getCurrentShop()
                // 不用再抛出 shopChanged 事件 ， 因为父组件是watch的当前店铺id所以改变店铺后只需要请求当前店铺就能刷新订单数据
                this.$emit('shopChanged')
            }).catch(e => {
                this.openMessage(0, e)
            })
        }
    }
}
</script>

<style lang="scss" scoped>
.station-container {
    position: relative;
    display: inline-block;
    cursor: pointer;

    input {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
    }

    ul {
        position: absolute;
        left: 50%;
        top: 35px;
        margin-left: -38px;
        min-width: 76px;
        background: #FFFFFF;
        box-shadow: 0 0 10px 0 rgba(0,0,0,0.15);
        z-index: 100;

        li {
            margin-top: 5px;
            margin-bottom: 5px;
            padding: 0 10px;
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
            line-height: 30px;
            white-space: nowrap;

            &:hover {
                background: #F5F7FA;
            }
        }

        &:before {
            content: '';
            position: absolute;
            top: -5px;
            left: 50%;
            width: 10px;
            height: 10px;
            transform: translateX(-50%) rotate(45deg);
            background: #fff;
        }
    }

    .slide-fade-enter-active {
        transition: all .5s ease;
    }
    .slide-fade-leave-active {
        transition: all .5s ease;
    }
    .slide-fade-enter, .slide-fade-leave-to
    /* .slide-fade-leave-active for below version 2.1.8 */ {
        transform: translateY(-20px);
        opacity: 0;
    }
}
</style>
