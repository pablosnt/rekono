import "@mdi/font/css/materialdesignicons.css";

import "vuetify/styles";
import { createVuetify } from "vuetify";
import VueApexCharts from "vue3-apexcharts";

export default defineNuxtPlugin((app) => {
  app.vueApp.use(createVuetify({}));
  app.vueApp.use(VueApexCharts);
});
