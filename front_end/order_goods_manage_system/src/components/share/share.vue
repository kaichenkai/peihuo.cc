<template>
    <el-dialog
    :visible.sync="dialogVisible"
    width="350px">
    <div class="container">
        <canvas class="canvas1" ref="canvas"></canvas>
        <p class="tip">本图片由森果系统自动生成</p>
        <p class="url">{{url}}</p>
        <button class="btn" @click="copy">复制链接</button>
    </div>
    </el-dialog>
</template>

<script>
const qrcode = require('qrcode')
const copy = require('copy-to-clipboard')

export default {
    data() {
        return {
            dialogVisible: false,
            url: ''
        }
    },

    methods: {
        open(url) {
            this.dialogVisible = true
            this.url = url
            this.$nextTick(function() {
                qrcode.toCanvas(this.$refs.canvas, this.url, (e) => {
                    if (e) {
                        this.openMessage(0, '生成二维码失败')
                    }
                })
            })
        },

        copy() {
            copy(this.url)
            this.openMessage(1, '复制成功')
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
/deep/ .el-dialog__header {
    background: #fff !important;
    height: 0px !important;
    line-height: 0px !important;
}
.container {
    text-align: center;
    .canvas1 {
        display: block;
        margin: 0 auto;
    }

    .tip {

    }

    .url {
        margin: 10px 0;
        padding: 5px 10px;
        width: 100%;
        text-align: left;
        word-break: break-word;
        line-height: 20px;
        background: #f9f9f9;
    }

    .btn {
        display: inline-block;
        padding: 5px 20px;
        font-size: 14px;
        background: #ddd;
        border: none;
        outline: none;

        &:active {
            transform: scale(.95);
        }
    }
}
</style>
