# apps/users/services/email_service.py
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

class EmailService:

    @staticmethod
    def enviar_correo_simple(asunto, mensaje, destinatario):
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )

    @staticmethod
    def enviar_correo_html(asunto, template, context, destinatario):
        html_message = render_to_string(template, context)
        send_mail(
            subject=asunto,
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=html_message,
            fail_silently=False,
        )
