import { test, expect } from '@playwright/test';

test('basic dashboard functionality', async ({ page }) => {
  await page.goto('/');

  // Check that the dashboard loads
  await expect(page.locator('h1')).toContainText('لوحة التحكم');

  // Check that tabs are visible
  await expect(page.locator('[role="tab"]')).toHaveCount(6);

  // Check that pending tab is active by default
  await expect(page.locator('[role="tab"][aria-selected="true"]')).toContainText('قيد الانتظار');
});

test('can switch between tabs', async ({ page }) => {
  await page.goto('/');

  // Click on processing tab
  await page.locator('text=معالجة').click();
  
  // Verify tab switched
  await expect(page.locator('[role="tab"][aria-selected="true"]')).toContainText('معالجة');
});

test('notifications inbox appears', async ({ page }) => {
  await page.goto('/');

  // Check notification bell icon exists
  await expect(page.locator('[data-testid="notification-bell"]')).toBeVisible();
});
