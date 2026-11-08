package org.telegram.tgnet;

import java.util.ArrayList;

/**
 * TLRPC.java - Official DrKLO/Telegram Android Implementation
 * Path: TMessagesProj/src/main/java/org/telegram/tgnet/TLRPC.java
 *
 * MTProto TL-Schema definitions and type registries.
 */
public class TLRPC {

    public interface RequestDelegate {
        void run(TLObject response, TL_error error);
    }

    public static class TL_error {
        public int code;
        public String text;
    }

    public static abstract class TLObject {
        public boolean disableFree = false;
        public abstract void serializeToStream(SerializedData stream);
        public void readParams(SerializedData stream, boolean exception) {}
    }

    public static class TL_boolTrue extends TLObject {
        public static final int constructor = 0x997275b5;
        @Override
        public void serializeToStream(SerializedData stream) {
            stream.writeInt32(constructor);
        }
    }

    public static class User extends TLObject {
        public static final int constructor = 0x2e56e78a;
        public long id;
        public long access_hash;
        public String first_name = "";
        public String last_name = "";
        public String username = "";
        public String phone = "";
        public boolean self = false;
        public boolean contact = false;
        public boolean mutual_contact = false;
        public boolean deleted = false;
        public boolean bot = false;

        public static User TLdeserialize(SerializedData stream, int constructor, boolean exception) {
            User user = new User();
            user.readParams(stream, exception);
            return user;
        }

        @Override
        public void serializeToStream(SerializedData stream) {
            stream.writeInt32(constructor);
            stream.writeInt64(id);
            stream.writeInt64(access_hash);
            stream.writeString(first_name != null ? first_name : "");
            stream.writeString(last_name != null ? last_name : "");
            stream.writeString(username != null ? username : "");
            stream.writeString(phone != null ? phone : "");
            stream.writeInt32(self ? 1 : 0);
        }

        @Override
        public void readParams(SerializedData stream, boolean exception) {
            id = stream.readInt64(exception);
            access_hash = stream.readInt64(exception);
            first_name = stream.readString(exception);
            last_name = stream.readString(exception);
            username = stream.readString(exception);
            phone = stream.readString(exception);
            self = stream.readInt32(exception) == 1;
        }
    }

    public static class TL_account_registerDevice extends TLObject {
        public static final int constructor = 0x637ea290;
        public int token_type;
        public String token;
        public boolean app_sandbox;
        public byte[] secret;
        public ArrayList<Long> other_uids = new ArrayList<>();

        @Override
        public void serializeToStream(SerializedData stream) {
            stream.writeInt32(constructor);
            stream.writeInt32(token_type);
            stream.writeString(token);
        }
    }

    public static class TL_account_getPassword extends TLObject {
        public static final int constructor = 0x548d30f8;
        @Override
        public void serializeToStream(SerializedData stream) {
            stream.writeInt32(constructor);
        }
    }

    public static class TL_account_password extends TLObject {
        public boolean has_password;
        public String hint = "";
        public String login_email_pattern = "";
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_updatePasswordSettings extends TLObject {
        public static final int constructor = 0xa59b102f;
        public TL_inputCheckPasswordSRP password;
        public TL_account_passwordInputSettings new_settings;
        @Override
        public void serializeToStream(SerializedData stream) {
            stream.writeInt32(constructor);
        }
    }

    public static class TL_inputCheckPasswordSRP extends TLObject {
        public long srp_id;
        public byte[] A;
        public byte[] M1;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_passwordInputSettings extends TLObject {
        public int flags;
        public String hint;
        public String email;
        public byte[] new_password_hash;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_getPrivacy extends TLObject {
        public InputPrivacyKey key;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_setPrivacy extends TLObject {
        public InputPrivacyKey key;
        public ArrayList<PrivacyRule> rules = new ArrayList<>();
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_privacyRules extends TLObject {
        public ArrayList<PrivacyRule> rules = new ArrayList<>();
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static abstract class InputPrivacyKey extends TLObject {}
    public static abstract class PrivacyRule extends TLObject {}

    public static class TL_account_getAuthorizations extends TLObject {
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_authorizations extends TLObject {
        public ArrayList<TL_authorization> authorizations = new ArrayList<>();
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_authorization extends TLObject {
        public long hash;
        public int flags;
        public String device_model;
        public String platform;
        public String system_version;
        public int api_id;
        public String app_name;
        public String app_version;
        public int date_created;
        public int date_active;
        public String ip;
        public String country;
        public String region;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_account_resetAuthorization extends TLObject {
        public long hash;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_auth_resetAuthorizations extends TLObject {
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_auth_sendCode extends TLObject {
        public String phone_number;
        public int api_id;
        public String api_hash;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_auth_sentCode extends TLObject {
        public String phone_code_hash;
        public int timeout;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_auth_signIn extends TLObject {
        public String phone_number;
        public String phone_code_hash;
        public String phone_code;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }

    public static class TL_auth_authorization extends TLObject {
        public User user;
        public byte[] future_auth_token;
        public int future_auth_token_expires;
        @Override
        public void serializeToStream(SerializedData stream) {}
    }
}
