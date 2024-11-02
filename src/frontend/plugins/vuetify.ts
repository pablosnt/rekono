import "@mdi/font/css/materialdesignicons.css";

import "vuetify/styles";
import { createVuetify } from "vuetify";
import VueApexCharts from "vue3-apexcharts";

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({});
  app.vueApp.use(vuetify);
  app.vueApp.use(VueApexCharts);
});
