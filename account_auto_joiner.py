# -*- coding: utf-8 -*-
"""
account_auto_joiner.py - نظام الانضمام التلقائي الدوري الذكي وعزل المجموعات المنضمة مسبقاً
================================================================================
المتطلبات:
1. روابط ثابتة في النظام الداخلي.
2. عند تسجيل دخول أي حساب:
   - عزل المجموعات المنضم إليها الحساب مسبقاً.
   - تلقائياً كل 5 دقائق (300 ثانية) يتم الانضمام إلى رابط جديد (انضمام جديد كل 5 دقائق).
   - استمرار العملية وهكذا دورياً مع رصد FloodWait وحماية الحساب.
"""

import os
import time
import json
import re
import logging
import threading
from datetime import datetime
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
from telethon.errors import (
    UserAlreadyParticipantError, FloodWaitError, InviteHashExpiredError,
    InviteHashInvalidError, ChannelsTooMuchError, InviteRequestSentError
)

logger = logging.getLogger("AccountAutoJoiner")

# ─── الروابط الثابتة للنظام الداخلي ───────────────────────────────────────────
SYSTEM_FIXED_TELEGRAM_LINKS = [
  "https://t.me/manadibbknk",
  "https://t.me/aboarah",
  "https://t.me/ampfec",
  "https://t.me/WdYk1XVBoO1lYmNk",
  "https://t.me/TbVN8C3aypIzYzI0",
  "https://t.me/saudi_camp/223909",
  "https://t.me/Delfry1119",
  "https://t.me/securit_gov",
  "https://t.me/aljumum1",
  "https://t.me/NCAedusa",
  "https://t.me/step_alhassani",
  "https://t.me/QiyasSTEP",
  "https://t.me/stepacademy",
  "https://t.me/steeep",
  "https://t.me/STEP_5117",
  "https://t.me/rooo5ij",
  "https://t.me/aramcoassessme",
  "https://t.me/himamroshn",
  "https://t.me/RowadSNB",
  "https://t.me/takeastepforward",
  "https://t.me/Tadawul_GDP",
  "https://t.me/CMAGDP",
  "https://t.me/STC_TIP",
  "https://t.me/KPMGdiscussion",
  "https://t.me/Deloitte_GDPsaudi",
  "https://t.me/PwCgraduPrpgram",
  "https://t.me/EYGrads",
  "https://t.me/+4JJT0LZTb4FhZTIx",
  "https://t.me/zain_Evolve",
  "https://t.me/swccjobs",
  "https://t.me/GDPalrajhi",
  "https://t.me/Alrajhi_GDPIT",
  "https://t.me/rajhiGDP",
  "https://t.me/Aseel14193",
  "https://t.me/taminat_mohbh",
  "https://t.me/jobsofsama",
  "https://t.me/AlinmaBank2",
  "https://t.me/EmdadAlkhebratGDP",
  "https://t.me/gdpmedgulf",
  "https://t.me/Ox52JAYEOXNhMjU0",
  "https://t.me/sadaia_1",
  "https://t.me/QiddiyaGDP",
  "https://t.me/SafwaMobilyy",
  "https://t.me/Takamol_GDP",
  "https://t.me/GIBJS",
  "https://t.me/coop_training",
  "https://t.me/sdgghjklv",
  "https://t.me/sda_fuel",
  "https://t.me/anbitgdp",
  "https://t.me/Seu_step",
  "https://t.me/SQA_SDA",
  "https://t.me/TuwaiqAcademy",
  "https://t.me/saudicamp_channel",
  "https://t.me/saudi_camp",
  "https://t.me/bsfmisk",
  "https://t.me/LeanGraduateProgram",
  "https://t.me/AFAQPROGRAM",
  "https://t.me/SIDFNokhab",
  "https://t.me/SGS_2023",
  "https://t.me/saudigroundservices",
  "https://t.me/SaudiLogisticsAcademy",
  "https://t.me/YouthGrowthProgramYGP",
  "https://t.me/NEOMGrOW",
  "https://t.me/tahafprogram",
  "https://t.me/+M12BpkxyR4FmMzg0",
  "https://t.me/tadreb_HRDF",
  "https://t.me/SAlaborlaw",
  "https://t.me/SanabilGDP",
  "https://t.me/nahdileadership",
  "https://t.me/DSCGDP",
  "https://t.me/saudiaramcoassessment",
  "https://t.me/SNBCap",
  "https://t.me/ksaco11",
  "https://t.me/militarey",
  "https://t.me/refah1B",
  "https://t.me/refah2B",
  "https://t.me/RAFAH_JUNIOR",
  "https://t.me/RAFAH_JUNIOR4",
  "https://t.me/RAFAH_JUNIOR5",
  "https://t.me/RefAhPrimary",
  "https://t.me/RAFAH_MIDDLE12",
  "https://t.me/RAFAH_MIDDLE2",
  "https://t.me/RAFAH_MIDDLE3",
  "https://t.me/RAFAH_Secondary1",
  "https://t.me/RAFAH_SECONDARYS",
  "https://t.me/RAFAH_Secondary1_3",
  "https://t.me/RAFAH_Secondary3",
  "https://t.me/RAFAH_SECONDARYQ",
  "https://t.me/RAFAHmath23",
  "https://t.me/RAFAH_Secondary5",
  "https://t.me/RAFAH_SECONDARY",
  "https://t.me/RefahEducational",
  "https://t.me/RAFAHqudrat12",
  "https://t.me/RAFAHqudrat",
  "https://t.me/RAFAH_ENGLISH",
  "https://t.me/RAFAH_ENGLISHELEM",
  "https://t.me/RAFAH_ENGLISHELEM1",
  "https://t.me/RAFAH_ENGLISHINTER",
  "https://t.me/RAFAH_ENGLISHINTER2",
  "https://t.me/RAFAH_ENGLISHINTER3",
  "https://t.me/RAFAH_ENGLISHSECOND",
  "https://t.me/RAFAH_JUNIOR_sci",
  "https://t.me/RAFAH_JUNIOR_sci654",
  "https://t.me/RAFAH_middle_sci",
  "https://t.me/RAFAH_physics",
  "https://t.me/RAFAH_chemistry",
  "https://t.me/RAFAH_Biolgy",
  "https://t.me/qdratalarjani2020",
  "https://t.me/RAFAH_tahsiliu",
  "https://t.me/Math202011",
  "https://t.me/mathPIZA",
  "https://t.me/RAFAH_Administrative",
  "https://t.me/raydeatalebda",
  "https://t.me/RAFAH_mawhiba",
  "https://t.me/RAFAH_STEAM",
  "https://t.me/RAFAHTechnique",
  "https://t.me/tashweqat",
  "https://t.me/RefahClassera",
  "https://t.me/RefAhgaem",
  "https://t.me/VE8GiUqDmTdNwjOF",
  "https://t.me/Refahtakrem",
  "https://t.me/mmmm2020mmm",
  "https://t.me/murciaksa",
  "https://t.me/sdaym_jeddah",
  "https://t.me/MrkhaledCs",
  "https://t.me/Infantry7",
  "https://t.me/ksa_military_colleges",
  "https://t.me/sdspnu",
  "https://t.me/HCT_CHAT2",
  "https://t.me/ZayedUniversity2",
  "https://t.me/AbuDhae",
  "https://t.me/UAEStudents2",
  "https://t.me/UAEgroupsa",
  "https://t.me/+ikaCXRdY7cszNDFk",
  "https://t.me/Accountttttttttttt43",
  "https://t.me/ebbtsamfresase",
  "https://t.me/militarySa",
  "https://t.me/amdd757hh",
  "https://t.me/ABAN10076",
  "https://t.me/usjsbkk",
  "https://t.me/MODJOBSSS",
  "https://t.me/JiRwPDKI5Y5M2Q0",
  "https://t.me/banatjedah",
  "https://t.me/TaibahUniversity1",
  "https://t.me/iiiiiiiiii881",
  "https://t.me/B58036",
  "https://t.me/R5802492",
  "https://t.me/M805029",
  "https://t.me/SB9r7eYyHsdlZTA0",
  "https://t.me/altkharg",
  "https://t.me/T58694",
  "https://t.me/Q58023",
  "https://t.me/Jazan580125",
  "https://t.me/Sh45238",
  "https://t.me/hawamel8",
  "https://t.me/QudratQ",
  "https://t.me/TRQIHH",
  "https://t.me/F455280",
  "https://t.me/psychologyimamu9",
  "https://t.me/tfolambakra",
  "https://t.me/taxijazan",
  "https://t.me/TajnidSA",
  "https://t.me/m_2cl",
  "https://t.me/waelqodorat",
  "https://t.me/flawe2",
  "https://t.me/TaxiMakka",
  "https://t.me/mayqklhhs503",
  "https://t.me/RWQSAE",
  "https://t.me/TxJeddah",
  "https://t.me/XR2006",
  "https://t.me/httpgjl",
  "https://t.me/Ask_Buraydah",
  "https://t.me/Alreyaddrivers",
  "https://t.me/aqarmousa",
  "https://t.me/tjnid",
  "https://t.me/GRTaief",
  "https://t.me/hnhdfjjdsshjc",
  "https://t.me/kropp22",
  "https://t.me/haedusa",
  "https://t.me/Fatma_Construction",
  "https://t.me/Bre1ada1",
  "https://t.me/x86x7x",
  "https://t.me/riyadh12344",
  "https://t.me/tteevf",
  "https://t.me/Saudi_program",
  "https://t.me/Arfz22",
  "https://t.me/alwm_edaryehh",
  "https://t.me/bcginksa",
  "https://t.me/sl28a",
  "https://t.me/ksacon6",
  "https://t.me/MOHMOH2222",
  "https://t.me/Coop_Training_TU",
  "https://t.me/siolhpi",
  "https://t.me/sss01930",
  "https://t.me/taifmoia",
  "https://t.me/deloittebrightstart",
  "https://t.me/wsailr8abeh",
  "https://t.me/k6imo",
  "https://t.me/coop_TVCT",
  "https://t.me/m2002gik",
  "https://t.me/YanbuIndustrialCollegeUnofficial",
  "https://t.me/m2002ou",
  "https://t.me/drugg8",
  "https://t.me/aazoiy",
  "https://t.me/AL_ghad_Colleges",
  "https://t.me/Alghad_College1447",
  "https://t.me/alghadeu",
  "https://t.me/Thebooks_of_Al_Ghad_College",
  "https://t.me/Alghad_College_Riyadh",
  "https://t.me/Alghad_College_qassim",
  "https://t.me/Alghad_College_tabuk",
  "https://t.me/Alghad_College_najran",
  "https://t.me/Alghad_College_abha",
  "https://t.me/Alghad_College_dammam",
  "https://t.me/Alghad_College_madinah",
  "https://t.me/Alghad_College_jeddah",
  "https://t.me/elntraa",
  "https://t.me/Ecoponwin",
  "https://t.me/v151180",
  "https://t.me/tvtc202",
  "https://t.me/nmaaaaaaaaaaaaaaaa",
  "https://t.me/sec4al",
  "https://t.me/travel_thailand",
  "https://t.me/SNBCapitalGDP",
  "https://t.me/irelandscholarshipsaudi",
  "https://t.me/hraaaag",
  "https://t.me/GroupMath",
  "https://t.me/altaelim2030",
  "https://t.me/itex24_io",
  "https://t.me/AlRukhsa",
  "https://t.me/CivilDefense1",
  "https://t.me/TVCT_HAIL",
  "https://t.me/dubaiguideD",
  "https://t.me/AskJeddah",
  "https://t.me/ukksa",
  "https://t.me/mathtmeS3",
  "https://t.me/mathtmeM3",
  "https://t.me/uofjeddahmed",
  "https://t.me/SRPSARC",
  "https://t.me/GrStudies",
  "https://t.me/alnashatt",
  "https://t.me/Teacherspool",
  "https://t.me/UNAcompany2021",
  "https://t.me/trbowy",
  "https://t.me/Barista_SA",
  "https://t.me/SALIC_GDP",
  "https://t.me/naql0000",
  "https://t.me/sparovin1",
  "https://t.me/saad_73333",
  "https://t.me/alfalahAD",
  "https://t.me/abdullaharabic",
  "https://t.me/resriy",
  "https://t.me/TTOOMAY_5",
  "https://t.me/NoorSystemExpertsGroup",
  "https://t.me/KFU0005",
  "https://t.me/albahauniv",
  "https://t.me/Saudi_Social_Studies_Forum",
  "https://t.me/naseej",
  "https://t.me/KFU2022i",
  "https://t.me/travelyasir707",
  "https://t.me/MurciaApartments",
  "https://t.me/GOSIGDPw",
  "https://t.me/cooptraning_inksachat",
  "https://t.me/Taifjobs1",
  "https://t.me/Geographyhemma",
  "https://t.me/thiqaedu2030",
  "https://t.me/energy_oil_gas",
  "https://t.me/SpireSA",
  "https://t.me/F997F",
  "https://t.me/BU_optics",
  "https://t.me/mim_careers",
  "https://t.me/ee_career",
  "https://t.me/ers73d",
  "https://t.me/jshdhdhdkjj",
  "https://t.me/economics22finance",
  "https://t.me/Qa2erScholarshipschat",
  "https://t.me/AguEduSA",
  "https://t.me/KSA_RSAF5",
  "https://t.me/ffffajuks",
  "https://t.me/teachingmethodsHou",
  "https://t.me/alhrbeauua",
  "https://t.me/ThecourtyardPhD",
  "https://t.me/hjanhwkyala",
  "https://t.me/durchy53dgunj",
  "https://t.me/+jt6K48y83_U5YjRk",
  "https://qxa.me/group",
  "https://t.me/mohmmd811",
  "https://t.me/Tm_gj",
  "https://t.me/TM_ASs",
  "https://t.me/TM_AGR_KSA",
  "https://t.me/Tm_cn",
  "https://t.me/Tm_yy",
  "https://t.me/TM_hi",
  "https://t.me/Shoop_SA",
  "https://t.me/on_vip",
  "https://t.me/TM_arab",
  "https://t.me/Tm_gg",
  "https://t.me/Tm_kas",
  "https://t.me/TM_2035",
  "https://t.me/eaqaratTMVip",
  "https://t.me/hgjbvccj",
  "https://t.me/HealthPrograms",
  "https://t.me/Patrolnew",
  "https://t.me/spspksaa",
  "https://t.me/Hail_1444",
  "https://t.me/SADAX2024",
  "https://t.me/al8oaat",
  "https://t.me/al7rss_almlky",
  "https://t.me/alhars4",
  "https://t.me/gov_sa00",
  "https://t.me/kfsc_ksa",
  "https://t.me/KFSC1446",
  "https://t.me/knegabdoalazez2021",
  "https://t.me/hajtamher",
  "https://t.me/NITI11220",
  "https://t.me/KsaEdu_Newss",
  "https://t.me/RASF91",
  "https://t.me/IATC2",
  "https://t.me/wizzKSA",
  "https://t.me/CreemUber",
  "https://t.me/KAU_STUDENTS1",
  "https://t.me/TAJNED11",
  "https://t.me/kdad1",
  "https://t.me/saifff114",
  "https://t.me/wwno4",
  "https://t.me/math_ar",
  "https://t.me/EngineersForum2021",
  "https://t.me/blogger884",
  "https://t.me/yanbugirls",
  "https://t.me/jedahh0",
  "https://t.me/tqu214",
  "https://t.me/albeni_alsudi",
  "https://t.me/UJ_students_22",
  "https://t.me/aramcocoop",
  "https://t.me/abokhalid112",
  "https://t.me/khibrat2021",
  "https://t.me/salla_zied1",
  "https://t.me/HIWPT1",
  "https://t.me/Jeddahonline",
  "https://t.me/taqat_jazan1",
  "https://t.me/mnghai",
  "https://t.me/ArabicC60",
  "https://t.me/flynas_cabincrew",
  "https://t.me/infinitynikki_arr",
  "https://t.me/masteruniversykingfaisal",
  "https://t.me/RoyalNavy1",
  "https://t.me/ERRlQ",
  "https://t.me/UQUniversity",
  "https://t.me/KSA_2021"
]

# مدير الجلسات وخيوط الانضمام لكل حساب
_WORKERS = {}
_WORKERS_LOCK = threading.Lock()

# سياق التطبيق ومراجع الاتصال (تُحقن عبر init_account_auto_joiner)
_SOCKETIO = None
_USERS_MAP = None
_USERS_LOCK = None
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def init_account_auto_joiner(socketio=None, users_map=None, users_lock=None, data_dir=None):
    """تهيئة محرك الانضمام وربطه بالسوكيت وقفل المستخدمين ومجلد البيانات"""
    global _SOCKETIO, _USERS_MAP, _USERS_LOCK, _DATA_DIR
    if socketio is not None:
        _SOCKETIO = socketio
    if users_map is not None:
        _USERS_MAP = users_map
    if users_lock is not None:
        _USERS_LOCK = users_lock
    if data_dir is not None:
        _DATA_DIR = data_dir


def _get_history_file(user_id):
    os.makedirs(_DATA_DIR, exist_ok=True)
    return os.path.join(_DATA_DIR, f"account_{user_id}_auto_join_history.json")


def _load_account_joined_cache(user_id):
    h_file = _get_history_file(user_id)
    if os.path.exists(h_file):
        try:
            with open(h_file, 'r', encoding='utf-8') as f:
                d = json.load(f)
                return set(d.get('joined', []))
        except Exception:
            pass
    return set()


def _save_account_joined_cache(user_id, joined_set, history_items=None):
    h_file = _get_history_file(user_id)
    try:
        with open(h_file, 'w', encoding='utf-8') as f:
            json.dump({
                'user_id': user_id,
                'joined': list(joined_set),
                'history': history_items or [],
                'updated_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving history for {user_id}: {e}")


def _emit_log(message, user_id=None):
    logger.info(f"[{user_id or 'System'}] {message}")
    if _SOCKETIO:
        try:
            if user_id:
                _SOCKETIO.emit('log_update', {'message': message}, to=user_id)
            else:
                _SOCKETIO.emit('log_update', {'message': message})
        except Exception:
            pass


async def _extract_account_existing_dialogs(client):
    """استخراج كافة المجموعات والقنوات المشترك فيها الحساب حالياً"""
    joined_usernames = set()
    joined_ids = set()
    joined_titles = set()
    try:
        dialogs = await client.get_dialogs(limit=600)
        for d in dialogs:
            if d.is_group or d.is_channel:
                ent = d.entity
                if ent:
                    uname = getattr(ent, 'username', None)
                    if uname:
                        joined_usernames.add(uname.lower().strip())
                    eid = getattr(ent, 'id', None)
                    if eid:
                        joined_ids.add(str(eid))
                    title = getattr(ent, 'title', None)
                    if title:
                        joined_titles.add(title.strip().lower())
    except Exception as e:
        logger.warning(f"Could not fetch full dialogs list: {e}")
    return joined_usernames, joined_ids, joined_titles


def _extract_peer_from_url(url):
    clean = url.strip()
    if clean.startswith('https://t.me/'):
        clean = clean[13:]
    elif clean.startswith('http://t.me/'):
        clean = clean[12:]
    elif clean.startswith('https://telegram.me/'):
        clean = clean[20:]
    elif clean.startswith('@'):
        clean = clean[1:]
    clean = clean.split('?')[0].split('/')[0].strip()
    return clean.lower()


def isolate_account_joined_groups(user_id, client_manager):
    """
    عزل المجموعات المنضم إليها الحساب مسبقاً:
    - فحص محادثات الحساب في تيليجرام
    - مقارنتها بالروابط الثابتة للنظام والروابط المحفوظة
    - عزل المنضم مسبقاً (isolated_already_joined)
    - استخراج الروابط المتبقية للانضمام الدوري (pending_links)
    """
    all_system_links = list(SYSTEM_FIXED_TELEGRAM_LINKS)

    # دمج الروابط المحفوظة من saved_links.json إذا توفرت
    saved_file = os.path.join(_DATA_DIR, 'saved_links.json')
    if os.path.exists(saved_file):
        try:
            with open(saved_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                for l in saved_data.get('links', []):
                    u = l.get('url', '').strip()
                    if u and u not in all_system_links:
                        all_system_links.append(u)
        except Exception:
            pass

    joined_cache = _load_account_joined_cache(user_id)

    # جلب المحادثات الحالية من تيليجرام
    joined_usernames = set()
    joined_ids = set()
    joined_titles = set()
    if client_manager and client_manager.client:
        try:
            coro = _extract_account_existing_dialogs(client_manager.client)
            joined_usernames, joined_ids, joined_titles = client_manager.run_coroutine(coro)
        except Exception as e:
            logger.warning(f"Error inspecting dialogs for {user_id}: {e}")

    isolated_already = []
    pending = []

    for link in all_system_links:
        norm = link.lower().strip()
        peer = _extract_peer_from_url(link)

        # 1. فحص الكاش الداخلي للحساب
        if norm in joined_cache or link in joined_cache:
            isolated_already.append(link)
            continue

        # 2. فحص معرف القناة/المجموعة العام
        if peer and peer in joined_usernames:
            isolated_already.append(link)
            joined_cache.add(norm)
            continue

        pending.append(link)

    # حفظ الكاش
    _save_account_joined_cache(user_id, joined_cache)

    account_name = "الحساب"
    if _USERS_MAP and _USERS_LOCK:
        with _USERS_LOCK:
            account_name = _USERS_MAP.get(user_id, {}).get('account_name') or account_name

    _emit_log(
        f"🔒 [عزل المجموعات المنضمة مسبقاً] تم فحص محادثات {account_name}: "
        f"عزل {len(isolated_already)} مجموعة منضمة مسبقاً | المتبقي {len(pending)} مجموعة جديدة للانضمام الدوري كل 5 دقائق.",
        user_id
    )

    if _SOCKETIO:
        try:
            _SOCKETIO.emit('auto_join_isolated', {
                'user_id': user_id,
                'isolated_count': len(isolated_already),
                'pending_count': len(pending),
                'total_count': len(all_system_links),
                'message': f"تم عزل {len(isolated_already)} مجموعة منضمة مسبقاً بنجاح"
            }, to=user_id)
        except Exception:
            pass

    return isolated_already, pending


async def _async_join_group(client, link):
    """محاولة الانضمام الفعلي لرابط سواء كان دعوة خاصة أو عامة"""
    clean = link.strip()
    if clean.startswith('https://t.me/'):
        clean_path = clean[13:]
    elif clean.startswith('http://t.me/'):
        clean_path = clean[12:]
    elif clean.startswith('https://telegram.me/'):
        clean_path = clean[20:]
    elif clean.startswith('@'):
        clean_path = clean[1:]
    else:
        clean_path = clean

    # 1. روابط الدعوة الخاصة (+ أو joinchat/)
    m_invite = re.search(r'(?:\+|joinchat/)([A-Za-z0-9_\-]+)', clean_path)
    if m_invite:
        invite_hash = m_invite.group(1)
        try:
            res = await client(ImportChatInviteRequest(hash=invite_hash))
            return {"success": True, "already": False, "message": "تم الانضمام بنجاح عبر رابط الدعوة"}
        except UserAlreadyParticipantError:
            return {"success": True, "already": True, "message": "أنت عضو بالفعل في هذه المجموعة"}
        except InviteRequestSentError:
            return {"success": True, "already": False, "message": "تم إرسال طلب انضمام للمجموعة (بانتظار المشرف)"}
        except FloodWaitError as e:
            return {"success": False, "flood": True, "seconds": e.seconds, "message": f"قيود FloodWait: يرجى الانتظار {e.seconds} ثانية"}
        except (InviteHashExpiredError, InviteHashInvalidError):
            return {"success": False, "already": False, "message": "رابط الدعوة غير صالح أو منتهي الصلاحية"}
        except ChannelsTooMuchError:
            return {"success": False, "limit": True, "message": "بلغ الحساب الحد الأقصى للقنوات والمجموعات"}
        except Exception as e:
            err_msg = str(e)
            if "USER_ALREADY_PARTICIPANT" in err_msg.upper():
                return {"success": True, "already": True, "message": "أنت عضو بالفعل في هذه المجموعة"}
            return {"success": False, "already": False, "message": f"خطأ رابط الدعوة: {err_msg[:120]}"}

    # 2. القنوات والمجموعات العامة
    peer = clean_path.split('/')[0].split('?')[0].strip()
    try:
        entity = await client.get_entity(peer)
        await client(JoinChannelRequest(channel=entity))
        return {"success": True, "already": False, "message": f"تم الانضمام بنجاح إلى @{peer}"}
    except UserAlreadyParticipantError:
        return {"success": True, "already": True, "message": f"أنت عضو بالفعل في @{peer}"}
    except FloodWaitError as e:
        return {"success": False, "flood": True, "seconds": e.seconds, "message": f"قيود FloodWait: يرجى الانتظار {e.seconds} ثانية"}
    except ChannelsTooMuchError:
        return {"success": False, "limit": True, "message": "بلغ الحساب الحد الأقصى للقنوات والمجموعات"}
    except Exception as e:
        err_msg = str(e)
        if "USER_ALREADY_PARTICIPANT" in err_msg.upper():
            return {"success": True, "already": True, "message": f"أنت عضو بالفعل في @{peer}"}
        return {"success": False, "already": False, "message": f"تعذر الانضمام: {err_msg[:120]}"}


def _account_auto_join_loop(user_id, client_manager, stop_event, pause_event, state):
    """
    حلقة العمل الدورية كل 5 دقائق (300 ثانية):
    - تنضم إلى رابط جديد
    - تنتظر 5 دقائق كاملة مع تحديث العداد التنازلي
    - تكرر العملية لرابط جديد كل 5 دقائق وهكذا
    """
    DELAY_BETWEEN_JOINS = 300  # 5 دقائق = 300 ثانية
    joined_cache = _load_account_joined_cache(user_id)
    history_items = []

    account_name = user_id
    if _USERS_MAP and _USERS_LOCK:
        with _USERS_LOCK:
            account_name = _USERS_MAP.get(user_id, {}).get('account_name') or user_id

    _emit_log(
        f"🚀 [بدء الانضمام التلقائي الدوري] الحساب ({account_name}): سيبدأ الانضمام كل 5 دقائق بمعدل رابط جديد كل 5 دقائق.",
        user_id
    )

    idx = 0
    total = len(state['pending'])

    # بدء العداد للانضمام الأول بعد مهلة قصيرة للتهيئة (10 ثوانٍ)
    first_join = True

    while not stop_event.is_set():
        if pause_event.is_set():
            state['status'] = 'paused'
            _emit_log("⏸ [انضمام تلقائي] تم الإيقاف المؤقت لعملية الانضمام الدوري.", user_id)
            while pause_event.is_set() and not stop_event.is_set():
                time.sleep(1)
            if stop_event.is_set():
                break
            state['status'] = 'running'
            _emit_log("▶️ [انضمام تلقائي] تم استئناف الانضمام الدوري.", user_id)

        if not state['pending']:
            _emit_log("🎉 [اكتمل الانضمام] تم الانتهاء من جميع الروابط المتاحة بنجاح!", user_id)
            state['status'] = 'completed'
            break

        # انتظار أولي بسيط قبل أول انضمام (10 ثوانٍ)، أو 5 دقائق بين كل انضمام والذي يليه
        wait_interval = 10 if first_join else DELAY_BETWEEN_JOINS
        first_join = False

        state['next_run_at'] = time.time() + wait_interval
        state['seconds_to_next'] = wait_interval

        # حلقة الانتظار مع تحديث العداد
        for rem in range(wait_interval, 0, -1):
            if stop_event.is_set():
                break
            while pause_event.is_set() and not stop_event.is_set():
                time.sleep(1)
            state['seconds_to_next'] = rem
            # بث نبضة دورية كل 15 ثانية للـ UI
            if rem % 15 == 0 or rem <= 5:
                if _SOCKETIO:
                    try:
                        _SOCKETIO.emit('auto_join_tick', {
                            'user_id': user_id,
                            'seconds_remaining': rem,
                            'pending_count': len(state['pending']),
                            'joined_count': state['joined_count']
                        }, to=user_id)
                    except Exception:
                        pass
            time.sleep(1)

        if stop_event.is_set():
            break

        # أخذ الرابط التالي من الطابور
        link = state['pending'].pop(0)
        idx += 1
        state['current_link'] = link
        state['current_idx'] = idx

        _emit_log(f"⏳ [انضمام دوري كل 5 دقائق] ({idx}/{total}) جارٍ الانضمام إلى: {link}...", user_id)

        # تنفيذ الانضمام
        join_result = {"success": False, "message": "خطأ غير متوقع"}
        try:
            if client_manager and client_manager.client:
                join_result = client_manager.run_coroutine(
                    _async_join_group(client_manager.client, link)
                )
        except Exception as join_ex:
            join_result = {"success": False, "message": str(join_ex)}

        # معالجة النتيجة
        is_succ = join_result.get('success', False)
        is_already = join_result.get('already', False)
        is_flood = join_result.get('flood', False)

        hist_entry = {
            'link': link,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': is_succ,
            'message': join_result.get('message', ''),
            'already': is_already
        }
        history_items.append(hist_entry)
        state['history'] = history_items[-50:]

        if is_succ:
            if is_already:
                state['isolated_already'].append(link)
                _emit_log(f"⏭ [تخطي - منضم مسبقاً] {link} — الحساب عضو بالفعل.", user_id)
            else:
                state['joined_count'] += 1
                joined_cache.add(link.lower().strip())
                _save_account_joined_cache(user_id, joined_cache, history_items)
                _emit_log(f"✅ [انضمام ناجح] تم الانضمام بنجاح إلى: {link}! (الانضمام التالي بعد 5 دقائق)", user_id)
        elif is_flood:
            wait_s = join_result.get('seconds', 60)
            state['failed_count'] += 1
            _emit_log(f"⏳ [تيليجرام FloodWait] يطلب الانتظار {wait_s} ثانية... جارٍ التهدئة ثم الاستئناف.", user_id)
            time.sleep(min(wait_s, 180))
            # إعادة الرابط للطابور للمحاولة لاحقاً
            state['pending'].insert(0, link)
        else:
            state['failed_count'] += 1
            _emit_log(f"❌ [تعذر الانضمام] {link}: {join_result.get('message')}", user_id)

        # تحديث الحالة المخزنة لمستخدم السوكيت
        if _USERS_MAP and _USERS_LOCK:
            with _USERS_LOCK:
                if user_id in _USERS_MAP:
                    _USERS_MAP[user_id]['auto_join_state'] = {
                        'running': True,
                        'total': total,
                        'done': idx,
                        'success': state['joined_count'],
                        'already': len(state['isolated_already']),
                        'fail': state['failed_count'],
                        'items': history_items[-30:],
                        'current_link': link,
                        'delay': DELAY_BETWEEN_JOINS,
                        'interval_minutes': 5
                    }

        if _SOCKETIO:
            try:
                _SOCKETIO.emit('auto_join_progress', {
                    'idx': idx,
                    'total': total,
                    'url': link,
                    'status': 'success' if is_succ else 'fail',
                    'reason': join_result.get('message', ''),
                    'joined_count': state['joined_count'],
                    'remaining': len(state['pending']),
                    'next_in_seconds': DELAY_BETWEEN_JOINS
                }, to=user_id)
            except Exception:
                pass

    if stop_event.is_set():
        state['status'] = 'stopped'
        _emit_log("⏹ تم إيقاف الانضمام التلقائي الدوري بناءً على طلب المستخدم أو تبديل الجلسة.", user_id)
    else:
        state['status'] = 'completed'


def start_account_login_auto_join(user_id, client_manager=None):
    """
    المحرك الرئيسي: يُستدعى تلقائياً عند تسجيل دخول أي حساب:
    1. عزل المجموعات المنضمة مسبقاً لهذا الحساب فوراً
    2. إطلاق خيط الانضمام التلقائي الدوري كل 5 دقائق
    """
    with _WORKERS_LOCK:
        # إذا كان هناك خيط يعمل بالفعل لهذا الحساب، أوقفه لبدء دورة نظيفة
        old_worker = _WORKERS.get(user_id)
        if old_worker and old_worker.get('thread') and old_worker['thread'].is_alive():
            logger.info(f"Stopping previous auto-join worker for {user_id} to refresh...")
            old_worker['stop_event'].set()
            time.sleep(0.5)

        # 1. عزل المجموعات المنضمة مسبقاً
        isolated_already, pending = isolate_account_joined_groups(user_id, client_manager)

        stop_event = threading.Event()
        pause_event = threading.Event()

        state = {
            'user_id': user_id,
            'status': 'running',
            'isolated_already': isolated_already,
            'pending': pending,
            'joined_count': 0,
            'failed_count': 0,
            'current_link': '',
            'current_idx': 0,
            'seconds_to_next': 300,
            'history': []
        }

        # 2. إطلاق خيط الانضمام كل 5 دقائق
        t = threading.Thread(
            target=_account_auto_join_loop,
            args=(user_id, client_manager, stop_event, pause_event, state),
            daemon=True,
            name=f"AutoJoin5Min_{user_id}"
        )
        t.start()

        _WORKERS[user_id] = {
            'thread': t,
            'stop_event': stop_event,
            'pause_event': pause_event,
            'state': state
        }

        # ربط الأحداث بـ USERS_MAP لضمان التوافق مع أزرار الإيقاف والتشغيل الموجودة
        if _USERS_MAP and _USERS_LOCK:
            with _USERS_LOCK:
                if user_id in _USERS_MAP:
                    _USERS_MAP[user_id]['auto_join_stop'] = stop_event
                    _USERS_MAP[user_id]['auto_join_pause'] = pause_event

        return state


def get_account_auto_join_status(user_id):
    """الحصول على تفاصيل حالة الانضمام التلقائي الدوري للحساب"""
    with _WORKERS_LOCK:
        worker = _WORKERS.get(user_id)
        if worker:
            st = worker['state']
            return {
                'ok': True,
                'status': st.get('status', 'running'),
                'isolated_count': len(st.get('isolated_already', [])),
                'pending_count': len(st.get('pending', [])),
                'joined_count': st.get('joined_count', 0),
                'failed_count': st.get('failed_count', 0),
                'seconds_to_next': st.get('seconds_to_next', 300),
                'current_link': st.get('current_link', ''),
                'history': st.get('history', [])[-20:]
            }
        return {
            'ok': False,
            'status': 'idle',
            'message': 'لم يتم تشغيل الانضمام التلقائي لهذا الحساب بعد'
        }


def pause_account_auto_join(user_id):
    with _WORKERS_LOCK:
        worker = _WORKERS.get(user_id)
        if worker and worker.get('pause_event'):
            worker['pause_event'].set()
            return True
    return False


def resume_account_auto_join(user_id):
    with _WORKERS_LOCK:
        worker = _WORKERS.get(user_id)
        if worker and worker.get('pause_event'):
            worker['pause_event'].clear()
            return True
    return False


def stop_account_auto_join(user_id):
    with _WORKERS_LOCK:
        worker = _WORKERS.get(user_id)
        if worker and worker.get('stop_event'):
            worker['stop_event'].set()
            return True
    return False
