<template>
<transition name="fade">
    <div class="loading-wall" v-if="showLoading">
        <div class="loading-bg">
            <img src="~@/assets/images/loading-spinning-bubbles.svg" alt="">
            <p class="text">{{text}}</p>
        </div>
    </div>
</transition>
</template>

<script>
// import { VueLoading } from 'vue-loading-template'
export default {
    data() {
        return {
            showLoading: false,
            text: '正在处理'
        }
    },

    created() {
    },

    methods: {
        setText(text = '正在处理') {
            this.text = text
        },

        show(text = '正在处理') {
            // document.body.appendChild(this.$el)
            this.showLoading = true
            this.text = text
        },

        close() {
            this.showLoading = false
            // if (document.body.contains(this.$el)) {
            //     document.body.removeChild(this.$el)
            // }
        }
    },

    components: {
        // VueLoading
    }
}
</script>

<style lang="scss">
.loading-wall {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;

    .loading-bg {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate3d(-50%, -50%, 0);
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 120px;
        width: 120px;
        background: rgba(0, 0, 0, .6);
        border-radius: 8px;
        color: #fff;
        z-index: 3;

        .text {
            margin-top: 15px;
        }

        .vue-loading {
            margin: 0;
        }
    }
}
</style>
