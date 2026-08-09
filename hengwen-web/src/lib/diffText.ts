export type DiffPart = { type: "same" | "del" | "add"; text: string };

const MAX_CELLS = 2_000_000;

export function diffText(original: string, suggestion: string): DiffPart[] {
  const a = Array.from(original);
  const b = Array.from(suggestion);
  const n = a.length;
  const m = b.length;

  if (n === 0 && m === 0) return [];
  if (n === 0) return [{ type: "add", text: suggestion }];
  if (m === 0) return [{ type: "del", text: original }];

  if (n * m > MAX_CELLS) {
    return [
      ...(n > 0 ? [{ type: "del" as const, text: original }] : []),
      ...(m > 0 ? [{ type: "add" as const, text: suggestion }] : []),
    ];
  }

  const dp: number[][] = Array.from({ length: n + 1 }, () =>
    new Array(m + 1).fill(0),
  );
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] =
        a[i] === b[j]
          ? dp[i + 1][j + 1] + 1
          : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }

  const parts: DiffPart[] = [];
  let mode: "same" | "del" | "add" | null = null;
  let buf = "";
  const emit = (next: "same" | "del" | "add", ch: string) => {
    if (mode === next) {
      buf += ch;
      return;
    }
    if (mode !== null) parts.push({ type: mode, text: buf });
    mode = next;
    buf = ch;
  };
  const flushAll = () => {
    if (mode !== null) parts.push({ type: mode, text: buf });
    mode = null;
    buf = "";
  };

  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      emit("same", a[i]);
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      emit("del", a[i]);
      i++;
    } else {
      emit("add", b[j]);
      j++;
    }
  }
  while (i < n) {
    emit("del", a[i]);
    i++;
  }
  while (j < m) {
    emit("add", b[j]);
    j++;
  }
  flushAll();

  return parts;
}
