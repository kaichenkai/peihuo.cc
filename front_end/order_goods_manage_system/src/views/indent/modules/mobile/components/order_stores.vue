<template>
    <div class="edit-quantity-bg" v-show="showDialog" @click="showDialog = false">
        <div class="container" @click.stop>
            <div class="item-container">
                <h2>今日已订货({{orderStoreList.length}})</h2>
                <img @click="showDialog = false" class="close" src="~@/assets/images/a11.png" alt="">
                <i class="line"></i>
                <div class="table-container">
                    <table>
                        <tr v-for="(item, index) in orderStoreList" :key="item.shop_id" >
                            <td>{{index + 1}}</td>
                            <td><img class="avatar" :src="item.headimgurl" alt=""></td>
                            <td>
                                {{item.shop}}
                            </td>
                            <td>{{item.creator}}</td>
                            <td>{{item.create_time && item.create_time.split(' ')[1]}}</td>
                        </tr>
                    </table>
                </div>

            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            showDialog: false
        }
    },

    props: {
        orderStoreList: Array
    },

    methods: {
        open() {
            this.showDialog = true
        }
    }
}
</script>

<style lang="scss" scoped>
.edit-quantity-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, .5);
    z-index: 1000;
    // transform: translateZ(3px);

    .container {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 410px;
        background: #fff;
        border-radius: 6px 6px 0 0;

        .close {
            position: absolute;
            top: 8px;
            right: 11px;
            width: 24px;
            height: 24px;
        }

        .item-container {
            margin: 12px 10px 0 10px;

            h2 {
                font-size: 20px;
                color: #009688;
            }

            .line {
                display: block;
                margin: 8px 0 10px 0px;
                height: 2px;
                background: #009688;

            }
        }

        .table-container {
            position: absolute;
            bottom: 10px;
            top: 50px;
            left: 10px;
            right: 10px;
            overflow: auto;
            -webkit-overflow-scrolling: touch;
        }

        table {
            table-layout: fixed;
            width: 100%;

            @mixin overflowHidden {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            tr {
                height: 30px;
                line-height: 30px;
            }
            td {
                font-size: 14px;
                color: #333333;

                &:nth-of-type(1) {
                    width: 20px;
                    font-size: 12px;
                    color: #999999;
                }

                &:nth-of-type(2) {
                    width: 22px;
                }

                &:nth-of-type(3) {
                    // width: 140px;
                    @include overflowHidden;
                }

                &:nth-of-type(4) {
                    // width: 50px;
                    text-align: center;
                    @include overflowHidden;
                }

                &:nth-of-type(5) {
                    width: 60px;
                }
            }
        }

        .avatar {
            display: inline-block;
            vertical-align: middle;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #D8D8D8;

            + span {
                display: inline-block;
                vertical-align: top;
                // width: 120px;
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
        }
    }
}
</style>
