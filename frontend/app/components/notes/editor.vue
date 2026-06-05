<template>
  <UEditor
    :key="`editor-${entityId}`"
    v-slot="{ editor, handlers }"
    v-model="modelValue"
    placeholder="Start writing or type / for commands..."
    content-type="markdown"
    :mention="false"
    :editable="canEdit"
    class="w-full"
    :extensions="extensions"
    :handlers="customHandlers"
    :starter-kit="{ link: { openOnClick: true }, codeBlock: false }"
  >
    <UEditorDragHandle
      v-slot="{ ui, onClick }"
      :editor="editor"
      aria-hidden="true"
      @node-change="selectedNode = $event"
    >
      <UButton
        icon="i-lucide-plus"
        color="neutral"
        variant="ghost"
        size="sm"
        aria-label="Add block"
        :class="ui.handle()"
        @click="
          (e) => {
            e.stopPropagation();

            const selected = onClick();
            handlers.suggestion?.execute(editor, { pos: selected?.pos }).run();
          }
        "
      />
      <UDropdownMenu
        v-slot="{ open }"
        :modal="false"
        :items="dragHandleItems(editor)"
        :content="{ side: 'left' }"
        :ui="{ content: 'w-48', label: 'text-xs' }"
        @update:open="editor.chain().setMeta('lockDragHandle', $event).run()"
      >
        <UButton
          icon="i-lucide-grip-vertical"
          variant="ghost"
          color="neutral"
          active-variant="soft"
          size="sm"
          aria-label="Drag to reorder block"
          :active="open"
          :class="ui.handle()"
        />
      </UDropdownMenu>
    </UEditorDragHandle>
    <UEditorEmojiMenu
      :editor="editor"
      :items="gitHubEmojis"
      :append-to="appendToBody"
    />
    <UEditorSuggestionMenu
      :editor="editor"
      :items="[
        [{ type: 'label', label: 'Basic' }, ...textItems],
        [{ type: 'label', label: 'Lists' }, ...listItems],
        [
          { type: 'label', label: 'Insert' },
          ...insertItems.filter((i) => !['Link', 'Code'].includes(i.label)),
        ],
      ]"
      :append-to="appendToBody"
    />
    <UEditorToolbar
      :editor="editor"
      :items="tableBubbleItems(editor)"
      layout="bubble"
      :should-show="
        ({ editor, view }: any) => {
          return (
            editor.state.selection instanceof CellSelection && view.hasFocus()
          );
        }
      "
    />
    <UEditorToolbar
      :editor="editor"
      :items="imageBubbleItems(editor)"
      layout="bubble"
      :should-show="
        ({ editor, view }: any) => {
          return editor.isActive('image') && view.hasFocus();
        }
      "
    />
    <UEditorToolbar
      :editor="editor"
      layout="bubble"
      :append-to="appendToBody"
      :items="[
        [
          {
            icon: 'i-lucide-type',
            content: { align: 'start' },
            tooltip: { text: 'Text style' },
            items: textItems,
          },
        ],
        styleItems,
        insertItems
          .filter(
            (i) =>
              !['Image', 'Divider', 'Code Block', 'Table'].includes(i.label),
          )
          .map((i) => {
            return {
              kind: i.kind,
              mark: i.mark,
              slot: i.slot,
              icon: i.icon,
              tooltip: i.tooltip,
            };
          }),
        listItems.map((i) => {
          return {
            kind: i.kind,
            mark: i.mark,
            slot: i.slot,
            icon: i.icon,
            tooltip: i.tooltip,
          };
        }),
      ]"
      :should-show="
        ({ editor, view, state }: any) => {
          if (
            editor.isActive('imageUpload') ||
            editor.isActive('image') ||
            state.selection instanceof CellSelection
          ) {
            return false;
          }
          const { selection } = state;
          return view.hasFocus() && !selection.empty;
        }
      "
    >
      <template #link>
        <NotesLink :editor="editor" auto-open />
      </template>
    </UEditorToolbar>
  </UEditor>
</template>

<script setup lang="ts">
import type { Editor, JSONContent } from "@tiptap/vue-3";
import { gitHubEmojis } from "@tiptap/extension-emoji";
import { TaskList } from "@tiptap/extension-list/task-list";
import { TaskItem } from "@tiptap/extension-list/task-item";
import { CodeBlockShiki } from "tiptap-extension-code-block-shiki";
import type {
  EditorToolbarItem,
  DropdownMenuItem,
  EditorCustomHandlers,
} from "@nuxt/ui";
import { mapEditorItems } from "@nuxt/ui/utils/editor";
import { ImageUpload } from "~/components/notes/extensions/EditorImageUpload";
import { TableKit } from "@tiptap/extension-table";
import { CellSelection } from "@tiptap/pm/tables";

defineProps<{ entityId: string | number; canEdit: boolean }>();
const modelValue = defineModel<string>();

const selectedNode = ref<{ node: JSONContent; pos: number }>();
const appendToBody = import.meta.client ? () => document.body : undefined;
const customHandlers = {
  imageUpload: {
    canExecute: (editor: Editor) =>
      editor.can().insertContent({ type: "imageUpload" }),
    execute: (editor: Editor) =>
      editor.chain().focus().insertContent({ type: "imageUpload" }),
    isActive: (editor: Editor) => editor.isActive("imageUpload"),
    isDisabled: undefined,
  },
  table: {
    canExecute: (editor: Editor) => editor.can().insertTable(),
    execute: (editor: Editor) =>
      editor
        .chain()
        .focus()
        .insertTable({ rows: 3, cols: 3, withHeaderRow: true }),
    isActive: (editor: Editor) => editor.isActive("table"),
    isDisabled: undefined,
  },
} satisfies EditorCustomHandlers;
const extensions = [
  CodeBlockShiki.configure({
    themes: { light: "github-dark", dark: "github-light" },
  }),
  ImageUpload,
  TableKit,
  TaskItem,
  TaskList,
];
const textItems = [
  { kind: "paragraph", label: "Paragraph", icon: "i-lucide-type" },
  {
    kind: "heading",
    level: 1,
    label: "Heading 1",
    icon: "i-lucide-heading-1",
  },
  {
    kind: "heading",
    level: 2,
    label: "Heading 2",
    icon: "i-lucide-heading-2",
  },
  {
    kind: "heading",
    level: 3,
    label: "Heading 3",
    icon: "i-lucide-heading-3",
  },
  {
    kind: "heading",
    level: 4,
    label: "Heading 4",
    icon: "i-lucide-heading-4",
  },
  {
    kind: "heading",
    level: 5,
    label: "Heading 5",
    icon: "i-lucide-heading-5",
  },
];
const listItems = [
  {
    kind: "bulletList",
    label: "Bullet List",
    icon: "i-lucide-list",
    tooltip: { text: "Bullet List" },
  },
  {
    kind: "orderedList",
    label: "Numbered List",
    icon: "i-lucide-list-ordered",
    tooltip: { text: "Numbered List" },
  },
  {
    kind: "taskList",
    label: "To-Do List",
    icon: "i-lucide-list-todo",
    tooltip: { text: "To-Do List" },
  },
];
const styleItems = [
  {
    kind: "mark",
    mark: "bold",
    icon: "i-lucide-bold",
    tooltip: { text: "Bold" },
  },
  {
    kind: "mark",
    mark: "italic",
    icon: "i-lucide-italic",
    tooltip: { text: "Italic" },
  },
  {
    kind: "mark",
    mark: "underline",
    icon: "i-lucide-underline",
    tooltip: { text: "Underline" },
  },
  {
    kind: "mark",
    mark: "strike",
    icon: "i-lucide-strikethrough",
    tooltip: { text: "Strikethrough" },
  },
];
const insertItems = [
  {
    kind: "imageUpload",
    icon: "i-lucide-image",
    label: "Image",
    tooltip: { text: "Image" },
  },
  {
    kind: "table",
    icon: "i-lucide-table",
    label: "Table",
    tooltip: { text: "Table" },
  },
  {
    kind: "blockquote",
    label: "Quote",
    icon: "i-mdi-format-quote-open",
    tooltip: { text: "Quote" },
  },
  {
    kind: "codeBlock",
    label: "Code Block",
    icon: "i-lucide-square-code",
    tooltip: { text: "Code Block" },
  },
  {
    kind: "mark",
    mark: "code",
    label: "Code",
    icon: "i-lucide-code",
    tooltip: { text: "Code" },
  },
  {
    kind: "link",
    slot: "link",
    label: "Link",
    icon: "i-lucide-link",
    tooltip: { text: "Link" },
  },
  {
    kind: "horizontalRule",
    label: "Divider",
    icon: "i-lucide-minus",
    tooltip: { text: "Divider" },
  },
];

function tableBubbleItems(editor: Editor) {
  return [
    [
      {
        icon: "i-lucide-table-cells-merge",
        tooltip: { text: "Merge cells" },
        onClick: () => {
          editor.chain().focus().mergeCells().run();
        },
      },
      {
        icon: "i-lucide-table-cells-split",
        tooltip: { text: "Split cells" },
        onClick: () => {
          editor.chain().focus().splitCell().run();
        },
      },
    ],
    [
      {
        icon: "material-symbols:add-row-above",
        tooltip: { text: "Add row above" },
        onClick: () => {
          editor.chain().focus().addRowBefore().run();
        },
      },
      {
        icon: "material-symbols:add-row-below",
        tooltip: { text: "Add row below" },
        onClick: () => {
          editor.chain().focus().addRowAfter().run();
        },
      },
      {
        icon: "i-lucide-x",
        tooltip: { text: "Delete row" },
        onClick: () => {
          editor.chain().focus().deleteRow().run();
        },
      },
    ],
    [
      {
        icon: "material-symbols:add-column-left",
        tooltip: { text: "Add column before" },
        onClick: () => {
          editor.chain().focus().addColumnBefore().run();
        },
      },
      {
        icon: "material-symbols:add-column-right",
        tooltip: { text: "Add column after" },
        onClick: () => {
          editor.chain().focus().addColumnAfter().run();
        },
      },
      {
        icon: "i-lucide-x",
        tooltip: { text: "Delete column" },
        onClick: () => {
          editor.chain().focus().deleteColumn().run();
        },
      },
    ],
    [
      {
        icon: "i-lucide-trash",
        tooltip: { text: "Delete table" },
        onClick: () => {
          editor.chain().focus().deleteTable().run();
        },
      },
    ],
  ] as EditorToolbarItem[][];
}

function imageBubbleItems(editor: Editor) {
  const node = editor.state.doc.nodeAt(editor.state.selection.from);
  return [
    [
      {
        icon: "i-lucide-download",
        to: node?.attrs?.src,
        download: "image",
        tooltip: { text: "Download" },
      },
      {
        icon: "i-lucide-image-up",
        tooltip: { text: "Replace" },
        onClick: () => {
          const { state } = editor;
          const { selection } = state;
          const pos = selection.from;
          const imageNode = state.doc.nodeAt(pos);
          if (imageNode && imageNode.type.name === "image") {
            editor
              .chain()
              .focus()
              .deleteRange({ from: pos, to: pos + imageNode.nodeSize })
              .insertContentAt(pos, { type: "imageUpload" })
              .run();
          }
        },
      },
    ],
    [
      {
        icon: "i-lucide-trash",
        tooltip: { text: "Delete" },
        onClick: () => {
          const { state } = editor;
          const { selection } = state;

          const pos = selection.from;
          const imageNode = state.doc.nodeAt(pos);

          if (imageNode && imageNode.type.name === "image") {
            editor
              .chain()
              .focus()
              .deleteRange({ from: pos, to: pos + imageNode.nodeSize })
              .run();
          }
        },
      },
    ],
  ] as EditorToolbarItem[][];
}

function dragHandleItems(editor: Editor) {
  if (!selectedNode.value?.node?.type) return [];
  const label = {
    type: "label",
    label: firstUpper(selectedNode.value.node.type),
  };
  const modificable = !["image", "table"].includes(
    selectedNode.value?.node?.type,
  );
  return mapEditorItems(editor, [
    modificable
      ? [
          label,
          {
            label: "Turn into",
            icon: "i-lucide-repeat-2",
            children: [
              ...textItems,
              ...insertItems.filter(
                (i) =>
                  !["Image", "Divider", "Code Block", "Table", "Link"].includes(
                    i.label,
                  ),
              ),
              ...listItems,
            ],
          },
          {
            kind: "clearFormatting",
            pos: selectedNode.value?.pos,
            label: "Clear formatting",
            icon: "i-lucide-rotate-ccw",
          },
        ]
      : [],
    [
      ...(modificable ? [] : [label]),
      {
        kind: "duplicate",
        pos: selectedNode.value?.pos,
        label: "Duplicate",
        icon: "i-lucide-copy",
      },
      {
        kind: "moveUp",
        pos: selectedNode.value?.pos,
        label: "Move up",
        icon: "i-lucide-arrow-up",
      },
      {
        kind: "moveDown",
        pos: selectedNode.value?.pos,
        label: "Move down",
        icon: "i-lucide-arrow-down",
      },
    ],
    [
      {
        kind: "delete",
        pos: selectedNode.value?.pos,
        label: "Delete",
        icon: "i-lucide-trash",
        color: "error",
      },
    ],
  ] as DropdownMenuItem[][]);
}
</script>
