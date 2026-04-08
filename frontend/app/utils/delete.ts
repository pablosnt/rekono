import type { ComponentDetails } from "~/types/crud";

// TODO: Test

export function buildDeleteMessage(
  entityType: string,
  targetEntity: string | undefined = undefined,
  warningTitle: string | undefined = undefined,
  warningDescription: string | undefined = undefined,
  verb: string = "delete",
): ComponentDetails[] {
  return [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        `Are you sure you want to ${verb} this ${smartLowerCase(entityType)}?`,
      ),
    },
    targetEntity
      ? {
          component: resolveComponent("UAlert"),
          props: {
            color: "neutral",
            variant: "subtle",
            description: targetEntity,
            ui: { root: "text-center font-bold" },
            class: "mt-4",
          },
        }
      : {},
    warningTitle || warningDescription
      ? {
          component: resolveComponent("UAlert"),
          props: {
            color: "error",
            icon: "i-lucide-triangle-alert",
            title: warningTitle,
            description: warningDescription,
            class: "mt-4",
          },
        }
      : {},
  ].filter((i) => Object.keys(i).length > 0);
}
