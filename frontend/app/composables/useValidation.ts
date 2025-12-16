import * as z from "zod";

export default function () {
  const utils = useUtils();
  const passwordPolicy = z
    .string("Password is required")
    .min(12, "Must be at least 12 characters")
    .refine((password) => /[a-z]/.test(password), {
      message: "Must be at least one lowercase letter",
    })
    .refine((password) => /[A-Z]/.test(password), {
      message: "Must be at least one uppercase letter",
    })
    .refine((password) => /[0-9]/.test(password), {
      message: "Must be at least one digit",
    })
    .refine((password) => /\W/.test(password), {
      message: "Must be at least one symbol",
    });

  function name(
    field: string = "name",
    required: boolean = true,
    max: number = 120,
  ) {
    const policy = required
      ? z.string(`${utils.firstUpper(field)} is required`).min(1)
      : z.string();
    return policy
      .max(max)
      .refine((name) => /^[\wÀ-ÿ\s.:\-[\]()@]*$/.test(name), {
        message: `Invalid ${field.toLowerCase()}`,
      });
  }

  function text(field: string, required: boolean = true) {
    const policy = required
      ? z.string(`${utils.firstUpper(field)} is required`).min(1)
      : z.string();
    return policy.refine((text) => /^[^;<>]*$/.test(text), {
      message: `Invalid ${field.toLowerCase()}`,
    });
  }

  return { passwordPolicy, name, text };
}
