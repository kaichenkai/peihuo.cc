let domain = ''

if (process.env.VUE_APP_RUN_ENV === 'DevelopmentServer') {
    domain = 'http://peihuo.senguo.cc/app'
} else if (process.env.VUE_APP_RUN_ENV === 'ProductionServer') {
    domain = 'https://ph.senguo.cc/admin'
}

export default domain
