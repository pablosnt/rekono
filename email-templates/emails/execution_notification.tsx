import { Button, Heading, Hr, Img, Preview, Text } from "react-email";
import { Layout } from "./_layout";
import {
  cell,
  Column,
  DASH,
  FindingTable,
  hostCell,
  hostPortCell,
  ReferenceCell,
} from "./_findings";

const summaryRows: [string, string, boolean][] = [
  ["Project", "{{ execution.task.target.project.name }}", false],
  ["Target", "{{ execution.task.target.target }}", true],
  ["Tool", "{{ execution.configuration.tool.name }}", false],
  ["Configuration", "{{ execution.configuration.name }}", false],
  ["Status", "{{ execution.status }}", false],
  ["Start", "{{ execution.start }}", false],
  ["End", "{{ execution.end }}", false],
  ["Executor", "{{ execution.task.executor.username }}", false],
];

const tables: {
  title: string;
  list: string;
  item: string;
  columns: Column[];
}[] = [
  {
    title: "OSINT",
    list: "osint",
    item: "o",
    columns: [
      { header: "Data", cell: cell("o.data"), bold: true },
      { header: "Data type", cell: cell("o.data_type") },
      { header: "Source", cell: cell("o.source") },
    ],
  },
  {
    title: "Hosts",
    list: "host",
    item: "h",
    columns: [
      { header: "IP", cell: cell("h.ip"), mono: true, bold: true },
      { header: "Domain", cell: cell("h.domain"), mono: true },
      { header: "OS", cell: cell("h.os") },
      { header: "OS type", cell: cell("h.os_type") },
      { header: "Country", cell: cell("h.country") },
      { header: "City", cell: cell("h.city") },
    ],
  },
  {
    title: "Ports",
    list: "port",
    item: "p",
    columns: [
      { header: "Host", cell: hostCell("p.host"), mono: true },
      { header: "Port", cell: cell("p.port"), mono: true, bold: true },
      { header: "Status", cell: cell("p.status") },
      { header: "Protocol", cell: cell("p.protocol") },
      { header: "Service", cell: cell("p.service"), bold: true },
    ],
  },
  {
    title: "Paths",
    list: "path",
    item: "p",
    columns: [
      { header: "Host / Port", cell: hostPortCell("p.port"), mono: true },
      { header: "Type", cell: cell("p.type") },
      { header: "Path", cell: cell("p.path"), bold: true },
      { header: "Status", cell: cell("p.status") },
    ],
  },
  {
    title: "Technologies",
    list: "technology",
    item: "t",
    columns: [
      { header: "Host / Port", cell: hostPortCell("t.port"), mono: true },
      { header: "Name", cell: cell("t.name"), bold: true },
      { header: "Version", cell: cell("t.version"), mono: true },
      { header: "Reference", cell: ReferenceCell("t", "Link") },
    ],
  },
  {
    title: "Credentials",
    list: "credential",
    item: "c",
    columns: [
      { header: "Technology", cell: cell("c.technology.name") },
      {
        header: "Host / Port",
        cell: hostPortCell("c.technology.port"),
        mono: true,
      },
      { header: "Email", cell: cell("c.email"), bold: true },
      { header: "Username", cell: cell("c.username"), bold: true },
      { header: "Secret", cell: cell("c.secret"), mono: true, bold: true },
      { header: "Context", cell: cell("c.context") },
    ],
  },
  {
    title: "Vulnerabilities",
    list: "vulnerability",
    item: "v",
    columns: [
      {
        header: "Host / Port",
        cell: hostPortCell("v.port", "v.technology.port"),
        mono: true,
      },
      { header: "Name", cell: cell("v.name"), bold: true },
      { header: "Severity", cell: cell("v.get_severity_display") },
      { header: "CVSS", cell: cell("v.cvss_base_score"), mono: true },
      { header: "CVE", cell: cell("v.cve"), mono: true, bold: true },
      { header: "EPSS", cell: cell("v.epss_score"), mono: true },
      { header: "Reference", cell: ReferenceCell("v", "Link") },
    ],
  },
  {
    title: "Exploits",
    list: "exploit",
    item: "e",
    columns: [
      { header: "Vulnerability", cell: cell("e.vulnerability.name") },
      {
        header: "Technology",
        cell: `{% if e.vulnerability.technology %}{{ e.vulnerability.technology.name }}{% elif e.technology %}{{ e.technology.name }}{% else %}${DASH}{% endif %}`,
      },
      { header: "Title", cell: cell("e.title"), bold: true },
      { header: "Exploit DB", cell: cell("e.edb_id"), mono: true },
      { header: "Reference", cell: ReferenceCell("e", "Link") },
    ],
  },
];

export default function ExecutionNotification() {
  return (
    <Layout>
      <Preview>See the summary and every finding from this scan.</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-2">
        {"{% if execution.configuration.tool.icon %}"}
        <Img
          src={"{{ execution.configuration.tool.icon }}"}
          alt=""
          width={28}
          height={28}
          className="inline-block align-middle mr-2 rounded"
        />
        {"{% endif %}"}
        {"{{ execution.configuration.tool.name }}"}
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-6">
        Your scan just finished. Here is the summary and everything Rekono
        found.
      </Text>
      <div className="bg-gray-50 border border-gray-200 rounded-md px-6 py-5 mb-8">
        <table cellPadding={0} cellSpacing={0} className="w-full">
          <tbody>
            {summaryRows.map(([label, value, isMono]) => (
              <tr key={label}>
                <td className="w-[38%] text-gray-400 text-[11px] font-bold uppercase tracking-widest py-1.5 pr-4 align-top">
                  {label}
                </td>
                <td
                  className={`text-gray-900 text-sm py-1.5 align-top${isMono ? " font-mono" : ""}`}
                >
                  {value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Button
        href={
          "{{ rekono_url }}/projects/{{ execution.task.target.project.id }}/scans/{{ execution.task.id }}"
        }
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline mb-8"
      >
        View scan
      </Button>
      <Hr className="border-gray-200 m-0 mb-8" />
      {tables.map((table) => (
        <FindingTable key={table.list} {...table} />
      ))}
    </Layout>
  );
}
