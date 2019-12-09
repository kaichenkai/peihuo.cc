<template>
    <el-dialog
        :title="mode=='create' ? '创建商品':'修改商品'"
        :visible.sync="dialogVisible"
        width="445px">
        <el-form label-position="right" label-width="77px" ref="form" size="small">
            <el-form-item label="商品名称：" class="required">
                <el-input v-selectTextOnFocus v-model="form.name" placeholder="" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="商品编码：">
                <el-input v-selectTextOnFocus v-model="form.code" placeholder="" @keyup.enter.native="confirm"></el-input>
            </el-form-item>
            <el-form-item label="整件体积：" style="margin-bottom:0">
                体积 {{volume_ || volume}} 立方米
            </el-form-item>
            <el-form-item label="" style="height:50px">
                长<input class="el-input__inner" type="number" v-selectTextOnFocus v-model="long" placeholder="输入整数" @keyup.enter.native="confirm" @input="longChange" style="width:70px;">cm
                宽<input class="el-input__inner" type="number" v-selectTextOnFocus v-model="width" placeholder="输入整数" @keyup.enter.native="confirm" @input="widthChange" style="width:70px;">cm
                高<input class="el-input__inner" type="number" v-selectTextOnFocus v-model="height" placeholder="输入整数" @keyup.enter.native="confirm" @input="heightChange" style="width:70px;">cm
            </el-form-item>
            <el-form-item label="整件重量：">
                <input class="el-input__inner" type="number" v-selectTextOnFocus v-model="weight" @input="weightChange" placeholder="输入两位之内小数" @keyup.enter.native="confirm" style="width:150px;"> kg
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <button class="btn confirm" @click="confirm">确认</button>
            <button class="btn cancel" @click="cancel">取消</button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    data() {
        return {
            dialogVisible: false,
            mode: 'create',
            form: {
                name: '',
                code: ''
            },
            long: '',
            width: '',
            height: '',
            weight: '',
            volume_: ''
        }
    },

    computed: {
        volume() {
            let _volume = Number((this.long * this.width * this.height / 1000000).toFixed(6) || 0) || 0
            return Number.isInteger(_volume) ? parseInt(_volume) : _volume
        }
    },

    updated() {
        if (this.mode === 'update') {
            this.$refs['form'].validate((valid) => {})
        }
    },

    methods: {
        longChange() {
            this.volume_ = ''
            this.long = parseInt(this.long)
        },
        widthChange() {
            this.volume_ = ''
            this.width = parseInt(this.width)
        },
        heightChange() {
            this.volume_ = ''
            this.height = parseInt(this.height)
        },
        weightChange() {
            if (this.weight !== '') {
                let weight = Number(Number(this.weight).toFixed(2))
                this.weight = Number.isInteger(weight) ? parseInt(weight) : weight
            }
        },
        open(obj) {
            this.dialogVisible = true
            this.mode = obj.mode
            this.cacheData = obj
            this.callback = obj.callback || function() {}
            if (this.mode === 'update') {
                this.getGoodsData()
            } else {
                this.form = {
                    name: '',
                    code: ''
                }
                this.long = ''
                this.width = ''
                this.height = ''
                this.weight = ''
                this.volume_ = ''
            }
        },

        getGoodsData() {
            this.$fetch.get({
                url: '/station/goods/' + this.cacheData.data.id
            }).then(data => {
                this.form = data.goods_dict
                this.volume_ = data.goods_dict.standards_volume
                this.weight = data.goods_dict.standards_weight || ''
                this.long = data.goods_dict.length || ''
                this.width = data.goods_dict.width || ''
                this.height = data.goods_dict.height || ''
            }).catch(e => {
                console.log(e)
                this.openMessage(0, '获取商品信息失败,' + e)
            })
        },

        confirm() {
            this.validator().then(() => {
                if (this.mode === 'create') {
                    this.createGoods()
                } else if (this.mode === 'update') {
                    this.updateGoods()
                }
            }).catch(e => {
                this.openMessage(2, e)
            })
        },

        createGoods() {
            this.form.firm_id = 1
            this.$fetch.post({
                url: '/station/goods',
                params: {
                    ...this.form,
                    // standards_volume: this.volume_ || this.volume,
                    standards_weight: this.weight,
                    length: this.long,
                    width: this.width,
                    height: this.height
                }
            }).then(data => {
                this.dialogVisible = false
                this.openMessage(1, '创建商品信息成功')
                this.callback()
            }).catch(e => {
                this.openMessage(0, '创建商品信息失败,' + e)
                console.log(e)
            })
        },

        updateGoods() {
            this.form.firm_id = 1
            this.$fetch.put({
                url: '/station/goods/' + this.cacheData.data.id,
                params: {
                    ...this.form,
                    action: 'edit_goodsinfo',
                    // standards_volume: this.volume_ || this.volume,
                    standards_weight: this.weight,
                    length: this.long,
                    width: this.width,
                    height: this.height
                }
            }).then(data => {
                this.dialogVisible = false
                this.callback()
                this.openMessage(1, '更新商品信息成功')
            }).catch(e => {
                this.openMessage(0, '更新商品信息失败,' + e)
                console.log(e)
            })
        },

        validator() {
            let validator = new this.$Validator()
            validator.add('isEmpty', this.form.name, '请输入商品名')
            // validator.add('isEmpty', this.form.code, '请输入商品编码')

            return validator.start()
        },

        cancel() {
            this.$refs['form'].validate((valid) => {})
            this.dialogVisible = false
        }
    }
}
</script>

<style lang="scss" scoped>
    /deep/ .el-form .el-form-item__label{
        line-height: 31px;
        font-size: 14px;
        color: #333333;
    }
    /deep/ .el-form-item--small.el-form-item{
        margin-bottom: 0px;
    }
    /deep/ .el-input__inner{
        height: 32px;
        padding: 0 8px;
    }
</style>
