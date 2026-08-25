from backend.agent.tools.search_assets_tool import _asset_query


def test_spoken_ordinal_becomes_digits() -> None:
    assert _asset_query("17-я") == "17"
    assert _asset_query("17") == "17"
    assert _asset_query("ХУ-17") == "ХУ-17"
    assert _asset_query(None) is None
