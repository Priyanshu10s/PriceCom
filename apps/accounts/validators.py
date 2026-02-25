from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator as BaseUserAttributeSimilarityValidator,
    MinimumLengthValidator as BaseMinimumLengthValidator,
    CommonPasswordValidator as BaseCommonPasswordValidator,
    NumericPasswordValidator as BaseNumericPasswordValidator,
)
from django.utils.translation import gettext as _

class CustomUserAttributeSimilarityValidator(BaseUserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Password aapke username se milta-julta nahi ho sakta."),
                code='password_too_similar',
            )

class CustomMinimumLengthValidator(BaseMinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Bhai, password thoda lamba rakho (Kam se kam 10 characters)."),
                code='password_too_short',
            )

class CustomCommonPasswordValidator(BaseCommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Ye password bahut common hai, kuch unique try karo!"),
                code='password_too_common',
            )

class CustomNumericPasswordValidator(BaseNumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Password mein sirf numbers nahi chalenge, alphabets bhi use karo."),
                code='password_entirely_numeric',
            )
