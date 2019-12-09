<template>
    <div class="message" :class="type" v-if="visible">
        {{content}}
    </div>
</template>

<script>
export default {
    name: "MyMessage",
    data() {
        return {
            content: '',
            time: 2000,
            visible: false,
            type: 'error' // 'success','warning','error'
        }
    },
    mounted() {
        this.close()
    },
    methods: {
        close() {
            window.setTimeout(() => {
                this.visible = false
            }, this.time)
        }
    }
}
</script>
<style lang="scss" scoped>
    .message{
        position: fixed;
        top: 0;
        left: 10%;
        width: 80%;
        padding: 12px 10px;
        line-height: 22px;
        text-align: center;
        border-radius: 10px;
        font-size: 14px;
        color: #fff;
        &.error{
            background-color: rgba(255,105,105,.8);
        }
        &.success{
            background-color: rgba(40,167,69,.8);
        }
    }
</style>
