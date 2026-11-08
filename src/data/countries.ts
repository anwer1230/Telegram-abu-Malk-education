export interface Country {
  name: string;
  nameAr: string;
  code: string;
  flag: string;
  format: string;
  iso: string;
}

export const COUNTRIES: Country[] = [
  // Arab World (Priority First for Arabic Locale)
  { name: 'Yemen', nameAr: 'اليمن', code: '+967', flag: '🇾🇪', format: '7XX XXX XXX', iso: 'YE' },
  { name: 'Saudi Arabia', nameAr: 'المملكة العربية السعودية', code: '+966', flag: '🇸🇦', format: '5X XXX XXXX', iso: 'SA' },
  { name: 'Egypt', nameAr: 'مصر', code: '+20', flag: '🇪🇬', format: '1X XXXX XXXX', iso: 'EG' },
  { name: 'United Arab Emirates', nameAr: 'الإمارات العربية المتحدة', code: '+971', flag: '🇦🇪', format: '5X XXX XXXX', iso: 'AE' },
  { name: 'Kuwait', nameAr: 'الكويت', code: '+965', flag: '🇰🇼', format: '9XX XXXXX', iso: 'KW' },
  { name: 'Qatar', nameAr: 'قطر', code: '+974', flag: '🇶🇦', format: 'XXXX XXXX', iso: 'QA' },
  { name: 'Oman', nameAr: 'عُمان', code: '+968', flag: '🇴🇲', format: '9XXX XXXX', iso: 'OM' },
  { name: 'Bahrain', nameAr: 'البحرين', code: '+973', flag: '🇧🇭', format: 'XXXX XXXX', iso: 'BH' },
  { name: 'Jordan', nameAr: 'الأردن', code: '+962', flag: '🇯🇴', format: '7X XXX XXXX', iso: 'JO' },
  { name: 'Iraq', nameAr: 'العراق', code: '+964', flag: '🇮🇶', format: '7XX XXX XXXX', iso: 'IQ' },
  { name: 'Syria', nameAr: 'سوريا', code: '+963', flag: '🇸🇾', format: '9XX XXX XXX', iso: 'SY' },
  { name: 'Lebanon', nameAr: 'لبنان', code: '+961', flag: '🇱🇧', format: 'XX XXX XXX', iso: 'LB' },
  { name: 'Palestine', nameAr: 'فلسطين', code: '+970', flag: '🇵🇸', format: '5XX XXX XXX', iso: 'PS' },
  { name: 'Morocco', nameAr: 'المغرب', code: '+212', flag: '🇲🇦', format: '6XX XX XX XX', iso: 'MA' },
  { name: 'Algeria', nameAr: 'الجزائر', code: '+213', flag: '🇩🇿', format: '5XX XX XX XX', iso: 'DZ' },
  { name: 'Tunisia', nameAr: 'تونس', code: '+216', flag: '🇹🇳', format: 'XX XXX XXX', iso: 'TN' },
  { name: 'Libya', nameAr: 'ليبيا', code: '+218', flag: '🇱🇾', format: '9X XXX XXXX', iso: 'LY' },
  { name: 'Sudan', nameAr: 'السودان', code: '+249', flag: '🇸🇩', format: '9X XXX XXXX', iso: 'SD' },
  { name: 'Mauritania', nameAr: 'موريتانيا', code: '+222', flag: '🇲🇷', format: 'XX XX XX XX', iso: 'MR' },
  { name: 'Somalia', nameAr: 'الصومال', code: '+252', flag: '🇸🇴', format: '6X XXX XXX', iso: 'SO' },
  { name: 'Djibouti', nameAr: 'جيبوتي', code: '+253', flag: '🇩🇯', format: '77 XX XX XX', iso: 'DJ' },
  { name: 'Comoros', nameAr: 'جزر القمر', code: '+269', flag: '🇰🇲', format: '3XX XX XX', iso: 'KM' },

  // Global - Americas
  { name: 'United States', nameAr: 'الولايات المتحدة', code: '+1', flag: '🇺🇸', format: '(XXX) XXX-XXXX', iso: 'US' },
  { name: 'Canada', nameAr: 'كندا', code: '+1', flag: '🇨🇦', format: '(XXX) XXX-XXXX', iso: 'CA' },
  { name: 'Mexico', nameAr: 'المكسيك', code: '+52', flag: '🇲🇽', format: 'XXX XXX XXXX', iso: 'MX' },
  { name: 'Brazil', nameAr: 'البرازيل', code: '+55', flag: '🇧🇷', format: '(XX) 9XXXX-XXXX', iso: 'BR' },
  { name: 'Argentina', nameAr: 'الأرجنتين', code: '+54', flag: '🇦🇷', format: '9 11 XXXX-XXXX', iso: 'AR' },
  { name: 'Colombia', nameAr: 'كولومبيا', code: '+57', flag: '🇨🇴', format: '3XX XXX XXXX', iso: 'CO' },
  { name: 'Chile', nameAr: 'تشيلي', code: '+56', flag: '🇨🇱', format: '9 XXXX XXXX', iso: 'CL' },
  { name: 'Peru', nameAr: 'بيرو', code: '+51', flag: '🇵🇪', format: '9XX XXX XXX', iso: 'PE' },
  { name: 'Venezuela', nameAr: 'فنزويلا', code: '+58', flag: '🇻🇪', format: '4XX XXX XXXX', iso: 'VE' },
  { name: 'Ecuador', nameAr: 'الإكوادور', code: '+593', flag: '🇪🇨', format: '9X XXX XXXX', iso: 'EC' },
  { name: 'Bolivia', nameAr: 'بوليفيا', code: '+591', flag: '🇧🇴', format: '7XXX XXXX', iso: 'BO' },
  { name: 'Paraguay', nameAr: 'باراغواي', code: '+595', flag: '🇵🇾', format: '9XX XXX XXX', iso: 'PY' },
  { name: 'Uruguay', nameAr: 'أوروغواي', code: '+598', flag: '🇺🇾', format: '9X XXX XXX', iso: 'UY' },
  { name: 'Guyana', nameAr: 'غيانا', code: '+592', flag: '🇬🇾', format: '6XX XXXX', iso: 'GY' },
  { name: 'Suriname', nameAr: 'سورينام', code: '+597', flag: '🇸🇷', format: '7XX XXXX', iso: 'SR' },
  { name: 'Guatemala', nameAr: 'غواتيمالا', code: '+502', flag: '🇬🇹', format: 'XXXX XXXX', iso: 'GT' },
  { name: 'Honduras', nameAr: 'هندوراس', code: '+504', flag: '🇭🇳', format: 'XXXX XXXX', iso: 'HN' },
  { name: 'El Salvador', nameAr: 'السلفادور', code: '+503', flag: '🇸🇻', format: 'XXXX XXXX', iso: 'SV' },
  { name: 'Nicaragua', nameAr: 'نيكاراغوا', code: '+505', flag: '🇳🇮', format: 'XXXX XXXX', iso: 'NI' },
  { name: 'Costa Rica', nameAr: 'كوستاريكا', code: '+506', flag: '🇨🇷', format: 'XXXX XXXX', iso: 'CR' },
  { name: 'Panama', nameAr: 'بنما', code: '+507', flag: '🇵🇦', format: '6XXX XXXX', iso: 'PA' },
  { name: 'Cuba', nameAr: 'كوبا', code: '+53', flag: '🇨🇺', format: '5 XXX XXXX', iso: 'CU' },
  { name: 'Dominican Republic', nameAr: 'جمهورية الدومينيكان', code: '+1809', flag: '🇩🇴', format: 'XXX XXXX', iso: 'DO' },
  { name: 'Haiti', nameAr: 'هايتي', code: '+509', flag: '🇭🇹', format: 'XX XX XXXX', iso: 'HT' },
  { name: 'Jamaica', nameAr: 'جامايكا', code: '+1876', flag: '🇯🇲', format: 'XXX XXXX', iso: 'JM' },
  { name: 'Trinidad and Tobago', nameAr: 'ترينيداد وتوباغو', code: '+1868', flag: '🇹🇹', format: 'XXX XXXX', iso: 'TT' },
  { name: 'Bahamas', nameAr: 'جزر البهاما', code: '+1242', flag: '🇧🇸', format: 'XXX XXXX', iso: 'BS' },
  { name: 'Barbados', nameAr: 'باربادوس', code: '+1246', flag: '🇧🇧', format: 'XXX XXXX', iso: 'BB' },
  { name: 'Belize', nameAr: 'بليز', code: '+501', flag: '🇧🇿', format: '6XX XXXX', iso: 'BZ' },
  { name: 'Puerto Rico', nameAr: 'بورتوريكو', code: '+1787', flag: '🇵🇷', format: 'XXX XXXX', iso: 'PR' },

  // Global - Europe
  { name: 'United Kingdom', nameAr: 'المملكة المتحدة', code: '+44', flag: '🇬🇧', format: 'XXXX XXXXXX', iso: 'GB' },
  { name: 'Germany', nameAr: 'ألمانيا', code: '+49', flag: '🇩🇪', format: 'XXXX XXXXXXX', iso: 'DE' },
  { name: 'France', nameAr: 'فرنسا', code: '+33', flag: '🇫🇷', format: 'X XX XX XX XX', iso: 'FR' },
  { name: 'Italy', nameAr: 'إيطاليا', code: '+39', flag: '🇮🇹', format: '3XX XXXXXXX', iso: 'IT' },
  { name: 'Spain', nameAr: 'إسبانيا', code: '+34', flag: '🇪🇸', format: '6XX XX XX XX', iso: 'ES' },
  { name: 'Russia', nameAr: 'روسيا', code: '+7', flag: '🇷🇺', format: 'XXX XXX-XX-XX', iso: 'RU' },
  { name: 'Turkey', nameAr: 'تركيا', code: '+90', flag: '🇹🇷', format: '5XX XXX XXXX', iso: 'TR' },
  { name: 'Netherlands', nameAr: 'هولندا', code: '+31', flag: '🇳🇱', format: '6 XXXXXXXX', iso: 'NL' },
  { name: 'Belgium', nameAr: 'بلجيكا', code: '+32', flag: '🇧🇪', format: '4XX XX XX XX', iso: 'BE' },
  { name: 'Switzerland', nameAr: 'سويسرا', code: '+41', flag: '🇨🇭', format: '7X XXX XX XX', iso: 'CH' },
  { name: 'Sweden', nameAr: 'السويد', code: '+46', flag: '🇸🇪', format: '7X XXX XX XX', iso: 'SE' },
  { name: 'Norway', nameAr: 'النرويج', code: '+47', flag: '🇳🇴', format: '9XX XX XXX', iso: 'NO' },
  { name: 'Denmark', nameAr: 'الدانمارك', code: '+45', flag: '🇩🇰', format: 'XX XX XX XX', iso: 'DK' },
  { name: 'Finland', nameAr: 'فنلندا', code: '+358', flag: '🇫🇮', format: '4X XXXXXXX', iso: 'FI' },
  { name: 'Poland', nameAr: 'بولندا', code: '+48', flag: '🇵🇱', format: 'XXX XXX XXX', iso: 'PL' },
  { name: 'Portugal', nameAr: 'البرتغال', code: '+351', flag: '🇵🇹', format: '9XX XXX XXX', iso: 'PT' },
  { name: 'Greece', nameAr: 'اليونان', code: '+30', flag: '🇬🇷', format: '69X XXX XXXX', iso: 'GR' },
  { name: 'Austria', nameAr: 'النمسا', code: '+43', flag: '🇦🇹', format: '6XX XXXXXXX', iso: 'AT' },
  { name: 'Czech Republic', nameAr: 'جمهورية التشيك', code: '+420', flag: '🇨🇿', format: 'XXX XXX XXX', iso: 'CZ' },
  { name: 'Ireland', nameAr: 'أيرلندا', code: '+353', flag: '🇮🇪', format: '8X XXX XXXX', iso: 'IE' },
  { name: 'Romania', nameAr: 'رومانيا', code: '+40', flag: '🇷🇴', format: '7XX XXX XXX', iso: 'RO' },
  { name: 'Ukraine', nameAr: 'أوكرانيا', code: '+380', flag: '🇺🇦', format: 'XX XXX XXXX', iso: 'UA' },
  { name: 'Hungary', nameAr: 'المجر', code: '+36', flag: '🇭🇺', format: 'XX XXX XXXX', iso: 'HU' },
  { name: 'Bulgaria', nameAr: 'بلغاريا', code: '+359', flag: '🇧🇬', format: '8X XXX XXXX', iso: 'BG' },
  { name: 'Croatia', nameAr: 'كرواتيا', code: '+385', flag: '🇭🇷', format: '9X XXX XXXX', iso: 'HR' },
  { name: 'Serbia', nameAr: 'صربيا', code: '+381', flag: '🇷🇸', format: '6X XXX XXXX', iso: 'RS' },
  { name: 'Slovakia', nameAr: 'سلوفاكيا', code: '+421', flag: '🇸🇰', format: '9XX XXX XXX', iso: 'SK' },
  { name: 'Belarus', nameAr: 'بيلاروسيا', code: '+375', flag: '🇧🇾', format: 'XX XXX-XX-XX', iso: 'BY' },
  { name: 'Slovenia', nameAr: 'سلوفينيا', code: '+386', flag: '🇸🇮', format: 'XX XXX XXX', iso: 'SI' },
  { name: 'Lithuania', nameAr: 'ليتوانيا', code: '+370', flag: '🇱🇹', format: '6XX XXXXX', iso: 'LT' },
  { name: 'Latvia', nameAr: 'لاتفيا', code: '+371', flag: '🇱🇻', format: '2XX XXXXX', iso: 'LV' },
  { name: 'Estonia', nameAr: 'إستونيا', code: '+372', flag: '🇪🇪', format: '5X XXX XXX', iso: 'EE' },
  { name: 'Cyprus', nameAr: 'قبرص', code: '+357', flag: '🇨🇾', format: '9X XXXXXX', iso: 'CY' },
  { name: 'Luxembourg', nameAr: 'لوكسمبورغ', code: '+352', flag: '🇱🇺', format: '6XX XXX XXX', iso: 'LU' },
  { name: 'Malta', nameAr: 'مالطا', code: '+356', flag: '🇲🇹', format: '9XXX XXXX', iso: 'MT' },
  { name: 'Iceland', nameAr: 'آيسلندا', code: '+354', flag: '🇮🇸', format: 'XXX XXXX', iso: 'IS' },
  { name: 'Albania', nameAr: 'ألبانيا', code: '+355', flag: '🇦🇱', format: '6X XXX XXXX', iso: 'AL' },
  { name: 'North Macedonia', nameAr: 'مقدونيا الشمالية', code: '+389', flag: '🇲🇰', format: '7X XXX XXX', iso: 'MK' },
  { name: 'Bosnia and Herzegovina', nameAr: 'البوسنة والهرسك', code: '+387', flag: '🇧🇦', format: '6X XXX XXX', iso: 'BA' },
  { name: 'Montenegro', nameAr: 'الجبل الأسود', code: '+382', flag: '🇲🇪', format: '6X XXX XXX', iso: 'ME' },
  { name: 'Moldova', nameAr: 'مولدوفا', code: '+373', flag: '🇲🇩', format: '6XX XXXXX', iso: 'MD' },
  { name: 'Georgia', nameAr: 'جورجيا', code: '+995', flag: '🇬🇪', format: '5XX XX XX XX', iso: 'GE' },
  { name: 'Armenia', nameAr: 'أرمينيا', code: '+374', flag: '🇦🇲', format: 'XX XXXXXX', iso: 'AM' },
  { name: 'Azerbaijan', nameAr: 'أذربيجان', code: '+994', flag: '🇦🇿', format: '5X XXX XX XX', iso: 'AZ' },
  { name: 'Monaco', nameAr: 'موناكو', code: '+377', flag: '🇲🇨', format: '6 XX XX XX XX', iso: 'MC' },
  { name: 'Liechtenstein', nameAr: 'ليختنشتاين', code: '+423', flag: '🇱🇮', format: 'XXX XXXX', iso: 'LI' },
  { name: 'Andorra', nameAr: 'أندورا', code: '+376', flag: '🇦🇩', format: 'XXX XXX', iso: 'AD' },
  { name: 'San Marino', nameAr: 'سان مارينو', code: '+378', flag: '🇸🇲', format: '66XX XXXX', iso: 'SM' },
  { name: 'Vatican City', nameAr: 'الفاتيكان', code: '+379', flag: '🇻🇦', format: 'XXX XXXX', iso: 'VA' },
  { name: 'Kosovo', nameAr: 'كوسوفو', code: '+383', flag: '🇽🇰', format: '4X XXX XXX', iso: 'XK' },

  // Global - Asia & Pacific
  { name: 'China', nameAr: 'الصين', code: '+86', flag: '🇨🇳', format: '1XX XXXX XXXX', iso: 'CN' },
  { name: 'India', nameAr: 'الهند', code: '+91', flag: '🇮🇳', format: 'XXXXX XXXXX', iso: 'IN' },
  { name: 'Indonesia', nameAr: 'إندونيسيا', code: '+62', flag: '🇮🇩', format: '8XX-XXXX-XXXX', iso: 'ID' },
  { name: 'Pakistan', nameAr: 'باكستان', code: '+92', flag: '🇵🇰', format: '3XX XXXXXXX', iso: 'PK' },
  { name: 'Bangladesh', nameAr: 'بنغلاديش', code: '+880', flag: '🇧🇩', format: '1XXX-XXXXXX', iso: 'BD' },
  { name: 'Japan', nameAr: 'اليابان', code: '+81', flag: '🇯🇵', format: '90-XXXX-XXXX', iso: 'JP' },
  { name: 'Philippines', nameAr: 'الفلبين', code: '+63', flag: '🇵🇭', format: '9XX XXX XXXX', iso: 'PH' },
  { name: 'Vietnam', nameAr: 'فيتنام', code: '+84', flag: '🇻🇳', format: '9X XXX XXXX', iso: 'VN' },
  { name: 'Iran', nameAr: 'إيران', code: '+98', flag: '🇮🇷', format: '9XX XXX XXXX', iso: 'IR' },
  { name: 'Thailand', nameAr: 'تايلاند', code: '+66', flag: '🇹🇭', format: '8X XXX XXXX', iso: 'TH' },
  { name: 'Myanmar', nameAr: 'ميانمار', code: '+95', flag: '🇲🇲', format: '9 XXX XXX XXX', iso: 'MM' },
  { name: 'South Korea', nameAr: 'كوريا الجنوبية', code: '+82', flag: '🇰🇷', format: '10-XXXX-XXXX', iso: 'KR' },
  { name: 'Afghanistan', nameAr: 'أفغانستان', code: '+93', flag: '🇦🇫', format: '7X XXX XXXX', iso: 'AF' },
  { name: 'Uzbekistan', nameAr: 'أوزبكستان', code: '+998', flag: '🇺🇿', format: '9X XXX XX XX', iso: 'UZ' },
  { name: 'Malaysia', nameAr: 'ماليزيا', code: '+60', flag: '🇲🇾', format: '1X-XXX XXXX', iso: 'MY' },
  { name: 'Nepal', nameAr: 'نيبال', code: '+977', flag: '🇳🇵', format: '98X XXXXXXX', iso: 'NP' },
  { name: 'Sri Lanka', nameAr: 'سريلانكا', code: '+94', flag: '🇱🇰', format: '7X XXX XXXX', iso: 'LK' },
  { name: 'Kazakhstan', nameAr: 'كازاخستان', code: '+7', flag: '🇰🇿', format: '7XX XXX-XX-XX', iso: 'KZ' },
  { name: 'Cambodia', nameAr: 'كمبوديا', code: '+855', flag: '🇰🇭', format: '1X XXX XXX', iso: 'KH' },
  { name: 'Tajikistan', nameAr: 'طاجيكستان', code: '+992', flag: '🇹🇯', format: '9X XXX XXXX', iso: 'TJ' },
  { name: 'Israel', nameAr: 'إسرائيل', code: '+972', flag: '🇮🇱', format: '5X-XXX-XXXX', iso: 'IL' },
  { name: 'Laos', nameAr: 'لاوس', code: '+856', flag: '🇱🇦', format: '20 XX XXX XXX', iso: 'LA' },
  { name: 'Kyrgyzstan', nameAr: 'قيرغيزستان', code: '+996', flag: '🇰🇬', format: '7XX XXXXXX', iso: 'KG' },
  { name: 'Turkmenistan', nameAr: 'تركمانستان', code: '+993', flag: '🇹🇲', format: '6X XXXXXX', iso: 'TM' },
  { name: 'Singapore', nameAr: 'سنغافورة', code: '+65', flag: '🇸🇬', format: 'XXXX XXXX', iso: 'SG' },
  { name: 'Mongolia', nameAr: 'منغوليا', code: '+976', flag: '🇲🇳', format: 'XX XX XXXX', iso: 'MN' },
  { name: 'Hong Kong', nameAr: 'هونغ كونغ', code: '+852', flag: '🇭🇰', format: 'XXXX XXXX', iso: 'HK' },
  { name: 'Taiwan', nameAr: 'تايوان', code: '+886', flag: '🇹🇼', format: '9XX XXX XXX', iso: 'TW' },
  { name: 'Maldives', nameAr: 'جزر المالديف', code: '+960', flag: '🇲🇻', format: '7XX XXXX', iso: 'MV' },
  { name: 'Brunei', nameAr: 'بروناي', code: '+673', flag: '🇧🇳', format: '7XX XXXX', iso: 'BN' },
  { name: 'Bhutan', nameAr: 'بوتان', code: '+975', flag: '🇧🇹', format: '17 XX XX XX', iso: 'BT' },
  { name: 'East Timor', nameAr: 'تيمور الشرقية', code: '+670', flag: '🇹🇱', format: '77XX XXXX', iso: 'TL' },
  { name: 'Macau', nameAr: 'ماكاو', code: '+853', flag: '🇲🇴', format: '6XXX XXXX', iso: 'MO' },
  { name: 'North Korea', nameAr: 'كوريا الشمالية', code: '+850', flag: '🇰🇵', format: '191 XXX XXXX', iso: 'KP' },

  // Global - Oceania & Pacific
  { name: 'Australia', nameAr: 'أستراليا', code: '+61', flag: '🇦🇺', format: '4XX XXX XXX', iso: 'AU' },
  { name: 'New Zealand', nameAr: 'نيوزيلندا', code: '+64', flag: '🇳🇿', format: '2X XXX XXXX', iso: 'NZ' },
  { name: 'Papua New Guinea', nameAr: 'بابوا غينيا الجديدة', code: '+675', flag: '🇵🇬', format: '7XXX XXXX', iso: 'PG' },
  { name: 'Fiji', nameAr: 'فيجي', code: '+679', flag: '🇫🇯', format: '7XX XXXX', iso: 'FJ' },
  { name: 'Samoa', nameAr: 'ساموا', code: '+685', flag: '🇼🇸', format: '7X XXXXX', iso: 'WS' },
  { name: 'Tonga', nameAr: 'تونغا', code: '+676', flag: '🇹🇴', format: '7XX XXXX', iso: 'TO' },
  { name: 'Vanuatu', nameAr: 'فانواتو', code: '+678', flag: '🇻🇺', format: '7XX XXXX', iso: 'VU' },
  { name: 'Solomon Islands', nameAr: 'جزر سليمان', code: '+677', flag: '🇸🇧', format: '7XX XXXX', iso: 'SB' },
  { name: 'Micronesia', nameAr: 'ميكرونيزيا', code: '+691', flag: '🇫🇲', format: '9XX XXXX', iso: 'FM' },
  { name: 'Kiribati', nameAr: 'كيريباتي', code: '+686', flag: '🇰🇮', format: '7X XXXXX', iso: 'KI' },
  { name: 'Marshall Islands', nameAr: 'جزر مارشال', code: '+692', flag: '🇲🇭', format: '235 XXXX', iso: 'MH' },
  { name: 'Palau', nameAr: 'بالاو', code: '+680', flag: '🇵🇼', format: '77X XXXX', iso: 'PW' },
  { name: 'Nauru', nameAr: 'ناورو', code: '+674', flag: '🇳🇷', format: '555 XXXX', iso: 'NR' },
  { name: 'Tuvalu', nameAr: 'توفالو', code: '+688', flag: '🇹🇻', format: '90 XXXX', iso: 'TV' },

  // Global - Africa
  { name: 'Nigeria', nameAr: 'نيجيريا', code: '+234', flag: '🇳🇬', format: '80X XXX XXXX', iso: 'NG' },
  { name: 'Ethiopia', nameAr: 'إثيوبيا', code: '+251', flag: '🇪🇹', format: '9XX XXX XXX', iso: 'ET' },
  { name: 'South Africa', nameAr: 'جنوب أفريقيا', code: '+27', flag: '🇿🇦', format: '8X XXX XXXX', iso: 'ZA' },
  { name: 'Kenya', nameAr: 'كينيا', code: '+254', flag: '🇰🇪', format: '7XX XXX XXX', iso: 'KE' },
  { name: 'Uganda', nameAr: 'أوغندا', code: '+256', flag: '🇺🇬', format: '7XX XXX XXX', iso: 'UG' },
  { name: 'Tanzania', nameAr: 'تنزانيا', code: '+255', flag: '🇹🇿', format: '7XX XXX XXX', iso: 'TZ' },
  { name: 'Ghana', nameAr: 'غانا', code: '+233', flag: '🇬🇭', format: '2X XXX XXXX', iso: 'GH' },
  { name: 'Ivory Coast', nameAr: 'ساحل العاج', code: '+225', flag: '🇨🇮', format: '0X XX XX XX XX', iso: 'CI' },
  { name: 'Cameroon', nameAr: 'الكاميرون', code: '+237', flag: '🇨🇲', format: '6XX XX XX XX', iso: 'CM' },
  { name: 'Madagascar', nameAr: 'مدغشقر', code: '+261', flag: '🇲🇬', format: '3X XX XXX XX', iso: 'MG' },
  { name: 'Angola', nameAr: 'أنغولا', code: '+244', flag: '🇦🇴', format: '9XX XXX XXX', iso: 'AO' },
  { name: 'Mozambique', nameAr: 'موزمبيق', code: '+258', flag: '🇲🇿', format: '8X XXX XXXX', iso: 'MZ' },
  { name: 'Zambia', nameAr: 'زامبيا', code: '+260', flag: '🇿🇲', format: '9XX XXX XXX', iso: 'ZM' },
  { name: 'Zimbabwe', nameAr: 'زيمبابوي', code: '+263', flag: '🇿🇼', format: '7X XXX XXXX', iso: 'ZW' },
  { name: 'Senegal', nameAr: 'السنغال', code: '+221', flag: '🇸🇳', format: '7X XXX XX XX', iso: 'SN' },
  { name: 'Chad', nameAr: 'تشاد', code: '+235', flag: '🇹🇩', format: '6X XX XX XX', iso: 'TD' },
  { name: 'Guinea', nameAr: 'غينيا', code: '+224', flag: '🇬🇳', format: '6XX XX XX XX', iso: 'GN' },
  { name: 'Rwanda', nameAr: 'رواندا', code: '+250', flag: '🇷🇼', format: '7XX XXX XXX', iso: 'RW' },
  { name: 'Benin', nameAr: 'بنين', code: '+229', flag: '🇧🇯', format: '9X XX XX XX', iso: 'BJ' },
  { name: 'Burundi', nameAr: 'بوروندي', code: '+257', flag: '🇧🇮', format: '7X XX XX XX', iso: 'BI' },
  { name: 'South Sudan', nameAr: 'جنوب السودان', code: '+211', flag: '🇸🇸', format: '9X XXX XXXX', iso: 'SS' },
  { name: 'Togo', nameAr: 'توغو', code: '+228', flag: '🇹🇬', format: '9X XX XX XX', iso: 'TG' },
  { name: 'Sierra Leone', nameAr: 'سيراليون', code: '+232', flag: '🇸🇱', format: '7X XXXXXX', iso: 'SL' },
  { name: 'Congo', nameAr: 'الكونغو', code: '+242', flag: '🇨🇬', format: '06 XXX XXXX', iso: 'CG' },
  { name: 'DR Congo', nameAr: 'جمهورية الكونغو الديمقراطية', code: '+243', flag: '🇨🇩', format: '8X XXX XXXX', iso: 'CD' },
  { name: 'Central African Republic', nameAr: 'جمهورية أفريقيا الوسطى', code: '+236', flag: '🇨🇫', format: '7X XX XX XX', iso: 'CF' },
  { name: 'Liberia', nameAr: 'ليبيريا', code: '+231', flag: '🇱🇷', format: '77 XXX XXXX', iso: 'LR' },
  { name: 'Namibia', nameAr: 'ناميبيا', code: '+264', flag: '🇳🇦', format: '81 XXX XXXX', iso: 'NA' },
  { name: 'Botswana', nameAr: 'بوتسوانا', code: '+267', flag: '🇧🇼', format: '7X XXX XXX', iso: 'BW' },
  { name: 'Gabon', nameAr: 'الغابون', code: '+241', flag: '🇬🇦', format: '06 XX XX XX', iso: 'GA' },
  { name: 'Lesotho', nameAr: 'ليسوتو', code: '+266', flag: '🇱🇸', format: '5XXX XXXX', iso: 'LS' },
  { name: 'Guinea-Bissau', nameAr: 'غينيا بيساو', code: '+245', flag: '🇬🇼', format: '9XX XXX XXX', iso: 'GW' },
  { name: 'Equatorial Guinea', nameAr: 'غينيا الاستوائية', code: '+240', flag: '🇬🇶', format: '222 XXX XXX', iso: 'GQ' },
  { name: 'Mauritius', nameAr: 'موريشيوس', code: '+230', flag: '🇲🇺', format: '5XXX XXXX', iso: 'MU' },
  { name: 'Eswatini', nameAr: 'إسواتيني (سوازيلاند)', code: '+268', flag: '🇸🇿', format: '7XXX XXXX', iso: 'SZ' },
  { name: 'Cape Verde', nameAr: 'الرأس الأخضر', code: '+238', flag: '🇨🇻', format: '9XX XX XX', iso: 'CV' },
  { name: 'São Tomé and Príncipe', nameAr: 'ساو تومي وبرينسيبي', code: '+239', flag: '🇸🇹', format: '9XX XXXX', iso: 'ST' },
  { name: 'Seychelles', nameAr: 'سيشل', code: '+248', flag: '🇸🇨', format: '2XX XXXX', iso: 'SC' },
  { name: 'Eritrea', nameAr: 'إريتريا', code: '+291', flag: '🇪🇷', format: '7 XXX XXX', iso: 'ER' },
  { name: 'Mali', nameAr: 'مالي', code: '+223', flag: '🇲🇱', format: '7X XX XX XX', iso: 'ML' },
  { name: 'Burkina Faso', nameAr: 'بوركينا فاسو', code: '+226', flag: '🇧🇫', format: '7X XX XX XX', iso: 'BF' },
  { name: 'Niger', nameAr: 'النيجر', code: '+227', flag: '🇳🇪', format: '9X XX XX XX', iso: 'NE' },
  { name: 'Malawi', nameAr: 'مالاوي', code: '+265', flag: '🇲🇼', format: '99X XXX XXX', iso: 'MW' },
];

// Quick index maps
const CODE_MAP = new Map<string, Country>();
const ISO_MAP = new Map<string, Country>();

COUNTRIES.forEach((c) => {
  if (!CODE_MAP.has(c.code)) {
    CODE_MAP.set(c.code, c);
  }
  ISO_MAP.set(c.iso.toUpperCase(), c);
});

export function findCountryByCode(code: string): Country | undefined {
  const clean = code.trim().startsWith('+') ? code.trim() : `+${code.trim()}`;
  return CODE_MAP.get(clean);
}

export function findCountryByIso(iso: string): Country | undefined {
  return ISO_MAP.get(iso.toUpperCase());
}

export function searchCountries(query: string, isArabic = false): Country[] {
  const q = query.trim().toLowerCase();
  if (!q) {
    return isArabic
      ? [...COUNTRIES].sort((a, b) => a.nameAr.localeCompare(b.nameAr, 'ar'))
      : [...COUNTRIES].sort((a, b) => a.name.localeCompare(b.name, 'en'));
  }

  const cleanNum = q.replace(/[^\d+]/g, '');

  return COUNTRIES.filter((c) => {
    if (c.name.toLowerCase().includes(q)) return true;
    if (c.nameAr.includes(q)) return true;
    if (c.iso.toLowerCase() === q) return true;
    if (cleanNum && (c.code.includes(cleanNum) || c.code.replace('+', '').startsWith(cleanNum.replace('+', '')))) {
      return true;
    }
    return false;
  }).sort((a, b) => {
    // Exact code match ranks highest
    if (a.code === cleanNum) return -1;
    if (b.code === cleanNum) return 1;
    return 0;
  });
}

export function detectCountryFromPhone(phoneNumber: string): Country | undefined {
  const clean = phoneNumber.trim().replace(/[^\d+]/g, '');
  if (!clean) return undefined;
  const withPlus = clean.startsWith('+') ? clean : `+${clean}`;

  // Check prefix matches from longest code to shortest
  for (let len = 5; len >= 1; len--) {
    const sub = withPlus.substring(0, len + 1);
    const found = COUNTRIES.find((c) => c.code === sub);
    if (found) return found;
  }
  return undefined;
}
