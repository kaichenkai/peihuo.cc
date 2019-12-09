<template>
    <label>
        <span class="no-checked" v-if="isChecked !== label"></span>
        <span class="checked" v-else>
            <span class="point"></span>
        </span>
        <slot></slot>
        <input type="radio" v-model="isChecked" :name="name" :value="label" hidden/>
    </label>
</template>

<script>
export default {
    props: {
        value: {
            type: [Boolean, String, Number]
        },

        label: {
            type: [Boolean, String, Number]
        },
        name: String
    },

    computed: {
        isChecked: {
            get() {
                return this.value
            },

            set(value) {
                console.log(value)
                this.$emit('input', value)
            }
        }
    },

    methods: {
    }
}
</script>

<style lang="scss" scoped>
label {
    display: inline-flex;
    vertical-align: middle;
    align-items: center;
    cursor: pointer;

    .no-checked, .checked {
        margin-right: 10px;
    }
}
.no-checked {
    display: block;
    height: 18px;
    width: 18px;
    border-radius: 50%;
    border: 1px solid #999999;
}

.checked {
    position: relative;
    display: block;
    height: 18px;
    width: 18px;
    border-radius: 50%;
    border: 1px solid #009688;

    .point {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate3d(-50%, -50%, 0);
        height: 12px;
        width: 12px;
        background: #009688;
        border-radius: 50%;
    }
}

.scale-enter-active, .scale-leave-active {
    transition: all .5s;
}
.scale-enter, .scale-leave-to /* .scale-leave-active below version 2.1.8 */ {
    width: 6px;
    height: 6px;
}
</style>
