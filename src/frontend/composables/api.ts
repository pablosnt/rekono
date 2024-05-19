export function useApi(
  endpoint: string,
  authentication: boolean = true,
  entity?: string,
) {
  const user = userStore();
  const refreshing = refreshStore();
  const tokens = useTokens();
  const config = useRuntimeConfig();
  const alert = useAlert();

  const defaultHeaders = {
    Accept: "application/json",
  };

  const default_size = 24;
  const max_size = 1000;
  let total = 0;

  function url(endpoint: string, extraPath?: string): string {
    let currentEndpoint = config.backendRootPath
      ? config.backendRootPath + endpoint
      : endpoint;
    if (extraPath) {
      currentEndpoint = `${currentEndpoint}/${extraPath}`;
    }
    if (config.backendUrl) {
      const url = new URL(config.backendUrl);
      url.pathname = currentEndpoint;
      return url.href;
    }
    return currentEndpoint;
  }

  function headers(authentication: boolean, extraHeaders?: object): object {
    const currentHeaders = defaultHeaders;
    const token = tokens.get().access;
    if (authentication) {
      if (!token) {
        forwardToLogin();
      }
      currentHeaders.Authorization = `Bearer ${token}`;
    }
    return Object.assign({}, currentHeaders, extraHeaders);
  }

  function request(
    endpoint: string,
    options = {},
    extraPath?: string,
    extraHeaders?: object,
  ): Promise {
    return $fetch(url(endpoint, extraPath), options).catch((error) => {
      let message = "Unexpected error";
      switch (error.statusCode) {
        case 400: {
          const firstValue = Object.values(error.data)[0];
          const value = Array.isArray(firstValue) ? firstValue[0] : firstValue;
          const field = Object.keys(error.data)[0];
          const body = `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
          message = field !== "non_field_errors" ? `${field}: ${body}` : body;
          break;
        }
        case 401:
          if (endpoint.includes("/api/security/refresh/")) {
            return Promise.reject(error);
          } else if (authentication) {
            if (refreshing.refreshing) {
              setTimeout(
                () => (options.headers = headers(authentication, extraHeaders)),
                1500,
              );
              return request(endpoint, options, extraPath, extraHeaders);
            } else {
              return refresh().then(() => {
                options.headers = headers(authentication, extraHeaders);
                return request(endpoint, options, extraPath, extraHeaders);
              });
            }
          } else {
            message = "Invalid credentials";
          }
          break;
        case 403:
          message = "You are not authorized to perform this operation";
          break;
        case 404:
          message = "Resource not found";
          break;
        case 429:
          message = "Too many requests";
          break;
      }
      if (message) {
        alert(message, "error");
      }
      return Promise.reject(error);
    });
  }

  function forwardToLogin(): Promise {
    tokens.remove();
    user.logout();
    if (refreshing.refreshing) {
      refreshing.change();
    }
    return navigateTo("/login");
  }

  function refresh(): Promise {
    refreshing.change();
    const refresh = tokens.get().refresh;
    if (!refresh) {
      forwardToLogin();
    } else {
      return request("/api/security/refresh/", {
        method: "POST",
        headers: headers(true),
        body: { refresh: refresh },
      })
        .then((response) => {
          tokens.remove();
          tokens.save(response);
          refreshing.change();
          return Promise.resolve();
        })
        .catch(() => {
          forwardToLogin();
          return Promise.reject();
        });
    }
  }

  function get(
    id?: number,
    extraPath?: string,
    extraHeaders?: object,
  ): Promise {
    return request(
      id ? `${endpoint}${id}/` : endpoint,
      { method: "GET", headers: headers(authentication, extraHeaders) },
      extraPath,
      extraHeaders,
    ).then((response) => {
      return Promise.resolve(response);
    });
  }

  function list(
    params = {},
    all = false,
    page = 1,
    items = [],
    extraPath?: string,
    extraHeaders?: object,
  ): Promise {
    const size = all ? max_size : default_size;
    return request(
      endpoint,
      {
        method: "GET",
        headers: headers(authentication, extraHeaders),
        params: Object.assign({}, params, { page: page, limit: size }),
      },
      extraPath,
      extraHeaders,
    ).then((response) => {
      total = response.count;
      if (all) {
        items = items.concat(response.results);
        if (page * size < total) {
          return list(params, all, page + 1);
        }
      } else {
        items = response.results;
      }
      return Promise.resolve({ items: items, total: total });
    });
  }

  function create(
    body: object,
    id?: number,
    extraPath?: string,
    extraHeaders?: object,
  ) {
    return request(
      id ? `${endpoint}${id}/` : endpoint,
      {
        method: "POST",
        headers: headers(authentication, extraHeaders),
        body: body,
      },
      extraPath,
      extraHeaders,
    ).then((response) => {
      if (response) {
        if (entity && !extraPath) {
          alert(
            `New ${entity.toLowerCase()} has been successfully created`,
            "success",
          );
        }
      }
      return Promise.resolve(response);
    });
  }

  function update(
    body: object,
    id?: number,
    extraPath?: string,
    extraHeaders?: object,
  ) {
    return request(
      id ? `${endpoint}${id}/` : endpoint,
      {
        method: "PUT",
        headers: headers(authentication, extraHeaders),
        body: body,
      },
      extraPath,
      extraHeaders,
    ).then((response) => {
      if (response) {
        if (entity && !extraPath) {
          alert(`${entity} has been successfully updated`, "success");
        }
      }
      return Promise.resolve(response);
    });
  }

  function remove(id?: number, extraPath?: string, extraHeaders?: object) {
    return request(
      id ? `${endpoint}${id}/` : endpoint,
      { method: "DELETE", headers: headers(authentication, extraHeaders) },
      extraPath,
      extraHeaders,
    ).then(() => {
      if (entity && !extraPath) {
        alert(`${entity} has been deleted`, "warning");
      }
      return Promise.resolve();
    });
  }

  return { get, list, create, update, remove, default_size, entity };
}
