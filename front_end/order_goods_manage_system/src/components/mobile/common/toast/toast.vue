<template>
<transition name="fade">
    <div class="toast" v-if="showToast">
        {{text}}
    </div>
</transition>
</template>

<script>
export default {
    data() {
        return {
            showToast: false,
            text: ''
        }
    },

    methods: {
        setText(text) {
            this.text = text
        }
    }
}
</script>

<style lang="scss" scoped>
.toast {
    position: fixed;
    bottom: 50px;
    left: 50%;
    transform: translateX(-50%);
    padding: 0 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    font-size: 14px;
    color: #fff;
    background: rgba(0, 0, 0, .4);
    border-radius: 15px;
    z-index: 1000;
    white-space: nowrap;
}
</style>
