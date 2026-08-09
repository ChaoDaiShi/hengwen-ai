import { describe, expect, it } from "vitest";
import { fileTypeForName } from "../src/lib/file";

describe("fileTypeForName", () => {
  it("normalizes supported extensions", () => {
    expect(fileTypeForName("论文.DOCX")).toBe(".docx");
    expect(fileTypeForName("notes.Md")).toBe(".md");
  });

  it("rejects missing and unsupported extensions", () => {
    expect(fileTypeForName("论文")).toBeNull();
    expect(fileTypeForName("论文.txt")).toBeNull();
    expect(fileTypeForName("论文.pdf.exe")).toBeNull();
  });
});
