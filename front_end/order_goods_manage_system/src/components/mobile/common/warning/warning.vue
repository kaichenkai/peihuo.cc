<template>
<!-- <el-dialog
    :title="title || '系统提醒'"
    :visible.sync="dialogVisible"
    width="40%">
    <p class="message" :style="`text-align: ${textAlign}`">{{message}}</p>
    <div v-html="html">
    </div>
    <span slot="footer" class="dialog-footer">
        <button class="btn confirm" :class="{'disabled': !confirmCanClick}" :disabled="!confirmCanClick" @click="confirm">{{confirmText || '确认'}}</button>
        <button class="btn cancel" @click="close">取消</button>
    </span>
</el-dialog> -->
<div class="warning-bg" v-if="dialogVisible" @click="dialogVisible = false">
    <div class="container" @click.stop>
        <p class="title">提交订货单</p>
        <i class="line"></i>
        <p class="message" :style="{'text-align': textAlign}">{{message}}</p>
        <div class="btn-group">
            <button class="cancel" @click="close">取消</button><button class="confirm" @click="confirm">确认</button>
        </div>
    </div>
</div>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            state: ''
        }
    },

    props: {
        title: String,
        message: String,
        textAlign: {
            default: 'center',
            type: String
        },
        html: String,
        confirmText: String,
        confirmCanClick: {
            type: Boolean,
            default: true
        }
    },

    methods: {
        open() {
            this.dialogVisible = true
        },

        confirm() {
            this.dialogVisible = false
            this.state = true
        },

        close() {
            this.state = false
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
.warning-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, .5);
    z-index: 1000;
    // transform: translateZ(4px);

    .container {
        position: absolute;
        top: 145px;
        left: 50%;
        transform: translateX(-50%);
        max-width: 355px;
        padding: 13px 10px 0px 10px;
        width: 96%;
        min-height: 162px;
        background: #FFFFFF;
        border-radius: 6px;

        .title {
            font-size: 16px;
            color: #009688;
        }

        .line {
            display: block;
            margin: 13px 0 20px 0;
            height: 2px;
            background: #009688;
        }

        .btn-group {
            position: absolute;
            // padding: 0 10px;
            bottom: 0;
            left: 10px;
            right: 10px;
            display: flex;
            align-items: center;
            margin-top: 20px;
            height: 50px;
            border-top: 2px #eff2f4 solid;

            button {
                flex: 1;
                background: transparent;
                height: 100%;

                &:active {
                    font-size: 14px;
                    transform: scale(1);
                }
            }

            .cancel {
                font-size: 16px;
                color: #666666;
                border-right: 1px #eff2f4 solid;
            }

            .confirm {
                font-size: 16px;
                color: #009688;
                border-left: 1px #eff2f4 solid;
            }
        }
    }
}
.message {
    font-size: 16px;
    line-height: 20px;
    color: #333333;
    letter-spacing: 0;
}

.disabled {
    background: #ddd !important;
    cursor: not-allowed;
}
</style>
