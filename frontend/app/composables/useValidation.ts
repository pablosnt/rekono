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

  function regex(
    field: string,
    required: boolean,
    max: number | undefined,
    regex: RegExp,
  ) {
    let policy = required
      ? z.string(`${utils.firstUpper(field)} is required`).min(1)
      : z.string();
    if (max) {
      policy = policy.max(max);
    }
    policy = policy.refine((value) => regex.test(value), {
      message: `Invalid ${field.toLowerCase()}`,
    });
    return required ? policy : policy.optional();
  }

  function name(
    field: string = "name",
    required: boolean = true,
    max: number = 120,
  ) {
    return regex(field, required, max, /^[\wÀ-ÿ\s.:\-[\]()@]*$/);
  }

  function text(field: string, required: boolean = true) {
    return regex(field, required, undefined, /^[^;<>]*$/);
  }

  function cve(
    field: string = "cve",
    required: boolean = true,
    max: number = 20,
  ) {
    return regex(field, required, max, /^CVE-\d{4}-\d{1,7}$/);
  }

  function target(
    field: string = "target",
    required: boolean = true,
    max: number = 100,
  ) {
    return regex(field, required, max, /^[\w\d.:\-/]{1,100}$/);
  }

  function target_regex(
    field: string = "target",
    required: boolean = true,
    max: number = 100,
  ) {
    return regex(field, required, max, /^[\w\d.,:\-/*?+()\\]{1,300}$/);
  }

  function secret(
    field: string = "secret",
    required: boolean = true,
    max: number = 500,
  ) {
    return regex(
      field,
      required,
      max,
      /^[\w\s./\-=+,:<>¿?¡!#&$()@%[\]{}*]{1,500}$/,
    );
  }

  return { passwordPolicy, name, text, cve, target, target_regex, secret };
}
