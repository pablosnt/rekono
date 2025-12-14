import { useUserStore } from "~/store/user";

export default function (
  base_endpoint: string = "/api/",
  authentication: boolean = true,
) {
  const config = useRuntimeConfig();
  const toast = useToast();
  const utils = useUtils();
  const defaultHeaders = { Accept: "application/json" };

  function url(endpoint: string): string {
    endpoint =
      endpoint.startsWith(base_endpoint) ||
      endpoint === "/api/security/refresh/"
        ? endpoint
        : base_endpoint + endpoint;
    endpoint = config.backendRootPath
      ? config.backendRootPath + endpoint
      : endpoint;
    if (config.backendUrl) {
      const url = new URL(config.backendUrl);
      url.pathname = endpoint;
      return url.href;
    }
    return endpoint;
  }

  function headers(extra?: object = {}): object {
    const headers = defaultHeaders;
    if (authentication) {
      const tokens = useTokens();
      const jwt = tokens.get().access;
      if (!jwt) {
        forwardToLogin();
      }
      headers.Authorization = `Bearer ${jwt}`;
    }
    return Object.assign({}, headers, extra);
  }

  function forwardToLogin(): Promise {
    const tokens = useTokens();
    const user = useUserStore();
    tokens.remove();
    user.logout();
    if (user.refreshing) {
      user.refresh();
    }
    return navigateTo("/login");
  }

  function parseErrorMessage(
    error: object,
    include_field: boolean = true,
  ): string {
    const field = Object.keys(error.data)[0];
    let value = Object.values(error.data)[0];
    value = Array.isArray(value) ? value[0] : value;
    const message = utils.firstUpper(value);
    return field !== "non_field_errors" && include_field
      ? `${field}: ${message}`
      : message;
  }

  function request(
    endpoint: string,
    options?: object,
    extraHeaders?: object,
    raw?: boolean = false,
  ): Promise {
    options.headers = headers(extraHeaders);
    return (
      raw ? $fetch.raw(url(endpoint), options) : $fetch(url(endpoint), options)
    ).catch((error) => {
      let message = "Unexpected error";
      switch (error.statusCode) {
        case 400: {
          message = parseErrorMessage(error);
          break;
        }
        case 401: {
          if (
            endpoint.includes("/api/security/refresh/") ||
            (error.data.detail &&
              error.data.detail === "Incorrect authentication credentials." &&
              (endpoint.includes("/api/profile/mfa/enable/") ||
                endpoint.includes("/api/profile/mfa/disable/") ||
                endpoint.includes("/api/telegram/link/") ||
                endpoint.includes("/api/profile/update-password/")))
          ) {
            return Promise.reject(error);
          } else if (authentication) {
            const user = useUserStore();
            if (user.refreshing) {
              function wait(): Promise {
                return new Promise((resolve, reject) => {
                  setTimeout(() => {
                    if (user.refreshing) {
                      return wait();
                    }
                    request(endpoint, options, headers, raw)
                      .then((response) => resolve(response))
                      .catch((error) => reject(error));
                  }, 500);
                });
              }
              return wait();
            } else {
              return refresh().then(() => {
                return request(endpoint, options, headers, raw);
              });
            }
          } else {
            message = "Invalid credentials";
          }
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
      toast.add({
        title: "Error",
        description: message,
        color: "error",
      });
      return Promise.reject(error);
    });
  }

  function refresh(): Promise {
    const tokens = useTokens();
    const user = useUserStore();
    user.refresh();
    const refresh = tokens.get().refresh;
    if (!refresh) {
      forwardToLogin();
      return Promise.reject();
    } else {
      return request("/api/security/refresh/", {
        method: "POST",
        body: { refresh: refresh },
      })
        .then((response) => {
          tokens.remove();
          tokens.login(response);
          user.refresh();
          return Promise.resolve();
        })
        .catch(() => {
          forwardToLogin();
          return Promise.reject();
        });
    }
  }

  function list(
    endpoint: string,
    params: object = {},
    all: boolean = false,
    page: number = 1,
    size: number = 24,
    extraHeaders?: object,
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
      return Promise.resolve({ items: items, total: total });
    });
  }

  function get(endpoint: string, extraHeaders?: object): Promise {
    return request(endpoint, { method: "GET" }, extraHeaders).then(
      (response) => {
        return Promise.resolve(response);
      },
    );
  }

  function download(endpoint: string, extraHeaders?: object): Promise {
    return request(
      endpoint,
      { method: "GET", responseType: "blob" },
      extraHeaders,
      true,
    ).then((response) => {
      const a = document.createElement("a");
      a.href = window.URL.createObjectURL(response._data);
      a.download = response.headers
        .get("content-disposition")
        .replace('attachment; filename="', "")
        .replace('"', "");
      a.click();
    });
  }

  function create(
    endpoint: string,
    body: object,
    extraHeaders?: object,
    entity?: string,
  ): Promise {
    return request(endpoint, { method: "POST", body: body }, extraHeaders).then(
      (response) => {
        if (entity) {
          toast.add({
            description: `${entity} has been successfully created`,
            color: "success",
          });
        }
        return Promise.resolve(response);
      },
    );
  }

  function update(
    endpoint: string,
    body: object,
    extraHeaders?: object,
    entity?: string,
  ): Promise {
    return request(endpoint, { method: "PUT", body: body }, extraHeaders).then(
      (response) => {
        if (entity) {
          toast.add({
            description: `${entity} has been successfully updated`,
            color: "success",
          });
        }
        return Promise.resolve(response);
      },
    );
  }

  function remove(
    endpoint: string,
    extraHeaders?: object,
    entity?: string,
  ): Promise {
    return request(endpoint, { method: "DELETE" }, extraHeaders).then(() => {
      if (entity) {
        toast.add({
          description: `${entity} has been deleted`,
          color: "warning",
        });
      }
      return Promise.resolve();
    });
  }

  return { get, list, download, create, update, remove, forwardToLogin };
}
