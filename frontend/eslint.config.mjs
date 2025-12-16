// @ts-check
import withNuxt from "./.nuxt/eslint.config.mjs";
import eslintConfigPrettier from "eslint-config-prettier";

export default withNuxt({
  rules: {
    "vue/multi-word-component-names": "off",
    "vue/require-default-prop": "off",
  },
}).append(eslintConfigPrettier);
// Your custom configs here
