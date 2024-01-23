// 导出一个函数
function txtSwitch(curStr, cumStr = '') {
    let strList = '—□■***0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefjhijklmnopqrstuvwxyz';
    if (!curStr || curStr.length == 0) {
        alert('缺少传入参数')
        return
    }
    return curStr.split("").map(
        (v) =>
        (v =
            v + cumStr.length ? cumStr.split("")[parseInt(Math.random() * cumStr.length)] : strList[parseInt(Math.random() * strList.length)])
    )
        .join("")
}

module.exports = txtSwitch;