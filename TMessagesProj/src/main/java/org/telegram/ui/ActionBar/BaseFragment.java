package org.telegram.ui.ActionBar;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.View;

import org.telegram.messenger.UserConfig;

/**
 * BaseFragment.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/ui/ActionBar/BaseFragment.java
 *
 * Base UI presentation unit within Telegram Android. Replaces standard Android
 * fragments for ultra-low latency view lifecycle, zero-allocation navigation,
 * and custom swipe-to-back transitions.
 */
public abstract class BaseFragment {

    protected int currentAccount = UserConfig.selectedAccount;
    protected View fragmentView;
    protected ActionBarLayout parentLayout;
    protected boolean isFinished = false;
    protected Bundle arguments;

    public BaseFragment() {
        this(null);
    }

    public BaseFragment(Bundle args) {
        arguments = args;
    }

    public void setCurrentAccount(int account) {
        currentAccount = account;
    }

    public int getCurrentAccount() {
        return currentAccount;
    }

    public Activity getParentActivity() {
        if (parentLayout != null) {
            return parentLayout.parentActivity;
        }
        return null;
    }

    public void setParentLayout(ActionBarLayout layout) {
        if (parentLayout != layout) {
            parentLayout = layout;
        }
    }

    public View getFragmentView() {
        return fragmentView;
    }

    public boolean onFragmentCreate() {
        return true;
    }

    public void onFragmentDestroy() {
        isFinished = true;
    }

    public void onResume() {}

    public void onPause() {}

    public abstract View createView(Context context);

    public boolean presentFragment(BaseFragment fragment) {
        return parentLayout != null && parentLayout.presentFragment(fragment);
    }

    public boolean presentFragment(BaseFragment fragment, boolean removeLast) {
        return parentLayout != null && parentLayout.presentFragment(fragment, removeLast, false, true, false);
    }

    public void finishFragment() {
        if (parentLayout != null) {
            parentLayout.closeLastFragment(true);
        }
    }
}
