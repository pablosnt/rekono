export const useToastPosition = () =>
  useState<"bottom-right" | "bottom-left">(
    "toast-position",
    () => "bottom-right",
  );
