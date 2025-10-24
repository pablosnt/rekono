export function useDates() {
  function getDuration(
    startISO: string,
    endISO: string = "",
    round: boolean = false,
  ): string {
    const start = new Date(startISO);
    const end = endISO ? new Date(endISO) : new Date();
    const seconds = Math.floor((end.getTime() - start.getTime()) / 1000);
    const fields = [
      { value: Math.floor(seconds / (3600 * 24 * 365)), name: "y" },
      {
        value: Math.floor((seconds % (3600 * 24 * 365)) / (3600 * 24 * 30)),
        name: "mon",
      },
      {
        value: Math.floor((seconds % (3600 * 24 * 30)) / (3600 * 24)),
        name: "d",
      },
      { value: Math.floor((seconds % (3600 * 24)) / 3600), name: "h" },
      { value: Math.floor((seconds % 3600) / 60), name: "min" },
      { value: Math.floor(seconds % 60), name: "s" },
    ];
    let duration = "";
    let count = 0;
    for (const field of fields) {
      if (field.value > 0) {
        count++;
        if (count === 3 && round) {
          duration = duration + "+";
          break;
        } else {
          duration = duration + `${field.value} ${field.name} `;
        }
      }
    }
    return duration.trim();
  }

  return { getDuration };
}
