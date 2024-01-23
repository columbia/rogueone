from fast.manager.registry import *
def test_fetch_dependencies():
   result = fetch_version_dependencies("semver", "5.1.0")
   assert result

#def test_fetch_tarball_url():
#   result = fetch_tarball_url("semver", "5.1.0")
#   assert result

def test_non_present_package():
    result = fetch_version_dependencies("rpc-websocket", "0.6.5")
    assert result