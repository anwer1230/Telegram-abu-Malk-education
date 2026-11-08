package org.telegram.ui;

import android.content.Context;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.telegram.messenger.AccountInstance;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.UserConfig;
import org.telegram.tgnet.TLRPC;
import org.telegram.ui.ActionBar.BaseFragment;

/**
 * DialogsActivity.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/ui/DialogsActivity.java
 *
 * The primary chat list and conversation overview screen.
 * Displays active conversations for the authenticated user and provides
 * account management and logout triggers.
 */
public class DialogsActivity extends BaseFragment {

    public DialogsActivity(Bundle args) {
        super(args);
    }

    @Override
    public View createView(Context context) {
        LinearLayout layout = new LinearLayout(context);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(32, 32, 32, 32);

        TextView header = new TextView(context);
        UserConfig userConfig = UserConfig.getInstance(currentAccount);
        TLRPC.User currentUser = userConfig.getCurrentUser();
        String displayName = currentUser != null ? (currentUser.first_name + " " + currentUser.last_name).trim() : "Telegram User";

        header.setText("Chats (" + displayName + " - Slot #" + currentAccount + ")");
        header.setTextSize(22);
        header.setPadding(0, 0, 0, 24);
        layout.addView(header);

        TextView info = new TextView(context);
        info.setText("Active authenticated session.\nUser ID: " + userConfig.getClientUserId() + "\nPhone: " + (currentUser != null ? currentUser.phone : "N/A"));
        info.setPadding(0, 0, 0, 32);
        layout.addView(info);

        // Logout button triggering Goal 4
        Button logoutButton = new Button(context);
        logoutButton.setText("Log Out");
        logoutButton.setOnClickListener(v -> {
            MessagesController.getInstance(currentAccount).performLogout(1);
        });
        layout.addView(logoutButton);

        return layout;
    }
}
