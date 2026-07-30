import type { Configuration, Finding, Tool, User } from "~/types/models";
import { hostOS } from "~/constants";
import { UAvatar, UBadge, UIcon, UButton } from "#components";

function valueCell(value?: string | number, extraClasses?: string) {
  return h(
    "span",
    { class: extraClasses ? `font-medium ${extraClasses}` : "font-medium" },
    value || "—",
  );
}

export default function () {
  const noDataCell = valueCell();

  function iconAndValueHeader(value: string, icon: string) {
    return iconAndValueCell(icon, value, "gray-500 dark:text-gray-400", true);
  }

  function iconAndValueCell(
    icon: string,
    value?: string | number,
    color: string = "neutral",
    isHeader?: boolean,
  ) {
    return value
      ? h("div", { class: "flex items-center gap-2" }, [
          h(UIcon, { name: icon, class: `w-4 h-4 text-${color}` }),
          isHeader ? h("span", value) : valueCell(value),
        ])
      : noDataCell;
  }

  function badgeCell(
    value: string | number | undefined,
    icon?: string,
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
    icon?: string,
    color: string = "neutral",
  ) {
    return entity && value
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
      port?.port
        ? port.protocol
          ? `${port.port}/${port.protocol}`
          : port.port.toString()
        : undefined,
      project,
      port ? getPortIcon(port.port, port.service) : undefined,
    );
  }

  function technologyCell(technology: Finding | undefined, project: number) {
    return findingCell(
      technology,
      "technologies",
      technology
        ? technology.name && technology.version
          ? `${technology.name} - ${technology.version}`
          : technology.name
        : undefined,
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
    link?: string,
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
              alt: tool.name,
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
      : linkCell(
          link,
          undefined,
          undefined,
          formatCount(count),
          internal,
          undefined,
          "px-0",
        );
  }

  function linkCell(
    link?: string,
    icon?: string,
    avatar?: string,
    text?: string,
    internal: boolean = true,
    ariaLabel?: string,
    extraClass?: string,
  ) {
    return link
      ? h(UButton, {
          to: link,
          class: `hover:text-primary hover:underline${extraClass ? ` ${extraClass}` : ""}`,
          icon,
          avatar: avatar
            ? { src: avatar, alt: text || ariaLabel || "" }
            : undefined,
          target: internal ? undefined : "_blank",
          label: text,
          variant: "ghost",
          color: "neutral",
          "aria-label": ariaLabel || text || "",
        })
      : noDataCell;
  }

  function externalLinkCell(
    link?: string,
    icon?: string,
    avatar?: string,
    text?: string,
    ariaLabel?: string,
  ) {
    return linkCell(link, icon, avatar, text, false, ariaLabel);
  }

  function usernameCell(user: User) {
    return valueCell(user ? `@${user.username}` : undefined);
  }

  return {
    noDataCell,
    valueCell,
    iconAndValueHeader,
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
