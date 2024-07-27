import MarkdownIt from "markdown-it";
import { full as emoji } from "markdown-it-emoji";
import marker from "markdown-it-mark";
import hljs from "highlight.js";
import "highlight.js/styles/qtcreator-dark.css";

export function useMarkdown() {
  return MarkdownIt({
    breaks: true,
    linkify: true,
    typographer: true,
    highlight: function (str, lang) {
      let result = "";
      try {
        if (lang && hljs.getLanguage(lang)) {
          result = hljs.highlight(str, { language: lang }).value;
        } else {
          result = hljs.highlightAuto(str).value;
        }
      } catch (__) {}
      if (result.length > 0) {
        result = '<pre><code class="hljs">' + result + "</code></pre>";
      }
      return result;
    },
  })
    .use(emoji)
    .use(marker);
}
