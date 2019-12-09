export const formatDate = function (v, format) {
    if (!v) return ""
    var d = v
    if (typeof v === 'string') {
        if (v.indexOf("/Date(") > -1) {
            d = new Date(parseInt(v.replace("/Date(", "").replace(")/", ""), 10))
        } else {
            d = new Date(Date.parse(v.replace(/-/g, "/").replace("T", " ").split(".")[0])) // .split(".")[0] 用来处理出现毫秒的情况，截取掉.xxx，否则会出错
        }
    }

    var o = {
        "M+": d.getMonth() + 1, // month
        "d+": d.getDate(), // day
        "h+": d.getHours(), // hour
        "m+": d.getMinutes(), // minute
        "s+": d.getSeconds(), // second
        "q+": Math.floor((d.getMonth() + 3) / 3), // quarter
        "S": d.getMilliseconds() // millisecond
    }

    if (/(y+)/.test(format)) {
        format = format.replace(RegExp.$1, (d.getFullYear() + "").substr(4 - RegExp.$1.length))
    }

    for (var k in o) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length === 1 ? o[k] : ("00" + o[k]).substr(("" + o[k]).length))
        }
    }
    return format
}

// 判断浏览器
export function isPC() {
    if (/Android|webOS|iPhone|iPad|BlackBerry/i.test(navigator.userAgent)) {
        return false
    } else {
        return true
    }
}

export function isWX() {
    var ua = navigator.userAgent.toLowerCase()
    var isWeixin = ua.indexOf('micromessenger') !== -1
    if (isWeixin) {
        return true
    } else {
        return false
    }
}

// 提取url参数

export function getQueryString(href, key) {
    var reg = new RegExp('[?&]' + key + '=([^&]*)', 'g')
    var match = (href || window.location.search).match(reg)
    if (!match) return
    if (match.length === 1) return decodeURIComponent(match[0].replace(reg, '$1'))
    match = match.map(function(item) {
        return decodeURIComponent(item.replace(reg, '$1'))
    })
    return match
}

export function replaceQueryString(paramName, replaceWith) {
    let oUrl = window.location.href.toString()
    let re = new RegExp('(' + 'code' + '=)([^&]*)', 'gi')
    let nUrl = oUrl.replace(re, paramName + '=' + replaceWith)
    return nUrl
}

// 获得对象数组中出现次数最多的前n项

export function getTheMostNitemInArray(arr, compareProject, n) { // compareProject为根据什么来计算出现次数
    arr = JSON.parse(JSON.stringify(arr))
    var count = 1
    var yuansu = [] // 存放数组array的不重复的元素
    var sum = [] // 存放数组array中每个不同元素的出现的次数
    for (var i = 0; i < arr.length; i++) {
        for (var j = i + 1; j < arr.length; j++) {
            if (arr[i][compareProject] === arr[j][compareProject]) {
                count++ // 用来计算与当前这个元素相同的个数
                arr.splice(j, 1) // 每找到一个相同的元素，就要把它移除掉，
                j--
            }
        }
        yuansu[i] = arr[i] // 将当前的元素存入到yuansu数组中
        sum[i] = count // 并且将有多少个当前这样的元素的个数存入sum数组中
        count = 1 // 再将count重新赋值，进入下一个元素的判断
    }
    var newArr = []
    for (var m = 0; m < yuansu.length; m++) { // 将元素和对应的出现次数组成一个对象放入数组
        var obj = {}
        obj.name = yuansu[m]
        obj.value = sum[m]
        newArr.push(obj)
    }
    newArr.sort(function (x, y) { // 根据出现次数进行排序
        return y.value - x.value
    })
    var nMostSearch = [] // 出现次数最多的n个项目
    newArr.slice(0, n).forEach(function (item) {
        nMostSearch.push(item.name)
    })
    return nMostSearch
}

export function differenceSet(arr1, arr2, key) { // 求两个对象数组的差集(arr1 - arr2)
    let arr = []
    arr1.forEach(element => {
        let bol = false
        arr2.forEach(ele => {
            if (element[key] === ele[key]) {
                bol = true
            }
        })
        if (!bol) {
            arr.push(element)
            bol = false
        }
    })
    return arr
}

export function dateFormat(time, format) {
    var t = new Date(time)
    var tf = function (i) { return (i < 10 ? '0' : '') + i }
    return format.replace(/yyyy|MM|dd|HH|mm|ss/g, function (a) {
        switch (a) {
            case 'yyyy':
                return tf(t.getFullYear())
            case 'MM':
                return tf(t.getMonth() + 1)
            case 'mm':
                return tf(t.getMinutes())
            case 'dd':
                return tf(t.getDate())
            case 'HH':
                return tf(t.getHours())
            case 'ss':
                return tf(t.getSeconds())
        }
    })
}
