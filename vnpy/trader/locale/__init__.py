import gettext
from pathlib import Path


localedir: Path = Path(__file__).parent

translations: gettext.GNUTranslations | gettext.NullTranslations = gettext.translation("vnpy", localedir=localedir,languages=['zh_CN'], fallback=True)

_ = translations.gettext
