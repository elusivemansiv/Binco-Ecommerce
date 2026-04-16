"""
Notification Service — Central engine for dispatching notifications.

Usage:
    from notifications.services import NotificationService
    NotificationService.notify_order_placed(order)
    NotificationService.notify_shipping_update(order)
"""
import logging
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template import Template, Context

from .models import Notification, NotificationTemplate

logger = logging.getLogger(__name__)


class NotificationService:
    """Dispatch notifications across email, SMS, push, and in-app channels."""

    # ──────────── HELPERS ────────────
    @staticmethod
    def _render_template_string(template_str, context_dict):
        """Replace {{placeholder}} style variables in template strings."""
        result = template_str
        for key, value in context_dict.items():
            result = result.replace(f'{{{{{key}}}}}', str(value))
        return result

    @staticmethod
    def _get_template(event):
        """Fetch a NotificationTemplate by event name."""
        try:
            return NotificationTemplate.objects.get(event=event, is_active=True)
        except NotificationTemplate.DoesNotExist:
            return None

    @staticmethod
    def _create_in_app_notification(user, notification_type, title, message, link='', icon='fa-bell', metadata=None):
        """Create an in-app notification record."""
        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            channel='in_app',
            title=title,
            message=message,
            link=link,
            icon=icon,
            status='sent',
            sent_at=timezone.now(),
            metadata=metadata or {},
        )

    @staticmethod
    def _send_email(to_email, subject, html_body, from_email=None):
        """Send an email notification."""
        try:
            from siteconfig.models import EmailSettings
            email_conf = EmailSettings.get()

            if email_conf.backend == 'console':
                logger.info(f'[EMAIL-CONSOLE] To: {to_email} | Subject: {subject}')
                return True

            sender = from_email or f'{email_conf.from_name} <{email_conf.from_email}>'
            msg = EmailMessage(
                subject=subject,
                body=html_body,
                from_email=sender,
                to=[to_email],
            )
            msg.content_subtype = 'html'
            msg.send(fail_silently=True)

            logger.info(f'[EMAIL-SENT] To: {to_email} | Subject: {subject}')
            return True
        except Exception as e:
            logger.error(f'[EMAIL-FAILED] To: {to_email} | Error: {e}')
            return False

    @staticmethod
    def _send_sms(phone_number, message):
        """Send an SMS notification (provider-agnostic stub)."""
        try:
            from siteconfig.models import SMSSettings
            sms_conf = SMSSettings.get()

            if sms_conf.provider == 'disabled':
                logger.info(f'[SMS-DISABLED] To: {phone_number} | Message: {message[:50]}...')
                return True

            if sms_conf.provider == 'twilio':
                # Twilio integration stub
                logger.info(f'[SMS-TWILIO] To: {phone_number} | Message: {message[:50]}...')
                # TODO: Integrate actual Twilio SDK
                return True

            if sms_conf.provider == 'bulksmsbd':
                logger.info(f'[SMS-BULKSMS] To: {phone_number} | Message: {message[:50]}...')
                # TODO: Integrate BulkSMS BD API
                return True

            return False
        except Exception as e:
            logger.error(f'[SMS-FAILED] To: {phone_number} | Error: {e}')
            return False

    # ──────────── ORDER EVENTS ────────────

    @classmethod
    def notify_order_placed(cls, order):
        """Fire notifications when an order is placed."""
        context = {
            'order_id': order.id,
            'customer_name': order.full_name,
            'total': str(order.get_final_total),
            'status': 'Confirmed',
            'payment_method': order.get_payment_method_display(),
        }

        tmpl = cls._get_template('order_placed')

        # In-app notification
        title = tmpl.in_app_title if tmpl else f'Order #{order.id} Confirmed!'
        message = tmpl.in_app_message if tmpl else f'Thank you {order.full_name}! Your order has been placed successfully.'
        title = cls._render_template_string(title, context)
        message = cls._render_template_string(message, context)

        cls._create_in_app_notification(
            user=order.user,
            notification_type='order_confirmation',
            title=title,
            message=message,
            link=f'/order/{order.id}/',
            icon='fa-check-circle',
            metadata={'order_id': order.id},
        )

        # Email
        try:
            from siteconfig.models import EmailSettings
            email_conf = EmailSettings.get()
            if email_conf.send_order_confirmation:
                subject = tmpl.email_subject if tmpl else f'Order #{order.id} Confirmed – Binco'
                body = tmpl.email_body if tmpl else f'<h2>Thank you, {order.full_name}!</h2><p>Your order #{order.id} has been placed.</p>'
                subject = cls._render_template_string(subject, context)
                body = cls._render_template_string(body, context)

                email_sent = cls._send_email(order.email, subject, body)
                Notification.objects.create(
                    user=order.user,
                    notification_type='order_confirmation',
                    channel='email',
                    title=subject,
                    message=body,
                    status='sent' if email_sent else 'failed',
                    sent_at=timezone.now() if email_sent else None,
                    metadata={'order_id': order.id},
                )
        except Exception as e:
            logger.error(f'Order email notification failed: {e}')

        # SMS
        try:
            from siteconfig.models import SMSSettings
            sms_conf = SMSSettings.get()
            if sms_conf.send_order_sms and order.phone:
                sms_text = tmpl.sms_body if tmpl else f'Binco: Order #{order.id} confirmed! Total: {order.get_final_total}. Thank you!'
                sms_text = cls._render_template_string(sms_text, context)
                cls._send_sms(order.phone, sms_text)
        except Exception as e:
            logger.error(f'Order SMS notification failed: {e}')

    @classmethod
    def notify_seller_new_order(cls, order):
        """Notify each seller about a new order containing their products."""
        # Get unique sellers from order items
        sellers = set()
        for item in order.items.all():
            if item.product and item.product.seller:
                sellers.add(item.product.seller)

        for seller in sellers:
            # Filter items belonging to this specific seller
            seller_items = order.items.filter(product__seller=seller)
            count = seller_items.count()
            
            context = {
                'order_id': order.id,
                'customer_name': order.full_name,
                'item_count': count,
            }

            title = f'New Order Received! (# {order.id})'
            message = f'You have a new order for {count} item(s) from {order.full_name}.'
            
            cls._create_in_app_notification(
                user=seller,
                notification_type='order_confirmation',
                title=title,
                message=message,
                link='/seller/orders/?status=active', # Link to seller's active orders
                icon='fa-shopping-cart',
                metadata={'order_id': order.id, 'role': 'seller'},
            )
            logger.info(f'[SELLER-NOTIFIED] Order #{order.id} notification sent to {seller.username}')

    @classmethod
    def notify_order_status_change(cls, order):
        """Fire notifications when order status changes."""
        status_map = {
            'processing': 'order_processing',
            'shipped': 'order_shipped',
            'delivered': 'order_delivered',
            'cancelled': 'order_cancelled',
            'return_requested': 'return_requested',
            'return_approved': 'return_approved',
        }

        event = status_map.get(order.status)
        if not event:
            return

        context = {
            'order_id': order.id,
            'customer_name': order.full_name,
            'total': str(order.get_final_total),
            'status': order.get_status_display(),
        }

        tmpl = cls._get_template(event)

        # In-app
        title = tmpl.in_app_title if tmpl else f'Order #{order.id} – {order.get_status_display()}'
        message = tmpl.in_app_message if tmpl else f'Your order #{order.id} status has been updated to: {order.get_status_display()}'
        title = cls._render_template_string(title, context)
        message = cls._render_template_string(message, context)

        icon_map = {
            'processing': 'fa-cog',
            'shipped': 'fa-truck',
            'delivered': 'fa-box-open',
            'cancelled': 'fa-times-circle',
            'return_requested': 'fa-undo',
            'return_approved': 'fa-check-double',
        }

        cls._create_in_app_notification(
            user=order.user,
            notification_type='order_status',
            title=title,
            message=message,
            link=f'/order/{order.id}/',
            icon=icon_map.get(order.status, 'fa-bell'),
            metadata={'order_id': order.id, 'status': order.status},
        )

        # Email
        try:
            from siteconfig.models import EmailSettings
            email_conf = EmailSettings.get()
            if email_conf.send_shipping_update:
                subject = tmpl.email_subject if tmpl else f'Order #{order.id} – {order.get_status_display()}'
                body = tmpl.email_body if tmpl else f'<h2>Order Update</h2><p>Hi {order.full_name}, your order #{order.id} is now: <strong>{order.get_status_display()}</strong></p>'
                subject = cls._render_template_string(subject, context)
                body = cls._render_template_string(body, context)
                cls._send_email(order.email, subject, body)
        except Exception as e:
            logger.error(f'Status email failed: {e}')

        # SMS
        try:
            from siteconfig.models import SMSSettings
            sms_conf = SMSSettings.get()
            if sms_conf.send_shipping_sms and order.phone:
                sms_text = tmpl.sms_body if tmpl else f'Binco: Order #{order.id} is now {order.get_status_display()}.'
                sms_text = cls._render_template_string(sms_text, context)
                cls._send_sms(order.phone, sms_text)
        except Exception as e:
            logger.error(f'Status SMS failed: {e}')

    @classmethod
    def notify_promotion(cls, users, promo_title, promo_message, link=''):
        """Send a promotional notification to multiple users."""
        tmpl = cls._get_template('promotion_blast')

        for user in users:
            context = {'customer_name': user.get_full_name() or user.username}

            title = tmpl.in_app_title if tmpl else promo_title
            message = tmpl.in_app_message if tmpl else promo_message
            title = cls._render_template_string(title, context)
            message = cls._render_template_string(message, context)

            cls._create_in_app_notification(
                user=user,
                notification_type='promotion',
                title=title,
                message=message,
                link=link,
                icon='fa-tags',
            )

    @classmethod
    def notify_welcome(cls, user):
        """Send welcome notification to a new user."""
        tmpl = cls._get_template('welcome_user')
        context = {'customer_name': user.get_full_name() or user.username}

        title = tmpl.in_app_title if tmpl else f'Welcome to Binco, {user.first_name or user.username}!'
        message = tmpl.in_app_message if tmpl else 'Start exploring amazing products on Binco Ecommerce.'
        title = cls._render_template_string(title, context)
        message = cls._render_template_string(message, context)

        cls._create_in_app_notification(
            user=user,
            notification_type='welcome',
            title=title,
            message=message,
            link='/',
            icon='fa-hand-wave',
        )
