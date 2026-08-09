import type { Report } from "../types/report";

export const ACCEPTED_FILE_TYPES = [".docx", ".pdf", ".md"] as const;

function extensionOf(name: string): string | null {
  const dot = name.lastIndexOf(".");
  return dot >= 0 ? name.slice(dot).toLowerCase() : null;
}

export function fileTypeForName(name: string): Report["fileType"] | null {
  const extension = extensionOf(name);
  return ACCEPTED_FILE_TYPES.find((fileType) => fileType === extension) ?? null;
}
