import { Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function UserMfa() {
  return (
    <Layout>
      <Preview>Your Rekono verification code</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-2">
        Verify your sign-in
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-7">
        Enter the code below to finish signing in to Rekono. It expires in a few
        minutes, so use it soon.
      </Text>
      <div className="bg-gray-50 border border-gray-200 rounded-lg px-5 py-5 mb-7">
        <Text className="text-gray-400 text-[11px] font-semibold uppercase tracking-wider m-0 mb-2">
          Verification code
        </Text>
        <Text className="font-mono text-primary text-sm font-semibold leading-relaxed break-all m-0">
          {"{{ user_otp }}"}
        </Text>
      </div>
      <Text className="text-gray-400 text-xs leading-relaxed m-0">
        Never share this code with anyone. If you did not try to sign in,
        someone may have your password. Reset it right away to keep your account
        secure.
      </Text>
    </Layout>
  );
}
