// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const Uglifyjs = require('uglifyjs-webpack-plugin')
module.exports = {
    baseUrl: './',
    configureWebpack: function(config) {
        if (process.env.NODE_ENV === 'production') {
            config.optimization = config.optimization || {}
            config.optimization.minimizer = config.optimization.minimizer || []
            config.optimization.minimizer.push(new Uglifyjs({
                uglifyOptions: {
                    compress: {
                        drop_debugger: true,
                        drop_console: true
                    }
                }
            }))
        }
    },

    chainWebpack: config => {
        config.module
            .rule('js')
            .exclude.add(/\.min\.js$/)
    }
}
