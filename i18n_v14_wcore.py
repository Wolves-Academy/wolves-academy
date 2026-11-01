# -*- coding: utf-8 -*-
"""Wolves strings: navigation, coach check-in, cancel a session, login."""

EN = {
    "w_nav_coaches": "Coaches", "w_nav_reports": "Reports",
    "w_report_weekly": "Weekly report", "w_report_trials": "Trials report",
    "w_hi_name": "Hi {n}",
    "w_checkin_q": "On court today?", "w_checkin_sub": "Check in so your day is counted.",
    "w_checkin_btn": "I'm on court", "w_checked_in": "You're checked in",
    "w_checked_in_at": "Since {t}", "w_checked_in_toast": "Checked in. Have a good session.",
    "w_cancel_session": "Cancel this session",
    "w_cancel_explain": "Rain, a holiday or a closed court: nobody loses a session. Packages of the players "
                        "affected move forward one session, and attendance already marked is removed.",
    "w_cancel_only_group": "Cancel only {g}", "w_cancel_all_day": "Close all sessions this day",
    "w_all_groups_day": "All groups", "wp_excel_tools": "Excel import / export", "wp_all_genders": "Boys & girls",
    "w_cancel_reason": "Reason (optional)", "w_cancel_reason_ph": "e.g. Rain, Eid, court closed",
    "w_cancel_confirm": "Cancel session", "w_cancelled_toast": "Session cancelled. {n} marks removed.",
    "w_coach_codes_hint": "Coaches sign in with their own codes. Manage them in",
    "enter_pin": "Your PIN or coach code",
}

AR = {
    "w_nav_coaches": "المدربين", "w_nav_reports": "التقارير",
    "w_report_weekly": "تقرير الأسبوع", "w_report_trials": "تقرير الحصص التجريبية",
    "w_hi_name": "أهلا {n}",
    "w_checkin_q": "إنت بالملعب اليوم؟", "w_checkin_sub": "سجّل حضورك عشان ينحسب يومك.",
    "w_checkin_btn": "أنا بالملعب", "w_checked_in": "حضورك مسجّل",
    "w_checked_in_at": "من الساعة {t}", "w_checked_in_toast": "تسجّل حضورك. يعطيك العافية.",
    "w_cancel_session": "إلغاء هالحصة",
    "w_cancel_explain": "مطر أو عطلة أو الملعب مسكّر: ولا لاعب بخسر حصة. اشتراك اللاعبين اللي إلهم علاقة "
                        "بيتأجل حصة، والحضور المسجّل بنشال.",
    "w_cancel_only_group": "ألغِ حصة {g} بس", "w_cancel_all_day": "سكّر كل حصص هاليوم",
    "w_all_groups_day": "كل المجموعات", "wp_excel_tools": "استيراد وتصدير إكسل", "wp_all_genders": "شباب وبنات",
    "w_cancel_reason": "السبب (اختياري)", "w_cancel_reason_ph": "مثلاً: مطر، عيد، الملعب مسكّر",
    "w_cancel_confirm": "ألغِ الحصة", "w_cancelled_toast": "انلغت الحصة. انشال {n} تسجيل.",
    "w_coach_codes_hint": "كل مدرب بيدخل بكوده الخاص. بتديرهم من",
    "enter_pin": "الرقم السري أو كود المدرب",
}

EN["w_days_month"] = "Days this month"
AR["w_days_month"] = "أيام هالشهر"

EN.update({"w_install_title": "Install Wolves on your phone", "w_install_sub": "Opens like an app, full screen, from your home screen.",
           "w_install_btn": "Install", "w_install_ios": "Tap the Share button, then Add to Home Screen.",
           "w_install_later": "Later",
           "w_ios_step1": "Tap Share", "w_ios_step2": "Scroll down and tap “Add to Home Screen”", "w_ios_step3": "Tap “Add”",
           "w_ios_safari": "Don't see it? You may be inside WhatsApp: open this link in Safari first.",
           "w_and_step1": "Tap the ⋮ menu at the top of Chrome", "w_and_step2": "Tap “Install app” or “Add to Home screen”"})
AR.update({"w_install_title": "نزّل تطبيق Wolves على تلفونك", "w_install_sub": "بيفتح زي التطبيق، شاشة كاملة، من الشاشة الرئيسية.",
           "w_install_btn": "تنزيل", "w_install_ios": "اكبس زر المشاركة، بعدين إضافة إلى الشاشة الرئيسية.",
           "w_install_later": "بعدين",
           "w_ios_step1": "اكبس زر المشاركة", "w_ios_step2": "انزل لتحت واكبس «إضافة إلى الشاشة الرئيسية»", "w_ios_step3": "اكبس «إضافة»",
           "w_ios_safari": "مش طالع معك؟ يمكن فاتح الرابط من الواتساب: افتحه بسفاري أول.",
           "w_and_step1": "اكبس قائمة ⋮ فوق بكروم", "w_and_step2": "اكبس «تثبيت التطبيق» أو «إضافة إلى الشاشة الرئيسية»"})

# schedules, adding existing players, dated freezes, coach days
EN.update({
    "w_grp_days": "Training days and times",
    "w_grp_days_hint": "Tick each day the group trains and its time. Nothing ticked = the academy's training days.",
    "w_grp_academy_days": "Academy days",
    "w_add_existing_hint": "Pick a player: they join this group on all its days.",
    "search_player": "Search a player", "w_on_sheet": "In this group",
    "w_add_new_instead": "Not in the list? Add a new player",
    "w_player_schedule": "Schedule",
    "w_player_schedule_hint": "Their group's days are ticked. Untick a day they skip, or tick another group's day they also come to.",
    "w_also_other_group": "Also trains with another group",
    "w_freeze_planned": "Planned", "w_freeze_del_q": "Delete this freeze period?", "delete": "Delete",
    "w_freeze_from": "From", "w_freeze_until": "Until (last day)",
    "w_freeze_until_hint": "Leave Until empty to freeze until you unfreeze. With dates it starts and ends by itself.",
    "w_freeze_need_until": "A freeze that starts later needs an end date.",
    "w_add_day": "Add a day (forgot to check in)", "w_via_marks": "took attendance",
    "w_remove_day_q": "Remove this day from the coach?",
})
AR.update({
    "w_grp_days": "أيام ومواعيد التمرين",
    "w_grp_days_hint": "علّم كل يوم بتتمرن فيه المجموعة ووقته. إذا ما علّمت ولا يوم = أيام تمرين الأكاديمية.",
    "w_grp_academy_days": "أيام الأكاديمية",
    "w_add_existing_hint": "اختار لاعب: بينضم لهالمجموعة بكل أيامها.",
    "search_player": "دوّر على لاعب", "w_on_sheet": "بهالمجموعة",
    "w_add_new_instead": "مش موجود بالقائمة؟ ضيف لاعب جديد",
    "w_player_schedule": "البرنامج", "w_also_other_group": "بيتمرن كمان مع مجموعة ثانية",
    "w_player_schedule_hint": "أيام مجموعته معلّمة. شيل يوم ما بيجي فيه، أو علّم يوم من مجموعة ثانية بيجي معها كمان.",
    "w_freeze_planned": "مخطط", "w_freeze_del_q": "بدك تحذف فترة التجميد؟", "delete": "حذف",
    "w_freeze_from": "من", "w_freeze_until": "لغاية (آخر يوم)",
    "w_freeze_until_hint": "اترك «لغاية» فاضي عشان يضل مجمّد لحد ما تفكّه. مع التواريخ بيبلش وبيخلص لحاله.",
    "w_freeze_need_until": "التجميد اللي ببلش بعدين لازم إله تاريخ نهاية.",
    "w_add_day": "ضيف يوم (نسي يسجّل)", "w_via_marks": "سجّل الحضور",
    "w_remove_day_q": "بدك تشيل هاليوم من المدرب؟",
})

# quick setup (hundreds of players) and package filters
EN.update({
    "w_quick_setup": "Quick setup", "all_word": "All", "select": "Select",
    "w_qs_sub": "Fix many players fast: group, gender, birth date and package. Change a row and tap Save, or tick players and set them all at once.",
    "w_need_group": "No group", "w_need_birth": "No birth date",
    "w_f_withpkg": "Active (has a package)", "w_f_noprice": "Price not set", "w_f_nopkg": "No package",
    "w_price_not_set": "Price not set", "w_paid": "Paid",
    "w_select_all_shown": "Select all shown", "w_showing_of": "{n} of {t}",
    "w_qs_left": "{n} left · ends {d}", "w_renew_12": "Renew",
    "w_set_group": "Group…", "w_apply_group": "Set group", "w_apply_package": "Set package",
    "w_saved": "Saved", "w_n_selected": "{n} selected", "w_save_n": "Save {n} changes",
    "w_working": "Saving", "w_done_n": "Done: {n} players", "w_bulk_sure": "Apply this package to {n} players?",
    "w_show_more": "Show more ({n})",
})
AR.update({
    "w_quick_setup": "ترتيب سريع", "all_word": "الكل", "select": "اختيار",
    "w_qs_sub": "رتّب لاعبين كثير بسرعة: المجموعة، الجنس، تاريخ الميلاد والاشتراك. غيّر بالسطر واكبس حفظ، أو علّم كذا لاعب وغيّرهم مرة وحدة.",
    "w_need_group": "بدون مجموعة", "w_need_birth": "بدون تاريخ ميلاد",
    "w_f_withpkg": "فعّال (عنده اشتراك)", "w_f_noprice": "السعر مش محدد", "w_f_nopkg": "بدون اشتراك",
    "w_price_not_set": "السعر مش محدد", "w_paid": "مدفوع",
    "w_select_all_shown": "اختار كل اللي ظاهرين", "w_showing_of": "{n} من {t}",
    "w_qs_left": "ضل {n} · بيخلص {d}", "w_renew_12": "تجديد",
    "w_set_group": "المجموعة…", "w_apply_group": "حط بالمجموعة", "w_apply_package": "حط الاشتراك",
    "w_saved": "انحفظ", "w_n_selected": "{n} مختارين", "w_save_n": "احفظ {n} تغييرات",
    "w_working": "عم يحفظ", "w_done_n": "خلص: {n} لاعب", "w_bulk_sure": "بدك تحط هالاشتراك لـ {n} لاعب؟",
    "w_show_more": "اعرض أكثر ({n})",
})
