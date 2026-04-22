import type {
  DefectDojoSettings,
  Integration,
  SmtpSettings,
  TelegramSettings,
  VirusTotalSettings,
} from "~/types/models";

export const useIntegrationsStore = defineStore("integrations", {
  state: () => ({
    telegram: null as TelegramSettings | null,
    smtp: null as SmtpSettings | null,
    virustotal: {
      integration: null as Integration | null,
      settings: null as VirusTotalSettings | null,
    },
    hacktricks: null as Integration | null,
    defectdojo: {
      integration: null as Integration | null,
      settings: null as DefectDojoSettings | null,
    },
  }),
  getters: {
    isEmpty(): boolean {
      return (
        this.telegram === null &&
        this.smtp === null &&
        this.virustotal.integration === null &&
        this.virustotal.settings === null &&
        this.hacktricks === null &&
        this.defectdojo.integration === null &&
        this.defectdojo.settings === null
      );
    },
  },
  actions: {
    fetchTelegram() {
      useApi("/api/telegram/settings/")
        .get("1/")
        .then((response: TelegramSettings) => (this.telegram = response));
    },
    fetchSmtp() {
      useApi("/api/smtp/")
        .get("1/")
        .then((response: SmtpSettings) => (this.smtp = response));
    },
    fetchVirusTotal() {
      useApi("/api/integrations/")
        .get("5/")
        .then(
          (response: Integration) => (this.virustotal.integration = response),
        );
      useApi("/api/virustotal/")
        .get("1/")
        .then(
          (response: VirusTotalSettings) =>
            (this.virustotal.settings = response),
        );
    },
    fetchHackTricks() {
      useApi("/api/integrations/")
        .get("3/")
        .then((response: Integration) => (this.hacktricks = response));
    },
    fetchDefectDojo() {
      useApi("/api/integrations/")
        .get("1/")
        .then(
          (response: Integration) => (this.defectdojo.integration = response),
        );
      useApi("/api/defectdojo/settings/")
        .get("1/")
        .then(
          (response: DefectDojoSettings) =>
            (this.defectdojo.settings = response),
        );
    },
    fetch() {
      this.fetchTelegram();
      this.fetchSmtp();
      this.fetchVirusTotal();
      this.fetchHackTricks();
      this.fetchDefectDojo();
    },
    updateTelegramSettings(data: TelegramSettings) {
      this.telegram = data;
    },
    updateSmtpSettings(data: SmtpSettings) {
      this.smtp = data;
    },
    updateIntegration(id: number, updates: Partial<Integration>) {
      if (id === 1 && this.defectdojo.integration) {
        this.defectdojo.integration = {
          ...this.defectdojo.integration,
          ...updates,
        };
      } else if (id === 3 && this.hacktricks) {
        this.hacktricks = { ...this.hacktricks, ...updates };
      } else if (id === 5 && this.virustotal.integration) {
        this.virustotal.integration = {
          ...this.virustotal.integration,
          ...updates,
        };
      }
    },
    updateVirusTotalSettings(data: VirusTotalSettings) {
      this.virustotal.settings = data;
    },
    updateDefectDojoSettings(data: DefectDojoSettings) {
      this.defectdojo.settings = data;
    },
  },
});
