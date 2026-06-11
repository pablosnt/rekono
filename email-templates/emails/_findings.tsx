import { Link, Text } from "react-email";

export const DASH = "-";

export const cell = (expr: string) => `{{ ${expr}|default:"${DASH}" }}`;

export const hostDomainOrIp = (host: string) =>
  `{% if ${host}.domain %}{{ ${host}.domain }}{% else %}{{ ${host}.ip }}{% endif %}`;

export const hostCell = (host: string) =>
  `{% if ${host} %}${hostDomainOrIp(host)}{% else %}${DASH}{% endif %}`;

const hostPortValue = (port: string) =>
  `{% if ${port}.host %}${hostDomainOrIp(`${port}.host`)}{% endif %}:{{ ${port}.port }}`;

export const hostPortCell = (...ports: string[]) =>
  `${ports
    .map((p, i) => `{% ${i ? "elif" : "if"} ${p} %}${hostPortValue(p)}`)
    .join("")}{% else %}${DASH}{% endif %}`;

export function ReferenceCell(
  item: string,
  label: React.ReactNode,
): React.ReactNode {
  return (
    <>
      {`{% if ${item}.reference %}`}
      <Link
        href={`{{ ${item}.reference }}`}
        className="text-primary font-semibold underline break-all"
      >
        {label}
      </Link>
      {`{% else %}${DASH}{% endif %}`}
    </>
  );
}

export function Field({
  label,
  value,
  mono,
  strong,
  children,
}: {
  label: string;
  value?: string;
  mono?: boolean;
  strong?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div className="mb-4">
      <Text className="text-gray-400 text-[11px] font-bold uppercase tracking-widest m-0 mb-0.5">
        {label}
      </Text>
      {children ?? (
        <Text
          className={`text-sm m-0 ${mono ? "font-mono " : ""}${
            strong ? "text-gray-900 font-bold" : "text-gray-700"
          }`}
        >
          {value}
        </Text>
      )}
    </div>
  );
}

export function ReferenceField() {
  return (
    <Field label="Reference">
      <Link
        href={"{{ finding.reference }}"}
        className="text-primary text-sm font-semibold underline break-all"
      >
        Reference
      </Link>
    </Field>
  );
}

export type Column = {
  header: string;
  cell: React.ReactNode;
  mono?: boolean;
  bold?: boolean;
};

export function FindingTable({
  title,
  list,
  item,
  columns,
}: {
  title: string;
  list: string;
  item: string;
  columns: Column[];
}) {
  return (
    <>
      {`{% if ${list} %}`}
      <Text className="text-gray-700 text-[11px] font-bold uppercase tracking-[0.07em] m-0 mb-2">
        {title}
      </Text>
      <table
        cellPadding={0}
        cellSpacing={0}
        className="w-full border-collapse border border-gray-200 mb-6"
      >
        <thead>
          <tr>
            {columns.map((c) => (
              <th
                key={c.header}
                className="bg-gray-100 text-gray-900 text-[11px] font-bold uppercase tracking-wider text-left px-3.5 py-2.5 border-b border-gray-200"
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {`{% for ${item} in ${list} %}`}
          <tr>
            {columns.map((c) => (
              <td
                key={c.header}
                className={`text-sm px-3.5 py-2.5 align-top border-b border-gray-200 ${
                  c.mono ? "font-mono " : ""
                }${c.bold ? "text-gray-900 font-bold" : "text-gray-700"}`}
              >
                {c.cell}
              </td>
            ))}
          </tr>
          {`{% endfor %}`}
        </tbody>
      </table>
      {`{% endif %}`}
    </>
  );
}
