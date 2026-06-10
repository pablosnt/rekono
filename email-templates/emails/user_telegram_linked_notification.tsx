import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserTelegramLinkedNotification() {
  return (
    <Layout>
      <Preview>Your Rekono account is now linked to Telegram</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        Telegram bot linked to your account
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-4">
        {
          "We linked your Rekono account to the Telegram bot on {{ time }}. You will now receive notifications directly in Telegram. If this was you, there is nothing else you need to do."
        }
      </Text>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        Do not recognise this activity? Your account may be at risk. Reset your
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
