import logging




def setup_logging() -> None:
  """Настройка глобального логирования для всего приложения."""
  log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"

  logging.basicConfig(
      level=logging.INFO,
      format=log_format,
      stream=sys.stdout,
      force=True

    )


# разобраться с конфигом
# залогировать слой сервиса
#
