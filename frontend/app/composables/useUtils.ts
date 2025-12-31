import type { FilterOption } from "~/types/crud";
import type { User } from "~/types/users";
import { useUserStore } from "~/store/user";

export default function () {
  function firstUpper(value: string) {
    return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
  }

  const stageOptions = [
    { label: "OSINT", value: 1, icon: "i-lucide-globe" },
    { label: "Enumeration", value: 2, icon: "i-lucide-network" },
    { label: "Vulnerabilities", value: 3, icon: "i-lucide-bug" },
    { label: "Services", value: 4, icon: "i-lucide-server" },
    { label: "Exploitation", value: 5, icon: "i-lucide-flame" },
  ];

  function getUserOptions(
    userOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    const userStore = useUserStore();
    useApi("/api/users/")
      .list("", queryParams, true)
      .then((response) => {
        if (userOptionsRef.value.length === 0) {
          userOptionsRef.value = [
            {
              label: "Current user",
              value: userStore.user,
            },
          ];
        }
        userOptionsRef.value = [
          ...userOptionsRef.value,
          ...(response.items as User[])
            .filter((user) => user.id.toString() !== userStore.user)
            .map((user) => ({
              label: user.username,
              value: user.id,
              avatar: {
                text: user.username.charAt(0).toUpperCase(),
                class: "bg-muted text-foreground",
              },
            })),
        ];
      })
      .catch(() => {
        userOptionsRef.value = [];
      });
  }

  function getToolOptions(
    toolOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    useApi("/api/tools/")
      .list("", queryParams, true)
      .then((response) => {
        toolOptionsRef.value = (response.items as Tool[]).map((tool) => ({
          avatar: tool.icon ? { src: tool.icon } : undefined,
          label: tool.name,
          value: tool.id,
        }));
      });
  }

  return { firstUpper, stageOptions, getUserOptions, getToolOptions };
}
