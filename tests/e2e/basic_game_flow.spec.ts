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

    await expect(
      page.getByRole('heading', { name: 'AlgoFOMO Admin Panel' }),
    ).toBeVisible();

    await page.getByTestId('admin-left-avatar-url-input').fill(leftAvatarUrl);
    await page.getByTestId('admin-right-avatar-url-input').fill(rightAvatarUrl);
    await page
      .getByTestId('admin-initial-momentum-input')
      .fill(initialMomentum.toString());
    await page.getByTestId('admin-token-input').fill(ADMIN_TOKEN);

    await page.getByTestId('admin-start-round-button').click();

    // Check for a success toast/message from the admin panel
    const adminResultMessage = page.getByTestId('admin-result-message');
    await expect(adminResultMessage).toBeVisible({ timeout: 10000 });
    await expect(adminResultMessage).toContainText(
      /New round started successfully/i,
    );
    // Optional: Could also check for the Round ID if needed: await expect(adminResultMessage).toContainText(/Round ID:/i);

    // 2. Verify Initial State on Main Page
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'AlgoFOMO' })).toBeVisible();
    await expect(page.getByTestId('arena-container')).toBeVisible();

    // Verify avatars
    await expect(page.getByTestId('arena-left-avatar-img')).toHaveAttribute(
      'src',
      leftAvatarUrl,
    );
    await expect(page.getByTestId('arena-right-avatar-img')).toHaveAttribute(
      'src',
      rightAvatarUrl,
    );

    // Verify momentum bar (aria-valuenow is good for progressbar role)
    const momentumBar = page
      .getByTestId('arena-momentum-bar')
      .locator('[role="progressbar"]');
    await expect(momentumBar).toBeVisible();
    await expect(momentumBar).toHaveAttribute(
      'aria-valuenow',
      initialMomentum.toString(),
      { timeout: 15000 },
    );

    // Verify pot amount
    await expect(page.getByTestId('arena-pot-amount')).toContainText(
      'Current Pot: 0 ALGO',
    ); // Exact match if format is stable

    // 3. User places a bet
    const betAmount = '10';
    const spellText = 'Test spell for impact';

    await expect(page.getByTestId('bet-drawer-card')).toBeVisible();

    await page.getByTestId('bet-drawer-side-left').click(); // Clicks the RadioGroupItem directly
    await page.getByTestId('bet-drawer-amount-input').fill(betAmount);
    await page.getByTestId('bet-drawer-spell-input').fill(spellText);
    await page.getByTestId('bet-drawer-submit-button').click();

    // 4. Verify Bet Impact (UI changes)
    const feedbackMessage = page.getByTestId('bet-drawer-feedback-message');
    await expect(feedbackMessage).toBeVisible({ timeout: 10000 });
    await expect(feedbackMessage).toContainText('Bet placed successfully!');

    // Pot amount should increase
    await expect(page.getByTestId('arena-pot-amount')).toContainText(
      `Current Pot: ${betAmount} ALGO`,
      { timeout: 10000 },
    );

    // Momentum should change based on impact.
    // For test bet: amount=10, spell="Test spell for impact" (4 words)
    // log_bet_term = log10(10) = 1.0
    // prompt_power_raw = 4/10 = 0.4. prompt_power = clamp(0.4, 0.5, 1.5) = 0.5
    // random_factor = [0.8, 1.2]
    // impact_min = 1.0 * 0.5 * 0.8 = 0.4
    // impact_max = 1.0 * 0.5 * 1.2 = 0.6
    // initialMomentum = 60. Bet on left.
    // new_float_momentum_min = 60 - 0.6 = 59.4 (rounds to 59)
    // new_float_momentum_max = 60 - 0.4 = 59.6 (rounds to 60)
    // So, expected integer momentum is 59 or 60.
    const newMomentumValueString =
      await momentumBar.getAttribute('aria-valuenow');
    expect(newMomentumValueString).not.toBeNull();
    const newMomentumValue = Number(newMomentumValueString);
    expect(newMomentumValue).toBeGreaterThanOrEqual(59);
    expect(newMomentumValue).toBeLessThanOrEqual(60);

    // Timer should extend - verify game is still active via a stable element in Arena
    await expect(page.getByTestId('arena-timer-display')).toBeVisible();

    await page.waitForTimeout(2000); // Wait for potential RT updates
  });
});
