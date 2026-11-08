package org.telegram.messenger;

import android.os.Handler;
import android.os.Looper;

import java.util.ArrayList;
import java.util.HashMap;

/**
 * NotificationCenter.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/messenger/NotificationCenter.java
 *
 * Scoped and global event notification dispatch engine. Coordinates multi-account
 * state transitions, logout events, 2FA updates, and screen invalidations.
 */
public class NotificationCenter {

    public static final int appDidLogout = 1;
    public static final int didReceivedNewMessages = 2;
    public static final int updateInterfaces = 3;
    public static final int dialogsNeedReload = 4;
    public static final int twoStepStateUpdated = 5;
    public static final int privacyRulesUpdated = 6;
    public static final int authorizationsUpdated = 7;
    public static final int didSetPasscode = 8;
    public static final int needShowAlert = 9;
    public static final int mainUserInfoChanged = 10;

    public interface NotificationCenterDelegate {
        void didReceivedNotification(int id, int account, Object... args);
    }

    private static volatile NotificationCenter[] Instance = new NotificationCenter[UserConfig.MAX_ACCOUNT_COUNT];
    private static volatile NotificationCenter GlobalInstance;

    private final int currentAccount;
    private final HashMap<Integer, ArrayList<Object>> observers = new HashMap<>();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    public static NotificationCenter getInstance(int num) {
        if (num < 0 || num >= UserConfig.MAX_ACCOUNT_COUNT) {
            num = 0;
        }
        NotificationCenter localInstance = Instance[num];
        if (localInstance == null) {
            synchronized (NotificationCenter.class) {
                localInstance = Instance[num];
                if (localInstance == null) {
                    Instance[num] = localInstance = new NotificationCenter(num);
                }
            }
        }
        return localInstance;
    }

    public static NotificationCenter getGlobalInstance() {
        NotificationCenter localInstance = GlobalInstance;
        if (localInstance == null) {
            synchronized (NotificationCenter.class) {
                localInstance = GlobalInstance;
                if (localInstance == null) {
                    GlobalInstance = localInstance = new NotificationCenter(-1);
                }
            }
        }
        return localInstance;
    }

    public NotificationCenter(int account) {
        currentAccount = account;
    }

    public void addObserver(Object observer, int id) {
        ArrayList<Object> list = observers.get(id);
        if (list == null) {
            list = new ArrayList<>();
            observers.put(id, list);
        }
        if (!list.contains(observer)) {
            list.add(observer);
        }
    }

    public void removeObserver(Object observer, int id) {
        ArrayList<Object> list = observers.get(id);
        if (list != null) {
            list.remove(observer);
        }
    }

    public void postNotificationName(final int id, final Object... args) {
        if (Looper.myLooper() == Looper.getMainLooper()) {
            postNotificationInternal(id, args);
        } else {
            mainHandler.post(() -> postNotificationInternal(id, args));
        }
    }

    private void postNotificationInternal(int id, Object... args) {
        ArrayList<Object> list = observers.get(id);
        if (list != null && !list.isEmpty()) {
            ArrayList<Object> copy = new ArrayList<>(list);
            for (Object obj : copy) {
                if (obj instanceof NotificationCenterDelegate) {
                    ((NotificationCenterDelegate) obj).didReceivedNotification(id, currentAccount, args);
                }
            }
        }
    }
}
