export function useUtils() {
  function displayNumber(value) {
    return value > 1000 ? Math.floor(value / 1000).toString() + "k" : value;
  }

  return { displayNumber };
}
