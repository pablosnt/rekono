<template>
  <MenuProject />
  <!-- 
    Separated on tabs. One Vue component per finding type, with links between them. Example, Technology has links to Port, Credentials, Vulnerabilities, Exploit
    OSINT
    Hosts (Ports)
    Port (Paths, Technologies, Vulnerabilities)
    Path
    Technology (Credentials, Vulnerabilities, Exploits)
    Credential (Displayed as Vulnerability?)
    Vulnerability (Exploit)
    Exploit
  -->
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
</script>
