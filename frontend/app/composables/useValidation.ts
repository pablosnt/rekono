import * as z from "zod";

export default function () {
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

  return { passwordPolicy };
}
