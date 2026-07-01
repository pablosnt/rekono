import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserEmailVerification() {
  return (
    <Layout>
      <Preview>Confirm this address to finish updating your email.</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        Verify your email address
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        We received a request to use this address for your Rekono account. Click
        the button below to confirm it. Your account email will only change once
        this address is verified.
      </Text>
      <Button
        href={"{{ rekono_url }}/email-verification?otp={{ user_otp }}"}
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Verify email
      </Button>
      <Text className="text-gray-400 text-xs leading-relaxed m-0 mt-8 mb-0">
        This link can only be used once and expires shortly. If you did not
        request this change, you can ignore this email.
      </Text>
    </Layout>
  );
}
