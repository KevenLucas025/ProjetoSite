from django.core.mail.backends.smtp import EmailBackend
import ssl


class CustomEmailBackend(EmailBackend):
    @property
    def ssl_context(self):
        return ssl._create_unverified_context()