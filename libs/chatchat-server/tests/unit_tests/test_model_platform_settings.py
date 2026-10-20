from chatchat.settings import ApiModelSettings, PlatformConfig


def test_minimax_platform_endpoints():
    platforms = {
        platform.platform_name: platform
        for platform in ApiModelSettings.model_fields["MODEL_PLATFORMS"].default
    }

    expected_endpoints = {
        "minimax-global": (
            "https://api.minimax.io/v1",
            "https://api.minimax.io/anthropic",
        ),
        "minimax-cn": (
            "https://api.minimaxi.com/v1",
            "https://api.minimaxi.com/anthropic",
        ),
    }

    for platform_name, endpoints in expected_endpoints.items():
        platform = platforms[platform_name]
        assert platform.platform_type == "minimax"
        assert platform.api_base_url == endpoints[0]
        assert platform.anthropic_api_base_url == endpoints[1]
        assert platform.llm_models == ["MiniMax-M3.1-Flash", "MiniMax-M3"]


def test_saved_platform_configuration_round_trip():
    saved = PlatformConfig(
        platform_name="minimax-saved",
        platform_type="minimax",
        llm_models=["MiniMax-M2.7", "my-custom-model"],
        embed_models=["saved-embedding"],
        text2speech_models=["saved-speech"],
        image2text_models=["saved-vision"],
    )
    restored = PlatformConfig.model_validate_json(saved.model_dump_json())
    assert restored.model_dump() == saved.model_dump()
