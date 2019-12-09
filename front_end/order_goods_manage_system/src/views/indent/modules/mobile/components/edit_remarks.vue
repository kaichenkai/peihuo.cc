<template>
<div class="warning-bg" v-if="dialogVisible" @click="dialogVisible = false">
    <div class="container" @click.stop>
        <p class="title">填写订货备注</p>
        <i class="line"></i>
        <input v-model="remark" type="text" placeholder="输入文字" maxlength="100">
        <p class="tip">剩余<span style="color: #FF7C56;">{{limit}}</span>个字</p>
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
            state: '',
            remark: ''
        }
    },

    computed: {
        limit() {
            return 100 - this.remark.length
        }
    },

    methods: {
        open(obj) {
            this.dialogVisible = true
            this.callback = obj.callback || function() {}
            this.remark = obj.data.remarks
        },

        confirm() {
            this.dialogVisible = false
            this.callback(this.remark)
        },

        close() {
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
    // transform: translateZ(3px);

    .container {
        position: absolute;
        top: 145px;
        left: 50%;
        transform: translateX(-50%);
        max-width: 355px;
        padding: 13px 10px 0px 10px;
        width: 96%;
        min-height: 200px;
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

        input {
            display: block;
            padding: 0 10px;
            margin: 0 auto;
            width: 100%;
            height: 36px;
            border-radius: 4px;
            background: #EFF2F4;
            border: none;
            font-size: 14px;
            color: #333333;
        }

        p.tip {
            margin-top: 10px;
            text-align: right;
            font-size: 12px;
            color: #333333;
            line-height: 16px;
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
