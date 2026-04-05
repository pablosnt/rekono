export default defineAppConfig({
  ui: {
    colors: {
      primary: "red",
      secondary: "black",
      neutral: "slate",
    },
    icons: {
      light: "i-lucide-sun",
      dark: "i-lucide-moon",
      loading: "i-lucide-loader",
    },
    editor: {
      slots: {
        base: [
          "[&_table]:w-full [&_table]:border-separate [&_table]:border-spacing-0 [&_table]:rounded-md",
          "[&_th]:py-3 [&_th]:px-4 [&_th]:font-semibold [&_th]:text-sm [&_th]:text-left [&_th]:bg-muted/50 [&_th]:border-t [&_th]:border-b [&_th]:border-e [&_th]:first:border-s [&_th]:border-muted",
          "[&_th_p]:my-0 [&_th_p]:leading-5",
          "[&_td]:py-3 [&_td]:px-4 [&_td]:text-sm [&_td]:text-left [&_td]:border-b [&_td]:border-e [&_td]:first:border-s [&_td]:border-muted",
          "[&_td_p]:my-0 [&_td_p]:leading-5 [&_td_code]:text-xs/5 [&_td_ul]:my-0 [&_td_ol]:my-0 [&_td_ul]:ps-4.5 [&_td_ol]:ps-4.5 [&_td_li]:leading-6 [&_td_li]:my-0.5",
          "[&_tr:first-child_th:first-child]:rounded-tl-md [&_tr:first-child_th:last-child]:rounded-tr-md [&_tr:last-child_td:first-child]:rounded-bl-md [&_tr:last-child_td:last-child]:rounded-br-md",
          "[&_.selectedCell]:bg-primary/10 [&_.selectedCell]:ring-2 [&_.selectedCell]:ring-primary [&_.selectedCell]:ring-inset",
          "[&_ul[data-type=taskList]]:list-none [&_ul[data-type=taskList]]:ps-1",
          "[&_ul[data-type=taskList]_li]:flex [&_ul[data-type=taskList]_li]:items-center [&_ul[data-type=taskList]_li]:ps-0",
          "[&_ul[data-type=taskList]_li_label]:inline-flex [&_ul[data-type=taskList]_li_label]:pr-2.5",
          "[&_ul[data-type=taskList]_li_label_input]:appearance-none [&_ul[data-type=taskList]_li_label_input]:size-4 [&_ul[data-type=taskList]_li_label_input]:rounded-sm [&_ul[data-type=taskList]_li_label_input]:ring [&_ul[data-type=taskList]_li_label_input]:ring-inset [&_ul[data-type=taskList]_li_label_input]:ring-accented [&_ul[data-type=taskList]_li_label_input]:bg-center",
          "[&_ul[data-type=taskList]_li_label_input:checked]:bg-primary [&_ul[data-type=taskList]_li_label_input:checked]:ring-primary [&_ul[data-type=taskList]_li_label_input:checked]:bg-[url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIwIDZMOSAxN2wtNS01Ii8+PC9zdmc+)] dark:[&_ul[data-type=taskList]_li_label_input:checked]:bg-[url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImJsYWNrIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIwIDZMOSAxN2wtNS01Ii8+PC9zdmc+)]",
          "[&_ul[data-type=taskList]_li[data-checked=true]>div>p]:line-through [&_ul[data-type=taskList]_li[data-checked=true]>div>p]:opacity-50",
        ],
      },
    },
  },
});
