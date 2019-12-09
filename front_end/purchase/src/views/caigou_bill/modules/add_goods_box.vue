<template>
    <div class="add_goods_box" @click="$emit('close')">
        <div class="content" @click.stop>
            <p>添加货品</p>
            <ul>
                <!-- <li>查看各店订货</li>
                <li>查看历史采购<span style="color:#009688;">(已采购8次)</span></li> -->
                <li @click="$emit('oneGoodManySupplier')">一品多供货商</li>
                <li @click="$emit('edit')">修改</li>
            </ul>
        </div>
    </div>
</template>
<script>
export default {
    data() {
        return {
        }
    }
}
</script>
<style lang="scss" scoped>
    .add_goods_box{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        .content{
            width: 94%;
            padding: 0 8px 10px 8px;
            background-color: #fff;
            border-radius: 5px;
            margin: 30% auto;
            p{
                height: 46px;
                line-height: 46px;
                border-bottom:2px solid #009688;
                font-size: 15px;
                font-weight: bold;
                color:#009688;
            }
            ul{
                padding-left: 8px;
                li{
                    height: 46px;
                    line-height: 46px;
                    font-size: 15px;
                    font-weight: bold;
                    color:#000;
                }
            }
        }
    }
</style>
