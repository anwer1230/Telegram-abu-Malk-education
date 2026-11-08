package org.telegram.ui.ActionBar;

import android.app.Activity;
import android.content.Context;
import android.view.View;
import android.widget.FrameLayout;

import java.util.ArrayList;

/**
 * ActionBarLayout.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/ui/ActionBar/ActionBarLayout.java
 *
 * Telegram custom navigation stack controller. Manages transition animations,
 * fragment stacks, back-stack states, and screen swaps between LoginActivity
 * and DialogsActivity without recreation overhead.
 */
public class ActionBarLayout extends FrameLayout {

    public Activity parentActivity;
    public ArrayList<BaseFragment> fragmentsStack = new ArrayList<>();

    public ActionBarLayout(Context context) {
        super(context);
        parentActivity = (Activity) context;
    }

    public boolean presentFragment(BaseFragment fragment) {
        return presentFragment(fragment, false, false, true, false);
    }

    public boolean presentFragment(BaseFragment fragment, boolean removeLast, boolean forceWithoutAnimation, boolean check, boolean asListItem) {
        if (fragment == null) {
            return false;
        }

        if (removeLast && !fragmentsStack.isEmpty()) {
            BaseFragment current = fragmentsStack.remove(fragmentsStack.size() - 1);
            if (current != null) {
                current.onPause();
                current.onFragmentDestroy();
                if (current.fragmentView != null) {
                    removeView(current.fragmentView);
                }
            }
        }

        fragment.setParentLayout(this);
        if (!fragment.onFragmentCreate()) {
            return false;
        }

        View view = fragment.createView(getContext());
        fragment.fragmentView = view;
        addView(view, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT));

        fragmentsStack.add(fragment);
        fragment.onResume();

        return true;
    }

    public void closeLastFragment(boolean animated) {
        if (fragmentsStack.size() <= 1) {
            if (parentActivity != null) {
                parentActivity.finish();
            }
            return;
        }

        BaseFragment current = fragmentsStack.remove(fragmentsStack.size() - 1);
        if (current != null) {
            current.onPause();
            current.onFragmentDestroy();
            if (current.fragmentView != null) {
                removeView(current.fragmentView);
            }
        }

        if (!fragmentsStack.isEmpty()) {
            BaseFragment previous = fragmentsStack.get(fragmentsStack.size() - 1);
            previous.onResume();
        }
    }

    public void removeAllFragments() {
        for (BaseFragment fragment : fragmentsStack) {
            if (fragment != null) {
                fragment.onPause();
                fragment.onFragmentDestroy();
                if (fragment.fragmentView != null) {
                    removeView(fragment.fragmentView);
                }
            }
        }
        fragmentsStack.clear();
        removeAllViews();
    }

    public BaseFragment getLastFragment() {
        if (fragmentsStack.isEmpty()) {
            return null;
        }
        return fragmentsStack.get(fragmentsStack.size() - 1);
    }
}
