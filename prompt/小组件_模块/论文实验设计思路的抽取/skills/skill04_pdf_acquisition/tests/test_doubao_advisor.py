from advisor.doubao_client import DoubaoPdfAdvisor


def test_advisor_requires_key():
    try:
        DoubaoPdfAdvisor("")
        assert False
    except ValueError:
        pass


def test_allow_list_filtering_rule():
    allowed = ["openalex_download", "doi_download"]
    proposed = ["invented_source", "doi_download"]
    safe = [value for value in proposed if value in allowed]
    ordered = safe + [value for value in allowed if value not in safe]
    assert ordered == ["doi_download", "openalex_download"]
