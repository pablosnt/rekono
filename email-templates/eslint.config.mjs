// @ts-check
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import { defineConfig } from "eslint/config";
import eslintConfigPrettier from "eslint-config-prettier";

export default defineConfig(
  {
    ignores: [".react-email/**", "node_modules/**"],
  },
  eslint.configs.recommended,
  tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
  },
  eslintConfigPrettier,
);
