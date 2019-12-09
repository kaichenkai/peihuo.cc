export default {
    isUserCanUploadFiles(state) { // 判断用户是否可以上传文件
        return state.canUploadFilesUsers.includes(state.userInfo.id)
    },

    canIUse: state => (role, id) => state.userPrivilege.isSuperAdmin || state.userPrivilege[role].includes(id)
}
