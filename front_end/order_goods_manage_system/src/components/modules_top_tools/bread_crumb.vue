<template>
    <div class="tool-container">
        <img  @click="goBack(-1)" src="~@/assets/images/a1.png" alt="">
        <span v-for="(item, index) in titles" :class="{'now': index == titles.length - 1}" :key="index" @click="goBack(index - titles.length + 1)">{{item}}<span v-if="index != titles.length - 1">/</span></span>
    </div>
</template>

<script>
export default {
    methods: {
        goBack(index) {
            if (index === 0) {
                return
            }
            this.$router.go(index)
        }
    },
    props: {
        titles: Array
    }
}
</script>

<style lang="scss" scoped>
.tool-container {
    font-size: 16px;
    color: #999999;
    letter-spacing: 0;
    line-height: 30px;
    user-select: none;

    img {
        margin-right: 5px;
        cursor: pointer;
    }

    span {
        padding: 2px;
        cursor: pointer;
    }

    > * {
        display: inline-block;
        vertical-align: middle;
    }

    .now {
        color: #151515;
    }
}
</style>
