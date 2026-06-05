import { Node, mergeAttributes } from "@tiptap/core";
import type { CommandProps, NodeViewRenderer } from "@tiptap/core";
import { VueNodeViewRenderer } from "@tiptap/vue-3";
import { NotesImage } from "#components";

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    imageUpload: {
      insertImageUpload: () => ReturnType;
    };
  }
}

export const ImageUpload = Node.create({
  name: "imageUpload",
  group: "block",
  atom: true,
  draggable: true,
  addAttributes() {
    return {};
  },
  parseHTML() {
    return [
      {
        tag: 'div[data-type="image-upload"]',
      },
    ];
  },
  renderHTML({ HTMLAttributes }) {
    return [
      "div",
      mergeAttributes(HTMLAttributes, { "data-type": "image-upload" }),
    ];
  },
  addNodeView(): NodeViewRenderer {
    return VueNodeViewRenderer(NotesImage);
  },
  addCommands() {
    return {
      insertImageUpload:
        () =>
        ({ commands }: CommandProps) => {
          return commands.insertContent({ type: this.name });
        },
    };
  },
});

export default ImageUpload;
