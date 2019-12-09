<template>
<el-dialog
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
</el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            state: ''
        }
    },

    created() {
        window.addEventListener('keydown', this.keydownEvent)
    },

    beforeDestroy() {
        window.removeEventListener('keydown', this.keydownEvent)
    },

    props: {
        title: String,
        message: String,
        textAlign: String,
        html: String,
        confirmText: String,
        confirmCanClick: {
            type: Boolean,
            default: true
        }
    },

    methods: {
        keydownEvent(e) {
            if (e.keyCode === 13) {
                this.confirm()
            }
        },

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
.message {
    font-size: 14px;
    line-height: 20px;
    color: #333333;
    letter-spacing: 0;
}

.disabled {
    background: #ddd !important;
    cursor: not-allowed;
}
</style>
