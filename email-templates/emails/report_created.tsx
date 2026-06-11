import { Button, Heading, Link, Preview, Text } from "react-email";
import { Layout } from "./_layout";

export default function ReportCreated() {
  return (
    <Layout>
      <Preview>Your Rekono report is ready to download</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        Your report is ready
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-8">
        {"Good news! Your {{ report.format|upper }} report generated from "}
        {
          "{% if report.task %}task{% elif report.target %}target{% else %}project{% endif %} "
        }
        <Link
          href={
            "{{ rekono_url }}/projects/{% if report.task %}{{ report.task.target.project.id }}/scans/{{ report.task.id }}{% elif report.target %}{{ report.target.project.id }}/targets/{{ report.target.id }}{% else %}{{ report.project.id }}{% endif %}"
          }
          className="text-primary font-semibold underline"
        >
          {
            "{% if report.task %}#{{ report.task.id }}{% elif report.target %}{{ report.target.target }}{% else %}{{ report.project.name }}{% endif %}"
          }
        </Link>
        {" is ready to download."}
      </Text>
      <Button
        href={
          "{{ rekono_url }}/projects/{% if report.task %}{{ report.task.target.project.id }}{% elif report.target %}{{ report.target.project.id }}{% else %}{{ report.project.id }}{% endif %}/reports"
        }
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Download report
      </Button>
    </Layout>
  );
}
