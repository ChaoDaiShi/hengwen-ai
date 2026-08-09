import { describe, expect, it } from "vitest";
import { scoreToVerdict } from "../src/lib/verdict";

describe("scoreToVerdict", () => {
  it("passes at or above 90", () => {
    expect(scoreToVerdict(90)).toBe("pass");
    expect(scoreToVerdict(100)).toBe("pass");
  });

  it("flags pending between 75 and 89", () => {
    expect(scoreToVerdict(75)).toBe("pending");
    expect(scoreToVerdict(89)).toBe("pending");
  });

  it("fails below 75", () => {
    expect(scoreToVerdict(74)).toBe("fail");
    expect(scoreToVerdict(0)).toBe("fail");
  });

  it("handles boundary exactly", () => {
    expect(scoreToVerdict(89.9)).toBe("pending");
  });
});
