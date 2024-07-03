export function useApi(
  endpoint: string,
  authentication: boolean = true,
  entity?: string,
) {
  const config = useRuntimeConfig();
  const alert = useAlert();

  const defaultHeaders = {
    Accept: "application/json",
  };

  const default_size = 24;
  const max_size = 1000;
  let total = 0;

  function url(endpoint: string): string {
    const currentEndpoint = config.backendRootPath
      ? config.backendRootPath + endpoint
      : endpoint;
    if (config.backendUrl) {
      const url = new URL(config.backendUrl);
      url.pathname = currentEndpoint;
      return url.href;
    }
    return currentEndpoint;
  }

  function headers(
    authentication: boolean,
    extraHeaders?: object,
    refreshing?: object,
    tokens?: object,
  ): object {
    tokens = tokens ? tokens : useTokens();
    refreshing = refreshing ? refreshing : refreshStore();
    const currentHeaders = defaultHeaders;
    const token = tokens.get().access;
    if (authentication) {
      if (!token) {
        forwardToLogin(refreshing, tokens);
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
    endpoint = extraPath ? `${endpoint}${extraPath}` : endpoint;
    return $fetch(url(endpoint), options).catch((error) => {
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
          console.log(endpoint);
          if (
            endpoint.includes("/api/security/refresh/") ||
            (error.data.detail &&
              error.data.detail === "Incorrect authentication credentials." &&
              (endpoint.includes("/api/profile/mfa/enable/") ||
                endpoint.includes("/api/profile/mfa/disable/") ||
                endpoint.includes("/api/telegram/link/")))
          ) {
            console.log("HELLO WORLD");
            return Promise.reject(error);
          } else if (authentication) {
            const tokens = useTokens();
            const refreshing = refreshStore();
            if (refreshing.refreshing) {
              function wait() {
                return new Promise((resolve, reject) => {
                  setTimeout(() => {
                    if (refreshing.refreshing) {
                      return wait();
                    }
                    options.headers = headers(
                      authentication,
                      extraHeaders,
                      refreshing,
                      tokens,
                    );
                    request(endpoint, options, undefined, extraHeaders)
                      .then((response) => resolve(response))
                      .catch((error) => reject(error));
                  }, 500);
                });
              }
              return wait();
            } else {
              return refresh(refreshing, tokens).then(() => {
                options.headers = headers(
                  authentication,
                  extraHeaders,
                  refreshing,
                  tokens,
                );
                return request(endpoint, options, undefined, extraHeaders);
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

  function forwardToLogin(refreshing: object, tokens: object): Promise {
    const user = userStore();
    tokens.remove();
    user.logout();
    if (refreshing.refreshing) {
      refreshing.change();
    }
    return navigateTo("/login");
  }

  function refresh(refreshing: object, tokens: object): Promise {
    refreshing.change();
    const refresh = tokens.get().refresh;
    if (!refresh) {
      forwardToLogin(refreshing, tokens);
    } else {
      return request("/api/security/refresh/", {
        method: "POST",
        headers: headers(true, {}, refreshing, tokens),
        body: { refresh: refresh },
      })
        .then((response) => {
          tokens.remove();
          tokens.save(response);
          refreshing.change();
          return Promise.resolve();
        })
        .catch(() => {
          forwardToLogin(refreshing, tokens);
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
