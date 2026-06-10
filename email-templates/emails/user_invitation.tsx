import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserInvitation() {
  return (
    <Layout>
      <Preview>You have been invited to join Rekono</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        You are invited to Rekono
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-4">
        Welcome aboard. Rekono is the offensive security platform that automates
        attack surface discovery and keeps your vulnerability management in one
        place.
      </Text>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        Your account is ready to be claimed. Create it below and start
        uncovering what is exposed before someone else does.
      </Text>
      <Button
        href={"{{ rekono_url }}/signup?otp={{ user_otp }}"}
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Accept invitation
      </Button>
    </Layout>
  );
}
