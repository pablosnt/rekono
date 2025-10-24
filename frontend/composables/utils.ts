export function useUtils() {
  function displayNumber(value: number): string {
    return value > 1000
      ? Math.floor(value / 1000).toString() + "k"
      : value.toString();
  }

  return { displayNumber };
}
