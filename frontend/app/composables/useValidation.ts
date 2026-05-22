import * as z from "zod";

function applyRegex(
  field: string,
  required: boolean,
  max: number | undefined,
  pattern: RegExp,
) {
  const fieldName = field.replaceAll("_", " ");
  let policy = required
    ? z.string(`${firstUpper(fieldName)} is required`).min(1)
    : z.string();
  if (max) {
    policy = policy.max(max);
  }
  policy = policy.refine((value) => pattern.test(value), {
    message: `Invalid ${fieldName.toLowerCase()}`,
  });
  return required ? policy : policy.optional();
}

export default function () {
  const passwordPolicy = z
    .string("Password is required")
    .min(12, "Must be at least 12 characters")
    .refine((password) => /[a-z]/u.test(password), {
      message: "Must be at least one lowercase letter",
    })
    .refine((password) => /[A-Z]/u.test(password), {
      message: "Must be at least one uppercase letter",
    })
    .refine((password) => /[0-9]/u.test(password), {
      message: "Must be at least one digit",
    })
    .refine((password) => /\W/u.test(password), {
      message: "Must be at least one symbol",
    });
  const email = z.email("Valid email is required");

  function name(
    field: string = "name",
    required: boolean = true,
    max: number = 120,
  ) {
    return applyRegex(field, required, max, /^[\wÀ-ÿ\s.:\-[\]()@]*$/u);
  }

  function text(field: string, required: boolean = true, max?: number) {
    return applyRegex(field, required, max, /^[^;<>]*$/u);
  }

  function cve(
    field: string = "cve",
    required: boolean = true,
    max: number = 20,
  ) {
    return applyRegex(field, required, max, /^CVE-\d{4}-\d{1,7}$/u);
  }

  function target(
    field: string = "target",
    required: boolean = true,
    max: number = 100,
  ) {
    return applyRegex(field, required, max, /^[\w\d.:\-/]{1,100}$/u);
  }

  function target_regex(
    field: string = "target",
    required: boolean = true,
    max: number = 100,
  ) {
    return applyRegex(field, required, max, /^[\w\d.,:\-/*?+()\\]{1,300}$/u);
  }

  function secret(
    field: string = "secret",
    required: boolean = true,
    max: number = 500,
  ) {
    return applyRegex(
      field,
      required,
      max,
      /^[\w\s./\-=+,:<>¿?¡!#&$()@%[\]{}*]{1,500}$/u,
    );
  }

  function path(
    field: string = "path",
    required: boolean = true,
    max: number = 500,
  ) {
    return applyRegex(field, required, max, /^[\w.\-_/\\]{0,500}/u);
  }

  return {
    passwordPolicy,
    name,
    text,
    cve,
    target,
    target_regex,
    secret,
    path,
    email,
  };
}
