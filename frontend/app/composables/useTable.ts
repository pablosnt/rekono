import type { Configuration, Finding, Tool, User } from "~/types/models";
import { hostOS } from "~/constants";
import { h } from "vue";
import { UAvatar, UBadge, UIcon } from "#components";

export default function () {
  const noDataCell = valueCell();

  function valueCell(
    value: string | number | undefined = undefined,
    extraClasses: string | undefined = undefined,
  ) {
    return h(
      "span",
      { class: extraClasses ? `font-medium ${extraClasses}` : "font-medium" },
      value || "—",
    );
  }

  function iconAndValueCell(
    value: string | number | undefined = undefined,
    icon: string,
    color: string = "neutral",
  ) {
    return value
      ? h("div", { class: "flex items-center gap-2" }, [
          h(UIcon, { name: icon, class: `w-4 h-4 text-${color}` }),
          valueCell(value),
        ])
      : noDataCell;
  }

  function badgeCell(
    value: string | number | undefined,
    icon: string | undefined = undefined,
    color: string = "neutral",
    variant: string = "subtle",
  ) {
    return value
      ? h(
          UBadge,
          { color: color, variant: variant },
          {
            default: () =>
              icon
                ? [
                    h(UIcon, {
                      name: icon,
                      class: "mr-1 text-lg",
                    }),
                    value,
                  ]
                : value,
          },
        )
      : noDataCell;
  }

  function hostCell(host: Finding | undefined, project: number) {
    if (host) {
      const config = hostOS.find((c) => c.value === host.os_type);
      return h(
        "a",
        {
          href: `/projects/${project}/hosts/${host.id}`,
          class:
            "flex items-center gap-2 font-medium hover:text-primary hover:underline",
          onClick: (e: Event) => e.stopPropagation(),
        },
        [
          h(UIcon, {
            name: config?.icon || "i-lucide-server",
            class: `text-lg text-${config?.color || "neutral"}`,
          }),
          host.ip || host.domain,
        ],
      );
    } else {
      return noDataCell;
    }
  }

  function portCell(port: Finding | undefined, project: number) {
    return port
      ? h(
          "a",
          {
            href: `/projects/${project}/ports/${port.id}`,
            class: "flex items-center gap-2 hover:text-primary hover:underline",
            onClick: (e: Event) => e.stopPropagation(),
          },
          [
            h(UIcon, {
              name: getPortIcon(port.port, port.service),
              class: "text-2xl",
            }),
            port.port,
          ],
        )
      : noDataCell;
  }

  function technologyCell(technology: Finding | undefined, project: number) {
    return technology
      ? h(
          "a",
          {
            href: `/projects/${project}/technologies/${technology.id}`,
            class: "font-medium hover:text-primary hover:underline",
            onClick: (e: Event) => e.stopPropagation(),
          },
          [`${technology.name} - ${technology.version}`],
        )
      : noDataCell;
  }

  function toolCell(tool: Tool, configuration: Configuration | undefined) {
    return h("div", { class: "flex items-center gap-2" }, [
      tool.icon
        ? h(UAvatar, {
            src: tool.icon,
            size: "2xs",
          })
        : h(UIcon, {
            name: "i-lucide-square-terminal",
            class: "w-4 h-4 text-muted-foreground shrink-0",
          }),
      valueCell(
        configuration ? `${tool.name}: ${configuration.name}` : tool.name,
      ),
    ]);
  }

  function counterCell(count: number, link: string, internal: boolean = true) {
    return count === 0
      ? valueCell("0", "text-muted-foreground")
      : linkCell(link, undefined, count.toString(), internal);
  }

  function linkCell(
    link: string | undefined,
    icon: string | undefined,
    text: string | undefined,
    internal: boolean = true,
  ) {
    const iconItem = icon
      ? h(UIcon, {
          name: icon,
          class: "text-lg",
        })
      : undefined;
    const textItem = text ? valueCell(text) : undefined;
    const linkConfig = {
      href: link,
      class: `hover:underline ${iconItem && textItem ? "flex items-center gap-2" : ""}`,
      onClick: (e: Event) => e.stopPropagation(),
    };
    if (internal) {
      linkConfig["class"] = `hover:text-primary ${linkConfig["class"]}`;
    } else {
      linkConfig["class"] = `text-primary ${linkConfig["class"]}`;
      linkConfig["target"] = "_blank";
      linkConfig["rel"] = "noopener noreferrer";
    }
    return link
      ? h(
          "a",
          linkConfig,
          [iconItem, textItem].filter((i) => i !== undefined),
        )
      : noDataCell;
  }

  function externalLinkCell(
    link: string | undefined,
    icon: string | undefined,
    text: string | undefined,
  ) {
    return linkCell(link, icon, text, false);
  }

  function usernameCell(user: User) {
    return valueCell(user ? `@${user.username}` : undefined);
  }

  return {
    noDataCell,
    valueCell,
    iconAndValueCell,
    badgeCell,
    hostCell,
    portCell,
    technologyCell,
    toolCell,
    counterCell,
    linkCell,
    externalLinkCell,
    usernameCell,
  };
}
