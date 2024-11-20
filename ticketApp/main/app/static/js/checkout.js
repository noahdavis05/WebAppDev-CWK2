// This is your test secret API key.
const stripe = Stripe("pk_test_51PhsUnGETTbhg7YVAwLLEfYUcIfwv0JikGqgLAttHPXBoBdGckg6JLDYe6bB6GyABL149zxFfxGfuhPS9csAXeLP005FHhi8dC");

initialize();

// Create a Checkout Session
async function initialize() {
  const fetchClientSecret = async () => {
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });
    const { clientSecret } = await response.json();
    return clientSecret;
  };

  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}