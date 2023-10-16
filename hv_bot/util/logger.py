import logging

import coloredlogs


def init_logger() -> None:
    # logging placeholders:
    # https://stackoverflow.com/questions/33715344/python-logging-vs-performance

    # coloredlogs API docs:
    # https://coloredlogs.readthedocs.io/en/latest/api.html

    COLOREDLOGS_LOG_FORMAT = '%(asctime)s.%(msecs)03d %(name)s[%(process)d] %(levelname)s %(message)s'

    COLOREDLOGS_FIELD_STYLES = {'asctime': {'color': 245, 'faint': True},
                                'hostname': {'color': 245, 'faint': True},
                                'levelname': {'bold': True, 'color': 250, 'bright': True},
                                'name': {'color': 245, 'faint': True},
                                'programname': {'color': 245, 'faint': True},
                                'username': {'color': 245, 'faint': True}}

    # can control various color and style, refer this link:
    # https://coloredlogs.readthedocs.io/en/latest/api.html#available-text-styles-and-colors
    COLOREDLOGS_LEVEL_STYLES = {'spam': {'color': 245, 'faint': True},
                                'debug': {'color': 245, 'faint': True},
                                'verbose': {'color': 250, 'normal': True},
                                'info': {'color': 250, 'normal': True},
                                'notice': {'color': 'yellow', 'bright': True},
                                'warning': {'color': 'yellow', 'bright': True},
                                'success': {'bold': True, 'color': 'green', 'bright': True},
                                'error': {'bold': True, 'color': 'red', 'bright': True},
                                'critical': {'bold': True, 'color': 'red', 'bright': True}}

    coloredlogs.install(level="DEBUG", fmt=COLOREDLOGS_LOG_FORMAT,
                        level_styles=COLOREDLOGS_LEVEL_STYLES, field_styles=COLOREDLOGS_FIELD_STYLES)

    # ignore logging level lower than WARNING in imported modules
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)

    # ignore logging level lower than INFO in my program
    logging.root.setLevel(logging.INFO)


if __name__ == '__main__':
    init_logger()
    # To observer the style of DEBUG level
    coloredlogs.set_level("DEBUG")

    logging.debug("test_logger debug")
    logging.info("test_logger info")
    logging.warning("test_logger warning")
    logging.error("test_logger error")
    logging.critical("test_logger critical")
