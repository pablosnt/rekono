export function useFilters() {
  const user = userStore();

  function getDefinitionFromKey(key, filtering) {
    const search = filtering.filter((item) => item.key === key);
    return search.length > 0 ? search[0] : null;
  }

  function getValue(item) {
    if (item.multiple) {
      return item.value.length > 0
        ? item.fieldValue
          ? item.value
              .map((f) => {
                return f[item.fieldValue];
              })
              .join(",")
          : item.value.join(",")
        : null;
    } else {
      return item.value !== null && item.value !== undefined && item.fieldValue
        ? item.value[item.fieldValue]
        : item.value;
    }
  }

  function collectionFromEnum(data) {
    return Object.entries(data).map(([k, v]) => {
      v.name = k;
      return v;
    });
  }

  function setDefault(item) {
    if (item.defaultValue === null || item.defaultValue === undefined) {
      item.value = item.defaultValue = item.multiple ? [] : null;
    } else if (item.collection) {
      item.value = item.multiple
        ? item.collection.filter((f) =>
            item.defaultValue.includes(
              item.fieldValue ? f[item.fieldValue] : f,
            ),
          )
        : item.collection.filter(
            (f) =>
              item.defaultValue === (item.fieldValue ? f[item.fieldValue] : f),
          )[0];
    } else {
      item.value = item.defaultValue;
    }
  }

  function build(filters) {
    return filters
      .filter(
        (item) =>
          !item.skip &&
          (!item.onlyAdmin || user.role === "Admin") &&
          (!item.onlyAuditor || ["Admin", "Auditor"].includes(user.role)),
      )
      .map((item) => {
        if (item.request) {
          item.request.then((response) => {
            item.collection = response.items;
            setDefault(item);
          });
        } else {
          if (item.key === "ordering") {
            item.collection = item.collection
              .map((item) => {
                let name =
                  item === "id"
                    ? "ID"
                    : `${item.charAt(0).toUpperCase()}${item.slice(1)}`;
                if (name.includes("__")) {
                  name = name.split("__")[1];
                  name = `${name.charAt(0).toUpperCase()}${name.slice(1)}`;
                } else if (name.includes("_")) {
                  name = name.split("_")[0];
                }
                return [
                  { id: item, name: name },
                  { id: `-${item}`, name: `${name} desc` },
                ];
              })
              .flat(1);
          }
          setDefault(item);
        }

        return item;
      });
  }

  return {
    getDefinitionFromKey,
    getValue,
    collectionFromEnum,
    setDefault,
    build,
  };
}
