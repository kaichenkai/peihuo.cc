export const payTypes = [
    {
        name: '现金',
        id: 0
    }, {
        name: '银行卡',
        id: 1
    },
    {
        name: '微信',
        id: 2
    },
    {
        name: '支付宝',
        id: 3
    },
    {
        name: '赊账',
        id: 4
    },
    {
        name: '其它',
        id: 5
    }
]

export function filterPayTypes(id) {
    const payType = payTypes.filter(value => value.id === id)
    if (payType.length > 0) {
        return payType[0].name
    } else {
        return '不存在的付款方式'
    }
}
