import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    def validate(self, password, user=None):
        errors = []

        if not re.search(r"[a-z]", password or ""):
            errors.append(_("A senha deve conter pelo menos uma letra minuscula."))

        if not re.search(r"[A-Z]", password or ""):
            errors.append(_("A senha deve conter pelo menos uma letra maiuscula."))

        if not re.search(r"[0-9]", password or ""):
            errors.append(_("A senha deve conter pelo menos um numero."))

        if not re.search(r"[^A-Za-z0-9]", password or ""):
            errors.append(_("A senha deve conter pelo menos um caractere especial."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Sua senha deve ter no minimo 8 caracteres e incluir letra maiuscula, letra minuscula, numero e caractere especial."
        )