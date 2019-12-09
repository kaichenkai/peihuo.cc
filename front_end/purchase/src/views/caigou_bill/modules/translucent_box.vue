<template>
    <div class="translucent_box">
        <div class="top">
            <span @click="$emit('closeBox')"></span>
            手工录入
        </div>
        <div class="content">
            <slot></slot>
        </div>
    </div>
</template>
<style lang="scss" scoped>
    .translucent_box{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,.6);
        .top{
            position: relative;
            left: 0;
            top: 0;
            height: 50px;
            line-height: 50px;
            font-size: 18px;
            color: #009688;
            font-weight: bold;
            text-align: center;
            background: rgba(0,0,0,.4);
            span{
                position: absolute;
                left: 0;
                top: 0;
                width: 50px;
                height: 50px;
                background: url("~@/assets/images/cg_close_btn.png") center/24px no-repeat;
            }
        }
        .content{
            position: absolute;
            width: 100%;
            left: 0;
            bottom: 0;
            height: 479px;
            background-color: #fff;
            border-radius: 5px 5px 0 0;
        }
    }
</style>
