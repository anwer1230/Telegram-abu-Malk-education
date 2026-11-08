package org.telegram.ui;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.ViewGroup;

import org.telegram.messenger.AccountInstance;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.FileLog;
import org.telegram.messenger.NotificationCenter;
import org.telegram.messenger.SharedConfig;
import org.telegram.messenger.UserConfig;
import org.telegram.ui.ActionBar.ActionBarLayout;
import org.telegram.ui.ActionBar.BaseFragment;

/**
 * LaunchActivity.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/ui/LaunchActivity.java
 *
 * Primary application entry point. Coordinates session startup, test account
 * sanitization, login redirection vs dialogs display, and dynamic multi-account
 * switching and logout routing.
 */
public class LaunchActivity extends Activity implements NotificationCenter.NotificationCenterDelegate {

    public static LaunchActivity instance;
    public ActionBarLayout actionBarLayout;
    private int currentAccount;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        ApplicationLoader.postInitApplication();
        super.onCreate(savedInstanceState);

        instance = this;

        // Goal 1: Purge any dummy, mock, or unauthenticated accounts on boot
        UserConfig.cleanupTestAccounts();

        currentAccount = UserConfig.selectedAccount;

        // Initialize Telegram Fragment presentation stack
        actionBarLayout = new ActionBarLayout(this);
        setContentView(actionBarLayout, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
        ));

        // Register for account lifecycle and logout events across accounts
        for (int a = 0; a < UserConfig.MAX_ACCOUNT_COUNT; a++) {
            NotificationCenter.getInstance(a).addObserver(this, NotificationCenter.appDidLogout);
            NotificationCenter.getInstance(a).addObserver(this, NotificationCenter.mainUserInfoChanged);
        }
        NotificationCenter.getGlobalInstance().addObserver(this, NotificationCenter.didSetPasscode);

        // Goal 2: Determine startup route based on session activation
        checkSessionAndNavigate();
    }

    /**
     * Goal 2: Reads UserConfig.isClientActivated() to route user immediately to:
     * - LoginActivity.java if no valid activated session exists
     * - DialogsActivity.java if a single genuine activated account exists
     */
    public void checkSessionAndNavigate() {
        UserConfig currentConfig = UserConfig.getInstance(currentAccount);

        // Verify if current account is authorized
        if (!currentConfig.isClientActivated()) {
            // Check if any other account is active
            int activatedCount = UserConfig.getActivatedAccountsCount();
            if (activatedCount > 0) {
                for (int a = 0; a < UserConfig.MAX_ACCOUNT_COUNT; a++) {
                    if (UserConfig.getInstance(a).isClientActivated()) {
                        currentAccount = a;
                        UserConfig.selectedAccount = a;
                        break;
                    }
                }
            }
        }

        // Final verification after checking all available accounts
        if (!UserConfig.getInstance(currentAccount).isClientActivated()) {
            FileLog.d("Goal 2: No active session. Launching LoginActivity immediately.");
            actionBarLayout.removeAllFragments();
            actionBarLayout.presentFragment(new LoginActivity(), true, false, true, false);
        } else {
            FileLog.d("Goal 2: Active real session detected (User ID: " + UserConfig.getInstance(currentAccount).getClientUserId() + "). Launching DialogsActivity.");
            actionBarLayout.removeAllFragments();
            actionBarLayout.presentFragment(new DialogsActivity(null), false, false, true, false);
        }
    }

    /**
     * Switches UI context to another active account.
     */
    public void switchToAccount(int account, boolean reload) {
        if (account < 0 || account >= UserConfig.MAX_ACCOUNT_COUNT) {
            return;
        }

        currentAccount = account;
        UserConfig.selectedAccount = account;

        if (reload) {
            actionBarLayout.removeAllFragments();
            if (UserConfig.getInstance(account).isClientActivated()) {
                actionBarLayout.presentFragment(new DialogsActivity(null), false, false, true, false);
            } else {
                actionBarLayout.presentFragment(new LoginActivity(), true, false, true, false);
            }
        }
    }

    /**
     * Goal 4: Handles account logout event.
     * If the logged out account was the only one, redirects to LoginActivity.
     * If other authenticated accounts remain, seamlessly transitions to the next active account.
     */
    @Override
    public void didReceivedNotification(int id, int account, Object... args) {
        if (id == NotificationCenter.appDidLogout) {
            FileLog.d("Goal 4: Logout event detected for account " + account);

            // Re-evaluate activated accounts
            int activatedRemaining = UserConfig.getActivatedAccountsCount();

            if (activatedRemaining > 0) {
                // Find next available authenticated account
                for (int a = 0; a < UserConfig.MAX_ACCOUNT_COUNT; a++) {
                    if (a != account && UserConfig.getInstance(a).isClientActivated()) {
                        FileLog.d("Switching to remaining authenticated account slot: " + a);
                        switchToAccount(a, true);
                        return;
                    }
                }
            }

            // No active accounts remain; reset to default slot and present login screen
            FileLog.d("No active accounts remain. Presenting LoginActivity.");
            UserConfig.selectedAccount = 0;
            currentAccount = 0;
            actionBarLayout.removeAllFragments();
            actionBarLayout.presentFragment(new LoginActivity(), true, false, true, false);

        } else if (id == NotificationCenter.mainUserInfoChanged) {
            // Re-check navigation upon user login or credential change
            if (account == currentAccount && UserConfig.getInstance(currentAccount).isClientActivated()) {
                actionBarLayout.removeAllFragments();
                actionBarLayout.presentFragment(new DialogsActivity(null), false, false, true, false);
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        BaseFragment last = actionBarLayout.getLastFragment();
        if (last != null) {
            last.onResume();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        BaseFragment last = actionBarLayout.getLastFragment();
        if (last != null) {
            last.onPause();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        for (int a = 0; a < UserConfig.MAX_ACCOUNT_COUNT; a++) {
            NotificationCenter.getInstance(a).removeObserver(this, NotificationCenter.appDidLogout);
            NotificationCenter.getInstance(a).removeObserver(this, NotificationCenter.mainUserInfoChanged);
        }
        NotificationCenter.getGlobalInstance().removeObserver(this, NotificationCenter.didSetPasscode);
        instance = null;
    }
}
