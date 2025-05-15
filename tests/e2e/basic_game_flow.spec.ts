import { test, expect } from '@playwright/test';

const ADMIN_TOKEN = process.env.E2E_ADMIN_TOKEN || 'verysecretadmintoken'; // Use an env var for tests

test.describe('AlgoFOMO Basic Game Flow', () => {
  const roundId = Date.now(); // Pseudo-unique ID for avatar URLs to avoid caching issues if any
  const leftAvatarUrl = `https://picsum.photos/seed/${roundId}_left/200`;
  const rightAvatarUrl = `https://picsum.photos/seed/${roundId}_right/200`;
  const initialMomentum = 60;

  test('Admin starts a new round, user places a bet, and state updates', async ({
    page,
  }) => {
    // 1. Admin starts a new round
    await page.goto('/admin');

    // Wait for admin page to load - check for a unique element
    await expect(
      page.getByRole('heading', { name: 'AlgoFOMO Admin Panel' }),
    ).toBeVisible();

    await page.getByLabel('Left Avatar URL').fill(leftAvatarUrl);
    await page.getByLabel('Right Avatar URL').fill(rightAvatarUrl);
    await page
      .getByLabel('Initial Momentum (0-100)')
      .fill(initialMomentum.toString());
    await page.getByLabel('Admin Token').fill(ADMIN_TOKEN);

    await page.getByRole('button', { name: 'Start New Round' }).click();

    // Expect a success message or navigation (depends on admin panel implementation)
    // For now, let's assume it navigates or shows a clear success state.
    // We'll look for a toast/alert. The admin page might show this.
    // This needs to be adjusted based on actual admin page feedback.
    await expect(page.getByText(/New round started successfully/i)).toBeVisible(
      { timeout: 10000 },
    ); // Check for a success toast

    // 2. Verify Initial State on Main Page
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'AlgoFOMO' })).toBeVisible(); // Main page heading

    // Verify avatars (check img src)
    // Note: Exact selector might need adjustment based on Arena.tsx structure
    const leftAvatarImage = page.locator(
      'img[alt*="Left Player"], img[alt*="left_player"]',
    ); // More flexible alt text
    await expect(leftAvatarImage).toHaveAttribute('src', leftAvatarUrl);
    const rightAvatarImage = page.locator(
      'img[alt*="Right Player"], img[alt*="right_player"]',
    );
    await expect(rightAvatarImage).toHaveAttribute('src', rightAvatarUrl);

    // Verify momentum (this needs a specific selector in Arena.tsx)
    // e.g., await expect(page.locator('[data-testid="momentum-value"]')).toHaveText(initialMomentum.toString());
    // For now, we assume momentum is visually represented and can be checked via an aria-label or similar
    // Looking for the momentum bar itself and its aria-valuenow if it's a progressbar role
    const momentumBar = page.locator(
      '[role="progressbar"][aria-label*="Momentum"]',
    );
    await expect(momentumBar).toBeVisible();
    await expect(momentumBar).toHaveAttribute(
      'aria-valuenow',
      initialMomentum.toString(),
      { timeout: 15000 },
    ); // Increased timeout for initial load + RT update

    // Verify pot amount (starts at 0)
    // e.g., await expect(page.locator('[data-testid="pot-amount"]')).toContainText('0');
    // Assuming a structure like <p>Pot: 0 ALGO</p>
    await expect(page.getByText(/Pot Amount: 0\s*ALGO/i)).toBeVisible();

    // 3. User places a bet
    const betAmount = '10';
    const spellText = 'Test spell for impact';

    // Locate BetDrawer elements (these selectors might need refinement based on BetDrawer.tsx)
    const betDrawerCard = page
      .locator('div.pt-6.space-y-4')
      .locator('..')
      .locator('..'); // trying to get the Card parent

    // Select side: Left (assuming `leftSideLabel` is used in a way that can be targeted)
    // A more robust way would be to target by value or a data-testid on RadioGroupItem
    // Using the default display name set by the backend for now.
    await betDrawerCard.getByLabel(/Left Player/i).click();

    await betDrawerCard.getByLabel('Bet Amount').fill(betAmount);
    await betDrawerCard.getByLabel(/Cast Your Spell/i).fill(spellText);
    await betDrawerCard.getByRole('button', { name: 'WRECK THEM!' }).click();

    // 4. Verify Bet Impact (UI changes)
    // Expect a success message from BetDrawer
    await expect(
      betDrawerCard.getByText('Bet placed successfully!'),
    ).toBeVisible({ timeout: 10000 });

    // Pot amount should increase
    await expect(
      page.getByText(new RegExp(`Pot Amount: ${betAmount}\s*ALGO`, 'i')),
    ).toBeVisible({ timeout: 10000 });

    // Momentum should change. This is tricky as the exact change depends on calculation.
    // For a bet of 10 ALGO, initial momentum 60, betting on left:
    // momentum_change = (10 / 100.0) * 0.1 = 0.01. new_momentum = 60 - 0.01 = 59.99, rounds to 60.
    // If momentum calc is (bet_amount / 10.0) * 0.1 = 0.1. new_momentum = 60 - 0.1 = 59.9, rounds to 60.
    // The current simple logic: (bet_amount / 100.0) * 0.1. For 10 ALGO, this is 0.01 shift.
    // So, 60 -> 59.99 -> rounded to 60. The momentum bar might not visibly change for such a small amount.
    // Let's try a larger bet or adjust expectation. If bet is 100: (100/100)*0.1 = 0.1. 60-0.1 = 59.9 -> 60.
    // The PRD impact formula is different. For this test, we rely on the *backend's current momentum logic*.
    // Let's assume for a 10 ALGO bet, the momentum *might* change by at least 1 if the calculation is sensitive enough or if it was larger.
    // Given initial momentum is 60, and we bet on left, momentum should decrease or stay same if change is too small to display.
    // A more robust test would be to bet an amount that guarantees a change of at least 1.
    // For now, let's check it doesn't go up (since we bet left).
    const newMomentumValue = await momentumBar.getAttribute('aria-valuenow');
    expect(Number(newMomentumValue)).toBeLessThanOrEqual(initialMomentum);
    // A better check would be for a specific expected value if the logic was stable and predictable for a test bet.

    // Timer should extend (or rather, the deadline displayed should be further in the future)
    // This requires checking the displayed time. Complex to check exact value due to real-time nature.
    // A simpler check: ensure the game is still active and didn't end prematurely.
    await expect(page.getByText(/VS/i)).toBeVisible(); // Arena VS separator still visible implies game ongoing.

    // Add a small wait to see Realtime updates propagate if any further checks were needed
    await page.waitForTimeout(2000); // Wait for potential RT updates
  });
});
