import {
  Body,
  Column,
  Container,
  Head,
  Hr,
  Html,
  Img,
  Row,
  Section,
  Tailwind,
  Text,
  pixelBasedPreset,
} from "react-email";

interface LayoutProps {
  children: React.ReactNode;
}

// TODO: Replace https://localhost by rekono_url + root path if any?
export function Layout({ children }: LayoutProps) {
  return (
    <Tailwind
      config={{
        presets: [pixelBasedPreset],
        theme: {
          extend: {
            colors: {
              primary: "#dc2626",
              secondary: "#000000",
            },
            fontFamily: {
              sans: ["Helvetica", "Arial", "sans-serif"],
              mono: ["Menlo", "Consolas", "monospace"],
            },
          },
        },
      }}
    >
      <Html lang="en">
        <Head>
          <title>Rekono</title>
        </Head>
        <Body className="bg-gray-100 m-0 p-0 font-sans">
          <Container className="max-w-[600px] mx-auto">
            <Section className="py-8">
              <Row>
                <Column className="text-center">
                  <Img
                    src={"https://localhost/logo-light.png"}
                    alt="Rekono"
                    height={36}
                    className="mx-auto"
                  />
                </Column>
              </Row>
            </Section>

            <Hr className="mb-5" />

            {children}

            <Section className="bg-secondary mt-10">
              <Row>
                <Column className="px-8 pt-4 pb-5 text-center">
                  <Text className="text-gray-400 text-[11px] m-0 mb-1.5 leading-relaxed">
                    {"© "}
                    {new Date().getFullYear()}
                    {" Rekono Maintainers"}
                  </Text>
                  <Text className="text-gray-500 text-[10px] m-0 leading-relaxed">
                    This is an automated message. Do not reply to this email.
                  </Text>
                </Column>
              </Row>
            </Section>
          </Container>
        </Body>
      </Html>
    </Tailwind>
  );
}
