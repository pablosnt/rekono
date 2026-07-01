import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserEmailChangeNotification() {
  return (
    <Layout>
      <Preview>
        Was this you? Review the change and secure your account.
      </Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        Your account email is being changed
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-4">
        {
          "We received a request on {{ time }} to change the email address on your Rekono account. The change will only take effect once the new address is verified. Until then, this address stays active."
        }
      </Text>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        Do not recognise this request? Your account may be at risk. Reset your
        password right away to lock it down.
      </Text>
      <Button
        href={"{{ rekono_url }}/reset-password"}
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Reset password
      </Button>
    </Layout>
  );
}
