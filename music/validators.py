from django.core.exceptions import ValidationError


def validate_mp3(value):
    if not value.name.endswith('.mp3'):
        raise ValidationError('請上傳mp3檔案格式')
