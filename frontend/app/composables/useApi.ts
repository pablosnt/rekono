import { useUserStore } from "~/store/user";

function parseErrorMessage(
  error: object,
  include_field: boolean = true,
): string {
  const field = Object.keys(error.data)[0];
  let value = Object.values(error.data)[0];
  value = Array.isArray(value) ? value[0] : value;
  const message = firstUpper(value);
  return field !== "non_field_errors" && include_field
    ? `${field}: ${message}`
    : message;
}

export default function (
  base_endpoint: string = "/api/",
  authentication: boolean = true,
) {
  const config = useRuntimeConfig();
  const toast = useToast();

  const defaultHeaders = { Accept: "application/json" };

  function url(endpoint: string): string {
    endpoint =
      endpoint.startsWith(base_endpoint) ||
      endpoint === "/api/security/refresh/"
        ? endpoint
        : base_endpoint + endpoint;
    if (config.public.backendUrl) {
      const backendUrl = new URL(config.public.backendUrl);
      if (backendUrl.pathname.endsWith("/")) {
        backendUrl.pathname = backendUrl.pathname.slice(0, -1);
      }
      backendUrl.pathname += endpoint;
      return backendUrl.href;
    }
    return endpoint;
  }

  function request(
    endpoint: string,
    options?: object,
    extraHeaders?: object,
    raw: boolean = false,
    toastOnError: number[] | null = null,
  ): Promise {
    if (toastOnError === null) {
      toastOnError = [400, 401, 403, 404, 429, 500];
    }
    const requestUrl = url(endpoint);
    options.headers = Object.assign({}, defaultHeaders, extraHeaders);
    if (authentication)
      options.credentials = config.public.backendUrl
        ? "include"
        : "same-origin";
    return (
      raw ? $fetch.raw(requestUrl, options) : $fetch(requestUrl, options)
    ).catch((error) => {
      let message = "Unexpected error";
      switch (error.statusCode) {
        case 400: {
          if (
            requestUrl.includes("/api/security/refresh/") ||
            requestUrl.includes("/api/security/logout/")
          )
            throw error;
          message = parseErrorMessage(error);
          break;
        }
        case 401: {
          if (
            requestUrl.includes("/api/security/refresh/") ||
            (error.data.detail &&
              error.data.detail === "Incorrect authentication credentials." &&
              (requestUrl.includes("/api/profile/mfa/enable/") ||
                requestUrl.includes("/api/profile/mfa/disable/") ||
                requestUrl.includes("/api/security/mfa/") ||
                requestUrl.includes("/api/telegram/link/") ||
                requestUrl.includes("/api/profile/update-password/")))
          ) {
            throw error;
          }
          if (authentication) {
            const user = useUserStore();
            if (user.refreshing) {
              const wait = (): Promise => {
                return new Promise((resolve, reject) => {
                  setTimeout(() => {
                    if (user.refreshing) {
                      return wait();
                    }
                    if (!user.is_authenticated) return reject();
                    request(endpoint, options, extraHeaders, raw, toastOnError)
                      .then((r) => resolve(r))
                      .catch((e) => reject(e));
                  }, 500);
                });
              };
              return wait();
            }
            return refresh().then(() => {
              return request(
                endpoint,
                options,
                extraHeaders,
                raw,
                toastOnError,
              );
            });
          }
          message = "Invalid credentials";
          break;
        }
        case 403: {
          message = "You are not authorized to perform this operation";
          break;
        }
        case 404: {
          message =
            endpoint.includes("/api/reports/") && options.method === "POST"
              ? parseErrorMessage(error, false)
              : "Resource not found";
          break;
        }
        case 429: {
          message = "Too many requests";
          break;
        }
      }
      if (
        toastOnError.includes(error.statusCode) ||
        (toastOnError.includes(500) && message === "Unexpected error")
      ) {
        toast.add({
          title: "Error",
          description: message,
          color: "error",
        });
      }
      throw error;
    });
  }

  function refresh(): Promise {
    const user = useUserStore();
    user.switchRefreshing();
    return request("/api/security/refresh/", {
      method: "POST",
      body: { refresh: refresh },
      credentials: true,
    })
      .then((response) => {
        user.switchRefreshing();
        return response;
      })
      .catch((error) => {
        user.logout();
        throw error;
      });
  }

  function list(
    endpoint: string,
    params: object = {},
    all: boolean = false,
    page: number = 1,
    size: number = 24,
    extraHeaders?: object,
    toastOnError: number[] | null = null,
    items: Array<object> = [],
  ): Promise {
    size = all ? 1000 : size;
    return request(
      endpoint,
      {
        method: "GET",
        params: Object.assign({}, params, { page: page, limit: size }),
      },
      extraHeaders,
      false,
      toastOnError,
    ).then((response) => {
      const total = response.count;
      if (all) {
        items = items.concat(response.results);
        if (page * size < total) {
          return list(
            endpoint,
            params,
            all,
            page + 1,
            size,
            extraHeaders,
            items,
          );
        }
      } else {
        items = response.results;
      }
      return { items: items, total: total };
    });
  }

  function get(
    endpoint: string,
    extraHeaders?: object,
    toastOnError: number[] | null = null,
  ): Promise {
    return request(
      endpoint,
      { method: "GET" },
      extraHeaders,
      false,
      toastOnError,
    );
  }

  function download(
    endpoint: string,
    extraHeaders?: object,
    toastOnError: number[] | null = null,
  ): Promise {
    return request(
      endpoint,
      { method: "GET", responseType: "blob" },
      extraHeaders,
      true,
      toastOnError,
    ).then((response) => {
      const a = document.createElement("a");
      a.href = window.URL.createObjectURL(response["_data"]);
      a.download =
        response.headers
          .get("content-disposition")
          ?.match(/filename="?([^"]+)"?/)?.[1] ?? "";
      a.click();
    });
  }

  function create(
    endpoint: string,
    body: object,
    extraHeaders?: object,
    entity?: string,
    toastOnError: number[] | null = null,
  ): Promise {
    return request(
      endpoint,
      { method: "POST", body: body },
      extraHeaders,
      false,
      toastOnError,
    ).then((response) => {
      if (entity) {
        toast.add({
          description: `${entity} has been successfully created`,
          color: "success",
        });
      }
      return response;
    });
  }

  function update(
    endpoint: string,
    body: object,
    extraHeaders?: object,
    entity?: string,
    toastOnError: number[] | null = null,
  ): Promise {
    return request(
      endpoint,
      { method: "PUT", body: body },
      extraHeaders,
      false,
      toastOnError,
    ).then((response) => {
      if (entity) {
        toast.add({
          description: `${entity} has been successfully updated`,
          color: "success",
        });
      }
      return response;
    });
  }

  function remove(
    endpoint: string,
    extraHeaders?: object,
    entity?: string,
    toastOnError: number[] | null = null,
  ): Promise {
    return request(
      endpoint,
      { method: "DELETE" },
      extraHeaders,
      false,
      toastOnError,
    ).then(() => {
      if (entity) {
        toast.add({
          description: `${entity} has been deleted`,
          color: "warning",
        });
      }
    });
  }

  return { get, list, download, create, update, remove, refresh };
}
