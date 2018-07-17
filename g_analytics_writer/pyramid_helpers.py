from . import AnalyticsWriter
from . import AnalyticsMode


# ==============================================================================


def includeme(config):
    """the pyramid includeme command
    including this will automatically setup the AnalyticsWriter object for every request
    """

    config_settings = config.get_settings()
    account_id = config_settings.get('g_analytics_writer.account_id')
    mode = int(config_settings.get('g_analytics_writer.mode', 0))
    if mode not in AnalyticsMode._valid_modes:
        raise ValueError("Invalid AnalyticsMode for AnalyticsWriter")
    single_push = None
    if mode in AnalyticsMode._supports_single_push:
        single_push = bool(int(config_settings.get('g_analytics_writer.single_push', 0)))
    use_comments = bool(int(config_settings.get('g_analytics_writer.use_comments', 0)))

    def _new_AnalyticsWriter(request):
        """simply creates a new hub"""
        return AnalyticsWriter(account_id,
                               mode=mode,
                               single_push=single_push,
                               use_comments=use_comments,
                               )

    config.add_request_method(_new_AnalyticsWriter,
                              'g_analytics_writer',
                              reify=True,
                              )
