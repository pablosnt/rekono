import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserPasswordReset() {
  return (
    <Layout>
      <Preview>Reset your Rekono password</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        Reset your password
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        We received a request to reset the password for your Rekono account.
        Click the button below to choose a new one and get back to securing your
        attack surface.
      </Text>
      <Button
        href={"{{ rekono_url }}/reset-password?otp={{ user_otp }}"}
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Reset password
      </Button>
      <Text className="text-gray-400 text-xs leading-relaxed m-0 mt-8 mb-0">
        This link can only be used once and expires shortly. If you did not
        request a password reset, you can ignore this email. Your password
        will remain unchanged.
      </Text>
    </Layout>
  );
}
