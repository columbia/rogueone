from fast.manager.package_changes import extract_name_and_versions, create_registry_url


def test_extract_name_and_version():
    strings = [
        ("zcomponent@google-analytics_0.0.1-->0.0.2", ("zcomponent@google-analytics", "0.0.1", "0.0.2")),
        ("zce-demo-pages_0.1.0-->0.2.0", ("zce-demo-pages", "0.1.0", "0.2.0")),
        ("zazuko@vocabularies_1.0.0-rc.0-->1.0.0-rc.1", ("zazuko@vocabularies", "1.0.0-rc.0", "1.0.0-rc.1")),
        ("yne@present_0.0.1-SNAPSHOT.1-->0.0.1-SNAPSHOT.2", ("yne@present", "0.0.1-SNAPSHOT.1", "0.0.1-SNAPSHOT.2")),
        ("wy_utils_test_1.1.0-->1.1.1", ("wy_utils_test", "1.1.0", "1.1.1")),
        ("exploratory-programming@epp_0.0.2-->0.0.3", ("exploratory-programming@epp", "0.0.2", "0.0.3"))
    ]
    for t in strings:
        assert extract_name_and_versions(t[0]) == t[1]


def test_create_registry_url_general():
    strings = [
        ("zcomponent@google-analytics", "@zcomponent/google-analytics"),
        ("zce-demo-pages", "zce-demo-pages"),
        ("zazuko@vocabularies", "@zazuko/vocabularies"),
        ("yne@present", "@yne/present"),
        ("wy_utils_test", "wy_utils_test"),
        ("exploratory-programming@epp", "@exploratory-programming/epp")
    ]
    for t in strings:
        assert create_registry_url(t[0]) == t[1]


def test_create_registry_url_with_ats():
    strings = [
        ("windmillcode@angular-wml-button-zero", "@windmillcode/angular-wml-button-zero"),
        ("xiaopx@px-vivo-loder-with-html-img", "@xiaopx/px-vivo-loder-with-html-img"),
        ("v.latyshev@eslint-config", "@v.latyshev/eslint-config"),
        ("vercel@postgres", "@vercel/postgres"),
        ("web3-react-x@coinbase-wallet", "@web3-react-x/coinbase-wallet")
    ]
    for t in strings:
        assert create_registry_url(t[0]) == t[1]


def test_extract_name_then_create_registry_url_general():
    strings = [
        ("zcomponent@google-analytics_0.0.1-->0.0.2", "@zcomponent/google-analytics"),
        ("zce-demo-pages_0.1.0-->0.2.0", "zce-demo-pages"),
        ("zazuko@vocabularies_1.0.0-rc.0-->1.0.0-rc.1", "@zazuko/vocabularies"),
        ("yne@present_0.0.1-SNAPSHOT.1-->0.0.1-SNAPSHOT.2", "@yne/present"),
        ("wy_utils_test_1.1.0-->1.1.1", "wy_utils_test"),
        ("exploratory-programming@epp_0.0.2-->0.0.3", "@exploratory-programming/epp")
    ]
    for t in strings:
        package_name, _, _ = extract_name_and_versions(t[0])
        url_name = create_registry_url(package_name)
        assert url_name == t[1]
