declare module "react-native-razorpay" {
  type CheckoutOptions = {
    key: string;
    amount: number;
    currency: string;
    order_id: string;
    name: string;
    description: string;
    theme?: { color?: string };
  };

  const RazorpayCheckout: {
    open(options: CheckoutOptions): Promise<unknown>;
  };
  export default RazorpayCheckout;
}
