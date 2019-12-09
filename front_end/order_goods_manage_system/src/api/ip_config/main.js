import DEV_URL from '@/dev_url.js'
let baseUrl = null

if (process.env.NODE_ENV === 'development') {
    baseUrl = DEV_URL
} else if (process.env.NODE_ENV === 'production') {
    baseUrl = 'https://ph.senguo.cc/api'
}

export default baseUrl
