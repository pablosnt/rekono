import type {
  DefectDojoSettings,
  Integration,
  SmtpSettings,
  TelegramSettings,
  VirusTotalSettings,
} from "~/types/models";

const FETCH_TTL = 5 * 60 * 1000; // 5 minutes

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
    lastFetched: {
      telegram: null as number | null,
      smtp: null as number | null,
      virustotal: null as number | null,
      hacktricks: null as number | null,
      defectdojo: null as number | null,
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
    isFresh(key: string): boolean {
      const last = this.lastFetched[key];
      return last && Date.now() - last < FETCH_TTL;
    },
    fetchTelegram() {
      if (this.isFresh("telegram")) return;
      useApi("/api/telegram/settings/")
        .get("1/")
        .then((response: TelegramSettings) => {
          this.telegram = response;
          this.lastFetched.telegram = Date.now();
        });
    },
    fetchSmtp() {
      if (this.isFresh("smtp")) return;
      useApi("/api/smtp/")
        .get("1/")
        .then((response: SmtpSettings) => {
          this.smtp = response;
          this.lastFetched.smtp = Date.now();
        });
    },
    fetchVirusTotal() {
      if (this.isFresh("virustotal")) return;
      Promise.all([
        useApi("/api/integrations/")
          .get("virustotal/")
          .then(
            (response: Integration) => (this.virustotal.integration = response),
          ),
        useApi("/api/virustotal/")
          .get("1/")
          .then(
            (response: VirusTotalSettings) =>
              (this.virustotal.settings = response),
          ),
      ]).then(() => (this.lastFetched.virustotal = Date.now()));
    },
    fetchHackTricks() {
      if (this.isFresh("hacktricks")) return;
      useApi("/api/integrations/")
        .get("hacktricks/")
        .then((response: Integration) => {
          this.hacktricks = response;
          this.lastFetched.hacktricks = Date.now();
        });
    },
    fetchDefectDojo() {
      if (this.isFresh("defectdojo")) return;
      Promise.all([
        useApi("/api/integrations/")
          .get("defectdojo/")
          .then(
            (response: Integration) => (this.defectdojo.integration = response),
          ),
        useApi("/api/defectdojo/settings/")
          .get("1/")
          .then(
            (response: DefectDojoSettings) =>
              (this.defectdojo.settings = response),
          ),
      ]).then(() => (this.lastFetched.defectdojo = Date.now()));
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
    updateIntegration(key: string, updates: Partial<Integration>) {
      if (key === "defectdojo" && this.defectdojo.integration) {
        this.defectdojo.integration = {
          ...this.defectdojo.integration,
          ...updates,
        };
      } else if (key === "hacktricks" && this.hacktricks) {
        this.hacktricks = { ...this.hacktricks, ...updates };
      } else if (key === "virustotal" && this.virustotal.integration) {
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
