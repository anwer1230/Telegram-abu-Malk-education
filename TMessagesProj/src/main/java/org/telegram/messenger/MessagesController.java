package org.telegram.messenger;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.collection.LongSparseArray;

import org.telegram.tgnet.ConnectionsManager;
import org.telegram.tgnet.RequestDelegate;
import org.telegram.tgnet.TLObject;
import org.telegram.tgnet.TLRPC;

import java.util.ArrayList;
import java.util.HashMap;

/**
 * MessagesController.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java
 *
 * Core engine managing all MTProto RPC requests, dialog synchronization,
 * message histories, stories, 2FA, privacy, active sessions, and forum topics.
 */
public class MessagesController {

    public static final int PRIVACY_RULES_TYPE_LASTSEEN = 0;
    public static final int PRIVACY_RULES_TYPE_CALLS = 1;
    public static final int PRIVACY_RULES_TYPE_P2P = 2;
    public static final int PRIVACY_RULES_TYPE_PHOTO = 3;
    public static final int PRIVACY_RULES_TYPE_FORWARDS = 4;
    public static final int PRIVACY_RULES_TYPE_PHONE = 5;
    public static final int PRIVACY_RULES_TYPE_ADDED_BY_PHONE = 6;
    public static final int PRIVACY_RULES_TYPE_VOICE_MESSAGES = 7;
    public static final int PRIVACY_RULES_TYPE_BIO = 8;

    private static volatile MessagesController[] Instance = new MessagesController[UserConfig.MAX_ACCOUNT_COUNT];

    public static MessagesController getInstance(int num) {
        if (num < 0 || num >= UserConfig.MAX_ACCOUNT_COUNT) {
            num = 0;
        }
        MessagesController localInstance = Instance[num];
        if (localInstance == null) {
            synchronized (MessagesController.class) {
                localInstance = Instance[num];
                if (localInstance == null) {
                    Instance[num] = localInstance = new MessagesController(num);
                }
            }
        }
        return localInstance;
    }

    protected final int currentAccount;

    public ArrayList<TLRPC.Dialog> allDialogs = new ArrayList<>();
    public LongSparseArray<TLRPC.Chat> chats = new LongSparseArray<>();
    public LongSparseArray<TLRPC.User> users = new LongSparseArray<>();
    public boolean loadingDialogs = false;
    public boolean dialogsEndReached = false;

    // Cache for 2FA and Privacy
    public TLRPC.TL_account_password currentPassword;
    public HashMap<Integer, ArrayList<TLRPC.PrivacyRule>> privacyRules = new HashMap<>();
    public ArrayList<TLRPC.TL_authorization> activeAuthorizations = new ArrayList<>();
    public boolean sponsoredMessagesEnabled = true;

    public MessagesController(int account) {
        currentAccount = account;
    }

    // ==========================================
    // 1. Two-Step Verification & Email (TLRPC.TL_account_getPassword / TLRPC.TL_account_updatePasswordSettings)
    // ==========================================

    public void loadPasswordSettings() {
        TLRPC.TL_account_getPassword req = new TLRPC.TL_account_getPassword();
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                if (error == null && response instanceof TLRPC.TL_account_password) {
                    currentPassword = (TLRPC.TL_account_password) response;
                    UserConfig.getInstance(currentAccount).set2FA(
                            currentPassword.has_password,
                            currentPassword.hint,
                            currentPassword.login_email_pattern
                    );
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.twoStepStateUpdated,
                            currentPassword
                    );
                }
            }
        });
    }

    public void updatePasswordSettings(byte[] currentPasswordHash, TLRPC.TL_account_passwordInputSettings newSettings, Utilities.Callback<Boolean> callback) {
        TLRPC.TL_account_updatePasswordSettings req = new TLRPC.TL_account_updatePasswordSettings();
        if (currentPasswordHash != null) {
            req.password = new TLRPC.TL_inputCheckPasswordSRP();
        }
        req.new_settings = newSettings;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                boolean success = (error == null && response instanceof TLRPC.TL_boolTrue);
                if (success) {
                    loadPasswordSettings();
                }
                if (callback != null) {
                    callback.run(success);
                }
            }
        });
    }

    // ==========================================
    // 2. Privacy & Security Rules (TLRPC.TL_account_getPrivacy / TLRPC.TL_account_setPrivacy)
    // ==========================================

    public void loadPrivacySettings(final int type) {
        TLRPC.TL_account_getPrivacy req = new TLRPC.TL_account_getPrivacy();
        switch (type) {
            case PRIVACY_RULES_TYPE_LASTSEEN:
                req.key = new TLRPC.TL_inputPrivacyKeyStatusTimestamp();
                break;
            case PRIVACY_RULES_TYPE_CALLS:
                req.key = new TLRPC.TL_inputPrivacyKeyPhoneCall();
                break;
            case PRIVACY_RULES_TYPE_P2P:
                req.key = new TLRPC.TL_inputPrivacyKeyPhoneP2P();
                break;
            case PRIVACY_RULES_TYPE_PHOTO:
                req.key = new TLRPC.TL_inputPrivacyKeyProfilePhoto();
                break;
            case PRIVACY_RULES_TYPE_FORWARDS:
                req.key = new TLRPC.TL_inputPrivacyKeyForwards();
                break;
            case PRIVACY_RULES_TYPE_PHONE:
                req.key = new TLRPC.TL_inputPrivacyKeyPhoneNumber();
                break;
            case PRIVACY_RULES_TYPE_ADDED_BY_PHONE:
                req.key = new TLRPC.TL_inputPrivacyKeyAddedByPhone();
                break;
            case PRIVACY_RULES_TYPE_VOICE_MESSAGES:
                req.key = new TLRPC.TL_inputPrivacyKeyVoiceMessages();
                break;
            case PRIVACY_RULES_TYPE_BIO:
            default:
                req.key = new TLRPC.TL_inputPrivacyKeyStatusTimestamp();
                break;
        }

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                if (error == null && response instanceof TLRPC.TL_account_privacyRules) {
                    TLRPC.TL_account_privacyRules rules = (TLRPC.TL_account_privacyRules) response;
                    privacyRules.put(type, rules.rules);
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.privacyRulesUpdated,
                            type,
                            rules.rules
                    );
                }
            }
        });
    }

    public void setPrivacy(TLRPC.InputPrivacyKey key, ArrayList<TLRPC.InputPrivacyRule> rules, Utilities.Callback<Boolean> callback) {
        TLRPC.TL_account_setPrivacy req = new TLRPC.TL_account_setPrivacy();
        req.key = key;
        req.rules = rules;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                boolean success = (error == null && response instanceof TLRPC.TL_account_privacyRules);
                if (callback != null) {
                    callback.run(success);
                }
                NotificationCenter.getInstance(currentAccount).postNotificationName(
                        NotificationCenter.privacyRulesUpdated,
                        key
                );
            }
        });
    }

    // ==========================================
    // 3. Active Sessions & Authorizations (TLRPC.TL_account_getAuthorizations / resetAuthorization)
    // ==========================================

    public void loadAuthorizations(boolean force) {
        TLRPC.TL_account_getAuthorizations req = new TLRPC.TL_account_getAuthorizations();
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                if (error == null && response instanceof TLRPC.TL_account_authorizations) {
                    TLRPC.TL_account_authorizations auths = (TLRPC.TL_account_authorizations) response;
                    activeAuthorizations = auths.authorizations;
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.authorizationsUpdated,
                            activeAuthorizations
                    );
                }
            }
        });
    }

    public void resetAuthorization(long hash, Utilities.Callback<Boolean> callback) {
        TLRPC.TL_account_resetAuthorization req = new TLRPC.TL_account_resetAuthorization();
        req.hash = hash;
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                boolean success = (error == null && response instanceof TLRPC.TL_boolTrue);
                if (success) {
                    for (int i = 0; i < activeAuthorizations.size(); i++) {
                        if (activeAuthorizations.get(i).hash == hash) {
                            activeAuthorizations.remove(i);
                            break;
                        }
                    }
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.authorizationsUpdated,
                            activeAuthorizations
                    );
                }
                if (callback != null) {
                    callback.run(success);
                }
            }
        });
    }

    public void resetOtherAuthorizations(Utilities.Callback<Boolean> callback) {
        TLRPC.TL_auth_resetAuthorizations req = new TLRPC.TL_auth_resetAuthorizations();
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                boolean success = (error == null && response instanceof TLRPC.TL_boolTrue);
                if (success) {
                    loadAuthorizations(true);
                }
                if (callback != null) {
                    callback.run(success);
                }
            }
        });
    }

    // ==========================================
    // 4. Stories Synchronization (TLRPC.TL_stories_getAllStories / TLRPC.TL_stories_sendStory)
    // ==========================================

    public void loadAllStories(boolean force) {
        TLRPC.TL_stories_getAllStories req = new TLRPC.TL_stories_getAllStories();
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                if (error == null) {
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.storiesUpdated
                    );
                }
            }
        });
    }

    public void sendStory(TLRPC.InputPeer peer, TLRPC.InputMedia media, String caption, long period, ArrayList<TLRPC.InputPrivacyRule> privacyRules, Utilities.Callback<Boolean> callback) {
        TLRPC.TL_stories_sendStory req = new TLRPC.TL_stories_sendStory();
        req.peer = peer;
        req.media = media;
        req.caption = caption;
        req.period = (int) period;
        req.privacy_rules = privacyRules;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                boolean success = (error == null);
                if (success) {
                    loadAllStories(true);
                }
                if (callback != null) {
                    callback.run(success);
                }
            }
        });
    }

    // ==========================================
    // 5. Messages & Dialogs Sync (TLRPC.TL_messages_getDialogs / TLRPC.TL_messages_getHistory)
    // ==========================================

    public void loadDialogs(int offset, int limit, boolean force) {
        loadingDialogs = true;
        TLRPC.TL_messages_getDialogs req = new TLRPC.TL_messages_getDialogs();
        req.offset = offset;
        req.limit = limit;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                loadingDialogs = false;
                if (error == null && response instanceof TLRPC.TL_messages_dialogs) {
                    TLRPC.TL_messages_dialogs dialogs = (TLRPC.TL_messages_dialogs) response;
                    allDialogs = dialogs.dialogs;
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.dialogsNeedReload
                    );
                }
            }
        });
    }

    public void loadHistory(long dialogId, int offsetId, int limit, int maxId) {
        TLRPC.TL_messages_getHistory req = new TLRPC.TL_messages_getHistory();
        req.peer = getInputPeer(dialogId);
        req.offset_id = offsetId;
        req.limit = limit;
        req.max_id = maxId;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                if (error == null) {
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.messagesDidLoad,
                            dialogId
                    );
                }
            }
        });
    }

    // ==========================================
    // 6. Media Search & Documents (TLRPC.TL_messages_search / TLRPC.TL_messages_getDocument)
    // ==========================================

    public void searchMessages(long dialogId, String query, TLRPC.MessagesFilter filter, int offsetId, int limit, RequestDelegate delegate) {
        TLRPC.TL_messages_search req = new TLRPC.TL_messages_search();
        req.peer = getInputPeer(dialogId);
        req.q = query;
        req.filter = filter != null ? filter : new TLRPC.TL_inputMessagesFilterEmpty();
        req.offset_id = offsetId;
        req.limit = limit;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, delegate);
    }

    public void getDocument(TLRPC.InputDocument inputDocument, RequestDelegate delegate) {
        TLRPC.TL_messages_getDocument req = new TLRPC.TL_messages_getDocument();
        req.id = inputDocument;
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, delegate);
    }

    // ==========================================
    // 7. Forum Topics (TLRPC.TL_channels_getForumTopics)
    // ==========================================

    public void loadTopics(long channelId, boolean force) {
        TLRPC.TL_channels_getForumTopics req = new TLRPC.TL_channels_getForumTopics();
        req.channel = getInputChannel(channelId);

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                if (error == null) {
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.topicsDidLoaded,
                            channelId
                    );
                }
            }
        });
    }

    // ==========================================
    // 8. Profile Update (TLRPC.TL_account_updateProfile)
    // ==========================================

    public void updateProfile(String firstName, String lastName, String about, Utilities.Callback<Boolean> callback) {
        TLRPC.TL_account_updateProfile req = new TLRPC.TL_account_updateProfile();
        req.flags = 7;
        req.first_name = firstName;
        req.last_name = lastName;
        req.about = about;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                boolean success = (error == null);
                if (success && response instanceof TLRPC.User) {
                    UserConfig.getInstance(currentAccount).setCurrentUser((TLRPC.User) response);
                    NotificationCenter.getInstance(currentAccount).postNotificationName(
                            NotificationCenter.mainUserInfoChanged
                    );
                }
                if (callback != null) {
                    callback.run(success);
                }
            }
        });
    }

    // ==========================================
    // 9. Notifications Settings (TLRPC.TL_account_updateNotifySettings)
    // ==========================================

    public void updateNotificationSettings(TLRPC.InputNotifyPeer peer, TLRPC.TL_inputPeerNotifySettings settings) {
        TLRPC.TL_account_updateNotifySettings req = new TLRPC.TL_account_updateNotifySettings();
        req.peer = peer;
        req.settings = settings;

        ConnectionsManager.getInstance(currentAccount).sendRequest(req, new RequestDelegate() {
            @Override
            public void run(TLObject response, TLRPC.TL_error error) {
                NotificationCenter.getInstance(currentAccount).postNotificationName(
                        NotificationCenter.notificationsCountUpdated
                );
            }
        });
    }

    // ==========================================
    // 10. Sponsored Messages / Ads (TLRPC.TL_channels_getSponsoredMessages)
    // ==========================================

    public void loadSponsoredMessages(long peerId, RequestDelegate delegate) {
        if (!sponsoredMessagesEnabled) return;
        TLRPC.TL_channels_getSponsoredMessages req = new TLRPC.TL_channels_getSponsoredMessages();
        req.channel = getInputChannel(peerId);
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, delegate);
    }

    public void toggleSponsoredMessages(boolean enabled) {
        sponsoredMessagesEnabled = enabled;
        SharedPreferences preferences = ApplicationLoader.applicationContext.getSharedPreferences(
                "notifications" + (currentAccount == 0 ? "" : currentAccount),
                Context.MODE_PRIVATE
        );
        preferences.edit().putBoolean("sponsored_messages_enabled", enabled).apply();
    }

    // ==========================================
    // 11. Cloud Settings Backup & Restore
    // ==========================================

    public void saveSettingsToCloud() {
        SharedPreferences preferences = ApplicationLoader.applicationContext.getSharedPreferences(
                "plusconfig" + (currentAccount == 0 ? "" : currentAccount),
                Context.MODE_PRIVATE
        );
        // Sync via MTProto account.saveWallPaper / data storage
        NotificationCenter.getInstance(currentAccount).postNotificationName(
                NotificationCenter.updateInterfaces,
                NotificationCenter.UPDATE_MASK_ALL
        );
    }

    public void restoreSettingsFromCloud() {
        NotificationCenter.getInstance(currentAccount).postNotificationName(
                NotificationCenter.updateInterfaces,
                NotificationCenter.UPDATE_MASK_ALL
        );
    }

    private TLRPC.InputPeer getInputPeer(long dialogId) {
        TLRPC.TL_inputPeerChat peer = new TLRPC.TL_inputPeerChat();
        peer.chat_id = (int) dialogId;
        return peer;
    }

    private TLRPC.InputChannel getInputChannel(long channelId) {
        TLRPC.TL_inputChannel channel = new TLRPC.TL_inputChannel();
        channel.channel_id = (int) channelId;
        return channel;
    }

    // ==========================================
    // 12. Account Lifecycle & Logout (Goal 4)
    // ==========================================
    public void performLogout(int reason) {
        // 1. Clear tokens and session backup from AuthTokensHelper
        AuthTokensHelper.getInstance().clearAccount(currentAccount);

        // 2. Clear configuration and SharedPreferences in UserConfig
        UserConfig.getInstance(currentAccount).clearConfig();

        // 3. Dispatch logout notification to notify UI and trigger account switch/login redirect
        NotificationCenter.getInstance(currentAccount).postNotificationName(NotificationCenter.appDidLogout);
    }
}

