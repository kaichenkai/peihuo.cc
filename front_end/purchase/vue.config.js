const path = require('path')

console.log(__dirname)
module.exports = {
    baseUrl: './',
    assetsDir: './static/mobile_purchase',
    // path: './static',
    pluginOptions: {
        'style-resources-loader': {
            preProcessor: 'scss',
            patterns: [
                path.resolve(__dirname, './src/assets/style/variable.scss'),
                path.resolve(__dirname, './src/assets/style/mixins.scss'),
                path.resolve(__dirname, './src/assets/style/transitions.scss')
            ]
        }
    }
}
