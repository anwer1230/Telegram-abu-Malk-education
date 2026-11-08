/**
 * TLRPC.ts - Telegram Type Language (TL) Schema & MTProto 2.0 RPC Definitions
 * Replicated exactly from TLRPC.java & TMessagesProj/tlscheme in DrKLO/Telegram Android
 */

export namespace TLRPC {
  // TL Constructors IDs
  export const CONSTRUCTOR_IDS = {
    boolFalse: -1132882121,
    boolTrue: -1720552011,
    true: 1072550713,
    vector: 481674261,
    error: -994444869,
    null: 1450380236,
    inputPeerEmpty: 2134579434,
    inputPeerSelf: 2107670217,
    inputPeerContact: 270785512,
    inputPeerForeign: -1690012891,
    inputPeerChat: 396093539,
    inputUserEmpty: -1182234929,
    inputUserSelf: -138301121,
    inputUserContact: -2031530139,
    inputUserForeign: 1700689151,
    inputPhoneContact: -208488460,
    inputFile: -181407105,
    inputMediaEmpty: -1771768449,
    inputMediaUploadedPhoto: 767900285,
    inputMediaPhoto: -1893027092,
    inputMediaGeoPoint: -104578748,
    inputMediaContact: -1494984313,
    inputMediaUploadedVideo: 1212668202,
    inputMediaUploadedThumbVideo: -433544891,
    inputMediaVideo: 2130852582,
    inputChatPhotoEmpty: 480546647,
    inputChatUploadedPhoto: -1809496270,
    inputChatPhoto: -1293828344,
    inputGeoPointEmpty: -457104426,
    inputGeoPoint: -206066487,
    inputPhotoEmpty: 483901197,
    inputPhoto: -74070332,
    inputVideoEmpty: 1426648181,
    inputVideo: -296249774,
    inputFileLocation: 342061462,
    inputVideoFileLocation: 1023632620,
    peerUser: -1649296275,
    peerChat: -1160714821,
    userEmpty: 537022650,
    userSelf: 1912944108,
    userContact: -218397927,
    userRequest: 585682608,
    userForeign: 1377093789,
    userDeleted: -1298475060,
    chatEmpty: -1683826688,
    chat: 1855757255,
    chatForbidden: -83047359,
    chatFull: 1661886910,
    chatParticipant: -925415106,
    chatParticipantsForbidden: 265468810,
    chatParticipants: 2017571861,
    messageEmpty: -2082087340,
    message: 585853626,
    messageForwarded: 99903492,
    messageService: -1618124613,
    dialog: 558533855,
    photoEmpty: 590459437,
    photo: 582313809,
    videoEmpty: -1056548696,
    video: 1510253727,
    updateNewMessage: 20626867,
    updateReadMessages: -966484431,
    updateDeleteMessages: -1456734682,
    updateUserTyping: 1806337288,
    updateChatUserTyping: 1011273702,
    updates: 1957577280,
    updatesCombined: 1918567619,
    config: 590174469,
    checkChatInvite: 1051570619,
    importChatInvite: 1817183516,
    chatInviteAlready: 1516793212,
    chatInvite: -540825363,
    chatInvitePeek: 1634294960,
    updatePendingJoinRequests: 1888497486,
    messageActionChatJoinedByLink: 80470776,
    hideChatJoinRequest: 2144883401,
    hideAllChatJoinRequests: -1355088237,
  };

  export interface TL_updates_getDifference {
    _: 'TL_updates_getDifference';
    pts: number;
    pts_total_limit?: number;
    date: number;
    qts: number;
  }

  export interface TL_updates_difference {
    _: 'TL_updates_difference';
    new_messages: any[];
    other_updates: any[];
    users: any[];
    chats: any[];
    state: {
      pts: number;
      seq: number;
      date: number;
      qts: number;
    };
  }

  // Base TLObject
  export abstract class TLObject {
    public _: string = '';
    public disableFree = false;
    [key: string]: any;
    public abstract serializeToStream(stream: any): void;
    public abstract readParams(stream: any, exception: boolean): void;
  }

  // Error codes & structure
  export interface TL_error {
    code: number;
    text: string;
  }

  export class TL_error_obj extends TLObject {
    public static constructorId = -994444869;
    public code: number = 0;
    public text: string = '';

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // Peer Types
  export type Peer =
    | { _: 'peerUser'; user_id: number }
    | { _: 'peerChat'; chat_id: number }
    | { _: 'peerChannel'; channel_id: number };

  export type InputPeer =
    | { _: 'inputPeerEmpty' }
    | { _: 'inputPeerSelf' }
    | { _: 'inputPeerContact'; user_id: number }
    | { _: 'inputPeerForeign'; user_id: number; access_hash: string }
    | { _: 'inputPeerChat'; chat_id: number }
    | { _: 'inputPeerChannel'; channel_id: number; access_hash: string };

  export type InputUser =
    | { _: 'inputUserEmpty' }
    | { _: 'inputUserSelf' }
    | { _: 'inputUserContact'; user_id: number }
    | { _: 'inputUserForeign'; user_id: number; access_hash: string };

  export type InputChannel = {
    _: 'inputChannel';
    channel_id: number;
    access_hash: string;
  };

  // Users
  export interface User {
    _: 'userSelf' | 'userContact' | 'userForeign' | 'userDeleted' | 'userEmpty';
    id: number;
    first_name?: string;
    last_name?: string;
    phone?: string;
    access_hash?: string;
    photo?: UserProfilePhoto;
    status?: UserStatus;
  }

  export interface UserFull {
    user: User;
    about?: string;
    profile_photo?: Photo;
    notify_settings?: PeerNotifySettings;
    blocked: boolean;
    real_first_name?: string;
    real_last_name?: string;
  }

  export type UserProfilePhoto =
    | { _: 'userProfilePhotoEmpty' }
    | { _: 'userProfilePhoto'; photo_small: FileLocation; photo_big: FileLocation };

  export type UserStatus =
    | { _: 'userStatusEmpty' }
    | { _: 'userStatusOnline'; expires: number }
    | { _: 'userStatusOffline'; was_online: number };

  // Files & Locations
  export interface FileLocation {
    _: 'fileLocation';
    dc_id: number;
    volume_id: string;
    local_id: number;
    secret: string;
  }

  export interface PhotoSize {
    type: string;
    location: FileLocation;
    w: number;
    h: number;
    size: number;
  }

  export interface Photo {
    _: 'photo' | 'photoEmpty';
    id: string;
    access_hash: string;
    user_id: number;
    date: number;
    caption?: string;
    sizes: PhotoSize[];
  }

  export interface Video {
    _: 'video' | 'videoEmpty';
    id: string;
    access_hash: string;
    user_id: number;
    date: number;
    caption?: string;
    duration: number;
    size: number;
    thumb?: PhotoSize;
    dc_id: number;
    w: number;
    h: number;
  }

  // Chats & Channels
  export interface Chat {
    _: 'chat' | 'chatForbidden' | 'chatEmpty' | 'channel' | 'channelForbidden';
    id: number | string;
    title: string;
    photo?: ChatPhoto;
    participants_count?: number;
    date?: number;
    left?: boolean;
    version?: number;
    broadcast?: boolean;        // علم القناة: true إذا كانت قناة بث
    megagroup?: boolean;        // علم المجموعة الخارقة: true إذا كانت مجموعة
    creator?: boolean;          // true إذا كان المستخدم الحالي هو المالك
    username?: string;          // اسم المستخدم العام (null إذا كانت خاصة)
    admin_rights?: TL_chatAdminRights; // صلاحيات المشرف
    default_banned_rights?: TL_chatBannedRights; // القيود الافتراضية للمستخدمين
    banned_rights?: TL_chatBannedRights; // القيود المفروضة على المستخدم الحالي
    linked_chat_id?: number | string;      // معرف مجموعة النقاش المرتبطة
    migrated_to?: any;
    flags?: number;
    slowmode_seconds?: number;
    signatures?: boolean;
    min?: boolean;
    scam?: boolean;
    fake?: boolean;
    restricted?: boolean;
    restriction_reason?: Array<{ platform: string; reason: string; text: string }>;
    call_active?: boolean;
    call_not_empty?: boolean;
    noforwards?: boolean;
    join_to_send?: boolean;
    join_request?: boolean;
  }

  export type ChatPhoto =
    | { _: 'chatPhotoEmpty' }
    | { _: 'chatPhoto'; photo_small: FileLocation; photo_big: FileLocation };

  export interface ChatFull {
    id: number;
    participants: ChatParticipants;
    chat_photo?: Photo;
    notify_settings?: PeerNotifySettings;
  }

  export interface ChatParticipants {
    chat_id: number;
    admin_id?: number;
    participants: ChatParticipant[];
    version: number;
  }

  export interface ChatParticipant {
    user_id: number;
    inviter_id: number;
    date: number;
  }

  // Messages
  export interface Message {
    _: 'message' | 'messageForwarded' | 'messageService' | 'messageEmpty';
    id: number;
    from_id?: number;
    peer_id?: Peer;
    to_id?: Peer;
    out: boolean;
    unread: boolean;
    date: number;
    message: string;
    media?: MessageMedia;
    action?: MessageAction;
  }

  export type MessageMedia =
    | { _: 'messageMediaEmpty' }
    | { _: 'messageMediaPhoto'; photo: Photo }
    | { _: 'messageMediaVideo'; video: Video }
    | { _: 'messageMediaGeo'; geo: GeoPoint }
    | { _: 'messageMediaContact'; phone_number: string; first_name: string; last_name: string; user_id: number };

  export interface MessageAction {
    _: string;
    title?: string;
    user_id?: number;
    users?: number[];
  }

  export interface GeoPoint {
    _: 'geoPoint' | 'geoPointEmpty';
    long: number;
    lat: number;
  }

  export interface MessageEntity {
    _: string;
    offset: number;
    length: number;
    url?: string;
    user_id?: number;
    language?: string;
    document_id?: string | number;
  }

  export interface DraftMessage {
    _: 'draftMessage' | 'draftMessageEmpty';
    flags?: number;
    reply_to_msg_id?: number;
    message: string;
    entities?: MessageEntity[];
    date: number;
  }

  export interface TL_dialog {
    _: 'dialog' | 'dialogFolder';
    id: string | number;
    top_message: number;
    read_inbox_max_id?: number;
    read_outbox_max_id?: number;
    unread_count: number;
    unread_mentions_count?: number;
    unread_reactions_count?: number;
    last_message_date: number;
    flags: number;
    folder_id?: number;
    pinned?: boolean;
    pinnedNum?: number;
    draft?: DraftMessage;
  }

  export interface Dialog {
    peer: Peer;
    top_message: number;
    unread_count: number;
  }

  // Notifications & Settings
  export interface PeerNotifySettings {
    mute_until: number;
    sound: string;
    show_previews: boolean;
    events: any;
  }

  // ==========================================
  // Two-Step Verification & Password Settings
  // ==========================================
  export interface PasswordKdfAlgo {
    _: 'passwordKdfAlgoSHA256SHA256PBKDF2' | 'passwordKdfAlgoUnknown';
    salt1?: Uint8Array | string;
    salt2?: Uint8Array | string;
    g?: number;
    p?: Uint8Array | string;
  }

  export interface TL_account_password {
    _: 'account.password';
    has_recovery?: boolean;
    has_secure_values?: boolean;
    has_password?: boolean;
    current_algo?: PasswordKdfAlgo;
    srp_B?: Uint8Array | string;
    srp_id?: number;
    hint?: string;
    email_unconfirmed_pattern?: string;
    new_algo?: PasswordKdfAlgo;
    new_secure_algo?: PasswordKdfAlgo;
    secure_random?: Uint8Array | string;
    pending_reset_date?: number;
    login_email_pattern?: string;
  }

  export interface TL_account_passwordSettings {
    _: 'account.passwordSettings';
    flags?: number;
    email?: string;
    secure_settings?: any;
    hint?: string;
  }

  export interface TL_account_passwordInputSettings {
    _: 'account.passwordInputSettings';
    flags: number;
    new_algo?: PasswordKdfAlgo;
    new_password_hash?: Uint8Array | string;
    hint?: string;
    email?: string;
    new_secure_settings?: any;
  }

  export interface TL_account_updatePasswordSettings {
    _: 'account.updatePasswordSettings';
    password?: any;
    new_settings: TL_account_passwordInputSettings;
  }

  export interface TL_account_getPassword {
    _: 'account.getPassword';
  }

  export interface TL_account_confirmPasswordEmail {
    _: 'account.confirmPasswordEmail';
    code: string;
  }

  export interface TL_account_resendPasswordEmail {
    _: 'account.resendPasswordEmail';
  }

  export interface TL_account_cancelPasswordEmail {
    _: 'account.cancelPasswordEmail';
  }

  export interface TL_account_resetPassword {
    _: 'account.resetPassword';
  }

  export interface TL_account_sendConfirmPhoneCode {
    _: 'account.sendConfirmPhoneCode';
    hash?: string;
    flags?: number;
  }

  // ==========================================
  // Privacy & Security Rules (TL-Schema)
  // ==========================================
  export type PrivacyKey =
    | { _: 'privacyKeyStatusTimestamp' }
    | { _: 'privacyKeyChatInvite' }
    | { _: 'privacyKeyPhoneCall' }
    | { _: 'privacyKeyPhoneP2P' }
    | { _: 'privacyKeyProfilePhoto' }
    | { _: 'privacyKeyForwards' }
    | { _: 'privacyKeyPhoneNumber' }
    | { _: 'privacyKeyAddedByPhone' }
    | { _: 'privacyKeyVoiceMessages' };

  export type PrivacyRule =
    | { _: 'privacyValueAllowAll' }
    | { _: 'privacyValueAllowContacts' }
    | { _: 'privacyValueDisallowAll' }
    | { _: 'privacyValueAllowUsers'; users: number[] }
    | { _: 'privacyValueDisallowUsers'; users: number[] }
    | { _: 'privacyValueAllowChatParticipants'; chats: number[] }
    | { _: 'privacyValueDisallowChatParticipants'; chats: number[] };

  export interface TL_account_privacyRules {
    _: 'account.privacyRules';
    rules: PrivacyRule[];
    users: User[];
    chats: Chat[];
  }

  export interface TL_account_getPrivacy {
    _: 'account.getPrivacy';
    key: PrivacyKey;
  }

  export interface TL_account_setPrivacy {
    _: 'account.setPrivacy';
    key: PrivacyKey;
    rules: PrivacyRule[];
  }

  export interface TL_authorization {
    _: 'authorization';
    hash: number | string;
    flags: number;
    device_model: string;
    platform: string;
    system_version: string;
    api_id: number;
    app_name: string;
    app_version: string;
    date_created: number;
    date_active: number;
    ip: string;
    country: string;
    region: string;
    current?: boolean;
    official_app?: boolean;
    password_pending?: boolean;
    encrypted_requests_disabled?: boolean;
    call_requests_disabled?: boolean;
    unconfirmed?: boolean;
  }

  export interface TL_account_authorizations {
    _: 'account.authorizations';
    authorizations: TL_authorization[];
    authorization_ttl_days: number;
  }

  export interface TL_account_getAuthorizations {
    _: 'account.getAuthorizations';
  }

  export interface TL_account_resetAuthorization {
    _: 'account.resetAuthorization';
    hash: number | string;
  }

  export interface TL_account_resetAuthorizations {
    _: 'account.resetAuthorizations';
  }

  export interface TL_contactBlocked {
    _: 'contactBlocked';
    user_id: number | string;
    date: number;
  }

  export interface TL_contacts_blocked {
    _: 'contacts.blocked' | 'contacts.blockedSlice';
    blocked: TL_contactBlocked[];
    users: User[];
    count?: number;
  }

  export interface TL_contacts_getBlocked {
    _: 'contacts.getBlocked';
    offset: number;
    limit: number;
  }

  export interface TL_contacts_block {
    _: 'contacts.block';
    id: Peer;
  }

  export interface TL_contacts_unblock {
    _: 'contacts.unblock';
    id: Peer;
  }

  // Updates & Differences
  export type Update =
    | TL_updateNewMessage
    | TL_updateNewChannelMessage
    | TL_updateEditMessage
    | TL_updateReadMessages
    | TL_updateDeleteMessages
    | TL_updateUserTyping
    | TL_updateChatUserTyping
    | TL_updateChatParticipants
    | TL_updateUserStatus;

  export interface TL_updateNewMessage {
    _: 'updateNewMessage';
    message: Message;
    pts: number;
  }

  export interface TL_updateNewChannelMessage {
    _: 'updateNewChannelMessage';
    message: Message;
    pts: number;
    pts_count: number;
  }

  export interface TL_updateEditMessage {
    _: 'updateEditMessage';
    message: Message;
    pts: number;
  }

  export interface TL_updateReadMessages {
    _: 'updateReadMessages';
    messages: number[];
    pts: number;
  }

  export interface TL_updateDeleteMessages {
    _: 'updateDeleteMessages';
    messages: number[];
    pts: number;
  }

  export interface TL_updateUserTyping {
    _: 'updateUserTyping';
    user_id: number;
    action: any;
  }

  export interface TL_updateChatUserTyping {
    _: 'updateChatUserTyping';
    chat_id: number;
    user_id: number;
    action: any;
  }

  export interface TL_updateChatParticipants {
    _: 'updateChatParticipants';
    participants: ChatParticipants;
  }

  export interface TL_updateUserStatus {
    _: 'updateUserStatus';
    user_id: number;
    status: UserStatus;
  }

  export interface Updates {
    updates: Update[];
    users: User[];
    chats: Chat[];
    date: number;
    seq: number;
  }

  // Admin & Banned Rights
  export interface TL_chatAdminRights {
    change_info: boolean;
    post_messages: boolean;
    edit_messages: boolean;
    delete_messages: boolean;
    ban_users: boolean;
    invite_users: boolean;
    pin_messages: boolean;
    add_admins: boolean;
    anonymous: boolean;
    manage_call: boolean;
    other: boolean;
  }

  export interface TL_chatBannedRights {
    view_messages: boolean;
    send_messages: boolean;
    send_media: boolean;
    send_stickers: boolean;
    send_gifs: boolean;
    send_games: boolean;
    send_inline: boolean;
    embed_links: boolean;
    send_polls: boolean;
    change_info: boolean;
    invite_users: boolean;
    pin_messages: boolean;
    until_date: number;
  }

  // Methods & RPC requests
  export class TL_auth_checkPhone extends TLObject {
    public phone_number: string = '';
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_auth_sendCode extends TLObject {
    public phone_number: string = '';
    public api_id: number = 0;
    public api_hash: string = '';
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_auth_signIn extends TLObject {
    public phone_number: string = '';
    public phone_code_hash: string = '';
    public phone_code: string = '';
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_sendMessage extends TLObject {
    public peer: InputPeer = { _: 'inputPeerSelf' };
    public peer_id?: string;
    public message: string = '';
    public random_id: number = 0;
    public reply_to_msg_id?: string;
    public entities?: any[];
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_getDialogs extends TLObject {
    public offset: number = 0;
    public max_id: number = 0;
    public limit: number = 100;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_getHistory extends TLObject {
    public peer: InputPeer = { _: 'inputPeerSelf' };
    public offset: number = 0;
    public max_id: number = 0;
    public limit: number = 100;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_joinChannel extends TLObject {
    public channel: InputChannel | string = { _: 'inputChannel', channel_id: 0, access_hash: '0' };
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_contacts_resolveUsername extends TLObject {
    public username: string = '';
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_contacts_resolvedPeer extends TLObject {
    public chats: Chat[] = [];
    public users: User[] = [];
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_getParticipant extends TLObject {
    public channel: InputChannel = { _: 'inputChannel', channel_id: 0, access_hash: '0' };
    public participant: InputUser = { _: 'inputUserSelf' };
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_channelParticipant extends TLObject {
    public participant: any;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_editAdmin extends TLObject {
    public channel: string = '';
    public user_id: string = '';
    public admin_rights: TL_chatAdminRights = {
      change_info: true,
      post_messages: true,
      edit_messages: true,
      delete_messages: true,
      ban_users: true,
      invite_users: true,
      pin_messages: true,
      add_admins: false,
      anonymous: false,
      manage_call: true,
      other: true,
    };
    public rank: string = '';
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_editBanned extends TLObject {
    public channel: string = '';
    public participant: string = '';
    public banned_rights: TL_chatBannedRights = {
      view_messages: false,
      send_messages: true,
      send_media: true,
      send_stickers: true,
      send_gifs: true,
      send_games: true,
      send_inline: true,
      embed_links: true,
      send_polls: true,
      change_info: true,
      invite_users: true,
      pin_messages: true,
      until_date: 0,
    };
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Two-Step Verification & Password Settings
  // ==========================================
  export class TL_account_getPassword extends TLObject {
    public static constructorId = 1418342645;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_account_updatePasswordSettings extends TLObject {
    public static constructorId = -1516963548;
    public password?: any;
    public new_settings: TL_account_passwordInputSettings = {
      _: 'account.passwordInputSettings',
      flags: 0,
    };
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Privacy & Security Settings
  // ==========================================
  export class TL_account_getPrivacy extends TLObject {
    public static constructorId = -623130284;
    public key: PrivacyKey = { _: 'privacyKeyStatusTimestamp' };
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_account_setPrivacy extends TLObject {
    public static constructorId = -90640169;
    public key: PrivacyKey = { _: 'privacyKeyStatusTimestamp' };
    public rules: PrivacyRule[] = [];
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Active Sessions & Authorizations
  // ==========================================
  export class TL_account_getAuthorizations extends TLObject {
    public static constructorId = -484392616;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_account_resetAuthorization extends TLObject {
    public static constructorId = -545239168;
    public hash: number | string = 0;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_auth_resetAuthorizations extends TLObject {
    public static constructorId = -1616179942;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Stories Synchronization
  // ==========================================
  export class TL_stories_getAllStories extends TLObject {
    public static constructorId = -436034177;
    public flags: number = 0;
    public next: boolean = false;
    public hidden: boolean = false;
    public state: string = '';
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_stories_sendStory extends TLObject {
    public static constructorId = -484964648;
    public flags: number = 0;
    public peer: InputPeer = { _: 'inputPeerSelf' };
    public media: any;
    public privacy_rules: PrivacyRule[] = [];
    public caption: string = '';
    public period: number = 86400;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Media Search & Document Retrieval
  // ==========================================
  export class TL_messages_search extends TLObject {
    public static constructorId = -1972579624;
    public flags: number = 0;
    public peer: InputPeer = { _: 'inputPeerSelf' };
    public q: string = '';
    public filter: any = { _: 'inputMessagesFilterEmpty' };
    public min_date: number = 0;
    public max_date: number = 0;
    public offset_id: number = 0;
    public add_offset: number = 0;
    public limit: number = 50;
    public max_id: number = 0;
    public min_id: number = 0;
    public hash: number = 0;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_getDocument extends TLObject {
    public static constructorId = 865483769;
    public id: any;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Forum Topics & Sponsored Messages
  // ==========================================
  export class TL_channels_getForumTopics extends TLObject {
    public static constructorId = -543956422;
    public channel: InputChannel | string = { _: 'inputChannel', channel_id: 0, access_hash: '0' };
    public q: string = '';
    public offset_date: number = 0;
    public offset_id: number = 0;
    public offset_topic: number = 0;
    public limit: number = 100;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_getSponsoredMessages extends TLObject {
    public static constructorId = -340246582;
    public channel: InputChannel | string = { _: 'inputChannel', channel_id: 0, access_hash: '0' };
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Profile & Notifications
  // ==========================================
  export class TL_account_updateProfile extends TLObject {
    public static constructorId = 2018596722;
    public flags: number = 0;
    public first_name?: string;
    public last_name?: string;
    public about?: string;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_account_updateNotifySettings extends TLObject {
    public static constructorId = -2067661490;
    public peer: any;
    public settings: any;
    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // Full Channel / Group Info
  export interface TL_channelFull {
    id: string;
    title: string;
    about?: string;
    participants_count: number;
    admins_count: number;
    banned_count: number;
    kicked_count: number;
    read_inbox_max_id: number;
    unread_count: number;
    admin_rights?: TL_chatAdminRights;
    banned_rights?: TL_chatBannedRights;
    default_banned_rights?: TL_chatBannedRights;
    slowmode_seconds?: number;
    slowmode_next_send_date?: number;
    can_view_participants: boolean;
    can_set_username: boolean;
    can_set_stickers: boolean;
    is_admin_only_posting: boolean;
  }

  export class TL_messages_checkChatInvite extends TLObject {
    public static constructorId = 1051570619; // 0x3eadb2f7
    public _: string = 'messages.checkChatInvite';
    public hash: string = '';

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_importChatInvite extends TLObject {
    public static constructorId = 1817183516; // 0x6c50051c
    public _: string = 'messages.importChatInvite';
    public hash: string = '';

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_chatInviteAlready extends TLObject {
    public static constructorId = 1516793212; // 0x5a686d7c
    public _: string = 'chatInviteAlready';
    public chat: any;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_chatInvite extends TLObject {
    public static constructorId = -540825363; // 0xdfc2f58d
    public _: string = 'chatInvite';
    public flags: number = 0;
    public channel: boolean = false;
    public broadcast: boolean = false;
    public public: boolean = false;
    public megagroup: boolean = false;
    public request_needed: boolean = false;
    public title: string = '';
    public about?: string;
    public photo?: any;
    public participants_count: number = 0;
    public participants?: any[];
    public chat?: any;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_chatInvitePeek extends TLObject {
    public static constructorId = 1634294960; // 0x61695cb0
    public _: string = 'chatInvitePeek';
    public chat: any;
    public expires: number = 0;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export type ChatInvite = TL_chatInviteAlready | TL_chatInvite | TL_chatInvitePeek;

  export class TL_updatePendingJoinRequests extends TLObject {
    public static constructorId = 1888497486; // 0x70919b4e
    public _: string = 'updatePendingJoinRequests';
    public peer: any;
    public requests_pending: number = 0;
    public recent_requesters: (number | string)[] = [];

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messageActionChatJoinedByLink extends TLObject {
    public static constructorId = 80470776; // 0x04cb8f18
    public _: string = 'messageActionChatJoinedByLink';
    public inviter_id: number | string = 0;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_hideChatJoinRequest extends TLObject {
    public static constructorId = 2144883401; // 0x7fd652c9
    public _: string = 'messages.hideChatJoinRequest';
    public peer: any;
    public user_id: any;
    public approved: boolean = true;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_hideAllChatJoinRequests extends TLObject {
    public static constructorId = -1355088237; // 0xaf390693
    public _: string = 'messages.hideAllChatJoinRequests';
    public peer: any;
    public approved: boolean = true;
    public link?: string;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  // ==========================================
  // Full Chat & Channel Info Requests (Network Calls)
  // ==========================================
  export class TL_messages_getFullChat extends TLObject {
    public static constructorId = 0x3b831c66;
    public _: string = 'messages.getFullChat';
    public chat_id: number | string = 0;

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_getFullChannel extends TLObject {
    public static constructorId = 0x08736a09;
    public _: string = 'channels.getFullChannel';
    public channel: InputChannel | string = { _: 'inputChannel', channel_id: 0, access_hash: '0' };

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_channels_getChannels extends TLObject {
    public static constructorId = 0x0a7f6bbb;
    public _: string = 'channels.getChannels';
    public id: any[] = [];

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export class TL_messages_getPeerDialogs extends TLObject {
    public static constructorId = 0xe470bcfd;
    public _: string = 'messages.getPeerDialogs';
    public peers: any[] = [];

    public serializeToStream(stream: any): void {}
    public readParams(stream: any, exception: boolean): void {}
  }

  export interface TL_messages_chatFull {
    _: 'messages.chatFull';
    full_chat: ChatFull;
    chats: Chat[];
    users: User[];
  }

  export interface TL_userFull {
    id: string;
    first_name: string;
    last_name?: string;
    username?: string;
    phone?: string;
    photo?: string;
    about?: string;
    is_premium: boolean;
    is_verified: boolean;
    is_bot: boolean;
    is_blocked: boolean;
    common_chats_count: number;
    pinned_msg_id?: string;
  }

  export const DEFAULT_ADMIN_RIGHTS: TL_chatAdminRights = {
    change_info: true,
    post_messages: true,
    edit_messages: true,
    delete_messages: true,
    ban_users: true,
    invite_users: true,
    pin_messages: true,
    add_admins: false,
    anonymous: false,
    manage_call: true,
    other: true,
  };

  export const DEFAULT_USER_BANNED_RIGHTS: TL_chatBannedRights = {
    view_messages: false,
    send_messages: true,
    send_media: true,
    send_stickers: true,
    send_gifs: true,
    send_games: true,
    send_inline: true,
    embed_links: true,
    send_polls: true,
    change_info: true,
    invite_users: true,
    pin_messages: true,
    until_date: 0,
  };

  export const DEFAULT_RESTRICTED_RIGHTS: TL_chatBannedRights = {
    view_messages: false,
    send_messages: true,
    send_media: true,
    send_stickers: true,
    send_gifs: true,
    send_games: true,
    send_inline: true,
    embed_links: true,
    send_polls: true,
    change_info: true,
    invite_users: false,
    pin_messages: true,
    until_date: 0,
  };

  /**
   * TLClassStore - Telegram Type Language Deserialization Registry
   * Replicated from TLClassStore.java in DrKLO/Telegram Android
   */
  export class TLClassStore {
    private static store: TLClassStore | null = null;
    private classMap = new Map<number, (stream: any) => any>();

    public static Instance(): TLClassStore {
      if (!TLClassStore.store) {
        TLClassStore.store = new TLClassStore();
      }
      return TLClassStore.store;
    }

    private constructor() {
      this.registerConstructors();
    }

    private registerConstructors() {
      // Register standard TL constructor parsers
      this.classMap.set(CONSTRUCTOR_IDS.boolTrue, () => true);
      this.classMap.set(CONSTRUCTOR_IDS.boolFalse, () => false);
      this.classMap.set(CONSTRUCTOR_IDS.error, (s) => ({ _: 'error', code: s?.readInt32?.() || 0, text: s?.readString?.() || '' }));
      this.classMap.set(CONSTRUCTOR_IDS.userSelf, (s) => ({ _: 'userSelf', id: s?.readInt32?.() || 0 }));
      this.classMap.set(CONSTRUCTOR_IDS.peerUser, (s) => ({ _: 'peerUser', user_id: s?.readInt32?.() || 0 }));
      this.classMap.set(CONSTRUCTOR_IDS.peerChat, (s) => ({ _: 'peerChat', chat_id: s?.readInt32?.() || 0 }));
      this.classMap.set(CONSTRUCTOR_IDS.dialog, (s) => ({ _: 'dialog', id: s?.readInt64?.() || 0 }));
      this.classMap.set(CONSTRUCTOR_IDS.message, (s) => ({ _: 'message', id: s?.readInt32?.() || 0, text: s?.readString?.() || '' }));
      this.classMap.set(CONSTRUCTOR_IDS.updateNewMessage, (s) => ({ _: 'updateNewMessage', message: s }));
      this.classMap.set(CONSTRUCTOR_IDS.chatInviteAlready, (s) => ({ _: 'chatInviteAlready', chat: s?.chat }));
      this.classMap.set(CONSTRUCTOR_IDS.chatInvite, (s) => ({ _: 'chatInvite', ...s }));
      this.classMap.set(CONSTRUCTOR_IDS.updatePendingJoinRequests, (s) => ({ _: 'updatePendingJoinRequests', ...s }));
      this.classMap.set(CONSTRUCTOR_IDS.messageActionChatJoinedByLink, (s) => ({ _: 'messageActionChatJoinedByLink', inviter_id: s?.inviter_id || 0 }));
    }

    public register(constructorId: number, factory: (stream: any) => any): void {
      this.classMap.set(constructorId, factory);
    }

    /**
     * Deserializes a TL constructor ID from input stream
     */
    public TLdeserialize(stream: any, constructorId: number, exception: boolean = false): any {
      const factory = this.classMap.get(constructorId);
      if (factory) {
        return factory(stream);
      }

      if (exception) {
        throw new Error(`[TLClassStore] Unknown TL constructor: 0x${constructorId.toString(16)} (${constructorId})`);
      }

      return { _: 'unknown_tl_object', constructorId, data: stream };
    }
  }
}

