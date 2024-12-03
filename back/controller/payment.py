from const import BASE_URL, STRIPE_API, STRIPE_SECRET
from stripe import StripeClient


class PaymentService:
    stripe.api_key = STRIPE_SECRET

    def __init__(self):
        self.stripe_client = StripeClient(api_key=STRIPE_API)
        pass

    def create_pay_session(self, amount, currency, name):
        try:
            session = stripe.checkout.Session.create(
               billing_address_collection="auto",
               line_items = [{
                    'price_data': {
                    'currency': currency,
                    'unit_amount': amount * 100,
                    'product_data': {
                        'name': name,
                    },
                    },
                    'quantity': 1,
                }],
                mode="payment",
                success_url= BASE_URL + "/api/payment/success",
                cancel_url= BASE_URL + "/api/payment/cancel",
            )
            return session  # Return session object for further use
        except stripe.error.StripeError as e:
            print(f"Error occurred: {e}")
            return None

    def confirm_payment_intent(self, payment_intent_id):
        return self.stripe_client.payment_intents.confirm(payment_intent_id)
    
    def cancel_payment_intent(self, payment_intent_id):
        return self.stripe_client.payment_intents.cancel(payment_intent_id)
    
    def retrieve_payment_intent(self, payment_intent_id):
        return self.stripe_client.payment_intents.retrieve(payment_intent_id)
    
    