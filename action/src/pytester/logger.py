from loggerman import logger, style
import mdit
from mdit.target.rich import HeadingConfig, PanelConfig, StyleConfig, InlineHeadingConfig, RuleConfig


def initialize_logger(title_number: int | list[int]):
    logger.initialize(
        realtime_levels=list(range(1, 7)),
        github=True,
        github_debug=True,
        title_number=title_number,
        level_style_debug=style.log_level(
            color="muted",
            icon="🔘",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(200, 255, 255), bold=True),
            ),
        ),
        level_style_success=style.log_level(
            color="success",
            icon="✅",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(0, 250, 0), bold=True),
            ),
        ),
        level_style_info=style.log_level(
            color="info",
            icon="ℹ️",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(0, 200, 255), bold=True),
            ),
        ),
        level_style_notice=style.log_level(
            color="warning",
            icon="⚠️",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(255, 230, 0), bold=True),
            ),
        ),
        level_style_warning=style.log_level(
            color="warning",
            icon="🚨",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(255, 185, 0), bold=True),
            ),
        ),
        level_style_error=style.log_level(
            color="danger",
            icon="🚫",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(255, 100, 50), bold=True),
            ),
        ),
        level_style_critical=style.log_level(
            color="danger",
            opened=True,
            icon="⛔",
            rich_config=PanelConfig(
                title_style=StyleConfig(color=(255, 30, 30), bold=True),
            ),
        ),
        target_configs_rich={
            "console": mdit.target.console(
                heading=(
                    HeadingConfig(
                        inline=InlineHeadingConfig(
                            style=StyleConfig(color=(255, 200, 255), bold=True),
                            rule=RuleConfig(style=StyleConfig(color=(250, 250, 230))),
                        )
                    ),
                    HeadingConfig(
                        inline=InlineHeadingConfig(
                            style=StyleConfig(color=(235, 160, 255), bold=True),
                            rule=RuleConfig(style=StyleConfig(color=(220, 220, 200))),
                        )
                    ),
                    HeadingConfig(
                        inline=InlineHeadingConfig(
                            style=StyleConfig(color=(215, 120, 255), bold=True),
                            rule=RuleConfig(style=StyleConfig(color=(190, 190, 170))),
                        )
                    ),
                    HeadingConfig(
                        inline=InlineHeadingConfig(
                            style=StyleConfig(color=(195, 80, 255), bold=True),
                            rule=RuleConfig(style=StyleConfig(color=(160, 160, 140))),
                        )
                    ),
                    HeadingConfig(
                        inline=InlineHeadingConfig(
                            style=StyleConfig(color=(175, 40, 255), bold=True),
                            rule=RuleConfig(style=StyleConfig(color=(130, 130, 110))),
                        )
                    ),
                    HeadingConfig(
                        inline=InlineHeadingConfig(
                            style=StyleConfig(color=(155, 0, 255), bold=True),
                            rule=RuleConfig(style=StyleConfig(color=(100, 100, 80))),
                        )
                    ),
                )
            )
        }
    )
