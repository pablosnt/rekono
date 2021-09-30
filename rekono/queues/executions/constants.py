from tools.enums import FindingType


finding_relations = {
    FindingType.OSINT: [],
    FindingType.HOST: [],
    FindingType.ENUMERATION: [FindingType.HOST],
    FindingType.HTTP_ENDPOINT: [FindingType.ENUMERATION],
    FindingType.TECHNOLOGY: [FindingType.ENUMERATION],
    FindingType.VULNERABILITY: [FindingType.TECHNOLOGY],
    FindingType.EXPLOIT: [FindingType.TECHNOLOGY, FindingType.VULNERABILITY]
}
