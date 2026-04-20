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

  function findingCell(
    entity: Finding | undefined,
    subpath: string,
    value: string | undefined,
    project: number,
    icon: string | undefined = undefined,
    color: string = "neutral",
  ) {
    return entity
      ? h(
          "a",
          {
            href: `/projects/${project}/${subpath}/${entity.id}`,
            class:
              "flex items-center gap-2 font-medium hover:text-primary hover:underline",
            onClick: (e: Event) => e.stopPropagation(),
          },
          icon
            ? [h(UIcon, { name: icon, class: `text-lg text-${color}` }), value]
            : [value],
        )
      : noDataCell;
  }

  function hostCell(host: Finding | undefined, project: number) {
    const config = host
      ? hostOS.find((c) => c.value === host.os_type)
      : undefined;
    return findingCell(
      host,
      "hosts",
      host?.domain || host?.ip,
      project,
      config?.icon || "i-lucide-server",
      config?.color || "neutral",
    );
  }

  function portCell(port: Finding | undefined, project: number) {
    return findingCell(
      port,
      "ports",
      port?.port ? port?.port.toString() : undefined,
      project,
      port ? getPortIcon(port.port, port.service) : undefined,
    );
  }

  function technologyCell(technology: Finding | undefined, project: number) {
    return findingCell(
      technology,
      "technologies",
      technology ? `${technology.name} - ${technology.version}` : undefined,
      project,
    );
  }

  function vulnerabilityCell(
    vulnerability: Finding | undefined,
    project: number,
  ) {
    return findingCell(
      vulnerability,
      "vulnerabilities",
      vulnerability?.name,
      project,
    );
  }

  function toolCell(
    tool: Tool,
    configuration: Configuration | undefined,
    link: string | undefined = undefined,
  ) {
    const baseClass = "flex items-center gap-2";
    return h(
      link ? "a" : "div",
      link
        ? {
            class: `${baseClass} hover:text-primary hover:underline`,
            href: link,
          }
        : { class: baseClass },
      [
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
      ],
    );
  }

  function counterCell(count: number, link: string, internal: boolean = true) {
    return count === 0
      ? valueCell("0", "text-muted-foreground")
      : linkCell(link, undefined, count.toString(), internal);
  }

  function linkCell(
    link: string | undefined,
    icon: string | undefined = undefined,
    avatar: string | undefined = undefined,
    text: string | undefined = undefined,
    internal: boolean = true,
  ) {
    if (!link) return noDataCell;
    const iconItem = icon
      ? h(UIcon, {
          name: icon,
          class: "text-lg",
        })
      : undefined;
    const textItem = text ? valueCell(text) : undefined;
    const linkConfig = {
      href: link,
      class: `hover:text-primary hover:underline ${iconItem && textItem ? "flex items-center gap-2" : ""}`,
      onClick: (e: Event) => e.stopPropagation(),
    };
    if (!internal) {
      linkConfig["target"] = "_blank";
      linkConfig["rel"] = "noopener noreferrer";
    }
    return h(
      "a",
      linkConfig,
      [
        iconItem,
        avatar ? h(UAvatar, { src: avatar }) : undefined,
        textItem,
      ].filter((i) => i !== undefined),
    );
  }

  function externalLinkCell(
    link: string | undefined,
    icon: string | undefined = undefined,
    avatar: string | undefined = undefined,
    text: string | undefined = undefined,
  ) {
    return linkCell(link, icon, avatar, text, false);
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
    vulnerabilityCell,
    toolCell,
    counterCell,
    linkCell,
    externalLinkCell,
    usernameCell,
  };
}
