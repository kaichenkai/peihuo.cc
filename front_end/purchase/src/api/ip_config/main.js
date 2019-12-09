let baseUrl = ''

if (process.env.NODE_ENV === 'development') {
    baseUrl = 'http://peihuo.senguo.cc/api'
} else if (process.env.NODE_ENV === 'production') {
    baseUrl = 'https://i.senguo.cc'
}

export default baseUrl
