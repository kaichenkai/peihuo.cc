// 制作采购意向单
<template>
    <div class="edit-wish-order-container">
        <!-- <bread-crumb :titles="['采购单', '采购意向单']"></bread-crumb>
        <i class="one-px-line"></i>
        <h2>{{formatDate(new Date(date.replace(/-/g, '/')), 'yyyy-MM-dd')}}采购意向单</h2> -->
        <table class="table" border="1px">
            <thead>
                <tr class="header">
                    <th class="left">序号</th>
                    <th class="left">商品序列号</th>
                    <th class="left">商品名</th>
                    <th class="left"><sort @sorted="sortPurchaser">采购员</sort></th>
                    <th class="center"><sort @sorted="sortStock">当前库存</sort></th>
                    <th class="left">意向单说明</th>
                    <th class="center">操作</th>
                </tr>
            </thead>
        </table>
        <div ref="outerContainer" class="outer-container">
            <div ref="innerContainer" class="inner-container">
                <div ref="header1" class="h3 left table-header" @click="isShowList[0] = !isShowList[0]">
                    <span class="title">正常订货({{wishOrderData.goods_data[0].length}})</span>
                    <el-button :disabled="!isCanEdit" @click.stop="addGoods(0)" class="add-btn" type="text">+添加商品</el-button>
                    <i class="el-icon"
                    :class="isShowList[0] ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"
                    ></i>
                </div>
                <table class="table" border="1px" v-show="isShowList[0]">
                <draggable element="tbody" :list="wishOrderData.goods_data[0]" :options="{draggable:'.tr-item', group:'people', 'disabled': !isCanEdit}">
                    <tr class="tr-item" v-for="(item, index) in wishOrderData.goods_data[0]" :key="'a' + index">
                        <td class="left">
                            <span>{{index + 1}}</span>
                        </td>
                        <td class="left">
                            <span>{{item.serial_number}}</span>
                        </td>
                        <td class="left">
                            <span :style="[{'color': item.order_goods_name_modified ? '#f66':''}]">{{ item.order_goods_name || item.goods_name || item.name }}</span>
                        </td>
                        <td class="left">
                            <span v-if="item.purchaser_name">{{item.purchaser_name}}</span>
                            <span v-else>-</span>
                        </td>
                        <td class="center">
                            {{item.stock || item.goods_storage}}
                        </td>
                        <td class="left">
                            <!-- <input :disabled="!isCanEdit" v-model="item.remarks" class="input remarks" type="text" /> -->
                            <el-autocomplete
                            :disabled="!isCanEdit"
                            class="input remarks"
                            v-model="item.remarks"
                            :fetch-suggestions="querySearch"
                            placeholder="请输入内容"
                            ></el-autocomplete>
                        </td>
                        <td class="center">
                            <el-popover trigger="hover" placement="left" :visible-arrow="false" :offset="50" >
                                <p><el-button :disabled="!isCanEdit" @click="setPurchare(item)" class="pop-btn" type="text">设置采购员</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="modifyGoodsName(item)" class="pop-btn" type="text">修改品名</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="modifyGoodsStock(item)" class="pop-btn" type="text">修改库存</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="moveTo(0, 1, item)" class="pop-btn" type="text">移到可能缺货</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="moveTo(0, 2, item)" class="pop-btn" type="text">移到暂时无货</el-button></p>
                                <!-- <p><el-button :disabled="!isCanEdit" @click="addTag('新品', item)" class="pop-btn" type="text">设置新品标签</el-button></p> -->
                                <p><el-button :disabled="!isCanEdit" @click="removeFromTheList(0, item)" class="pop-btn" type="text">移出意向单</el-button></p>
                                <div slot="reference" class="name-wrapper">
                                    <el-button type="text">操作</el-button>
                                </div>
                            </el-popover>
                        </td>
                    </tr>
                    </draggable>
                </table>
                <div ref="header2" class="h3 left table-header" @click="isShowList[1] = !isShowList[1]">
                    <span class="title">可能缺货({{wishOrderData.goods_data[1].length}})</span>
                    <el-button :disabled="!isCanEdit" @click.stop="addGoods(1)" class="add-btn" type="text">+添加商品</el-button>
                    <i class="el-icon"
                    :class="isShowList[1] ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"
                    ></i>
                </div>
                <table class="table" border="1px" v-show="isShowList[1]">
                <draggable element="tbody" :list="wishOrderData.goods_data[1]" :options="{draggable:'.tr-item', group:'people', 'disabled': !isCanEdit}">
                    <tr class="tr-item" v-for="(item, index) in wishOrderData.goods_data[1]" :key="'b' + index">
                        <td class="left">
                            <span>{{index + wishOrderData.goods_data[0].length + 1}}</span>
                        </td>
                        <td class="left">
                            <span>{{item.serial_number}}</span>
                        </td>
                        <td class="left">
                            <span :style="[{'color': item.order_goods_name_modified ? '#f66':''}]">{{ item.order_goods_name || item.goods_name || item.name }}</span>
                        </td>
                        <td class="left">
                            <span v-if="item.purchaser_name">{{item.purchaser_name}}</span>
                            <span v-else>-</span>
                        </td>
                        <td class="center">
                            {{item.stock || item.goods_storage}}
                        </td>
                        <td class="left">
                            <!-- <input :disabled="!isCanEdit" v-model="item.remarks" class="input remarks" type="text" /> -->
                            <el-autocomplete
                            :disabled="!isCanEdit"
                            class="input remarks"
                            v-model="item.remarks"
                            :fetch-suggestions="querySearch"
                            placeholder="请输入内容"
                            ></el-autocomplete>
                        </td>
                        <td class="center">
                            <el-popover trigger="hover" placement="left" :visible-arrow="false" :offset="50">
                                <p><el-button :disabled="!isCanEdit" @click="setPurchare(item)" class="pop-btn" type="text">设置采购员</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="modifyGoodsName(item)" class="pop-btn" type="text">修改品名</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="modifyGoodsStock(item)" class="pop-btn" type="text">修改库存</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="moveTo(1, 0, item)" class="pop-btn" type="text">移到正常订货</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="moveTo(1, 2, item)" class="pop-btn" type="text">移到暂时无货</el-button></p>
                                <!-- <p><el-button :disabled="!isCanEdit" @click="addTag('新品', item)" class="pop-btn" type="text">设置新品标签</el-button></p> -->
                                <p><el-button :disabled="!isCanEdit" @click="removeFromTheList(1, item)" class="pop-btn" type="text">移出意向单</el-button></p>
                                <div slot="reference" class="name-wrapper">
                                    <el-button type="text">操作</el-button>
                                </div>
                            </el-popover>
                        </td>
                    </tr>
                    </draggable>
                </table>
                <div ref="header3" class="h3 left table-header" @click="isShowList[2] = !isShowList[2]">
                    <span class="title">暂时无货({{wishOrderData.goods_data[2].length}})</span>
                    <el-button :disabled="!isCanEdit" @click.stop="addGoods(2)" class="add-btn" type="text">+添加商品</el-button>
                    <i class="el-icon"
                    :class="isShowList[2] ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"
                    ></i>
                </div>

                <table class="table" border="1px" v-show="isShowList[2]">
                <draggable element="tbody" :list="wishOrderData.goods_data[2]" :options="{draggable:'.tr-item', group:'people', 'disabled': !isCanEdit}">
                    <tr class="tr-item" v-for="(item, index) in wishOrderData.goods_data[2]" :key="'c' + index">
                        <td class="left">
                            <span>{{index + wishOrderData.goods_data[0].length + wishOrderData.goods_data[1].length + 1}}</span>
                        </td>
                        <td class="left">
                            <span>{{item.serial_number}}</span>
                        </td>
                        <td class="left">
                            <span :style="[{'color': item.order_goods_name_modified ? '#f66':''}]">{{ item.order_goods_name || item.goods_name || item.name }}</span>
                        </td>
                        <td class="left">
                            <span v-if="item.purchaser_name">{{item.purchaser_name}}</span>
                            <span v-else>-</span>
                        </td>
                        <td class="center">
                            {{item.stock || item.goods_storage}}
                        </td>
                        <td class="left">
                            <!-- <input :disabled="!isCanEdit" v-model="item.remarks" class="input remarks" type="text" /> -->
                            <el-autocomplete
                            :disabled="!isCanEdit"
                            class="input remarks"
                            v-model="item.remarks"
                            :fetch-suggestions="querySearch"
                            placeholder="请输入内容"
                            ></el-autocomplete>
                        </td>
                        <td class="center">
                            <el-popover trigger="hover" placement="left" :visible-arrow="false" :offset="50">
                                <p><el-button :disabled="!isCanEdit" @click="setPurchare(item)" class="pop-btn" type="text">设置采购员</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="modifyGoodsName(item)" class="pop-btn" type="text">修改品名</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="modifyGoodsStock(item)" class="pop-btn" type="text">修改库存</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="moveTo(2, 0, item)" class="pop-btn" type="text">移到正常订货</el-button></p>
                                <p><el-button :disabled="!isCanEdit" @click="moveTo(2, 1, item)" class="pop-btn" type="text">移到可能缺货</el-button></p>
                                <!-- <p><el-button :disabled="!isCanEdit" @click="addTag('新品', item)" class="pop-btn" type="text">设置新品标签</el-button></p> -->
                                <p><el-button :disabled="!isCanEdit" @click="removeFromTheList(2, item)" class="pop-btn" type="text">移出意向单</el-button></p>
                                <div slot="reference" class="name-wrapper">
                                    <el-button type="text">操作</el-button>
                                </div>
                            </el-popover>
                        </td>
                    </tr>
                    </draggable>
                </table>
            </div>
        </div>
        <div class="button-group" v-if="!wishOrderId || wishOrderData.status == 1 || isModify">
            <el-upload
            v-if="isUserCanUploadFiles"
            class="import-wishOrder-btn"
            name="files"
            ref="upload"
            :limit="1"
            :show-file-list="false"
            :on-success="uploadSuccess"
            :on-error="uploadError"
            :data="{
                action: 'wish_order_parser',
                wish_date: wishDate
            }"
            action="/api/parser/order">
            <button class="btn share">导入</button>
            </el-upload>
            <!-- <button @click="save" class="btn share">保存草稿</button> -->
            <button class="btn confirm" @click="confirm">制作完成</button>
        </div>
        <div class="button-group" v-else>
            <button class="btn share" @click="exportWishorder">导出</button>
            <button class="btn share" v-if="isShowModifyBtn" @click="modify">修改</button>
            <button class="btn confirm" @click="share">分享</button>
        </div>
        <choose-goods-box ref="chooseGoodsBox"></choose-goods-box>
        <share-box ref="share"></share-box>
        <modify-goods-name ref="modifyGoodsName"></modify-goods-name>
        <set-purchaser ref="setPurchaser"></set-purchaser>
        <modify-stock ref="modifyStock"></modify-stock>
    </div>
</template>

<script>
import BreadCrumb from '@/components/modules_top_tools/bread_crumb'
import ChooseGoodsBox from './components/choose_goods'
import ShareBox from '@/components/share/share'
import ModifyGoodsName from './components/modify_goods_name'
import domain from '@/config/domain'
import StickyListHeaders from 'sticky-list-headers'
import setPurchaser from '../components/set_purchaser'
import Draggable from 'vuedraggable'
import { mapState, mapGetters } from 'vuex'
import ApiUrl from '@/api/ip_config/main'
import remarksManager from '../js/remarks_manager'
import ModifyStock from './components/modi_stock'
import * as utils from '@/utils'
import _ from 'lodash'

export default {
    data() {
        return {
            wishDate: '',
            isShowList: {
                0: true,
                1: true,
                2: true
            },
            removedGoodsList: [],
            wishOrderData: {
                goods_data: { // 大部分的代码逻辑，都是依赖于这个对象的key值进行绑定的
                    0: [], // 正常订货
                    1: [], // 可能缺货
                    2: [] // 暂时无货
                }
            },
            wishOrderId: '',
            isModify: false
        }
    },

    computed: {
        ...mapState(['stationInfo']),

        ...mapGetters(['isUserCanUploadFiles']),
        isCanEdit() {
            return this.isModify || ![2, 3, 4].includes(this.wishOrderData.status)
        },

        isShowModifyBtn() {
            let nowDate = {
                year: new Date().getFullYear(),
                month: new Date().getMonth(),
                day: new Date().getDate()
            }
            let wishOrderCreateDay = (this.wishOrderData.create_time && this.wishOrderData.create_time.split(' ')[0].replace(/-/g, '/')) || new Date()
            let wishOrderCreateDate = {
                year: new Date(wishOrderCreateDay).getFullYear(),
                month: new Date(wishOrderCreateDay).getMonth(),
                day: new Date(wishOrderCreateDay).getDate()
            }
            if (_.isEqual(nowDate, wishOrderCreateDate) && this.wishOrderData.status < 3) {
                return true
            } else {
                return false
            }
        }
    },

    watch: {
        'wishOrderData.goods_data': {
            handler: function() {
                if (this.stickyListHeaders) {
                    this.$nextTick(function() {
                        this.stickyListHeaders.refresh()
                    })
                }
            },
            deep: true
        },

        isShowList: {
            handler: function() {
                if (this.stickyListHeaders) {
                    this.$nextTick(function() {
                        this.stickyListHeaders.refresh()
                    })
                }
            },
            deep: true
        }
    },

    created() {
        // this.date = this.$route.query.date
        // this.wishOrderId = this.$route.query.id
        // if (this.wishOrderId) {
        //     this.getWishOrder()
        // } else {
        //     this.getLastWishOrder()
        // }
        this.getCurrentWishOrder().then(data => {
            // debugger
            this.wishOrderId = data.id
            this.getWishOrder()
        })
        this.remarksList = remarksManager.getRemarksLimit(3)
    },

    mounted() {
        this.stickyListHeaders = new StickyListHeaders({
            outerContainer: this.$refs.outerContainer,
            innerContainer: this.$refs.innerContainer,
            headers: [
                this.$refs.header1,
                this.$refs.header2,
                this.$refs.header3
            ]
        })
    },

    methods: {
        formatDate: utils.formatDate,

        getCurrentWishOrder() {
            return this.$fetch.get({
                url: '/wishorder/current'
            }).then(data => {
                this.wishDate = data.order_data.wish_date
                return data.order_data
            }).catch(e => {
                this.openMessage(0, e || '获取当前意向单失败')
            })
        },

        getLastWishOrder() {
            this.$fetch.get({
                url: '/wishorder/last'
            }).then(data => {
                this.wishOrderData.goods_data = Object.assign({}, this.wishOrderData.goods_data, data.order_data.goods_data)
                this.mergeGoodsStocksToTableData()
                this.cacheServerData()
            }).catch(e => {
                this.openMessage(2, '获取上次意向单失败，请手动填写意向单')
            })
        },

        getWishOrder() {
            this.$fetch.get({
                url: '/wishorder/' + this.wishOrderId
            }).then(data => {
                // 将数据合并，避免出现某种商品状态列表不存在的情况
                data.order_data.goods_data = Object.assign({}, this.wishOrderData.goods_data, data.order_data.goods_data)
                this.wishOrderData = data.order_data
                this.isModify = false
                if (this.wishOrderData.status === 1) {
                    this.mergeGoodsStocksToTableData()
                }
                this.cacheServerData()
            }).catch(e => {
                this.openMessage(0, '获取意向单数据失败,' + e)
            })
        },

        // 缓存数据用于列表排序后还原之前的顺序功能
        cacheServerData() {
            this.cachedServerData = JSON.parse(JSON.stringify(this.wishOrderData))
        },

        // 获取最新的商品库存并且合并到表单数据中
        async mergeGoodsStocksToTableData() {
            let goodsStocks = await this.getGoodsStocks()
            this.wishOrderData.goods_data.length = 3
            this.wishOrderData.goods_data = Array.from(this.wishOrderData.goods_data, data => {
                return data.map(value => {
                    value.stock = goodsStocks[value.goods_id] || value.stock
                    return value
                })
            })
            this.cacheServerData()
        },

        getGoodsStocks() {
            return this.$fetch.get({
                url: '/warehouse/goodsstocks',
                params: {
                    goods_ids: this.transformData().map(value => value.goods_id).join('|')
                }
            }).then(data => {
                return data.stock_data
            }).catch(e => {
                this.openMessage(2, e || '获取商品实时库存失败')
            })
        },

        sortPurchaser(type) {
            switch (type) {
                case 0: this.wishOrderData = JSON.parse(JSON.stringify(this.cachedServerData)); break
                case 1: for (let i in this.wishOrderData.goods_data) {
                    this.wishOrderData.goods_data[i] = this.wishOrderData.goods_data[i].sort((a, b) => {
                        return a.purchaser_name.localeCompare(b.purchaser_name)
                    })
                }; break
                case 2: for (let i in this.wishOrderData.goods_data) {
                    this.wishOrderData.goods_data[i] = this.wishOrderData.goods_data[i].sort((a, b) => {
                        return -a.purchaser_name.localeCompare(b.purchaser_name)
                    })
                }; break
            }
        },

        sortStock(type) {
            // debugger
            switch (type) {
                case 0: this.wishOrderData = JSON.parse(JSON.stringify(this.cachedServerData)); break
                case 1: for (let i in this.wishOrderData.goods_data) {
                    this.wishOrderData.goods_data[i] = this.wishOrderData.goods_data[i].sort((a, b) => {
                        return (a.stock || a.goods_storage) - (b.stock || b.goods_storage)
                    })
                }; break
                case 2: for (let i in this.wishOrderData.goods_data) {
                    this.wishOrderData.goods_data[i] = this.wishOrderData.goods_data[i].sort((a, b) => {
                        return (b.stock || b.goods_storage) - (a.stock || a.goods_storage)
                    })
                }; break
            }
        },

        setPurchare(row) {
            this.$refs.setPurchaser.open({
                data: row,
                wishOrderData: this.wishOrderId,
                callback: (id, name) => {
                    row.purchaser_id = id
                    row.purchaser_name = name
                    this.cacheServerData()
                }
            })
        },

        querySearch(queryString, cb) {
            let arr = this.remarksList
            cb(queryString ? arr.filter(str => str.value.indexOf(queryString) !== -1) : arr)
        },

        /**
         * 添加商品，将选中以及移除的商品都传入商品选择组件用于业务逻辑的判断
         */
        addGoods(type) {
            this.$refs.chooseGoodsBox.open({
                choosedList: this.wishOrderData.goods_data,
                removedList: this.removedGoodsList.reduce((last, next) => {
                    return [...new Set([...last, next.goods_id])] // 去重
                }, []),
                callback: (obj) => {
                    this.$set(this.wishOrderData.goods_data, type, this.distinctAndConcatGoodsList(
                        type,
                        ...obj.goods.map(value => ((value.goods_id = value.id), value) // 将得倒的商品id 转换成 goods_id字段
                        )
                    ))
                }
            })
        },

        // 用于商品列表商品去重
        /**
         * type {Number} 商品的状态 ['正常订货'， ‘可能缺货’， ‘暂时无货’] 对应 this.wishOrderData.goods_data数组下标
         * goods 单个或者多个需要合并的商品
         */
        distinctAndConcatGoodsList(type, ...goods) {
            // 首先删除其他分类中同样的商品
            this.wishOrderData.goods_data.length = 3
            Array.from(this.wishOrderData.goods_data, (item, index) => {
                goods.forEach(goodsItem => {
                    if (this.findIndex(index, goodsItem) !== -1) {
                        item.splice(this.findIndex(index, goodsItem), 1)
                    }
                })
            })

            // 去掉goods之前的obersver
            goods = JSON.parse(JSON.stringify(goods))

            // 其次将商品合并
            return this.wishOrderData.goods_data[type].concat(goods)
        },

        /**
         * nowList {Number} 商品的状态 ['正常订货'， ‘可能缺货’， ‘暂时无货’] 对应 this.wishOrderData.goods_data数组下标
         * targetList 同 nowList
         * item 需要移动的商品
         */
        moveTo(nowList, targetList, item) {
            // debugger
            // console.log(this.wishOrderData.goods_data[nowList]
            // this.removeFromTheList(nowList, item)
            this.$set(this.wishOrderData.goods_data, targetList, this.distinctAndConcatGoodsList(targetList, item))
            // this.wishOrderData.goods_data[targetList] = this.distinctAndConcatGoodsList(targetList, item)
        },

        /**
         * nowList {Number} 商品的状态 ['正常订货'， ‘可能缺货’， ‘暂时无货’] 对应 this.wishOrderData.goods_data数组下标
         * item 需要删除的商品
         */
        removeFromTheList(nowList, item) {
            this.removedGoodsList.push(item)
            this.wishOrderData.goods_data[nowList].splice(
                this.findIndex(nowList, item), 1
            )
        },

        isTheListHasItem(list, item) {
            return list.some(goods => goods.id === item.id)
        },

        /**
         * listNumber {Number} 商品的状态 ['正常订货'， ‘可能缺货’， ‘暂时无货’] 对应 this.wishOrderData.goods_data数组下标
         * item 需要查找的商品
         */
        findIndex(listNumber, item) {
            return this.wishOrderData.goods_data[listNumber].findIndex(goods => goods.goods_id === item.goods_id)
        },

        /**
         * 修改品名
         */
        modifyGoodsName(item) {
            this.$refs.modifyGoodsName.open({
                data: item,
                callback: (orderGoodsName) => {
                    this.$set(item, 'order_goods_name', orderGoodsName)
                    this.$set(item, 'order_goods_name_modified', true)
                }
            })
        },

        /**
        * 修改库存
        */
        modifyGoodsStock(item) {
            this.$refs.modifyStock.open({
                data: item,
                callback: () => {
                    if (this.wishOrderId) {
                        this.getWishOrder()
                    } else {
                        this.getLastWishOrder()
                    }
                }
            })
        },

        /**
         * 暂存意向单
         */
        save() {
            this.updateRemarks()
            this.uploadData(false)
        },

        updateRemarks() {
            this.transformData().forEach(value => {
                remarksManager.setRemark(value.remarks)
            })
        },

        exportWishorder() {
            window.open(ApiUrl + '/export/wishorder/' + this.wishOrderId)
        },

        importWishOrder() {

        },

        share() {
            this.$refs.share.open(domain + `/#/indent?stationId=${this.stationInfo.id}&storeName=${this.stationInfo.name}`)
        },

        uploadSuccess(data) {
            console.log(data)
            if (data.success) {
                this.openMessage(1, '上传成功')
                this.refresh(data.data.wish_order_id)
            } else {
                this.openMessage(0, data.error_text || '上传失败')
            }
            this.$refs.upload.clearFiles()
        },

        uploadError(data) {
            this.openMessage(0, '上传失败')
            this.$refs.upload.clearFiles()
        },

        modify() {
            this.$myWarning({
                message: '若已有分店根据此意向单提交订货请求，此修改可能对已有数据造成影响'
            }).then(() => {
                this.isModify = true
                this.mergeGoodsStocksToTableData()
            }).catch(e => {})
        },

        /**
         * 提交意向单
         */
        confirm() {
            this.updateRemarks()
            this.$myWarning({
                message: '确定已完成？完成之后将不可编辑'
            }).then(data => {
                this.uploadData(true)
            }).catch(e => {

            })
        },

        uploadData(commit) {
            let method = 'post'
            let url = '/wishorder'

            if (this.wishOrderId) {
                method = 'put'
                url = '/wishorder/' + this.wishOrderId
            }
            this.$fetch[method]({
                url: url,
                params: {
                    wish_date: this.date,
                    commit: commit,
                    goods_list: this.transformData()
                }
            }).then(data => {
                this.openMessage(1, '保存成功')
                if (method === 'post') {
                    this.refresh(data.order_id)
                } else {
                    this.getWishOrder()
                }
            }).catch(e => {
                this.openMessage(0, '保存失败,' + e)
            })
        },

        /**
         * 如果是post请求说明这个意向单是第一次提交，所以需要更改当前window url中的数据。
         * 然后再请求意向单数据，以免当前页面刷新，没有意向单id而判断为重新创建意向单
         * */
        refresh(wishOrderId) {
            this.$router.replace({
                path: '/main/purchaseCenter/edit',
                query: {
                    date: this.date,
                    id: wishOrderId
                }
            })
            this.wishOrderId = wishOrderId
            this.getWishOrder()
        },

        /**
         * 将 this.wishOrderData.goods_data 转换为 暂存提交意向单接口需要的一维数组
         */
        transformData() {
            this.wishOrderData.goods_data.length = 3
            // 将 wishOrderData.goods_data 对象转换成 转换成一维数组并且给每个项添加对应的status值
            return Array.from(this.wishOrderData.goods_data, (item, index) =>
                item.map(obj => {
                    let cloneObj = JSON.parse(JSON.stringify(obj))
                    cloneObj.status = index
                    cloneObj.order_goods_name = cloneObj.order_goods_name || cloneObj.goods_name || cloneObj.name
                    delete cloneObj.id
                    return cloneObj
                })
            ).reduce((last, next) => [...last, ...next], [])
        }
    },

    components: {
        BreadCrumb,
        ChooseGoodsBox,
        ShareBox,
        ModifyGoodsName,
        setPurchaser,
        Draggable,
        ModifyStock
    }
}
</script>

<style lang="scss" scoped>
.edit-wish-order-container {
    position: relative;
    height: 100%;
}

.one-px-line {
    margin: 5px 0 25px 0;
}

h2 {
    margin-bottom: 20px;
    font-size: 20px;
    color: #333333;
    letter-spacing: 0;
    text-align: center;
}

.outer-container {
    position: absolute;
    top: 43px;
    left: 0;
    right: 0;
    bottom: 0;

    .inner-container {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        overflow: auto;
    }

    .inner-container::-webkit-scrollbar {display:none}

}

.table-header {
    // margin-top: -1px;
    // margin-bottom: -1px;
    padding-left: 10px;
    background: #fff;
    border: 1px solid #F2F2F2;
    z-index: 1;
    cursor: pointer;

    .title {
        font-size: 16px;
        color: #333333;
        font-weight: bold;
    }
    .add-btn {
        margin-left: 14px;
        color: #009688;
    }

    .el-icon {
        margin-right: 20px;
        float: right;
        line-height: 40px;
    }
}

@mixin tableColumnWidth {

        &:nth-of-type(1) {
            min-width: 55px;
            max-width: 55px;
            width: 60px;
        }

        &:nth-of-type(2) {
            min-width: 110px;
            width: 100px;
        }

        &:nth-of-type(3) {
            min-width: 310px;
        }

        &:nth-of-type(4) {
            width: 120px;
        }

        &:nth-of-type(5) {
            min-width: 100px;
            max-width: 100px;
            width: 100px;
        }

        &:nth-of-type(6) {
            min-width: 203px;
        }

        &:nth-of-type(7) {
            max-width: 100px;
            min-width: 100px;
            width: 100px;
        }

}

table {
    table-layout:fixed;
    width: 100%;
    min-width: 800px;

    .center {
        text-align: center;
    }

    .left {
        padding-left: 10px;
        padding-right: 10px;
    }

    .tr-item {
        &:hover {
            background: #f5f7fa;
        }
    }

    /deep/ .el-input.is-disabled .el-input__inner {
        background: transparent;
    }

    td {
        position: relative;
        border: 1px solid #F2F2F2;
        font-size: 14px;
        color: #333333;
        @include tableColumnWidth;
    }

    tr {
        height: 40px;
        line-height: 40px;
        text-align: left;
    }

    .header {
        background: #F2F2F2;
        border: 1px solid #F2F2F2;
        user-select: none;

        th {
            font-size: 14px;
            color: #333333;
            letter-spacing: 0;
            @include tableColumnWidth;
        }
    }

    td {
        font-size: 14px;
        color: #333333;
        letter-spacing: 0;
        // background: #fff;

        @include tableColumnWidth;
    }

    td[colspan='5'] {
        background: #FCFCFC;
    }

    .name-wrapper {
        display: inline-block;
    }
}

.pop-btn {
    color: #666 !important;

    &:hover {
        color: #333 !important;
    }

    &:active {
        color: #333 !important;
    }
}

.button-group {
    position: absolute;
    top: -58px;
    right: 25px;
    // margin-top: 208px;
    text-align: center;
    height: 67px;
    line-height: 67px;
}

.btn {
    box-sizing: border-box;
    // padding: 5px 18px;
    width: 80px;
    height: 30px;
    line-height: 28px;
    font-size: 14px;
    border-radius: 2px;
    outline: none;
    border: none;
    user-select: none;

    &:active {
        transform: scale(.9);
    }
}

.import-wishOrder-btn {
    display: inline-block;
}

.confirm {
    margin-left: 10px;
    background: #009688;
    color: #fff;
    border: 1px #009688 solid;
}

.share {
    margin-left: 10px;
    color: #009688;
    border: 1px solid #009688;
    border-radius: 2px;
}

// .tag {
//     padding: 2px 8px;
//     // display: inline-block;
//     border-radius: 2px;
//     font-size: 12px;
//     color: #F88B30;
//     border: 1px #F88B30 solid;
// }

.remarks {
    // padding: 0 10px;
    width: 100%;
    /* height: 25px; */
    font-size: 14px;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    border: none;

    /deep/ .el-input__inner {
        border: none;
    }
}
</style>
