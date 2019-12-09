<template>
    <div class="title-tools">
        <h1>{{config.title}}</h1>
        <span v-if="config.tools" v-for="(item,index) in config.tools" :key="index" @click="item.callback">{{item.name}}</span>
    </div>
</template>

<script>
export default {
    props: {
        config: {
            default: () => {
                return {

                }
            },
            type: Object
        }
    }
}
</script>

<style lang="scss" scoped>
.title-tools {
    margin-bottom: 10px;
    user-select: none;
}
h1 {
    display: inline-block;
    margin-right: 20px;
    font-size: 16px;
    color: #333333;
    letter-spacing: 0;
    line-height: 30px;
}

span {
    display: inline-block;
    margin-right: 15px;
    font-size: 14px;
    color: rgba(107,164,239,0.95);
    letter-spacing: 0;
    cursor: pointer;
}
</style>
