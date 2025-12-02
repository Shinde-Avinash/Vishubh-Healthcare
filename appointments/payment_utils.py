"""
Payment gateway integration utilities for Razorpay
"""
import razorpay
from django.conf import settings
from decimal import Decimal


class PaymentGateway:
    """Razorpay payment gateway integration"""
    
    def __init__(self):
        """Initialize Razorpay client"""
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, currency='INR', receipt=None):
        """
        Create a payment order
        
        Args:
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            receipt: Receipt ID for reference
            
        Returns:
            dict: Order details from Razorpay
        """
        # Convert amount to paise (smallest currency unit)
        amount_in_paise = int(Decimal(amount) * 100)
        
        order_data = {
            'amount': amount_in_paise,
            'currency': currency,
            'payment_capture': 1  # Auto capture payment
        }
        
        if receipt:
            order_data['receipt'] = receipt
        
        try:
            order = self.client.order.create(data=order_data)
            return {
                'success': True,
                'order_id': order['id'],
                'amount': amount,
                'currency': currency,
                'order_data': order
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify payment signature
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature to verify
            
        Returns:
            bool: True if signature is valid
        """
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def get_payment_details(self, payment_id):
        """
        Fetch payment details
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            dict: Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'success': True,
                'payment': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, payment_id, amount=None):
        """
        Refund a payment
        
        Args:
            payment_id: Razorpay payment ID
            amount: Amount to refund (in paise), None for full refund
            
        Returns:
            dict: Refund details
        """
        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = int(Decimal(amount) * 100)
            
            refund = self.client.payment.refund(payment_id, refund_data)
            return {
                'success': True,
                'refund': refund
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def create_payment_order(appointment):
    """
    Create a payment order for an appointment
    
    Args:
        appointment: Appointment instance
        
    Returns:
        dict: Order creation result
    """
    gateway = PaymentGateway()
    receipt = f"APT_{appointment.id}_{appointment.patient.id}"
    
    return gateway.create_order(
        amount=float(appointment.payment_amount),
        receipt=receipt
    )


def verify_payment_signature(order_id, payment_id, signature):
    """
    Verify Razorpay payment signature
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Payment signature
        
    Returns:
        bool: True if valid
    """
    gateway = PaymentGateway()
    return gateway.verify_payment(order_id, payment_id, signature)
