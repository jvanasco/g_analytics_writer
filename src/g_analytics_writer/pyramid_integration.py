from . import AnalyticsWriter
from . import AnalyticsMode
from . import GtagDimensionsStrategy

from pyramid.settings import asbool

# logging
import logging

log = logging.getLogger(__name__)


# ==============================================================================


def includeme(config):
    """the pyramid includeme command
    including this will automatically setup the AnalyticsWriter object for every request
    """

    config_settings = config.get_settings()
    account_id = config_settings.get("g_analytics_writer.account_id")
    mode = int(config_settings.get("g_analytics_writer.mode", 0))

    # stuff them all in here
    kwargs = {}
    if mode not in AnalyticsMode._valid_modes:
        raise ValueError(
            "Invalid AnalyticsMode for AnalyticsWriter: g_analytics_writer.mode"
        )
    kwargs["mode"] = mode

    use_comments = config_settings.get("g_analytics_writer.use_comments")
    if use_comments is not None:
        kwargs["use_comments"] = asbool(use_comments)

    single_push = None
    if mode in AnalyticsMode._supports_single_push:
        single_push = config_settings.get("g_analytics_writer.single_push")
        if single_push is not None:
            kwargs["single_push"] = asbool(single_push)

    force_ssl = config_settings.get("g_analytics_writer.force_ssl")
    if force_ssl is not None:
        kwargs["force_ssl"] = asbool(force_ssl)

    global_custom_data = config_settings.get("g_analytics_writer.global_custom_data")
    if global_custom_data is not None:
        kwargs["global_custom_data"] = asbool(global_custom_data)

    gtag_dimensions_strategy = config_settings.get(
        "g_analytics_writer.gtag_dimensions_strategy"
    )
    if gtag_dimensions_strategy is not None:
        gtag_dimensions_strategy = int(gtag_dimensions_strategy)
        if gtag_dimensions_strategy not in GtagDimensionsStrategy._valid:
            raise ValueError(
                "Invalid GtagDimensionsStrategy for AnalyticsWriter: g_analytics_writer.gtag_dimensions_strategy"
            )
        kwargs["gtag_dimensions_strategy"] = gtag_dimensions_strategy

    """
    :amp_clientid_integration 
    integrates the client_id of amp and non-amp pages
    see https://support.google.com/analytics/answer/7486764
    """
    amp_clientid_integration = config_settings.get(
        "g_analytics_writer.amp_clientid_integration"
    )
    if amp_clientid_integration is not None:
        kwargs["amp_clientid_integration"] = asbool(amp_clientid_integration)

    json_dumps_callable = config_settings.get("g_analytics_writer.json_dumps_callable")
    if json_dumps_callable:
        # if this isn't a callable function, then use pyramid's DottedNameResolver
        if not callable(json_dumps_callable):
            json_dumps_callable = config.name_resolver.resolve(json_dumps_callable)
        kwargs["json_dumps_callable"] = json_dumps_callable

    log.debug("parsed setup for g_analytics_writer: %s" % kwargs)

    def _new_AnalyticsWriter(request):
        """simply creates a new hub"""
        return AnalyticsWriter(account_id, **kwargs)

    config.add_request_method(_new_AnalyticsWriter, "g_analytics_writer", reify=True)
