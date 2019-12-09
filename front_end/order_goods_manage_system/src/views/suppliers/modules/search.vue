<template>
    <div class="search">
        <input type="text" placeholder="请输入商品名/首字母">
        <span>

        </span>
    </div>
</template>
<script>
export default {

}
</script>

<style lang="scss" scoped>
    .search{
        position: absolute;
        top:65px;
        right: 15px;
        width: 300px;
        input{
            width: 100%;
            height: 30px;
            background: #FFFFFF;
            border: 1px solid #DDDDDD;
            font-size: 16px;
            color: #999999;
            text-indent: 10px;
            outline: none;
        }
        span{
            position: absolute;
            top:6px;
            right:11px;
            width: 17px;
            height: 17px;
            background-color: #009688;
            border-radius: 50%;
            cursor: pointer;
        }
    }
</style>
