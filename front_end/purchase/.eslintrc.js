module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/essential',
    '@vue/standard'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'quotes': 0,
    'indent': ['error', 4],
    'space-before-function-paren': ["error", {
        "anonymous": "never",
        "named": "never",
        "asyncArrow": "never"
    }]
  },
  parserOptions: {
    parser: 'babel-eslint'
  }
}
