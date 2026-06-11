import { Button, Heading, Preview, Text } from "react-email";
import { Layout } from "./_layout";
import { Field, hostDomainOrIp, ReferenceField } from "./_findings";

export default function AlertNotification() {
  return (
    <Layout>
      <Preview>A finding just matched one of your alert rules.</Preview>
      <Heading className="text-gray-900 text-2xl font-bold m-0 mb-4">
        {
          'New {% if finding_type == "OSINT" %}OSINT{% else %}{{ finding_type|lower }}{% endif %} detected'
        }
      </Heading>
      <Text className="text-gray-500 text-sm leading-relaxed m-0 mb-6">
        Heads up! One of your alert rules just matched. Here is what Rekono
        found.
      </Text>
      <div className="bg-gray-50 border border-gray-200 rounded-md px-6 py-5 mb-8">
        {'{% if finding_type == "OSINT" %}'}
        <Field label="Data" value={"{{ finding.data }}"} strong />
        <Field label="Data type" value={"{{ finding.data_type }}"} />
        {"{% if finding.source %}"}
        <Field label="Source" value={"{{ finding.source }}"} />
        {"{% endif %}"}

        {'{% elif finding_type == "Host" %}'}
        <Field label="IP" value={"{{ finding.ip }}"} mono strong />
        {"{% if finding.domain %}"}
        <Field label="Domain" value={"{{ finding.domain }}"} mono strong />
        {"{% endif %}"}
        {"{% if finding.os %}"}
        <Field label="OS" value={"{{ finding.os }}"} />
        {"{% endif %}"}
        <Field label="OS type" value={"{{ finding.os_type }}"} />
        {"{% if finding.country %}"}
        <Field label="Country" value={"{{ finding.country }}"} />
        {"{% endif %}"}
        {"{% if finding.city %}"}
        <Field label="City" value={"{{ finding.city }}"} />
        {"{% endif %}"}

        {'{% elif finding_type == "Port" %}'}
        {"{% if finding.host %}"}
        <Field label="Host" value={hostDomainOrIp("finding.host")} mono />
        {"{% endif %}"}
        <Field label="Port" value={"{{ finding.port }}"} mono strong />
        <Field label="Status" value={"{{ finding.status }}"} />
        {"{% if finding.protocol %}"}
        <Field label="Protocol" value={"{{ finding.protocol }}"} />
        {"{% endif %}"}
        {"{% if finding.service %}"}
        <Field label="Service" value={"{{ finding.service }}"} strong />
        {"{% endif %}"}

        {'{% elif finding_type == "Technology" %}'}
        {"{% if finding.port and finding.port.host %}"}
        <Field label="Host" value={hostDomainOrIp("finding.port.host")} mono />
        {"{% endif %}"}
        {"{% if finding.port %}"}
        <Field label="Port" value={"{{ finding.port.port }}"} mono />
        {"{% endif %}"}
        <Field label="Name" value={"{{ finding.name }}"} strong />
        {"{% if finding.version %}"}
        <Field label="Version" value={"{{ finding.version }}"} mono />
        {"{% endif %}"}
        {"{% if finding.reference %}"}
        <ReferenceField />
        {"{% endif %}"}

        {'{% elif finding_type == "Credential" %}'}
        {"{% if finding.technology %}"}
        {"{% if finding.technology.port and finding.technology.port.host %}"}
        <Field
          label="Host"
          value={hostDomainOrIp("finding.technology.port.host")}
          mono
        />
        {"{% endif %}"}
        {"{% if finding.technology.port %}"}
        <Field label="Port" value={"{{ finding.technology.port.port }}"} mono />
        {"{% endif %}"}
        <Field label="Technology" value={"{{ finding.technology.name }}"} />
        {"{% endif %}"}
        {"{% if finding.email %}"}
        <Field label="Email" value={"{{ finding.email }}"} strong />
        {"{% endif %}"}
        {"{% if finding.username %}"}
        <Field label="Username" value={"{{ finding.username }}"} strong />
        {"{% endif %}"}
        {"{% if finding.secret %}"}
        <Field label="Secret" value={"{{ finding.secret }}"} mono strong />
        {"{% endif %}"}
        {"{% if finding.context %}"}
        <Field label="Context" value={"{{ finding.context }}"} />
        {"{% endif %}"}

        {'{% elif finding_type == "Vulnerability" %}'}
        {
          "{% if finding.technology and finding.technology.port and finding.technology.port.host %}"
        }
        <Field
          label="Host"
          value={hostDomainOrIp("finding.technology.port.host")}
          mono
        />
        {"{% elif finding.port and finding.port.host %}"}
        <Field label="Host" value={hostDomainOrIp("finding.port.host")} mono />
        {"{% endif %}"}
        {"{% if finding.technology and finding.technology.port %}"}
        <Field label="Port" value={"{{ finding.technology.port.port }}"} mono />
        {"{% elif finding.port %}"}
        <Field label="Port" value={"{{ finding.port.port }}"} mono />
        {"{% endif %}"}
        {"{% if finding.technology %}"}
        <Field label="Technology" value={"{{ finding.technology.name }}"} />
        {"{% endif %}"}
        <Field label="Name" value={"{{ finding.name }}"} strong />
        <Field label="Severity" value={"{{ finding.get_severity_display }}"} />
        {"{% if finding.cvss_base_score and finding.cvss_vector %}"}
        <Field
          label="CVSS"
          value={"{{ finding.cvss_base_score }} ({{ finding.cvss_vector }})"}
          mono
        />
        {"{% elif finding.cvss_base_score %}"}
        <Field label="CVSS" value={"{{ finding.cvss_base_score }}"} mono />
        {"{% elif finding.cvss_vector %}"}
        <Field label="CVSS" value={"{{ finding.cvss_vector }}"} mono />
        {"{% endif %}"}
        {"{% if finding.cve %}"}
        <Field label="CVE" value={"{{ finding.cve }}"} mono strong />
        {"{% endif %}"}
        {"{% if finding.euvd_id %}"}
        <Field label="EUVD" value={"{{ finding.euvd_id }}"} mono strong />
        {"{% endif %}"}
        {"{% if finding.ghsa_id %}"}
        <Field label="GHSA" value={"{{ finding.ghsa_id }}"} mono strong />
        {"{% endif %}"}
        {"{% if finding.osv_generic_id %}"}
        <Field label="OSV" value={"{{ finding.osv_generic_id }}"} mono strong />
        {"{% endif %}"}
        {"{% if finding.cwes %}"}
        <Field label="CWE" value={'{{ finding.cwes|join:", " }}'} mono />
        {"{% endif %}"}
        {"{% if finding.epss_score %}"}
        <Field label="EPSS" value={"{{ finding.epss_score }}"} mono />
        {"{% endif %}"}
        <Field
          label="Trending"
          value={'{{ finding.trending|yesno:"Yes,No" }}'}
        />
        {"{% if finding.reference %}"}
        <ReferenceField />
        {"{% endif %}"}
        {"{% endif %}"}
      </div>
      <Button
        href={`{{ rekono_url }}/projects/{{ alert.project.id }}/{% if finding_type == "OSINT" %}osint{% elif finding_type == "Host" %}hosts{% elif finding_type == "Port" %}ports{% elif finding_type == "Technology" %}technologies{% elif finding_type == "Credential" %}credentials{% else %}vulnerabilities{% endif %}/{{ finding.id }}`}
        className="bg-primary text-white rounded-md px-7 py-3 font-bold text-sm no-underline"
      >
        Review finding
      </Button>
    </Layout>
  );
}
