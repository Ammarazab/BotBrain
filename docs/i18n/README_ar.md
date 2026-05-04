<div dir="rtl">

<!-- LOGO -->
<p align="center">
  <a href="https://botbot.bot" target="_blank">
    <img src="../images/Botbrainlogo.png" alt="BotBot" width="250">
  </a>
</p>

<p align="center">
  دماغ واحد، أي روبوت.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/ROS2-Humble-blue?logo=ros" alt="ROS 2 Humble">
  <img src="https://img.shields.io/badge/Next.js-15-black?logo=next.js" alt="Next.js 15">
  <img src="https://img.shields.io/badge/License-MIT-purple" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Jetson-76B900?logo=nvidia" alt="Jetson">
</p>

<p align="center">
  <a href="https://botbot.bot"><img src="https://img.shields.io/badge/-Website-000?logo=vercel&logoColor=white" alt="Website"></a>
  <a href="https://discord.gg/CrTbJzxXes"><img src="https://img.shields.io/badge/-Discord-5865F2?logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://www.linkedin.com/company/botbotrobotics"><img src="https://img.shields.io/badge/-LinkedIn-0A66C2?logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://www.youtube.com/@botbotrobotics"><img src="https://img.shields.io/badge/-YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
</p>

<p align="center">
  <a href="../../README.md"><img src="https://img.shields.io/badge/🇺🇸_English-blue" alt="English"></a>
  <a href="README_pt.md"><img src="https://img.shields.io/badge/🇧🇷_Português-blue" alt="Português"></a>
  <a href="README_fr.md"><img src="https://img.shields.io/badge/🇫🇷_Français-blue" alt="Français"></a>
  <a href="README_zh-CN.md"><img src="https://img.shields.io/badge/🇨🇳_中文-blue" alt="中文"></a>
  <a href="README_es.md"><img src="https://img.shields.io/badge/🇪🇸_Español-blue" alt="Español"></a>
  <a href="README_ar.md"><img src="https://img.shields.io/badge/🇸🇦_العربية-blue" alt="العربية"></a>
</p>

# BotBrain مفتوح المصدر (BBOSS) <img src="../images/bot_eyes.png" alt="🤖" width="50" style="vertical-align: middle;">

BotBrain هو مجموعة مكوّنات معيارية مفتوحة المصدر للبرمجيات والعتاد، تتيح لك القيادة والمشاهدة ورسم الخرائط والملاحة (يدوياً أو ذاتياً) والمراقبة وإدارة الروبوتات ذات الأرجل (الرباعية، والثنائية، والشبيهة بالإنسان) أو ذات العجلات المتوافقة مع ROS2 من خلال واجهة ويب بسيطة وقوية. يوفر العتاد حوامل قابلة للطباعة ثلاثية الأبعاد وصندوقاً خارجياً لتركيب BotBrain على روبوتك دون عناء.

- مصمم حول كاميرا Intel RealSense D435i وعائلة لوحات NVIDIA Jetson
- اللوحات المدعومة رسمياً: Jetson Nano و Jetson Orin Nano (دعم AGX و Thor قادم قريباً)
- كل شيء معياري - لست مضطراً لتشغيل كل الوحدات (بعض وحدات الذكاء الاصطناعي الثقيلة تتطلب Orin AGX)

<p align="center">
  <a href="https://youtu.be/L7nLiKkLVP4">📹 شاهد الفيديو التعريفي لـ BotBrain 📹</a>
</p>

<p align="center">
  <a href="https://youtu.be/VBv4Y7lat8Y">📹 شاهد BotBrain يكمل ساعة من الدوريات الذاتية في مكتبنا</a>
</p>


<h2 align="center">✨ نظرة عامة على الميزات</h2>

<table>
  <tr>
    <td align="center" width="50%">
      <img src="../images/gifs/Dash:Fleet.gif" alt="لوحة المعلومات والتحكم بالأسطول" width="400"><br>
      <h3>لوحة المعلومات والتحكم بالأسطول</h3>
      <p>لوحة معلومات شاملة لعرض الحالة ومعلومات الروبوت والانتقال السريع إلى الأقسام الأخرى</p>
    </td>
    <td align="center" width="50%">
      <img src="../images/gifs/Cockpitscreenstudio.gif" alt="قمرة القيادة" width="400"><br>
      <h3>قمرة القيادة (CockPit)</h3>
      <p>صفحة تحكم معدّة مسبقاً تشمل الكاميرا الأمامية والخلفية والنموذج ثلاثي الأبعاد والخريطة والملاحة، إضافة إلى أزرار التحكم السريع</p>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="../images/gifs/MyUI.gif" alt="واجهتي" width="400"><br>
      <h3>واجهتي (My UI)</h3>
      <p>واجهة تحكم قابلة للتخصيص بكل ميزات قمرة القيادة</p>
    </td>
    <td align="center" width="50%">
      <img src="../images/gifs/Missions.gif" alt="المهام" width="400"><br>
      <h3>المهام</h3>
      <p>أنشئ مهامًا لينفذها الروبوت ويتنقل ذاتياً</p>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="../images/gifs/Health.gif" alt="الحالة" width="400"><br>
      <h3>الحالة</h3>
      <p>اعرض الحالة الكاملة لـ BotBrain: استخدام المعالج/الرسومات/الذاكرة، والتحكم بآلة الحالات وحالة العقد، والتحكم باتصال الواي فاي</p>
    </td>
    <td align="center" width="50%">
      <img src="../images/gifs/Profile.gif" alt="الملف الشخصي" width="400"><br>
      <h3>الملف الشخصي</h3>
      <p>خصّص مظهر BotBrain، عيّن ألواناً مخصصة وملفات سرعة</p>
    </td>
  </tr>
</table>

<p align="center">
  <img src="../images/assembly.gif" alt="تجميع BotBrain" width="600"><br>
  <h3 align="center">عتاد مفتوح المصدر</h3>
  <p>طباعة ثلاثية الأبعاد سريعة وسهل التركيب ومصمم ليُثبَّت على أي روبوت.
  شغّل روبوتك مع BotBrain في أقل من 30 دقيقة.</p>
</p>

<p align="center">
  <a href="https://youtu.be/xZ5c619bTEQ">📹 شاهد دليل تجميع عتاد BotBrain</a>
</p>


## قائمة الميزات الكاملة

### دعم منصات روبوت متعددة
- **Unitree Go2 و Go2-W** - روبوتات رباعية الأرجل بواجهة عتاد وتحكم كاملة
- **Unitree G1** - روبوت شبيه بالإنسان بتحكم في وضعية الجزء العلوي وانتقالات FSM
- **DirectDrive Tita** - روبوت ثنائي الأرجل بتحكم كامل
- **روبوتات مخصصة** - إطار قابل للتوسعة لإضافة أي منصة متوافقة مع ROS2
- **ذات أرجل وعجلات** - البنية تدعم كلا نوعي التنقل

### العتاد والمستشعرات
- **صندوق قابل للطباعة ثلاثية الأبعاد** - تصميم بتركيب سريع مع محولات تثبيت خاصة بكل روبوت (Go2 و G1 و Direct drive Tita)
- **Intel RealSense D435i** - دعم كاميرا مزدوجة للعرض و SLAM/الملاحة
- **IMU وقياس الحركة** - تقدير الموقع في الوقت الفعلي من جميع المنصات المدعومة
- **مراقبة البطارية** - حالة بطارية لكل روبوت مع تقدير وقت التشغيل

### الذكاء الاصطناعي والإدراك (قريباً)
- **اكتشاف الكائنات YOLOv8/v11** - أكثر من 80 فئة، محسّن لـ TensorRT، تتبع في الوقت الفعلي على BotBrain (قريباً)
- **التحكم باللغة الطبيعية ROSA** - أوامر روبوت محادثية عبر LLM
- **سجل الاكتشاف** - سجل قابل للبحث مع الصورة والمعلومات/الوصف (قريباً)

### الملاحة الذاتية
- **RTABMap SLAM** - رسم خرائط بصري بكاميرا واحدة أو كاميرتي RealSense D435i
- **تكامل Nav2** - تخطيط المسارات وتجنب العوائق الديناميكي وسلوكيات التعافي
- **تخطيط المهام** - أنشئ ونفّذ دوريات ذاتية متعددة نقاط الطريق
- **ملاحة بالنقر** - حدد الأهداف مباشرة على واجهة الخريطة
- **إدارة الخرائط** - الحفظ والتحميل والتبديل وتعيين مواقع الأساس

### تنسيق النظام
- **إدارة دورة الحياة** - تشغيل/إيقاف منسّق للعقد مع ترتيب التبعيات
- **آلة الحالات** - حالات النظام مع تشغيل/إيقاف تلقائي
- **التحكم بالسرعة بناءً على الأولوية** - تحكيم أوامر بـ 6 مستويات (عصا التحكم > الملاحة > الذكاء الاصطناعي)
- **مفتاح الإيقاف عند الفقد** - قفل أمان عتادي/برمجي لجميع أوامر الحركة
- **إيقاف الطوارئ** - تسلسل إيقاف طوارئ شامل

### واجهات التحكم
- **قمرة القيادة (CockPit)** - صفحة تحكم معدّة مسبقاً مع كاميرات ونموذج ثلاثي الأبعاد وخريطة وإجراءات سريعة
- **واجهتي (My UI)** - لوحة معلومات قابلة للتخصيص بالسحب والإفلات وعناصر قابلة لتغيير الحجم
- **عصي تحكم افتراضية** - تحكم بعصا مزدوجة باللمس/الفأرة مع ضبط السرعة
- **دعم وحدات التحكم** - PS5 و Xbox أو عصا تحكم عامة مع ربط أزرار مخصص وتبديل الأوضاع
- **تحكم لوحة المفاتيح** - عناصر تحكم WASD
- **ملفات السرعة** - إعدادات سرعة متعددة لأوضاع تشغيل مختلفة (مبتدئ، عادي، جنوني)
- **إجراءات الروبوت** - الوقوف/الجلوس، القفل/الفتح، اختيار المشية، الأضواء، انتقالات الأوضاع

### الكاميرا والفيديو
- **بث متعدد الكاميرات** - اكتشاف ديناميكي للكاميرا الأمامية والخلفية والمواضيع المخصصة
- **برامج ترميز H.264/H.265** - تحجيم الدقة، التحكم بمعدل الإطارات، تحسين عرض النطاق الترددي
- **تسجيل داخل المتصفح** - سجّل الفيديو من الكاميرات واحفظه في مجلد التنزيلات
- **عرض ثلاثي الأبعاد** - نموذج روبوت يستند إلى URDF مع تراكب مسح الليزر ومسار الملاحة

### مراقبة النظام
- **إحصائيات Jetson** - طراز اللوحة، إصدار JetPack، وضع الطاقة، وقت التشغيل
- **مراقبة المعالج/معالج الرسومات** - استخدام كل نواة، التردد، الذاكرة، التحكم الحراري
- **تتبع الطاقة** - الفولتية والتيار والقدرة لكل قضيب مع رصد الذروات
- **الحرارة والمراوح** - حرارة المعالج/الرسومات/SOC مع التحكم بسرعة المروحة
- **التخزين والذاكرة** - تنبيهات استخدام القرص، مراقبة RAM/Swap

### الشبكات والأسطول
- **لوحة تحكم WiFi** - مسح الشبكات، التبديل، ومراقبة الإشارة
- **أوضاع الاتصال** - WiFi، Ethernet، 4G، نقطة اتصال مع تتبع زمن الاستجابة
- **أسطول متعدد الروبوتات** - اتصالات متزامنة، أوامر على مستوى الأسطول، لوحة معلومات الحالة
- **التشخيصات** - صحة العقد، سجلات الأخطاء/التحذيرات، تصور آلة الحالات

### التخصيص وتجربة المستخدم
- **سمات فاتحة/داكنة** - ألوان تمييز مخصصة، تفضيلات دائمة
- **تخطيطات متجاوبة** - الجوال والجهاز اللوحي وسطح المكتب مع دعم اللمس
- **ملفات المستخدمين** - الصورة الرمزية، اسم العرض، لون السمة عبر Supabase Auth
- **متعدد اللغات** - الإنجليزية والبرتغالية والعربية مع التنسيقات الإقليمية
- **تسجيل التدقيق** - سجل أحداث قابل للبحث عبر أكثر من 10 فئات مع تصدير CSV
- **تحليلات النشاط** - خرائط حرارية للاستخدام وتتبع استخدام الروبوت

## جدول المحتويات

- [نظرة عامة](#نظرة-عامة)
- [هيكل المشروع](#هيكل-المشروع)
- [المتطلبات](#المتطلبات)
- [التثبيت](#التثبيت)
  - [إعداد العتاد](#1-إعداد-العتاد)
  - [إعداد Supabase](#2-إعداد-supabase)
  - [إعداد البرمجيات](#3-إعداد-البرمجيات)
- [تطوير الواجهة الأمامية](#تطوير-الواجهة-الأمامية)
- [الإعدادات](#الإعدادات)
- [الروبوتات المخصصة](#إضافة-دعم-لروبوتات-أخرى--روبوتات-مخصصة)
- [استكشاف الأخطاء وإصلاحها](#استكشاف-الأخطاء-وإصلاحها)
- [المساهمة](#المساهمة)
- [الترخيص](#الترخيص)

## نظرة عامة

يتكون BotBrain من ثلاثة مكوّنات رئيسية:

### العتاد
صندوق قابل للطباعة ثلاثية الأبعاد مع حوامل داخلية مصممة لاستيعاب لوحة NVIDIA Jetson وكاميرتين من Intel RealSense D435i. يتيح التصميم المعياري تركيب BotBrain على منصات روبوت مختلفة دون تصنيع مخصص.

### الواجهة الأمامية
لوحة معلومات ويب مبنية بـ Next.js 15 و React 19 و TypeScript. توفر تحكماً لحظياً بالروبوت وبث الكاميرا وتصور الخرائط وتخطيط المهام ومراقبة النظام وإدارة الأسطول، ويمكن الوصول إليها من أي متصفح على الشبكة.

### الروبوت (مساحة عمل ROS2)
مجموعة من حزم ROS2 Humble تتعامل مع:
- **التشغيل والتنسيق** (`bot_bringup`) - إطلاق النظام والتنسيق
- **التموضع** (`bot_localization`) - SLAM المعتمد على RTABMap لرسم الخرائط والتموضع
- **الملاحة** (`bot_navigation`) - تكامل Nav2 للحركة الذاتية
- **الإدراك** (`bot_yolo`) - اكتشاف الكائنات YOLOv8/v11
- **مشغّلات الروبوت** - حزم خاصة بمنصات Unitree Go2/G1 و DirectDrive Tita والروبوتات المخصصة

<p align="center">
  <a href="https://discord.gg/9Jkq5tBk6f">انضم إلى خادم Discord الخاص بنا للنقاش حول BotBrain والروبوتات</a>
</p>

---

## هيكل المشروع

<div dir="ltr">

```
BotBrain/
├── frontend/          # Next.js 15 web dashboard (React 19, TypeScript)
├── botbrain_ws/       # ROS 2 Humble workspace
│   └── src/
│       ├── bot_bringup/          # Main launch & system orchestration
│       ├── bot_custom_interfaces/# Custom ROS 2 messages, services, actions
│       ├── bot_description/      # URDF/XACRO models & robot_state_publisher
│       ├── bot_jetson_stats/     # Jetson hardware monitoring
│       ├── bot_localization/     # RTABMap SLAM
│       ├── bot_navigation/       # Nav2 autonomous navigation
│       ├── bot_rosa/             # ROSA AI natural language control
│       ├── bot_state_machine/    # Lifecycle & state management
│       ├── bot_yolo/             # YOLOv8/v11 object detection
│       ├── g1_pkg/               # Unitree G1 support
│       ├── go2_pkg/              # Unitree Go2 support
│       ├── joystick-bot/         # Game controller interface
│       └── tita_pkg/             # DirectDrive Tita robot support
├── hardware/          # 3D printable enclosure (STL/STEP/3MF)
└── docs/              # Documentation
```

</div>

---

## المتطلبات

### العتاد

| المكون | المتطلب |
|--------|---------|
| **الحوسبة** | NVIDIA Jetson (Nano أو Orin Nano أو سلسلة AGX) |
| **الكاميرات** | كاميرتان Intel RealSense D435i |
| **الروبوت** | روبوت متوافق مع ROS2 Humble أو Unitree Go2 و Go2-W، Unitree G1، Direct Drive Tita، أو [روبوت مخصص](../../botbrain_ws/README.md#creating-a-custom-robot-package) |
| **الشبكة** | اتصال Ethernet أو WiFi |

### البرمجيات

| المكون | المتطلب |
|--------|---------|
| **نظام التشغيل** | يُوصى بـ JetPack 6.2 (Ubuntu 22.04) |
| **الحاويات** | Docker و Docker Compose |
| **Node.js** | الإصدار 20+ (لتطوير الواجهة الأمامية محلياً فقط) |

---

## التثبيت

يحتوي BotBrain على مكوّنين رئيسيين: **العتاد** (الصندوق المطبوع ثلاثياً والمكونات الداخلية) و**البرمجيات** (تطبيق ويب الواجهة الأمامية ومساحة عمل ROS2).

### 1. إعداد العتاد

اطبع الصندوق ثلاثياً وجمّع الإلكترونيات.

**القطع الرئيسية:** طابعة ثلاثية الأبعاد، خيط PLA، NVIDIA Jetson، كاميرتا RealSense D435i، محول جهد.

> **[دليل تجميع العتاد](../../hardware/README.md)** - تعليمات مفصلة لبناء BotBrain
>
> **[فيديو التجميع الكامل](https://youtu.be/xZ5c619bTEQ)** - شرح فيديو خطوة بخطوة لعملية تجميع BotBrain

### 2. إعداد Supabase

تتطلب لوحة المعلومات الويب Supabase للمصادقة وتخزين البيانات. ستحتاج إلى إنشاء مشروع Supabase مجاني خاص بك.

> **[دليل إعداد Supabase](../SUPABASE_SETUP.md)** - تعليمات كاملة مع مخطط قاعدة البيانات

**ملخص سريع:**
1. أنشئ مشروعاً على [supabase.com](https://supabase.com)
2. شغّل ترحيلات SQL من دليل الإعداد
3. انسخ مفاتيح API للخطوة التالية

### 3. إعداد البرمجيات

> **[دليل إعداد WiFi لـ G1](../g1-wifi-setup.md)** - إذا كنت تستخدم روبوت G1، يرجى الرجوع إلى هذا المستند أولاً.

#### التبعيات الخارجية

**نظام التشغيل:**
- **NVIDIA JetPack 6.2** (موصى به)
- توزيعات Linux أخرى قد تعمل لكنها ليست مدعومة رسمياً

**Docker و Docker Compose:**

مطلوبان للنشر داخل الحاويات:

1. تثبيت Docker:

<div dir="ltr">

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker packages:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

</div>

راجع [دليل التثبيت الرسمي لـ Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) لمزيد من التفاصيل.

2. تمكين Docker بدون sudo:

<div dir="ltr">

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

</div>

راجع [خطوات ما بعد التثبيت](https://docs.docker.com/engine/install/linux-postinstall/) لمزيد من التفاصيل.

#### خطوات التثبيت

**الخطوة 1: استنساخ المستودع**

<div dir="ltr">

```bash
git clone https://github.com/botbotrobotics/BotBrain.git
cd BotBrain
```

</div>

**الخطوة 2: تشغيل سكربت التثبيت**

سيقوم سكربت التثبيت الآلي بتكوين الروبوت وإعداد خدمة التشغيل التلقائي:

<div dir="ltr">

```bash
sudo ./install.sh
```

</div>

يمكن العثور على مزيد من التفاصيل حول المعلومات المطلوبة في المثبّت [هنا](../installation-guide.md).

**الخطوة 3: إعادة تشغيل النظام**

<div dir="ltr">

```bash
sudo reboot
```

</div>

بعد إعادة التشغيل، سيبدأ النظام تلقائياً تشغيل حاويات Docker لجميع عقد ROS2 وخادم الويب.

**الخطوة 4: الوصول إلى واجهة الويب**

| طريقة الوصول | الرابط |
|--------------|--------|
| من نفس الحاسوب | `http://localhost` |
| الوصول عبر الشبكة | `http://<JETSON_IP>` |

اعرف عنوان IP الخاص بـ Jetson:

<div dir="ltr">

```bash
hostname -I
```

</div>

> **ملاحظة:** تأكد من أن الجهازين على نفس الشبكة وأن المنفذ 80 غير محظور بواسطة جدار الحماية.

> **ملاحظة:** أيضاً إذا اخترت g1-internal، فسيكون منفذ الويب 3000. لذا سيكون رابط الويب: `http://<JETSON_IP>:3000`

---

## تطوير الواجهة الأمامية

لتطوير الواجهة الأمامية محلياً (دون حزمة الروبوت الكاملة):

### الإعداد

<div dir="ltr">

```bash
cd frontend

# Copy environment template
cp .env.example .env.local

# Edit with your Supabase credentials
nano .env.local
```

</div>

### متغيرات البيئة

| المتغير | مطلوب | الوصف |
|---------|-------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | نعم | رابط مشروع Supabase الخاص بك |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | نعم | مفتاح Supabase العام/المجهول |
| `NEXT_PUBLIC_ROS_IP` | لا | عنوان IP الافتراضي للروبوت (الافتراضي: 192.168.1.95) |
| `NEXT_PUBLIC_ROS_PORT` | لا | منفذ ROS bridge (الافتراضي: 9090) |

### التشغيل

<div dir="ltr">

```bash
# Install dependencies
npm install

# Development server (full features)
npm run dev

# Development server (open source edition)
npm run dev:oss

# Production build
npm run build
npm start
```

</div>

---

## الإعدادات

### إعداد الروبوت

عدّل `botbrain_ws/robot_config.yaml`:

<div dir="ltr">

```yaml
robot_configuration:
  robot_name: "my_robot"           # Namespace for all topics
  robot_model: "go2"               # go2, tita, g1, or custom
  network_interface: "eth0"        # Network interface for ROS2
  openai_api_key: ""               # For AI features (optional)
```

</div>

### إعداد الكاميرا

أرقام التسلسل والتحويلات الخاصة بالكاميرات تُعدّ لكل روبوت في:
- `botbrain_ws/src/go2_pkg/config/camera_config.yaml`
- `botbrain_ws/src/g1_pkg/config/camera_config.yaml`
- `botbrain_ws/src/tita_pkg/config/camera_config.yaml`

اعرف الأرقام التسلسلية لكاميراتك:

<div dir="ltr">

```bash
rs-enumerate-devices | grep "Serial Number"
```

</div>

---

## إضافة دعم لروبوتات أخرى / روبوتات مخصصة

لإضافة دعم لمنصة روبوت جديدة في BotBrain:

1. **حزمة الواجهة الخلفية / ROS2**: اتبع دليل [إنشاء حزمة روبوت مخصص](../../botbrain_ws/README.md#creating-a-custom-robot-package) الشامل
2. **الواجهة الأمامية**: أضف ملف روبوت في إعدادات واجهة الويب

---

## استكشاف الأخطاء وإصلاحها

### فشل اتصال WebSocket
- تحقق من تشغيل rosbridge: `ros2 node list | grep rosbridge`
- تأكد من أن جدار الحماية يسمح بالمنفذ 9090: `sudo ufw allow 9090`
- تأكد من صحة عنوان IP في إعدادات اتصال الروبوت داخل الواجهة

### الكاميرا غير مكتشَفة
- اعرض الكاميرات المتصلة: `rs-enumerate-devices`
- افحص توصيلات USB وتأكد من أن الكاميرات تتلقى الطاقة
- تحقق من تطابق الأرقام التسلسلية في `camera_config.yaml` مع كاميراتك
- افحص أذونات USB: `sudo usermod -a -G video $USER`

### مشاكل Docker
- تأكد من تشغيل Docker بدون sudo (راجع تعليمات التثبيت)
- افحص الوصول إلى GPU: `docker run --gpus all nvidia/cuda:11.0-base nvidia-smi`
- اعرض سجلات الحاوية: `docker compose logs -f bringup`

### الواجهة الأمامية لا تُحمّل
- تحقق من بيانات اعتماد Supabase في `.env.local`
- افحص وحدة تحكم المتصفح بحثاً عن الأخطاء
- تأكد من تثبيت Node.js v20+: `node --version`

### الروبوت لا يتحرك
- تحقق من تشغيل twist_mux: `ros2 topic echo /cmd_vel_out`
- تأكد من أن واجهة عتاد الروبوت نشطة: `ros2 lifecycle get /robot_write_node`
- تحقق من عدم تفعيل إيقاف الطوارئ في الواجهة

### تحتاج إلى مزيد من المساعدة؟
انضم إلى [مجتمع Discord الخاص بنا](https://discord.gg/CrTbJzxXes) للحصول على دعم لحظي ومناقشات مع مجتمع BotBrain.

---

## المساهمة

نرحب بالمساهمات! سواء كنت تصلح أخطاء أو تضيف ميزات أو تحسّن الوثائق أو تضيف دعماً لروبوتات جديدة، فمساعدتك موضع تقدير. إذا كنت تستطيع جعل BotBrain أفضل أو أسرع، فلا تتردد.

انضم إلى [خادم Discord الخاص بنا](https://discord.gg/CrTbJzxXes) لمناقشة الأفكار والحصول على المساعدة أو التنسيق مع المساهمين الآخرين.

### سير عمل التطوير

1. **انسخ المستودع (Fork)**

<div dir="ltr">

   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/botbotrobotics/BotBrain.git
   cd BotBrain
   ```

</div>

2. **أنشئ فرعاً للميزة**

<div dir="ltr">

   ```bash
   git checkout -b feature/your-amazing-feature
   ```

</div>

3. **نفّذ التغييرات**
   - أضف اختبارات للوظائف الجديدة
   - حدّث ملفات README ذات الصلة
   - تأكد من بناء جميع الحزم بنجاح
   - اتبع معايير برمجة ROS 2

4. **اختبر بدقة**

5. **سجّل التغييرات (Commit)**

<div dir="ltr">

   ```bash
   git add .
   git commit -m "Add feature: brief description of changes"
   ```

</div>

6. **ادفع إلى نسختك (Push)**

<div dir="ltr">

   ```bash
   git push origin feature/your-amazing-feature
   ```

</div>

7. **افتح طلب سحب (Pull Request)**
   - قدّم وصفاً واضحاً للتغييرات
   - أشِر إلى أي قضايا مرتبطة
   - أضف لقطات شاشة أو فيديوهات لتغييرات الواجهة/السلوك

---

## BotBrain Pro

<p align="center">
  <img src="../images/botbrainpro.png" alt="BotBrain Pro" width="600">
</p>

النسخة الاحترافية / المؤسسية من BotBrain مع حماية IP67 وحمولات مخصصة مثل CamCam (كاميرا حرارية + بالأشعة تحت الحمراء)، و ZoomZuum (كاميرا RGB طويلة المدى بزووم 30x)، ونماذج ذكاء اصطناعي متقدمة، وتكامل مع IoT (LoRA)، واتصال بيانات 3-5G، والخدمة والصيانة، والتكاملات المتقدمة مع الحمولات المخصصة، وأكثر من ذلك بكثير. [اعرف المزيد هنا](https://botbot.bot) أو [احجز قيادتك التجريبية الآن](https://www.botbot.bot/testdrive).

---

## السلامة

يمكن للروبوتات أن تؤذي الناس وتؤذي نفسها عند تشغيلها بشكل غير صحيح أو أثناء التطوير. يرجى مراعاة ممارسات السلامة التالية:

- **استخدم زر إيقاف طوارئ فعلياً** - لا تعتمد على إيقاف برمجي وحده أبداً
- **أعد توليد مفاتيح API** إذا تسرّبت
- **اختبر التغييرات في المحاكاة** قبل تشغيلها على عتاد فعلي
- **ابتعد عن الروبوت** أثناء الاختبار الأولي

> **إخلاء مسؤولية:** BotBot غير مسؤولة عن أي أعطال أو حوادث أو أضرار ناتجة عن استخدام هذا البرنامج أو العتاد. يتحمّل المستخدم كامل المسؤولية عن التشغيل الآمن والاختبار والنشر للروبوتات التي تستخدم BotBrain.

---

## مكتبات الطرف الثالث

راجع [docs/DEPENDENCIES.md](../DEPENDENCIES.md) للحصول على قائمة كاملة بحزم الواجهة الأمامية و ROS المستخدمة.

---

## الترخيص

هذا المشروع مرخّص بموجب **رخصة MIT** - راجع ملف [LICENSE](../LICENSE) للتفاصيل.

---

<p align="center">صُنع بـ 💜 في البرازيل</p>

<p align="left">
  <img src="../images/icon.png" width="110">
</p>

</div>
