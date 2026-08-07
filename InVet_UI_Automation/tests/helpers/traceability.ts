import type { TestInfo } from "@playwright/test";

export type TraceabilityRefs = {
  slice: string;
  userStory: string;
  criteria: string[];
};

export type GherkinScenario = {
  feature: string;
  scenario: string;
  given: string[];
  when: string[];
  then: string[];
  and?: string[];
};

export function annotateTraceability(
  testInfo: TestInfo,
  refs: TraceabilityRefs,
): void {
  testInfo.annotations.push({ type: "slice", description: refs.slice });
  testInfo.annotations.push({ type: "us", description: refs.userStory });

  for (const criterion of refs.criteria) {
    testInfo.annotations.push({ type: "ca", description: criterion });
  }
}

export async function attachGherkinScenario(
  testInfo: TestInfo,
  gherkin: GherkinScenario,
): Promise<void> {
  testInfo.annotations.push({ type: "feature", description: gherkin.feature });
  testInfo.annotations.push({ type: "scenario", description: gherkin.scenario });

  for (const value of gherkin.given) {
    testInfo.annotations.push({ type: "given", description: value });
  }

  for (const value of gherkin.when) {
    testInfo.annotations.push({ type: "when", description: value });
  }

  for (const value of gherkin.then) {
    testInfo.annotations.push({ type: "then", description: value });
  }

  for (const value of gherkin.and ?? []) {
    testInfo.annotations.push({ type: "and", description: value });
  }

  const lines = [
    `Feature: ${gherkin.feature}`,
    `Scenario: ${gherkin.scenario}`,
    ...gherkin.given.map((value) => `Given ${value}`),
    ...gherkin.when.map((value) => `When ${value}`),
    ...gherkin.then.map((value) => `Then ${value}`),
    ...(gherkin.and ?? []).map((value) => `And ${value}`),
  ];

  await testInfo.attach("gherkin", {
    body: Buffer.from(lines.join("\n"), "utf8"),
    contentType: "text/plain",
  });
}
