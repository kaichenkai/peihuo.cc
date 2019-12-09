<template>
    <div class="sort-container" @click="changeSort">
        <span>
            <slot></slot>
        </span>
        <div class="icon-warpper">
            <i class="el-icon el-icon-caret-top" :class="{'active': tag == 1}" @click.stop="active(1)"></i>
            <i class="el-icon el-icon-caret-bottom" :class="{'active': tag == 2}" @click.stop="active(2)"></i>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            actived: '',
            tag: 0
        }
    },

    props: ['name'],

    methods: {
        active(item) {
            this.tag = item
            this.$emit('sorted', item, this.name)
        },

        changeSort() {
            this.tag = (this.tag + 1) % 3
            this.$emit('sorted', this.tag, this.name)
        }
    }
}
</script>

<style lang="scss" scoped>
.sort-container {
    cursor: pointer;

    span {
        display: inline-block;
        vertical-align: middle;
    }

    .icon-warpper {
        display: inline-flex;
        vertical-align: middle;
        flex-direction: column;
        width: 14px;
        height: 28px;
        align-items: center;
        justify-content: center;

        i.el-icon {
            color: #c0c4cc;
        }

        .el-icon-caret-top {
            transform: translateY(4px);
        }

        .el-icon-caret-bottom {
            transform: translateY(-4px);
        }
    }

    .active {
        color: #008688 !important;
    }
}
</style>
