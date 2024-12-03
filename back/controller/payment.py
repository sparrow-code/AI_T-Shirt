from const import BASE_URL, STRIPE_API, STRIPE_SECRET
from stripe


class PaymentService:
    stripe.api_key = STRIPE_SECRET

    def __init__(self, logger):
        # self.stripe_client = StripeClient(api_key=STRIPE_API)
        self.logger = logger
        pass

    async def create_pay_session(self, amount, currency, name):
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
                success_url= "{BASE_URL}/api/payment/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url= "{BASE_URL}/api/payment/cancel?session_id={CHECKOUT_SESSION_ID}",
            )
            return session  # Return session object for further use
        except stripe.error.StripeError as e:
            print(f"Error occurred: {e}")
            return None

    async def payment_success(self, session_id):
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            self.logger.info(session)
            return session
        except stripe.error.StripeError as e:
            print(f"Error occurred: {e}")
            return None

    async def payment_cancel(self, session_id):
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            self.logger.info(session)
            return session
        except stripe.error.StripeError as e:
            print(f"Error occurred: {e}")
            return None