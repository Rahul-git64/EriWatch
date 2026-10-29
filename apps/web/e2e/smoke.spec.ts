import { expect, test } from "@playwright/test";

test("homepage displays EriWatch title", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", {
      name: /EriWatch: Satellite Early Warning & Grievance Platform/i,
    }),
  ).toBeVisible();
});
