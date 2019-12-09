<template>
    <div class="station-container">
        <h1>{{stationInfo.name}}<i :style="[{'transform': isFocus ? 'rotate(180deg)' : ''}]" class="el-icon el-icon-caret-bottom"></i></h1>
        <input @focus="isFocus = true" @blur="isFocus = false" type="text">
        <transition name="slide-fade">
            <ul v-show="isFocus">
                <li v-for="station in stationList" :key="station.id" @click="chooseStation(station)">{{station.name}}</li>
            </ul>
        </transition>
    </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
    data() {
        return {
            isFocus: false,
            stationList: []
        }
    },
    created() {
        this.getStations()
    },
    methods: {
        chooseStation(stationInfo) {
            if (stationInfo.id === this.stationInfo.id) {
                return
            }
            this.$fetch.put({
                url: '/currentstation',
                params: {
                    station_id: stationInfo.id
                }
            }).then(data => {
                window.location.reload()
            }).catch(e => {
                this.openMessage(0, e)
            })
        },

        getStations() {
            return this.$fetch.get({
                url: '/stations'
            }).then(data => {
                this.stationList = data.station_list
            }).catch(e => {
                this.openMessage(0, e || '获取中转站列表失败')
            })
        }
    },

    computed: {
        ...mapState(['stationInfo'])
    }
}
</script>

<style lang="scss" scoped>
.station-container {
    position: relative;
    display: inline-block;
    cursor: pointer;

    input {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
    }

    i {
        transition: transform .5s;
    }

    ul {
        position: absolute;
        left: 50%;
        margin-left: -120px;
        width: 240px;
        background: #FFFFFF;
        box-shadow: 0 0 10px 0 rgba(0,0,0,0.15);
        z-index: 100;

        li {
            margin-top: 5px;
            margin-bottom: 5px;
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
            line-height: 30px;

            &:hover {
                background: #F5F7FA;
            }
        }

        &:before {
            content: '';
            position: absolute;
            top: -5px;
            left: 50%;
            width: 10px;
            height: 10px;
            transform: translateX(-50%) rotate(45deg);
            background: #fff;
        }
    }

    .slide-fade-enter-active {
        transition: all .5s ease;
    }
    .slide-fade-leave-active {
        transition: all .5s ease;
    }
    .slide-fade-enter, .slide-fade-leave-to
    /* .slide-fade-leave-active for below version 2.1.8 */ {
        transform: translateY(-20px);
        opacity: 0;
    }
}
</style>
