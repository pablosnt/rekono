import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserEnableAccount() {
  return (
    <Layout>
      <Preview>
        Your account is active again. Set a password to get back in.
      </Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        {"{% if user.first_name %}"}
        {"Welcome back, {{ user.first_name }}!"}
        {"{% elif user.username %}"}
        {"Welcome back, {{ user.username }}!"}
        {"{% else %}"}
        Welcome back!
        {"{% endif %}"}
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-4">
        Your Rekono account is active and ready to use. Set your password below
        to start using it.
      </Text>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        Once that is done, you can pick up right where you left off.
      </Text>
      <Button
        href={"{{ rekono_url }}/reset-password?otp={{ user_otp }}"}
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Set password
      </Button>
    </Layout>
  );
}
