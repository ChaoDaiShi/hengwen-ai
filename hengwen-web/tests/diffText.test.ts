import { describe, expect, it } from "vitest";
import { diffText } from "../src/lib/diffText";

describe("diffText", () => {
  it("returns empty for two empty strings", () => {
    expect(diffText("", "")).toEqual([]);
  });

  it("marks entire addition when original is empty", () => {
    expect(diffText("", "新增")).toEqual([{ type: "add", text: "新增" }]);
  });

  it("marks entire deletion when suggestion is empty", () => {
    expect(diffText("删除", "")).toEqual([{ type: "del", text: "删除" }]);
  });

  it("keeps unchanged text as same", () => {
    expect(diffText("原文", "原文")).toEqual([{ type: "same", text: "原文" }]);
  });

  it("detects a substituted middle segment", () => {
    expect(diffText("衡量，然后修改", "衡量，再修改")).toEqual([
      { type: "same", text: "衡量，" },
      { type: "del", text: "然后" },
      { type: "add", text: "再" },
      { type: "same", text: "修改" },
    ]);
  });
});
