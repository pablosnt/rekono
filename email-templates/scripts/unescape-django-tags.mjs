import { readdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

// React escapes characters like quotes when rendering text content, so Django
// expressions such as {{ value|default:"-" }} are exported as
// {{ value|default:&quot;-&quot; }}, which Django can no longer parse. This
// script restores the original characters, but only inside Django delimiters,
// to keep the rest of the HTML untouched.

const ENTITIES = {
  "&quot;": '"',
  "&#x27;": "'",
  "&#39;": "'",
  "&amp;": "&",
  "&lt;": "<",
  "&gt;": ">",
};

const DJANGO_TAG = /\{\{.*?\}\}|\{%.*?%\}/gs;
const ENTITY = /&(?:quot|#x27|#39|amp|lt|gt);/g;

const outDir = process.argv[2];
if (!outDir) {
  console.error("Usage: node unescape-django-tags.mjs <outDir>");
  process.exit(1);
}

const files = (await readdir(outDir)).filter((file) => file.endsWith(".html"));
for (const file of files) {
  const path = join(outDir, file);
  const content = await readFile(path, "utf8");
  const unescaped = content.replace(DJANGO_TAG, (tag) =>
    tag.replace(ENTITY, (entity) => ENTITIES[entity]),
  );
  if (unescaped !== content) {
    await writeFile(path, unescaped);
  }
}
