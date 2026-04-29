        const API_BASE =
            window.location.protocol.startsWith("http")
                ? window.location.origin
                : "http://localhost:8102";
        const STORAGE_KEY = "eterna-active-loved-one";
        const AUTH_STORAGE_KEY = "eterna-auth-token";
        const demoProfile = {
            id: "demo-local-profile",
            name: "爸爸",
            relationship: "父亲",
            cover_title: "写给爸爸的一页家书",
            cover_photo_asset_id: null,
            cover_photo_url: "",
            personality_traits: {
                personality: "温柔、踏实、总会先问你今天累不累",
                catchphrase: "孩子，照顾好自己。"
            },
            speaking_style: "温柔踏实",
            memories: [
                "你总会先问我今天有没有按时吃饭。",
                "小时候放学下雨，你常常站在校门口等我。"
            ],
            voice_sample_paths: [],
            voice_sample_urls: [],
            photo_paths: [],
            photo_urls: [],
            video_paths: [],
            video_urls: [],
            model3d_paths: [],
            model3d_urls: []
        };

        let activeLovedOne = null;
        let serviceOnline = false;
        let chatBusy = false;
        let toastTimer = null;
        let selectedChatMode = "text";
        let lovedOneDirectory = [];
        let activeMemories = [];
        let activeChatHistory = [];
        let activeMediaAssets = [];
        let activeProactiveFeed = [];
        let activeProactiveSettings = null;
        let activeProactiveBridgeConfigured = false;
        let activeDigitalHumanModel = null;
        let activeDigitalHumanFragments = [];
        let activeDigitalHumanBuilds = [];
        let activeDigitalHumanHistory = [];
        let activeCallBridgeStatus = null;
        let guideRecorder = null;
        let guideChunks = [];
        let guideRecognition = null;
        let guideTranscriptCache = "";
        let guideRecording = false;
        let mediaFilter = "all";
        let authToken = "";
        let authMode = "register";
        let currentUser = null;
        let currentSubscription = null;
        let planCatalog = [];
        let pendingPlanCode = "";
        const LICENSED_HOME_MUSIC_URL = "";
        const LICENSED_HOME_MUSIC_CANDIDATES = [
            LICENSED_HOME_MUSIC_URL,
            "/assets/home-music.mp3",
            "/assets/home-music.wav",
            "/assets/mengdi.mp3",
            "/assets/mengdi.wav",
            "/assets/梦底.mp3",
            "/assets/梦底.wav",
        ].filter(Boolean);
        let memorialMusicPlaying = false;
        let memorialMusicContext = null;
        let memorialMusicMaster = null;
        let memorialMusicWindSource = null;
        let memorialMusicTimers = [];
        let memorialMusicElement = null;
        let resolvedMemorialMusicUrl = "";
        let memorialMusicLookupPromise = null;
        let currentLanguage = "zh";
        const UI_LANGUAGE_STORAGE_KEY = "eterna-ui-language";
        const MARKETING_COPY = {
            zh: {
                __title: "念念 Eterna | 念念不忘，ta一直在",
                brandTagline: "念念不忘，ta一直在",
                topNote: "把想念安放在一个会回应、会被珍藏的地方。",
                langHelper: "首页双语",
                heroEyebrow: "纪念亲人的数字陪伴空间",
                heroTitle: "让一句“我想你了”有地方落下",
                heroIntro: "把熟悉的称呼、叮嘱、笑声和你们共同经历过的日常，安放进一册会继续生长的纪念档案里。语音、照片、视频和回忆会一起慢慢拼回 ta 的样子，让每次想念都有一个温柔的入口。",
                heroPoemMark: "首页题字",
                heroPoemLine1: "梦里寻你千百度",
                heroPoemLine2: "那人却在念念处",
                heroPoemNote: "把那些走散在梦里、晚霞里和旧相册里的身影，重新安放回一个会回应、会被珍藏、会继续陪伴你的地方。",
                heroPrimaryCta: "为 ta 点亮纪念档案",
                heroSecondaryCta: "先听一段陪伴",
                seasonSpringTitle: "春",
                seasonSpringText: "微风把新绿和想念一起轻轻吹来。",
                seasonSummerTitle: "夏",
                seasonSummerText: "天空、海面和远处的人影，都慢慢亮起来。",
                seasonAutumnTitle: "秋",
                seasonAutumnText: "落叶安静落下，旧日的叮嘱也重新落回耳边。",
                seasonWinterTitle: "冬",
                seasonWinterText: "就算夜深了，灯还亮着，陪伴也还在。",
                sceneFragmentATitle: "人物与风景",
                sceneFragmentAText: "老人、父亲、母亲和孩子站在一起，身后是海、天和还没走远的晚霞。",
                sceneFragmentBTitle: "微风与落叶",
                sceneFragmentBText: "风从海面吹来，也把树叶和旧时的称呼，一起吹回心里。",
                sceneFragmentCTitle: "四季变迁",
                sceneFragmentCText: "春夏秋冬都会经过，但你熟悉的声音、样子和故事会被一直留着。",
                sceneFragmentDTitle: "纪念仍在生长",
                sceneFragmentDText: "当你再回来时，这里依然有海浪、飞鸟、灯光和继续回应你的陪伴。",
                sceneCaptionTitle: "梦里寻你千百度，那人却在念念处",
                sceneCaptionText: "人物、风景、微风、落叶和四季变迁，会把想念从心里慢慢铺展开来，让整个首页像一本会呼吸的纪念画册。",
                demoEyebrow: "剧情 Demo · 配乐版 v2",
                demoHeading: "24 秒，把想念拍成一段会呼吸的纪念短片",
                demoIntro: "这版把情绪、旁白和真实配乐的起伏放在一起：从安静的深夜，到一句话终于被重新接住，再到纪念如何慢慢变成长期陪伴。",
                demoMetaLine: "剧情线：失落夜晚 → 建档 → 对话 → 纪念延续",
                demoMetaDuration: "时长：24 秒",
                demoNoteEyebrow: "镜头结构",
                demoNoteHeading: "不是怀旧摆拍，而是一段有温度的产品叙事。",
                demoNoteText: "情绪被放在前面，但每一幕都对应一个真实功能入口。它先让人感到“想念”，再让人看见这份想念如何被安放、被保存、被继续回应。",
                demoBeat1Title: "第一幕：没人回应的夜晚",
                demoBeat1Text: "先让用户感到“失去回应”这件事，而不是直接推销 AI。",
                demoBeat2Title: "第二幕：念念出现",
                demoBeat2Text: "用提醒和建档流程，把产品定位成一个可以回来的入口。",
                demoBeat3Title: "第三幕：一句话被接住",
                demoBeat3Text: "通过“今天有点想你，也有点累”，把对话、口头禅和情绪回接演出来。",
                demoBeat4Title: "第四幕：纪念可以继续发生",
                demoBeat4Text: "展示生日祝福、声音相册和回忆影像，把单次对话提升成长期陪伴。",
                featuresEyebrow: "陪伴方式",
                featuresHeading: "把纪念做成可以慢慢回来的日常",
                featuresIntro: "念念不是一个短暂的新鲜功能，而是一个能长久使用的纪念空间。每个能力都围绕回忆、牵挂、问候和长期陪伴来设计。",
                feature1Title: "语音电话",
                feature1Text: "上传一段录音后，系统会提炼说话节奏和情绪风格，再把回复合成为更适合通话场景的语音陪伴。",
                feature2Title: "视频陪伴",
                feature2Text: "当照片和视频素材足够时，页面会进入更强在场感的影像陪伴模式，让“见面”这件事更接近真实。",
                feature3Title: "智能对话",
                feature3Text: "记住说话方式、共同经历和情绪语境，让回应更像“这个人会怎么说”，而不是模板式回答。",
                feature4Title: "生活关怀",
                feature4Text: "节日、天气、生日、普通的一天，都可以成为主动问候的触发点，让纪念回到生活本身。",
                feature5Title: "数字分身",
                feature5Text: "语音、照片、视频和共同回忆会一起进入档案，让这个数字人不止会说话，也会越来越像 ta 本人。",
                feature6Title: "家族传承",
                feature6Text: "让一段关系不只停留在当下，也能被下一代看见、听见，成为真正可传承的数字遗产。",
                workbenchEyebrow: "档案工作台",
                workbenchHeading: "把纪念做成真正可管理的日常",
                workbenchIntro: "这里不是展示页，而像一本会继续被翻阅的家庭纪念册。你可以切换亲人档案、补回忆、查看最近对话，逐步把这个数字分身养完整。",
                chatSectionEyebrow: "对话体验",
                chatSectionHeading: "从一句想念，慢慢回到熟悉的语气里",
                chatSectionIntro: "先创建一个亲人档案，再把语音、照片和视频补进去，让这里不只是一个会回复的窗口，而更像一个能被慢慢找回来的陪伴入口。",
                chatPrompt1: "今天有点想你",
                chatPrompt2: "最近工作有点累",
                chatPrompt3: "想和你说说今天的好消息",
                modeText: "文字陪伴",
                modeVoice: "语音电话",
                modeVideo: "视频陪伴",
                ritualEyebrow: "纪念流程",
                ritualHeading: "先替 ta 留下一盏灯，再慢慢把样子拼回来",
                ritualText: "名字、关系和口头禅决定人格轮廓；语音、照片、视频和回忆决定这个分身像不像 ta。你不需要一次性准备完整，只要让声音、面容和神态一点点回来。",
                timeline1Title: "1. 创建分身档案",
                timeline1Text: "先记下名字、关系和那些一开口就知道是 ta 的表达方式，让系统有一个真实的人物底稿。",
                timeline2Title: "2. 上传语音、照片、视频",
                timeline2Text: "语音会校准说话方式，照片会慢慢还原面容，如果还有视频，分身会更接近 ta 的神态和动作。",
                timeline3Title: "3. 继续留下回忆",
                timeline3Text: "从一段短短的故事开始，让回应不止会说话，而是真正知道你们一起经历过什么。",
                ritualPrimaryCta: "现在就创建档案",
                pricingEyebrow: "订阅方案",
                pricingHeading: "按你想保留的亲密程度来选择",
                pricingIntro: "从最基础的声音纪念，到完整的视频与家族传承，定价围绕“陪伴深度”而不是功能堆叠。",
                paymentsEyebrow: "出海支付准备",
                paymentsHeading: "把海外收款先准备成一套可切换的底盘",
                paymentsIntro: "在 Stripe 正式上线前，先把 PayPal、Creem、Stripe 三条路梳理清楚：谁适合低门槛试水，谁适合早期独立开发，谁适合长期 SaaS 运营。",
                paymentsBadge: "独立开发记录",
                paymentsMeta: "周末碎片时间，也先把海外收款路径走通。",
                paymentsJournalTitle: "不要把所有收款都压在单一渠道上",
                paymentsJournalText: "对于独立站和海外 SaaS，Stripe 最方便，但风控也最严格。更稳妥的做法是先准备低门槛渠道跑实验，再为长期订阅业务准备更稳的收款底盘。",
                paymentsPoint1Title: "APP 与独立站不是同一题",
                paymentsPoint1Text: "iOS 可以更多依赖 Apple Pay；独立站和 SaaS 则需要自己搭建 checkout、webhook、权限同步和风控预案。",
                paymentsPoint2Title: "先有备份渠道，再上主渠道",
                paymentsPoint2Text: "Stripe 体验最好，但封控也最严格。先把 PayPal 和 Creem 这样的补充渠道准备好，业务才不至于被单点卡死。",
                paymentsPoint3Title: "产品、税费和 webhook 要一起设计",
                paymentsPoint3Text: "价格展示、税费是否含税、支付完成回调、权限开通和用户重定向，必须在同一条链路里一起跑通。",
                paymentsPoint4Title: "念念当前的准备方向",
                paymentsPoint4Text: "主页先把全球收款策略说明清楚，下一步再接正式 checkout、webhook、套餐权限和多通道回退。",
                paypalStatus: "低门槛实验渠道",
                paypalTitle: "适合先跑通第一笔海外收入",
                paypalText: "个人 PayPal 配合 Ko-fi 一类的平台就能先开始，门槛低，适合验证需求，但不适合作为唯一支付通道。",
                paypalPoint1: "优点：个人账号 + 信用卡即可起步",
                paypalPoint2: "限制：主要依赖 PayPal 本身，信用卡路径不够完整",
                paypalPoint3: "适合：最早期验证、赞助与补充收款",
                creemStatus: "大陆开发者友好",
                creemTitle: "适合个人开发者先把 SaaS 支付跑起来",
                creemText: "不用先注册公司，对大陆开发者更友好，测试和联调也快，但要认真准备 KYC、产品说明和 webhook 链路。",
                creemPoint1: "优点：不强制公司主体，可接支付宝收款",
                creemPoint2: "注意：身份验证更建议用护照，不要只依赖身份证",
                creemPoint3: "适合：早期 SaaS、测试环境联调、补充渠道",
                stripeStatus: "长期主渠道",
                stripeTitle: "适合把订阅、权限和全球支付做成标准底层",
                stripeText: "Stripe 体验完整、生态成熟，最适合长期 SaaS 运营，但开户和风控要求也最高，必须把公司、银行和合规链路一次准备好。",
                stripePoint1: "优点：开发体验完整，订阅与 webhook 生态成熟",
                stripePoint2: "挑战：风控严格，主体、银行和资料要更扎实",
                stripePoint3: "适合：长期订阅、正式收费、全球标准化支付",
                paymentsRoadmap1Title: "1. 多渠道备份",
                paymentsRoadmap1Text: "先准备 PayPal / Creem / Stripe 的角色分工，避免被单一风控卡住。",
                paymentsRoadmap2Title: "2. 测试链路跑通",
                paymentsRoadmap2Text: "先在测试环境把 checkout、webhook、权限发放和返回页都验证完整。",
                paymentsRoadmap3Title: "3. 定价与税费一致",
                paymentsRoadmap3Text: "价格展示、税费含不含税、套餐权限、订阅状态要在前后端保持一致。",
                paymentsRoadmap4Title: "4. 正式收款上线",
                paymentsRoadmap4Text: "等主体、账号、风控和文档稳定后，再打开真实的全球支付入口。",
                footerVersion: "念念 Eterna v1.0",
                footerTagline: "念念不忘，ta一直在",
            },
            en: {
                __title: "Eterna | Memory that stays and answers back",
                brandTagline: "Memory that stays and answers back",
                topNote: "A place where longing can be held, answered, and kept.",
                langHelper: "Language",
                heroEyebrow: "Digital companionship for the people you miss most",
                heroTitle: "Give “I miss you” a place to land",
                heroIntro: "Store familiar names, small reminders, laughter, and the ordinary days you once shared inside a living memorial archive. Voice, photos, video, and memory rebuild their presence piece by piece, so every moment of longing has a gentle place to return to.",
                heroPoemMark: "Front-page inscription",
                heroPoemLine1: "I searched for you a thousand times in dreams,",
                heroPoemLine2: "and found you here, in Nian Nian.",
                heroPoemNote: "The figures that drifted away into dreams, dusk, and old family albums are placed back into a space that can answer, be preserved, and keep accompanying you.",
                heroPrimaryCta: "Light a memorial archive",
                heroSecondaryCta: "Hear a moment of company",
                seasonSpringTitle: "Spring",
                seasonSpringText: "A soft breeze carries new green and longing together.",
                seasonSummerTitle: "Summer",
                seasonSummerText: "Sky, sea, and distant figures slowly brighten into view.",
                seasonAutumnTitle: "Autumn",
                seasonAutumnText: "Leaves fall quietly, and old words return to the ear.",
                seasonWinterTitle: "Winter",
                seasonWinterText: "Even late at night, the light is still on and the company is still here.",
                sceneFragmentATitle: "People and landscape",
                sceneFragmentAText: "An elder, a father, a mother, and a child stand together against sea, sky, and the afterglow of dusk.",
                sceneFragmentBTitle: "Breeze and falling leaves",
                sceneFragmentBText: "Wind comes off the sea and carries old names and familiar tones back to the heart.",
                sceneFragmentCTitle: "The passing seasons",
                sceneFragmentCText: "Spring, summer, autumn, and winter move on, but the voice, posture, and stories you knew can still remain.",
                sceneFragmentDTitle: "Memory keeps growing",
                sceneFragmentDText: "When you come back, the waves, birds, light, and that answering presence are still here.",
                sceneCaptionTitle: "I searched for you in dreams and found you here.",
                sceneCaptionText: "People, landscape, breeze, falling leaves, and the passing seasons unfold longing slowly, turning the homepage into a memorial album that feels alive.",
                demoEyebrow: "Brand Film Demo · scored cut v2",
                demoHeading: "A 24-second memorial short that breathes",
                demoIntro: "This cut puts emotion, voice-over, and the rise and fall of music into one line: from a quiet night, to a sentence finally being answered, to memory becoming long-term companionship.",
                demoMetaLine: "Arc: lonely night → archive → conversation → continuing remembrance",
                demoMetaDuration: "Duration: 24s",
                demoNoteEyebrow: "Shot structure",
                demoNoteHeading: "Not nostalgia for display, but product storytelling with warmth.",
                demoNoteText: "Emotion comes first, but every beat is tied to a real product entry point. It first lets people feel the absence, then shows how memory can be held, preserved, and answered again.",
                demoBeat1Title: "Beat 1: A night with no reply",
                demoBeat1Text: "Start from the feeling of not being answered, instead of starting with AI as a pitch.",
                demoBeat2Title: "Beat 2: Eterna appears",
                demoBeat2Text: "Use reminders and archive creation to position the product as a doorway you can return to.",
                demoBeat3Title: "Beat 3: One sentence is caught",
                demoBeat3Text: "Use “I miss you today, and I am tired” to show how dialogue, catchphrases, and emotion are connected back.",
                demoBeat4Title: "Beat 4: Memory continues",
                demoBeat4Text: "Show birthday greetings, voice albums, and memory films so the product feels like ongoing companionship, not a one-off chat.",
                featuresEyebrow: "Ways of companionship",
                featuresHeading: "Make remembrance something you can return to",
                featuresIntro: "Eterna is not a short-lived novelty. It is a memorial space designed for long-term use, where every capability serves memory, care, greetings, and ongoing presence.",
                feature1Title: "Voice calls",
                feature1Text: "Upload a short recording and the system extracts speaking rhythm and emotional tone, then synthesizes a reply suited for phone-style companionship.",
                feature2Title: "Video presence",
                feature2Text: "When enough photo and video material is available, the experience becomes a more vivid visual presence, making “seeing them again” feel more real.",
                feature3Title: "Conversational memory",
                feature3Text: "Remember speaking style, shared experiences, and emotional context so responses feel closer to how that person would really speak.",
                feature4Title: "Everyday care",
                feature4Text: "Holidays, weather, birthdays, and ordinary days can all become triggers for gentle outreach, bringing remembrance back into daily life.",
                feature5Title: "Digital twin",
                feature5Text: "Voice, photos, videos, and shared memories become one archive so the digital person does not just answer, but gradually feels more like them.",
                feature6Title: "Family legacy",
                feature6Text: "Let a relationship remain visible and audible to the next generation as a true digital family legacy.",
                workbenchEyebrow: "Archive workspace",
                workbenchHeading: "Turn remembrance into something you can manage",
                workbenchIntro: "This is not a static display page. It works more like a family memorial book you can keep returning to, switching profiles, adding memories, and growing each digital twin over time.",
                chatSectionEyebrow: "Conversation experience",
                chatSectionHeading: "Start with longing, and return to a familiar voice",
                chatSectionIntro: "Create a profile first, then add voice, photos, and videos so this feels less like a generic reply box and more like a place where presence can slowly be recovered.",
                chatPrompt1: "I miss you today",
                chatPrompt2: "Work has felt heavy lately",
                chatPrompt3: "I want to share today's good news",
                modeText: "Text companion",
                modeVoice: "Voice call",
                modeVideo: "Video companion",
                ritualEyebrow: "Memorial flow",
                ritualHeading: "Leave a light first, then rebuild their presence",
                ritualText: "Name, relationship, and catchphrases shape the outline; voice, photos, video, and memory decide how close this twin feels. You do not need everything at once. Let the voice, face, and gestures come back gradually.",
                timeline1Title: "1. Create the profile",
                timeline1Text: "Start with the name, relationship, and expressions that immediately sound like them so the system has a real human foundation.",
                timeline2Title: "2. Add voice, photos, and video",
                timeline2Text: "Voice calibrates how they spoke, photos recover the face, and video helps the twin feel closer to their gestures and movement.",
                timeline3Title: "3. Keep adding memories",
                timeline3Text: "Start with one short story so the system does not just talk, but knows what the two of you really lived through together.",
                ritualPrimaryCta: "Create an archive now",
                pricingEyebrow: "Plans",
                pricingHeading: "Choose the depth of companionship you want to keep",
                pricingIntro: "From basic voice remembrance to full video presence and family legacy, the plans are structured around depth of companionship rather than feature clutter.",
                paymentsEyebrow: "Global payments readiness",
                paymentsHeading: "Prepare overseas payments as a switchable foundation",
                paymentsIntro: "Before turning on live Stripe billing, map out the three common routes first: which one is best for low-friction experiments, which suits solo builders, and which is right for long-term SaaS operations.",
                paymentsBadge: "Indie builder notes",
                paymentsMeta: "Weekend fragments can still be enough to get the payment stack mapped out.",
                paymentsJournalTitle: "Do not bet your entire revenue flow on one gateway",
                paymentsJournalText: "Stripe offers the best developer and subscription experience, but its risk controls are also the strictest. A safer approach is to keep a low-barrier experiment route ready first, then build a stronger base for long-term recurring revenue.",
                paymentsPoint1Title: "Apps and independent sites are different problems",
                paymentsPoint1Text: "For iOS, Apple Pay solves much of the path. For an indie site or SaaS, you need your own checkout, webhook, entitlement sync, and fallback plan.",
                paymentsPoint2Title: "Prepare backup channels before the main channel",
                paymentsPoint2Text: "Stripe is the cleanest option, but it should not be your only option. Having PayPal and Creem ready protects the business from a single point of failure.",
                paymentsPoint3Title: "Product, tax, and webhooks must be designed together",
                paymentsPoint3Text: "Displayed pricing, tax inclusion, payment callbacks, entitlement grants, and user redirects all need to work as one chain.",
                paymentsPoint4Title: "What Eterna is preparing next",
                paymentsPoint4Text: "The homepage now explains the global collection strategy clearly. The next step is live checkout, webhooks, plan entitlements, and multi-gateway fallback.",
                paypalStatus: "Low-barrier experiment channel",
                paypalTitle: "Best for the very first overseas payment",
                paypalText: "A personal PayPal account paired with platforms like Ko-fi is enough to start. It is lightweight and useful for demand validation, but not ideal as the only payment rail.",
                paypalPoint1: "Advantage: a personal account plus a card is enough to get started",
                paypalPoint2: "Constraint: heavily depends on PayPal itself, with a narrower direct card path",
                paypalPoint3: "Best for: earliest validation, sponsorship, and backup collection",
                creemStatus: "Friendly for China-based builders",
                creemTitle: "Best for getting an early SaaS payment flow working",
                creemText: "You do not need to register a company first, which makes it friendlier for solo builders in mainland China. It is fast for testing, but KYC, product description, and webhook handling still need to be done carefully.",
                creemPoint1: "Advantage: no company entity required at the start, with Alipay payouts available",
                creemPoint2: "Watch-out: passport-based verification is usually more reliable than ID-card-only attempts",
                creemPoint3: "Best for: early SaaS testing, sandbox integration, and backup collection",
                stripeStatus: "Long-term main channel",
                stripeTitle: "Best for turning subscriptions into a standard global payment layer",
                stripeText: "Stripe is the strongest long-term choice for subscriptions, entitlements, and global billing, but its onboarding and risk controls are also the most demanding. Company, banking, and compliance paths need to be ready first.",
                stripePoint1: "Advantage: mature developer tooling and subscription webhook ecosystem",
                stripePoint2: "Challenge: stricter risk review and stronger entity / banking requirements",
                stripePoint3: "Best for: formal subscription billing and standardized global payments",
                paymentsRoadmap1Title: "1. Diversify gateways",
                paymentsRoadmap1Text: "Assign clear roles to PayPal, Creem, and Stripe so the business is not blocked by one control point.",
                paymentsRoadmap2Title: "2. Validate the full test flow",
                paymentsRoadmap2Text: "Run checkout, webhooks, entitlement delivery, and return pages completely in the sandbox before anything goes live.",
                paymentsRoadmap3Title: "3. Keep pricing and tax consistent",
                paymentsRoadmap3Text: "Displayed prices, tax inclusion, plan entitlements, and subscription state should stay aligned across the stack.",
                paymentsRoadmap4Title: "4. Launch live billing carefully",
                paymentsRoadmap4Text: "Only open real global billing after the entity, accounts, risk controls, and documentation are stable.",
                footerVersion: "Eterna v1.0",
                footerTagline: "Memory that stays and answers back",
            }
        };
        const PLAN_COPY_FIELD_MAP = {
            seed: { nameId: "planName-seed", itemIds: ["planSeedItem1", "planSeedItem2", "planSeedItem3", "planSeedItem4", "planSeedItem5"] },
            tree: { nameId: "planName-tree", itemIds: ["planTreeItem1", "planTreeItem2", "planTreeItem3", "planTreeItem4"] },
            garden: { nameId: "planName-garden", itemIds: ["planGardenItem1", "planGardenItem2", "planGardenItem3", "planGardenItem4"] },
            family: { nameId: "planName-family", itemIds: ["planFamilyItem1", "planFamilyItem2", "planFamilyItem3", "planFamilyItem4"] },
        };
        const PLAN_MARKETING_COPY = {
            zh: {
                seed: { name: "思念种子", items: ["声音风格建模", "语音电话", "文字对话", "基础记忆归档", "1 位亲人"], note: "适合先把一位亲人的声音留住。", guestButton: "选择这个方案", authedButton: "立即开通", currentButton: "当前方案", currentNote: "你当前正在使用这个套餐，这里的能力已经实时绑定到账号。" },
                tree: { name: "思念之树", items: ["语音对话", "生日提醒", "3 位亲人", "更多记忆容量"], note: "适合一个家庭同时整理多位亲人的语音陪伴。", guestButton: "选择这个方案", authedButton: "立即开通", currentButton: "当前方案", currentNote: "你当前正在使用这个套餐，这里的能力已经实时绑定到账号。" },
                garden: { name: "思念花园", items: ["视频陪伴", "完整纪念能力", "5 位亲人", "优先体验新功能"], note: "适合需要语音电话和视频陪伴都长期开放的家庭。", guestButton: "推荐优先体验", authedButton: "立即开通", currentButton: "当前方案", currentNote: "你当前正在使用这个套餐，这里的能力已经实时绑定到账号。" },
                family: { name: "思念家族", items: ["多人分身档案", "家族传承", "无限亲人", "定制化服务"], note: "适合长期家族纪念、更多成员与更高容量。", guestButton: "联系定制方案", authedButton: "联系定制方案", currentButton: "当前方案", currentNote: "你当前正在使用这个套餐，这里的能力已经实时绑定到账号。" },
            },
            en: {
                seed: { name: "Memory Seed", items: ["Voice style model", "Voice calls", "Text companion", "Core memory archive", "1 loved one"], note: "Best for preserving one familiar voice first.", guestButton: "Choose this plan", authedButton: "Activate now", currentButton: "Current plan", currentNote: "You are already using this plan and its abilities are bound to your account." },
                tree: { name: "Memory Tree", items: ["Voice conversation", "Birthday reminders", "3 loved ones", "More memory capacity"], note: "Best for a household organizing voice companionship for several people.", guestButton: "Choose this plan", authedButton: "Activate now", currentButton: "Current plan", currentNote: "You are already using this plan and its abilities are bound to your account." },
                garden: { name: "Memory Garden", items: ["Video companion", "Full memorial abilities", "5 loved ones", "Priority access to new features"], note: "Best for families who want long-term voice and video companionship together.", guestButton: "Recommended", authedButton: "Activate now", currentButton: "Current plan", currentNote: "You are already using this plan and its abilities are bound to your account." },
                family: { name: "Family Legacy", items: ["Multiple digital twins", "Family inheritance", "Unlimited loved ones", "Custom service"], note: "Best for long-term family remembrance with higher capacity and more members.", guestButton: "Talk to us", authedButton: "Talk to us", currentButton: "Current plan", currentNote: "You are already using this plan and its abilities are bound to your account." },
            }
        };

        function isEnglish() {
            return currentLanguage === "en";
        }

        function pickCopy(zhText, enText) {
            return isEnglish() ? enText : zhText;
        }

        function setText(id, value) {
            const element = document.getElementById(id);
            if (element && typeof value === "string") {
                element.textContent = value;
            }
        }

        function getPlanCopy(code) {
            return PLAN_MARKETING_COPY[currentLanguage]?.[code] || PLAN_MARKETING_COPY.zh[code];
        }

        function applyPlanMarketingCopy() {
            Object.entries(PLAN_COPY_FIELD_MAP).forEach(([code, meta]) => {
                const copy = getPlanCopy(code);
                if (!copy) {
                    return;
                }
                setText(meta.nameId, copy.name);
                meta.itemIds.forEach((id, index) => setText(id, copy.items[index] || ""));
            });
        }

        function applyChatPromptCopy() {
            ["chatPrompt1", "chatPrompt2", "chatPrompt3"].forEach((id) => {
                const button = document.getElementById(id);
                const text = MARKETING_COPY[currentLanguage]?.[id];
                if (button && text) {
                    button.textContent = text;
                    button.dataset.prompt = text;
                }
            });
        }

        function updateLanguageToggleUi() {
            document.getElementById("langZh")?.classList.toggle("active", currentLanguage === "zh");
            document.getElementById("langEn")?.classList.toggle("active", currentLanguage === "en");
        }

        function applyMarketingCopy() {
            const copy = MARKETING_COPY[currentLanguage] || MARKETING_COPY.zh;
            document.title = copy.__title;
            Object.entries(copy).forEach(([key, value]) => {
                if (key.startsWith("__") || key.startsWith("chatPrompt")) {
                    return;
                }
                setText(key, value);
            });
            applyChatPromptCopy();
            applyPlanMarketingCopy();
            updateLanguageToggleUi();
            document.documentElement.lang = currentLanguage === "en" ? "en" : "zh-CN";
        }

        function refreshLanguageAwareUi() {
            applyMarketingCopy();
            updateMemorialMusicUi();
            updateAuthSurface();
            if (activeLovedOne) {
                applyLovedOne(activeLovedOne, false);
            } else {
                refreshChatIntro();
            }
        }

        function setLanguage(language, persist = true) {
            currentLanguage = language === "en" ? "en" : "zh";
            if (persist) {
                localStorage.setItem(UI_LANGUAGE_STORAGE_KEY, currentLanguage);
            }
            refreshLanguageAwareUi();
        }

        function initLanguageToggle() {
            const stored = localStorage.getItem(UI_LANGUAGE_STORAGE_KEY);
            const detected = stored || ((navigator.language || "").toLowerCase().startsWith("en") ? "en" : "zh");
            setLanguage(detected, false);
        }

        document.addEventListener("DOMContentLoaded", () => {
            bindModalEvents();
            bindMediaInputs();
            restoreAuthToken();
            initReveal();
            restoreLovedOne();
            hydrateRuntimeState();
            handleCheckoutReturn();
            refreshChatIntro();
            setupDemoVideo();
            initMemorialMusic();
            initLanguageToggle();
            updateSelectedMediaMeta();
            initGuideCapture();
            document.getElementById("proactiveCadence")?.addEventListener("change", (event) => {
                const weekdayField = document.getElementById("proactiveWeekday");
                if (weekdayField?.parentElement) {
                    weekdayField.parentElement.style.display = event.target.value === "weekly" ? "grid" : "none";
                }
            });
            const intensity = document.getElementById("chatIntensity");
            const intensityValue = document.getElementById("chatIntensityValue");
            if (intensity && intensityValue) {
                intensityValue.textContent = intensity.value;
                intensity.addEventListener("input", (event) => {
                    intensityValue.textContent = event.target.value;
                });
            }
        });

        function initMemorialMusic() {
            updateMemorialMusicUi();
            if (LICENSED_HOME_MUSIC_CANDIDATES.length) {
                void resolveLicensedMemorialMusicUrl();
            }
        }

        function updateMemorialMusicUi(message = "") {
            const button = document.getElementById("musicToggleButton");
            const label = document.getElementById("musicToggleLabel");
            const status = document.getElementById("musicStatus");
            const idleLabel = pickCopy("点亮纪念乐声", "Play memorial music");
            const playingLabel = pickCopy("暂停纪念乐声", "Pause memorial music");
            const idleMessage = pickCopy(
                "轻点一下，首页会响起纪念乐声；如果已放入授权曲目，会优先播放授权音频。",
                "Tap once to start the memorial score. If a licensed track is present, it will be used first."
            );
            const playingMessage = pickCopy(
                "纪念乐声正在陪你停留在这一页。",
                "The memorial score is now keeping you company on this page."
            );
            if (button) {
                button.classList.toggle("playing", memorialMusicPlaying);
            }
            if (label) {
                label.textContent = memorialMusicPlaying ? playingLabel : idleLabel;
            }
            if (status) {
                status.textContent = message || (memorialMusicPlaying ? playingMessage : idleMessage);
            }
        }

        async function resolveLicensedMemorialMusicUrl() {
            if (resolvedMemorialMusicUrl) {
                return resolvedMemorialMusicUrl;
            }
            if (memorialMusicLookupPromise) {
                return memorialMusicLookupPromise;
            }
            memorialMusicLookupPromise = (async () => {
                for (const candidate of LICENSED_HOME_MUSIC_CANDIDATES) {
                    try {
                        const response = await fetch(candidate, {
                            method: "HEAD",
                            cache: "no-store",
                        });
                        if (response.ok) {
                            resolvedMemorialMusicUrl = candidate;
                            updateMemorialMusicUi(
                                pickCopy(
                                    "已检测到授权曲目，点击后会优先播放该音频。",
                                    "A licensed track was found and will be used first when playback starts."
                                )
                            );
                            return candidate;
                        }
                    } catch (error) {
                        // ignore and try next candidate
                    }
                }
                return "";
            })();
            return memorialMusicLookupPromise;
        }

        function buildMemorialNoiseBuffer(context) {
            const length = context.sampleRate * 2;
            const buffer = context.createBuffer(1, length, context.sampleRate);
            const data = buffer.getChannelData(0);
            let last = 0;
            for (let i = 0; i < length; i += 1) {
                const white = Math.random() * 2 - 1;
                last = (last + 0.02 * white) / 1.02;
                data[i] = last * 0.6;
            }
            return buffer;
        }

        function scheduleMemorialTone(context, startAt, frequency, duration, gainValue, type = "triangle") {
            const oscillator = context.createOscillator();
            const gain = context.createGain();
            const filter = context.createBiquadFilter();
            oscillator.type = type;
            oscillator.frequency.setValueAtTime(frequency, startAt);
            filter.type = "lowpass";
            filter.frequency.setValueAtTime(1800, startAt);
            gain.gain.setValueAtTime(0.0001, startAt);
            gain.gain.linearRampToValueAtTime(gainValue, startAt + 0.6);
            gain.gain.exponentialRampToValueAtTime(Math.max(0.0001, gainValue * 0.75), startAt + duration * 0.58);
            gain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);
            oscillator.connect(filter);
            filter.connect(gain);
            gain.connect(memorialMusicMaster);
            oscillator.start(startAt);
            oscillator.stop(startAt + duration + 0.12);
        }

        function scheduleMemorialCycle(context, startAt) {
            const phrases = [
                [
                    [293.66, 0.0, 2.8, 0.042, "triangle"],
                    [440.0, 0.42, 2.1, 0.018, "sine"],
                    [523.25, 1.7, 1.8, 0.02, "sine"],
                ],
                [
                    [329.63, 0.0, 2.9, 0.042, "triangle"],
                    [493.88, 0.5, 2.1, 0.018, "sine"],
                    [587.33, 1.88, 1.6, 0.022, "sine"],
                ],
                [
                    [246.94, 0.0, 3.1, 0.04, "triangle"],
                    [392.0, 0.48, 2.3, 0.018, "sine"],
                    [440.0, 1.7, 1.9, 0.02, "sine"],
                ],
                [
                    [261.63, 0.0, 3.2, 0.04, "triangle"],
                    [392.0, 0.36, 2.4, 0.016, "sine"],
                    [523.25, 1.96, 1.8, 0.021, "sine"],
                ],
            ];
            const cycleLength = 12.8;
            phrases.forEach((phrase, index) => {
                const phraseStart = startAt + index * 3.2;
                phrase.forEach(([frequency, delay, duration, gainValue, type]) => {
                    scheduleMemorialTone(context, phraseStart + delay, frequency, duration, gainValue, type);
                });
            });
            return cycleLength;
        }

        async function startGeneratedMemorialMusic() {
            const AudioContextRef = window.AudioContext || window.webkitAudioContext;
            if (!AudioContextRef) {
                throw new Error("当前浏览器不支持网页音频。");
            }

            memorialMusicContext = new AudioContextRef();
            memorialMusicMaster = memorialMusicContext.createGain();
            memorialMusicMaster.gain.setValueAtTime(0.0001, memorialMusicContext.currentTime);
            memorialMusicMaster.connect(memorialMusicContext.destination);

            const noiseSource = memorialMusicContext.createBufferSource();
            noiseSource.buffer = buildMemorialNoiseBuffer(memorialMusicContext);
            noiseSource.loop = true;
            const noiseFilter = memorialMusicContext.createBiquadFilter();
            noiseFilter.type = "lowpass";
            noiseFilter.frequency.value = 780;
            const noiseGain = memorialMusicContext.createGain();
            noiseGain.gain.value = 0.014;
            noiseSource.connect(noiseFilter);
            noiseFilter.connect(noiseGain);
            noiseGain.connect(memorialMusicMaster);
            noiseSource.start();
            memorialMusicWindSource = noiseSource;

            const firstStart = memorialMusicContext.currentTime + 0.18;
            const cycleLength = scheduleMemorialCycle(memorialMusicContext, firstStart);
            const timer = window.setInterval(() => {
                if (!memorialMusicContext || memorialMusicContext.state === "closed") {
                    return;
                }
                scheduleMemorialCycle(memorialMusicContext, memorialMusicContext.currentTime + 0.16);
            }, cycleLength * 1000);
            memorialMusicTimers.push(timer);

            memorialMusicMaster.gain.linearRampToValueAtTime(0.18, memorialMusicContext.currentTime + 1.2);
        }

        async function startLicensedMemorialMusic(url) {
            if (!memorialMusicElement) {
                memorialMusicElement = new Audio(url);
                memorialMusicElement.loop = true;
                memorialMusicElement.preload = "auto";
                memorialMusicElement.volume = 0.58;
            } else if (memorialMusicElement.src !== new URL(url, window.location.href).href) {
                memorialMusicElement.pause();
                memorialMusicElement = new Audio(url);
                memorialMusicElement.loop = true;
                memorialMusicElement.preload = "auto";
                memorialMusicElement.volume = 0.58;
            }
            memorialMusicElement.currentTime = 0;
            await memorialMusicElement.play();
        }

        async function startMemorialMusic() {
            if (memorialMusicPlaying) {
                return;
            }
            const licensedUrl = await resolveLicensedMemorialMusicUrl();
            if (licensedUrl) {
                await startLicensedMemorialMusic(licensedUrl);
            } else {
                await startGeneratedMemorialMusic();
            }
            memorialMusicPlaying = true;
            updateMemorialMusicUi(
                licensedUrl
                    ? pickCopy("已点亮首页纪念乐声。", "Memorial music is now playing on the homepage.")
                    : pickCopy(
                        "当前已播放站内纪念氛围乐；把授权曲目文件放进 assets 后，这里会自动切换到指定音频。",
                        "The built-in memorial score is playing now. Once a licensed track is added to assets, playback will switch automatically."
                    )
            );
        }

        async function stopMemorialMusic() {
            memorialMusicTimers.forEach((timer) => window.clearInterval(timer));
            memorialMusicTimers = [];

            if (memorialMusicElement) {
                memorialMusicElement.pause();
                memorialMusicElement.currentTime = 0;
            }

            if (memorialMusicWindSource) {
                try {
                    memorialMusicWindSource.stop();
                } catch (error) {
                    // ignore repeated stop
                }
                memorialMusicWindSource.disconnect();
                memorialMusicWindSource = null;
            }

            if (memorialMusicContext) {
                try {
                    await memorialMusicContext.close();
                } catch (error) {
                    // ignore close failures
                }
            }

            memorialMusicContext = null;
            memorialMusicMaster = null;
            memorialMusicPlaying = false;
            updateMemorialMusicUi(pickCopy("纪念乐声已经停下来了。", "Memorial music has been paused."));
        }

        async function toggleMemorialMusic() {
            try {
                if (memorialMusicPlaying) {
                    await stopMemorialMusic();
                    return;
                }
                await startMemorialMusic();
            } catch (error) {
                memorialMusicPlaying = false;
                updateMemorialMusicUi(pickCopy("这段音乐还没成功点亮，请再点一次试试。", "The track did not start this time. Please try again."));
                showToast(error.message || pickCopy("当前浏览器暂时无法播放首页音乐。", "This browser could not play the homepage music right now."), "error");
            }
        }

        function initReveal() {
            const revealNodes = document.querySelectorAll(".reveal");
            const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            if (reducedMotion) {
                revealNodes.forEach((node) => node.classList.add("is-visible"));
                return;
            }

            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add("is-visible");
                            observer.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.12 }
            );

            revealNodes.forEach((node) => observer.observe(node));
        }

        function initGuideCapture() {
            const transcript = document.getElementById("dhGuideTranscript");
            if (!transcript) {
                return;
            }
            transcript.value = guideTranscriptCache || "";
            setGuideStatus("准备好后，点击开始录音并讲述。", "neutral");
        }

        function setGuideStatus(message, tone = "neutral") {
            const status = document.getElementById("dhGuideStatus");
            const meta = document.getElementById("dhGuideMeta");
            if (status) {
                status.textContent = message;
            }
            if (meta) {
                meta.textContent = tone === "recording" ? "录音中" : tone === "saved" ? "已填充" : "可录制";
            }
        }

        async function startGuideRecording() {
            if (guideRecording) {
                return;
            }
            if (!navigator.mediaDevices?.getUserMedia) {
                showToast("当前浏览器不支持录音。", "error");
                return;
            }
            const transcript = document.getElementById("dhGuideTranscript");
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                guideChunks = [];
                guideRecorder = new MediaRecorder(
                    stream,
                    MediaRecorder.isTypeSupported("audio/webm") ? { mimeType: "audio/webm" } : undefined
                );
                guideRecorder.ondataavailable = (event) => {
                    if (event.data?.size) {
                        guideChunks.push(event.data);
                    }
                };
                guideRecorder.onstop = () => {
                    stream.getTracks().forEach((track) => track.stop());
                    const blob = new Blob(guideChunks, { type: guideRecorder.mimeType || "audio/webm" });
                    handleGuideRecording(blob);
                };
                guideRecorder.start();
                guideRecording = true;
                document.getElementById("dhGuideStart").disabled = true;
                document.getElementById("dhGuideStop").disabled = false;
                setGuideStatus("正在录音并转写中…", "recording");

                if (window.SpeechRecognition || window.webkitSpeechRecognition) {
                    const Recognizer = window.SpeechRecognition || window.webkitSpeechRecognition;
                    guideRecognition = new Recognizer();
                    guideRecognition.continuous = true;
                    guideRecognition.interimResults = true;
                    guideRecognition.lang = "zh-CN";
                    guideRecognition.onresult = (event) => {
                        let draft = "";
                        for (let i = event.resultIndex; i < event.results.length; i += 1) {
                            draft += event.results[i][0].transcript;
                        }
                        guideTranscriptCache = draft.trim();
                        if (transcript) {
                            transcript.value = guideTranscriptCache;
                        }
                    };
                    guideRecognition.onerror = () => {};
                    guideRecognition.start();
                }
            } catch (error) {
                showToast("无法开始录音，请检查麦克风权限。", "error");
            }
        }

        function stopGuideRecording() {
            if (!guideRecording) {
                return;
            }
            guideRecording = false;
            document.getElementById("dhGuideStart").disabled = false;
            document.getElementById("dhGuideStop").disabled = true;
            if (guideRecorder?.state === "recording") {
                guideRecorder.stop();
            }
            if (guideRecognition) {
                guideRecognition.stop();
                guideRecognition = null;
            }
            setGuideStatus("录音已结束，正在整理内容。", "neutral");
        }

        async function handleGuideRecording(blob) {
            if (!blob || !blob.size) {
                return;
            }
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!currentUser || isLocalProfile(profile)) {
                setGuideStatus("录音已完成，登录后可保存并自动填表。", "neutral");
                return;
            }
            try {
                const form = new FormData();
                form.append("file", blob, `guide-${Date.now()}.webm`);
                const response = await apiFetch(`/api/loved-ones/${profile.id}/voice`, {
                    method: "POST",
                    body: form
                });
                if (!response.ok) {
                    throw new Error("upload failed");
                }
                await loadActiveMediaAssets();
                setGuideStatus("录音已上传，正在自动填表。", "neutral");
                applyGuideTranscript();
            } catch (error) {
                setGuideStatus("录音上传失败，请稍后重试。", "neutral");
            }
        }

        function extractTraits(text, traits) {
            return traits.filter((trait) => text.includes(trait));
        }

        function extractSentences(text, keywords) {
            return text
                .split(/[。！？!?]/)
                .map((sentence) => sentence.trim())
                .filter((sentence) => sentence && keywords.some((keyword) => sentence.includes(keyword)));
        }

        function parseGuideTranscript(text) {
            const result = {
                relationship: "",
                personaTraits: [],
                voiceTraits: [],
                visualTraits: [],
                memories: [],
                keyLine: ""
            };
            if (!text) {
                return result;
            }

            const relationHints = ["妈妈", "爸爸", "爷爷", "奶奶", "外公", "外婆", "姐姐", "哥哥", "弟弟", "妹妹", "老师", "朋友", "恋人", "妻子", "丈夫", "儿子", "女儿"];
            const relationMatch = relationHints.find((hint) => text.includes(hint));
            if (relationMatch) {
                result.relationship = relationMatch;
            }

            const personaTraits = ["温柔", "认真", "细心", "直爽", "幽默", "安静", "踏实", "坚强", "乐观", "爱笑", "有仪式感", "爱干净", "有责任感", "稳重", "热心"];
            result.personaTraits = extractTraits(text, personaTraits);

            const voiceTraits = ["语速快", "语速慢", "声音轻", "声音低", "语气温柔", "爱叮嘱", "口头禅", "常说", "爱笑着说", "喜欢叫我"];
            result.voiceTraits = extractTraits(text, voiceTraits);
            const speechSentences = extractSentences(text, ["口头禅", "常说", "说话", "语气", "声音", "笑"]);
            if (speechSentences.length) {
                result.voiceTraits.push(...speechSentences.slice(0, 2));
            }

            const visualSentences = extractSentences(text, ["身高", "体型", "头发", "发型", "眼睛", "笑", "穿", "衣服", "手", "背影", "戴"]);
            result.visualTraits = visualSentences.slice(0, 3);

            const memorySentences = extractSentences(text, ["那年", "那天", "小时候", "去年", "我们", "一起", "第一次", "最后一次", "在"]);
            result.memories = memorySentences.slice(0, 3);

            const keyLineMatch = text.match(/最想听到[^。！？!?]*[。！？!?]?/);
            result.keyLine = keyLineMatch ? keyLineMatch[0] : "";

            return result;
        }

        async function applyGuideTranscript() {
            const transcript = document.getElementById("dhGuideTranscript");
            const text = transcript?.value.trim() || "";
            if (!text) {
                showToast("先录一段或填写口述内容。", "error");
                return;
            }
            guideTranscriptCache = text;
            const parsed = parseGuideTranscript(text);

            if (parsed.personaTraits.length) {
                setDigitalHumanPills("dhPersonaCore", parsed.personaTraits, "人物底稿待补充");
            }
            const relationship = parsed.relationship ? `关系/称谓：${parsed.relationship}` : "关系/称谓：待补充";
            const keyLine = parsed.keyLine ? `最想听到的一句话：${parsed.keyLine}` : "最想听到的一句话：待补充";
            const anchors = document.getElementById("dhRelationshipAnchors");
            if (anchors) {
                anchors.textContent = `${relationship}\n${keyLine}`;
            }

            if (parsed.voiceTraits.length) {
                setDigitalHumanPills("dhVoiceTraits", parsed.voiceTraits, "当前还没有足够的声音画像。");
                document.getElementById("dhVoiceMeta").textContent = "已补充";
                document.getElementById("dhVoiceStatus").textContent = "已从口述中提取到语气与说话习惯。";
            }
            if (parsed.visualTraits.length) {
                setDigitalHumanPills("dhVisualTraits", parsed.visualTraits, "当前还没有足够的视觉画像。");
                document.getElementById("dhVisualMeta").textContent = "已补充";
                document.getElementById("dhVisualStatus").textContent = "已从口述中提取到外貌与气质线索。";
            }

            if (parsed.memories.length) {
                const now = new Date().toISOString();
                const fragments = parsed.memories.map((memory, index) => ({
                    id: `guide-${Date.now()}-${index}`,
                    title: "口述片段",
                    content: memory,
                    fragment_kind: "memory_anchor",
                    modality: "voice",
                    weight: 0.9,
                    created_at: now,
                    source_type: "guide"
                }));
                activeDigitalHumanFragments = [...fragments, ...activeDigitalHumanFragments].slice(0, 24);
                renderDigitalHumanFragments(activeDigitalHumanFragments);
            }

            if (currentUser && activeLovedOne && !isLocalProfile(activeLovedOne)) {
                try {
                    await apiFetch("/api/memories", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            loved_one_id: activeLovedOne.id,
                            content: text,
                            memory_type: "story",
                            importance: 6
                        })
                    });
                    await Promise.allSettled([loadDigitalHumanConsole(), loadActiveMediaAssets()]);
                } catch (error) {
                    // ignore
                }
            }
            setGuideStatus("已自动填充并保存片段。", "saved");
            showToast("已从口述内容自动填入控制台。", "success");
        }

        function setupDemoVideo() {
            const video = document.getElementById("demoVideo");
            if (!video) {
                return;
            }

            const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            if (prefersReducedMotion) {
                video.removeAttribute("autoplay");
                video.pause();
                return;
            }

            const tryPlay = () => {
                const playPromise = video.play();
                if (playPromise && typeof playPromise.catch === "function") {
                    playPromise.catch(() => {});
                }
            };

            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            tryPlay();
                        } else {
                            video.pause();
                        }
                    });
                },
                { threshold: 0.35 }
            );

            observer.observe(video);
        }

        function bindMediaInputs() {
            ["voiceFiles", "photoFiles", "videoFiles", "managerVoiceFiles", "managerPhotoFiles", "managerVideoFiles", "managerModel3dFiles", "dhModel3dFiles"].forEach((id) => {
                const input = document.getElementById(id);
                if (!input) {
                    return;
                }
                input.addEventListener("change", updateSelectedMediaMeta);
            });
        }

        function restoreAuthToken() {
            authToken = localStorage.getItem(AUTH_STORAGE_KEY) || "";
        }

        function persistAuthToken(token) {
            authToken = token || "";
            if (authToken) {
                localStorage.setItem(AUTH_STORAGE_KEY, authToken);
            } else {
                localStorage.removeItem(AUTH_STORAGE_KEY);
            }
        }

        async function apiFetch(path, options = {}) {
            const headers = new Headers(options.headers || {});
            if (authToken) {
                headers.set("Authorization", `Bearer ${authToken}`);
            }
            const response = await fetch(`${API_BASE}${path}`, {
                ...options,
                headers
            });
            if (response.status === 401) {
                persistAuthToken("");
                currentUser = null;
                currentSubscription = null;
                updateAuthSurface();
            }
            return response;
        }

        function requireAccount(message = "请先登录后再继续。") {
            if (currentUser) {
                return true;
            }
            showToast(message, "error");
            openAuthModal("register");
            return false;
        }

        function getPlanFeatures() {
            return currentSubscription?.features || { text: true, voice: false, video: false, voice_upload: false, video_upload: false };
        }

        function getSelectedFiles(id) {
            return Array.from(document.getElementById(id)?.files || []);
        }

        function summarizeSelection(files, emptyText, unit) {
            if (!files.length) {
                return emptyText;
            }

            const names = files.slice(0, 2).map((file) => file.name).join("、");
            const suffix = files.length > 2 ? ` 等 ${files.length}${unit}` : ` · 共 ${files.length}${unit}`;
            return `${names}${suffix}`;
        }

        function updateSelectedMediaMeta() {
            document.getElementById("voiceFilesMeta").textContent = summarizeSelection(
                getSelectedFiles("voiceFiles"),
                "还没有选择语音文件。",
                "段语音"
            );
            document.getElementById("photoFilesMeta").textContent = summarizeSelection(
                getSelectedFiles("photoFiles"),
                "还没有选择照片。",
                "张照片"
            );
            document.getElementById("videoFilesMeta").textContent = summarizeSelection(
                getSelectedFiles("videoFiles"),
                "还没有选择视频。",
                "段视频"
            );
            const managerVoiceMeta = document.getElementById("managerVoiceFilesMeta");
            const managerPhotoMeta = document.getElementById("managerPhotoFilesMeta");
            const managerVideoMeta = document.getElementById("managerVideoFilesMeta");
            if (managerVoiceMeta) {
                managerVoiceMeta.textContent = summarizeSelection(
                    getSelectedFiles("managerVoiceFiles"),
                    "还没有选择语音文件。",
                    "段语音"
                );
            }
            if (managerPhotoMeta) {
                managerPhotoMeta.textContent = summarizeSelection(
                    getSelectedFiles("managerPhotoFiles"),
                    "还没有选择照片。",
                    "张照片"
                );
            }
            if (managerVideoMeta) {
                managerVideoMeta.textContent = summarizeSelection(
                    getSelectedFiles("managerVideoFiles"),
                    "还没有选择视频。",
                    "段视频"
                );
            }
            const managerModel3dMeta = document.getElementById("managerModel3dFilesMeta");
            if (managerModel3dMeta) {
                managerModel3dMeta.textContent = summarizeSelection(
                    getSelectedFiles("managerModel3dFiles"),
                    "还没有选择 3D 重建文件。",
                    "份文件"
                );
            }
            const dhModel3dMeta = document.getElementById("dhModel3dUploadMeta");
            if (dhModel3dMeta) {
                dhModel3dMeta.textContent = summarizeSelection(
                    getSelectedFiles("dhModel3dFiles"),
                    "支持 glb / gltf / usdz / obj / fbx / stl / ply / zip。",
                    "份文件"
                );
            }
        }

        function resolveMediaUrl(url) {
            if (!url) {
                return "";
            }
            if (/^(https?:|blob:|data:)/.test(url)) {
                return url;
            }
            return `${API_BASE}${url}`;
        }

        function canRenderModel3dInline(asset) {
            const name = String(asset?.original_filename || "").toLowerCase();
            const mime = String(asset?.mime_type || "").toLowerCase();
            return (
                mime.includes("gltf") ||
                mime.includes("model") ||
                [".glb", ".gltf", ".usdz"].some((ext) => name.endsWith(ext))
            );
        }

        function renderModel3dPreview(container, asset, compact = false) {
            const assetUrl = resolveMediaUrl(asset.url);
            const modelViewerReady = Boolean(window.customElements?.get("model-viewer"));
            if (canRenderModel3dInline(asset) && modelViewerReady) {
                const viewer = document.createElement("model-viewer");
                viewer.setAttribute("src", assetUrl);
                viewer.setAttribute("camera-controls", "");
                viewer.setAttribute("auto-rotate", "");
                viewer.setAttribute("interaction-prompt", "none");
                viewer.setAttribute("shadow-intensity", "1");
                viewer.setAttribute("touch-action", "pan-y");
                viewer.alt = asset.original_filename || "3D reconstruction";
                if (compact) {
                    viewer.style.minHeight = "180px";
                }
                container.append(viewer);
            } else {
                const fallback = document.createElement("div");
                fallback.className = "model3d-fallback";
                fallback.textContent = "当前文件格式不能直接在线预览，但已经进入数字人的 3D 重建素材库。";
                container.append(fallback);
            }

            const link = document.createElement("a");
            link.href = assetUrl;
            link.target = "_blank";
            link.rel = "noreferrer";
            link.className = "inline-action";
            link.textContent = "打开原始 3D 文件";
            container.append(link);
        }

        function normalizeTags(tags) {
            return (Array.isArray(tags) ? tags : [])
                .map((tag) => String(tag || "").trim())
                .filter((tag) => tag.length > 0);
        }

        function formatModel3dStage(stage) {
            const map = {
                uploaded: "已上传",
                aligned: "已对齐",
                textured: "已贴图",
                rigged: "已骨骼",
                ready: "已可用",
                integrated: "已并入模型"
            };
            return map[stage] || "未标记";
        }

        function getAvailableModes(profile) {
            const assetModes = profile?.digital_twin_profile?.available_modes || ["text"];
            if (!currentUser || isLocalProfile(profile)) {
                return assetModes;
            }
            const features = getPlanFeatures();
            return assetModes.filter((mode) => {
                if (mode === "text") {
                    return features.text;
                }
                if (mode === "voice") {
                    return features.voice;
                }
                if (mode === "video") {
                    return features.video;
                }
                return false;
            });
        }

        function formatAvailableModes(modes) {
            const labels = {
                text: pickCopy("文字陪伴", "Text companion"),
                voice: pickCopy("语音电话", "Voice calls"),
                video: pickCopy("视频陪伴", "Video companion")
            };
            return modes.map((mode) => labels[mode] || mode).join(" / ");
        }

        function collectMemoryDrafts(rawValue) {
            return rawValue
                .split(/\n+/)
                .map((line) => line.replace(/^[•*\-\d.、\s]+/, "").trim())
                .filter(Boolean);
        }

        function setInteractionMode(mode, force = false) {
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            const availableModes = getAvailableModes(profile);
            const assetModes = profile?.digital_twin_profile?.available_modes || ["text"];
            const features = getPlanFeatures();
            if (!force && mode !== "text" && !availableModes.includes(mode)) {
                showToast(
                    mode === "voice"
                        ? (!features.voice && currentUser
                            ? pickCopy("当前套餐还没有开放语音电话，请先升级套餐。", "Voice calls are not included in the current plan yet. Upgrade the plan first.")
                            : pickCopy("先上传语音素材，才能开启语音电话。", "Upload voice material first to unlock voice calls."))
                        : (!features.video && currentUser
                            ? pickCopy("当前套餐还没有开放视频陪伴，请先升级套餐。", "Video companion is not included in the current plan yet. Upgrade the plan first.")
                            : assetModes.includes("voice")
                                ? pickCopy("再补充照片或视频，才能进入视频陪伴。", "Add more photos or videos before entering video companion mode.")
                                : pickCopy("先补充语音和照片或视频，才能进入视频陪伴。", "Add voice plus photo or video material first to unlock video companion mode.")),
                    "error"
                );
                return;
            }

            selectedChatMode = availableModes.includes(mode) ? mode : "text";
            updateModeControls(profile);
        }

        function updateModeControls(profile) {
            const availableModes = getAvailableModes(profile);
            const buttons = {
                text: document.getElementById("modeText"),
                voice: document.getElementById("modeVoice"),
                video: document.getElementById("modeVideo")
            };

            if (!availableModes.includes(selectedChatMode)) {
                selectedChatMode = availableModes.includes("voice") ? "voice" : "text";
            }

            Object.entries(buttons).forEach(([mode, button]) => {
                if (!button) {
                    return;
                }
                button.disabled = mode !== "text" && !availableModes.includes(mode);
                button.classList.toggle("active", mode === selectedChatMode);
            });

            const twin = profile.digital_twin_profile || buildClientTwinProfile(profile);
            const subscriptionText = currentSubscription?.plan_name
                ? pickCopy(
                    `当前套餐：${getLocalizedPlanName(currentSubscription)}。`,
                    `Plan: ${getLocalizedPlanName(currentSubscription)}.`
                )
                : pickCopy("登录后，模式权限会与套餐绑定。", "Sign in to bind mode access to your plan.");
            document.getElementById("modeAvailability").textContent = isEnglish()
                ? `Available now: ${formatAvailableModes(availableModes)}. ${subscriptionText} Model readiness: ${twin.completion_percent || 0}%.`
                : `当前可用：${formatAvailableModes(availableModes)}。${subscriptionText}${twin.summary}`;
        }

        function clearResponseMedia() {
            const responseMedia = document.getElementById("responseMedia");
            const audioCard = document.getElementById("audioCard");
            const videoCard = document.getElementById("videoCard");
            const responseAudio = document.getElementById("responseAudio");
            const responseVideo = document.getElementById("responseVideo");
            const modeNote = document.getElementById("modeNote");
            const responseMemoryRefs = document.getElementById("responseMemoryRefs");

            responseMedia.classList.remove("active");
            audioCard.hidden = true;
            videoCard.hidden = true;
            responseAudio.pause();
            responseAudio.removeAttribute("src");
            responseAudio.load();
            responseVideo.pause();
            responseVideo.removeAttribute("src");
            responseVideo.load();
            modeNote.textContent = "";
            if (responseMemoryRefs) {
                responseMemoryRefs.textContent = "";
            }
        }

        function renderResponseMedia(response, profile) {
            const activeMode = response?.interaction_mode || selectedChatMode;
            const responseMedia = document.getElementById("responseMedia");
            const audioCard = document.getElementById("audioCard");
            const videoCard = document.getElementById("videoCard");
            const responseAudio = document.getElementById("responseAudio");
            const responseVideo = document.getElementById("responseVideo");
            const modeNote = document.getElementById("modeNote");
            const responseMemoryRefs = document.getElementById("responseMemoryRefs");

            const audioUrl = resolveMediaUrl(response?.response_audio_url);
            const videoUrl = resolveMediaUrl(response?.response_video_url);
            const fallbackVideoUrl =
                activeMode === "video" && !videoUrl && profile?.video_urls?.[0]
                    ? resolveMediaUrl(profile.video_urls[0])
                    : "";

            audioCard.hidden = !audioUrl;
            videoCard.hidden = !(videoUrl || fallbackVideoUrl);

            if (audioUrl) {
                responseAudio.src = audioUrl;
                responseAudio.load();
                responseAudio.play().catch(() => {});
            } else {
                responseAudio.pause();
                responseAudio.removeAttribute("src");
                responseAudio.load();
            }

            const finalVideoUrl = videoUrl || fallbackVideoUrl;
            if (finalVideoUrl) {
                responseVideo.src = finalVideoUrl;
                responseVideo.load();
            } else {
                responseVideo.pause();
                responseVideo.removeAttribute("src");
                responseVideo.load();
            }

            modeNote.textContent =
                response?.mode_note ||
                (activeMode === "video" && profile?.video_urls?.[0]
                    ? "当前视频陪伴会优先返回 Mimo 生成的纪念短片；如果视频合成暂时不可用，会回退到你上传的影像素材。"
                    : activeMode === "voice"
                        ? "当前语音电话模式会优先生成陪伴式语音回复。"
                        : "当前是文字陪伴模式。");

            if (responseMemoryRefs) {
                const refs = Array.isArray(response?.memory_refs) ? response.memory_refs : [];
                responseMemoryRefs.textContent = refs.length ? `参考回忆：${refs.slice(0, 2).join("；")}` : "";
            }

            if (audioUrl || finalVideoUrl || modeNote.textContent) {
                responseMedia.classList.add("active");
            } else {
                responseMedia.classList.remove("active");
            }
        }

        function buildClientTwinWorkflow({
            memoryCount,
            voiceCount,
            photoCount,
            videoCount,
            signalCount,
            availableModes
        }) {
            const features = currentSubscription?.features || {
                text: true,
                voice: true,
                video: true,
                voice_upload: true,
                video_upload: true
            };

            function makeStep({ code, title, current, target, pendingDetail, activeDetail, completedDetail, locked = false, lockedDetail = "" }) {
                const safeTarget = Math.max(target, 1);
                if (locked) {
                    return {
                        code,
                        title,
                        status: "locked",
                        current,
                        target,
                        progress_percent: 0,
                        detail: lockedDetail || pendingDetail
                    };
                }

                if (current >= safeTarget) {
                    return {
                        code,
                        title,
                        status: "completed",
                        current,
                        target,
                        progress_percent: 100,
                        detail: completedDetail
                    };
                }

                if (current > 0) {
                    return {
                        code,
                        title,
                        status: "active",
                        current,
                        target,
                        progress_percent: Math.round((current / safeTarget) * 100),
                        detail: activeDetail
                    };
                }

                return {
                    code,
                    title,
                    status: "pending",
                    current,
                    target,
                    progress_percent: 0,
                    detail: pendingDetail
                };
            }

            const steps = [
                makeStep({
                    code: "identity_seed",
                    title: "人格底稿",
                    current: signalCount,
                    target: 4,
                    pendingDetail: "先补全名字、关系、说话方式和一两个性格线索，让系统先知道 ta 是谁。",
                    activeDetail: "人格底稿已经开始成形，再补一句口头禅或更具体的说话方式会更像 ta。",
                    completedDetail: "名字、关系、性格和说话方式已经具备，分身的人格底稿已可用。"
                }),
                makeStep({
                    code: "memory_grounding",
                    title: "共同记忆校准",
                    current: memoryCount,
                    target: 6,
                    pendingDetail: "先写下几段只属于你们的日常细节，让回应不只是泛泛安慰。",
                    activeDetail: "系统已经抓住一部分共同经历，再补几条生活记忆会更像真实亲人。",
                    completedDetail: "共同记忆已经足够支撑长期对话，分身开始拥有稳定的生活语境。"
                }),
                makeStep({
                    code: "voice_calibration",
                    title: "声音校准",
                    current: voiceCount,
                    target: 2,
                    pendingDetail: "上传至少一段清晰语音，让声音和说话节奏开始被还原。",
                    activeDetail: "声音特征已经在校准中，再补一段不同场景的语音会更自然。",
                    completedDetail: "声音样本已经足够，语气、语速和情绪节奏开始稳定下来。",
                    locked: !features.voice_upload,
                    lockedDetail: "当前套餐还没有开放语音建模上传，先用文字和照片推进人格轮廓。"
                }),
                makeStep({
                    code: "visual_restoration",
                    title: "面容与神态还原",
                    current: photoCount + videoCount,
                    target: 3,
                    pendingDetail: "先上传照片，分身才会逐渐具备熟悉的面容和气质。",
                    activeDetail: "面容与神态正在恢复中，再补充照片或视频会更接近 ta 的在场感。",
                    completedDetail: "照片和影像素材已经具备，分身开始拥有更稳定的视觉识别感。"
                }),
                makeStep({
                    code: "presence_activation",
                    title: "多模态陪伴激活",
                    current: availableModes.length,
                    target: 1 + Number(Boolean(features.voice)) + Number(Boolean(features.video)),
                    pendingDetail: "先把人格底稿和记忆打牢，系统才会逐步解锁更像真人的陪伴模式。",
                    activeDetail: "系统已经解锁了一部分陪伴形态，继续补素材会把文字推进到语音或视频。",
                    completedDetail: "当前套餐对应的陪伴模式已经全部激活，这个数字家人可以持续被维护和陪伴。"
                })
            ];

            const actionableSteps = steps.filter((step) => ["active", "pending"].includes(step.status));
            const currentStage = actionableSteps[0] || steps[steps.length - 1];
            const completedTitles = steps.filter((step) => step.status === "completed").map((step) => step.title);

            const nextActions = [];
            if (signalCount < 4) {
                nextActions.push({
                    type: "identity",
                    title: "补一句最像 ta 的说话方式",
                    detail: "比如口头禅、称呼习惯、说话快慢，这会决定分身最基本的表达质感。",
                    cta_label: "完善档案"
                });
            }
            if (memoryCount < 6) {
                nextActions.push({
                    type: "memory",
                    title: `再补 ${Math.max(1, Math.min(3, 6 - memoryCount))} 条共同回忆`,
                    detail: "优先写具体场景、常做的事和 ta 会怎么回应你，让对话开始带有生活细节。",
                    cta_label: "添加回忆"
                });
            }
            if (voiceCount < 2) {
                nextActions.push(
                    features.voice_upload
                        ? {
                            type: "voice",
                            title: "补充语音样本",
                            detail: "至少两段清晰语音最容易还原语气和停顿。",
                            cta_label: "上传语音"
                        }
                        : {
                            type: "upgrade",
                            title: "当前套餐未开放语音建模",
                            detail: "先用文字和照片维护分身，后续升级套餐即可接入语音电话。",
                            cta_label: "查看套餐"
                        }
                );
            }
            if (photoCount < 2) {
                nextActions.push({
                    type: "photo",
                    title: `再补 ${Math.max(1, 2 - photoCount)} 张代表性照片`,
                    detail: "优先选正脸、日常笑容和熟悉场景的照片，能更快稳定面容气质。",
                    cta_label: "上传照片"
                });
            }
            if (videoCount < 1) {
                nextActions.push(
                    features.video_upload
                        ? {
                            type: "video",
                            title: "补一段视频素材",
                            detail: "一段家庭录像就能显著增强神态、动作节奏和在场感。",
                            cta_label: "上传视频"
                        }
                        : {
                            type: "upgrade",
                            title: "视频陪伴仍未开放",
                            detail: "当前套餐先把声音和照片养完整，升级后就能继续视频陪伴。",
                            cta_label: "查看套餐"
                        }
                );
            }

            if (!nextActions.length) {
                nextActions.push({
                    type: "chat",
                    title: "开始和 ta 长期对话",
                    detail: "现在最有价值的是持续补充新的日常，分身会随着对话和回忆继续变得更像 ta。",
                    cta_label: "开始陪伴"
                });
            }

            const workflowSummary = completedTitles.length
                ? `系统已自动完成「${completedTitles.slice(0, 2).join("、")}」等阶段，当前正在推进「${currentStage.title}」。`
                : `系统正在从「${currentStage.title}」开始自动搭建这个数字家人的业务流。`;

            return {
                current_stage_code: currentStage.code,
                current_stage_title: currentStage.title,
                workflow_steps: steps,
                next_actions: nextActions.slice(0, 3),
                workflow_summary: workflowSummary,
                recommended_focus: nextActions[0]?.title || currentStage.title,
                model_readiness: {
                    text_ready: memoryCount > 0 && signalCount >= 2,
                    voice_ready: availableModes.includes("voice"),
                    video_ready: availableModes.includes("video")
                }
            };
        }

        function buildClientIdentitySummary(lovedOne, twin) {
            const traits = lovedOne.personality_traits || {};
            const identityBits = [`${lovedOne.name || "ta"}是用户的${lovedOne.relationship || "亲人"}`];
            if (lovedOne.speaking_style) {
                identityBits.push(`说话方式偏“${lovedOne.speaking_style}”`);
            }
            if (Object.keys(traits).length) {
                identityBits.push(`性格线索：${Object.entries(traits).slice(0, 3).map(([key, value]) => `${key}：${value}`).join("；")}`);
            }

            const parts = [`人物底稿：${identityBits.join("，")}`];
            if ((lovedOne.memories || []).length) {
                parts.push(`关键回忆：${lovedOne.memories.slice(-3).join("；")}`);
            }
            if (twin?.workflow_summary) {
                parts.push(`自动流程：${twin.workflow_summary}`);
            }
            if (twin?.current_stage_title) {
                parts.push(`当前阶段：${twin.current_stage_title}；当前可用陪伴模式：${formatAvailableModes(twin.available_modes || ["text"])}`);
            }
            return parts.join("\n");
        }

        function buildClientTwinProfile(lovedOne) {
            const memoryCount = (lovedOne.memories || []).filter((item) => String(item || "").trim()).length;
            const voiceCount = (lovedOne.voice_sample_paths || []).length;
            const photoCount = (lovedOne.photo_paths || []).length;
            const videoCount = (lovedOne.video_paths || []).length;
            const model3dCount = (lovedOne.model3d_paths || []).length;
            const coverage = [memoryCount, voiceCount, photoCount + videoCount + model3dCount].filter((count) => count > 0).length;
            const profileSignalCount = [
                lovedOne.name,
                lovedOne.relationship,
                lovedOne.speaking_style,
                Object.keys(lovedOne.personality_traits || {}).length ? "traits" : ""
            ].filter(Boolean).length;
            const coverageScore = (coverage / 3) * 0.55;
            const depthScore =
                (Math.min(memoryCount, 8) / 8) * 0.15 +
                (Math.min(voiceCount, 3) / 3) * 0.12 +
                (Math.min(photoCount, 4) / 4) * 0.08 +
                (Math.min(videoCount, 2) / 2) * 0.06 +
                (Math.min(model3dCount, 2) / 2) * 0.05 +
                (profileSignalCount / 4) * 0.04;
            const completionPercent = Math.round((coverageScore + depthScore) * 100);
            const availableModes = ["text"];
            if (voiceCount > 0) {
                availableModes.push("voice");
            }
            if (voiceCount > 0 && (photoCount > 0 || videoCount > 0)) {
                availableModes.push("video");
            }
            const workflow = buildClientTwinWorkflow({
                memoryCount,
                voiceCount,
                photoCount,
                videoCount: videoCount + model3dCount,
                signalCount: profileSignalCount,
                availableModes
            });

            if (coverage === 0) {
                return {
                    memory_count: memoryCount,
                    voice_count: voiceCount,
                    photo_count: photoCount,
                    video_count: videoCount,
                    model3d_count: model3dCount,
                    has_memory: false,
                    has_voice: false,
                    has_photo: false,
                    has_video: false,
                    has_model3d: false,
                    coverage,
                    completion_percent: completionPercent,
                    completeness_label: "待补充分身素材",
                    summary: "先留下几段文字记忆，再补充语音、照片和视频，数字分身才会逐渐像 ta。",
                    available_modes: availableModes,
                    ...workflow
                };
            }

            if (completionPercent < 55) {
                return {
                    memory_count: memoryCount,
                    voice_count: voiceCount,
                    photo_count: photoCount,
                    video_count: videoCount,
                    model3d_count: model3dCount,
                    has_memory: memoryCount > 0,
                    has_voice: voiceCount > 0,
                    has_photo: photoCount > 0,
                    has_video: videoCount > 0,
                    has_model3d: model3dCount > 0,
                    coverage,
                    completion_percent: completionPercent,
                    completeness_label: "分身轮廓已开始成形",
                    summary: "已经留住了一部分辨识度，继续补充回忆、声音和影像，这个分身会更接近 ta。",
                    available_modes: availableModes,
                    ...workflow
                };
            }

            if (completionPercent < 82) {
                return {
                    memory_count: memoryCount,
                    voice_count: voiceCount,
                    photo_count: photoCount,
                    video_count: videoCount,
                    model3d_count: model3dCount,
                    has_memory: memoryCount > 0,
                    has_voice: voiceCount > 0,
                    has_photo: photoCount > 0,
                    has_video: videoCount > 0,
                    has_model3d: model3dCount > 0,
                    coverage,
                    completion_percent: completionPercent,
                    completeness_label: "立体分身正在成形",
                    summary: "文字记忆、声音和影像已经开始互相校准，这个数字分身会越来越接近 ta。",
                    available_modes: availableModes,
                    ...workflow
                };
            }

            return {
                memory_count: memoryCount,
                voice_count: voiceCount,
                photo_count: photoCount,
                video_count: videoCount,
                model3d_count: model3dCount,
                has_memory: memoryCount > 0,
                has_voice: voiceCount > 0,
                has_photo: photoCount > 0,
                has_video: videoCount > 0,
                has_model3d: model3dCount > 0,
                coverage,
                completion_percent: completionPercent,
                completeness_label: "完整数字分身已就绪",
                summary: "文字、声音、照片和动态影像都已具备，这个数字分身已经有了更完整的在场感。",
                available_modes: availableModes,
                ...workflow
            };
        }

        function buildLocalDigitalHumanFragments(lovedOne) {
            const profile = lovedOne || demoProfile;
            const fragments = [];
            const traits = profile.personality_traits || {};
            fragments.push({
                id: `local-fragment-${profile.id}-identity`,
                source_type: "profile",
                source_id: profile.id,
                modality: "profile",
                fragment_kind: "identity_core",
                title: "身份关系",
                content: `${profile.name || "ta"}是用户的${profile.relationship || "亲人"}。`,
                weight: 5,
                created_at: new Date().toISOString()
            });
            if (profile.speaking_style) {
                fragments.push({
                    id: `local-fragment-${profile.id}-voice-style`,
                    source_type: "profile",
                    source_id: profile.id,
                    modality: "profile",
                    fragment_kind: "speaking_style",
                    title: "说话方式",
                    content: `ta的表达方式偏向：${profile.speaking_style}。`,
                    weight: 4.7,
                    created_at: new Date().toISOString()
                });
            }
            if (traits.catchphrase) {
                fragments.push({
                    id: `local-fragment-${profile.id}-catchphrase`,
                    source_type: "profile",
                    source_id: profile.id,
                    modality: "text",
                    fragment_kind: "trait_signal",
                    title: "口头禅",
                    content: `ta常会这样说：“${traits.catchphrase}”`,
                    weight: 4.8,
                    created_at: new Date().toISOString()
                });
            }
            (profile.memories || []).slice(0, 8).forEach((memory, index) => {
                fragments.push({
                    id: `local-fragment-${profile.id}-memory-${index}`,
                    source_type: "memory",
                    source_id: `local-memory-${index}`,
                    modality: "text",
                    fragment_kind: "memory_anchor",
                    title: `共同回忆 ${index + 1}`,
                    content: memory,
                    weight: Math.max(3.2, 4.8 - index * 0.2),
                    created_at: new Date().toISOString()
                });
            });
            (profile.voice_sample_paths || []).slice(0, 3).forEach((_, index) => {
                fragments.push({
                    id: `local-fragment-${profile.id}-voice-${index}`,
                    source_type: "voice",
                    source_id: `local-voice-${index}`,
                    modality: "audio",
                    fragment_kind: "voice_trait",
                    title: `语音样本 ${index + 1}`,
                    content: "已上传语音样本，声音的停顿、语速和安慰感会继续被提炼。",
                    weight: 4.3,
                    created_at: new Date().toISOString()
                });
            });
            (profile.photo_paths || []).slice(0, 4).forEach((_, index) => {
                fragments.push({
                    id: `local-fragment-${profile.id}-photo-${index}`,
                    source_type: "photo",
                    source_id: `local-photo-${index}`,
                    modality: "image",
                    fragment_kind: "visual_trait",
                    title: `照片素材 ${index + 1}`,
                    content: "已上传照片素材，面容、神情和熟悉气质会继续被提炼。",
                    weight: 3.9,
                    created_at: new Date().toISOString()
                });
            });
            (profile.video_paths || []).slice(0, 2).forEach((_, index) => {
                fragments.push({
                    id: `local-fragment-${profile.id}-video-${index}`,
                    source_type: "video",
                    source_id: `local-video-${index}`,
                    modality: "video",
                    fragment_kind: "motion_trait",
                    title: `视频素材 ${index + 1}`,
                    content: "已上传视频素材，动作节奏、眼神和在场感会继续被提炼。",
                    weight: 4.1,
                    created_at: new Date().toISOString()
                });
            });
            (profile.model3d_paths || []).slice(0, 2).forEach((_, index) => {
                fragments.push({
                    id: `local-fragment-${profile.id}-model3d-${index}`,
                    source_type: "model3d",
                    source_id: `local-model3d-${index}`,
                    modality: "spatial",
                    fragment_kind: "reconstruction_trait",
                    title: `3D 重建 ${index + 1}`,
                    content: "已上传真人 3D 重建素材，立体外观与空间形态会继续被提炼。",
                    weight: 4.5,
                    created_at: new Date().toISOString()
                });
            });
            return fragments;
        }

        function buildLocalDigitalHumanModel(lovedOne) {
            const profile = lovedOne || demoProfile;
            const twin = profile.digital_twin_profile || buildClientTwinProfile(profile);
            const fragments = buildLocalDigitalHumanFragments(profile);
            const identitySummary = profile.identity_model_summary || buildClientIdentitySummary(profile, twin);
            const traits = profile.personality_traits || {};
            const personaTraits = Object.entries(profile.personality_traits || {}).map(([key, value]) => `${key}：${value}`);
            return {
                loved_one_id: profile.id,
                build_status: "ready",
                build_version: 1,
                source_stats: {
                    memory_count: twin.memory_count || 0,
                    voice_count: twin.voice_count || 0,
                    photo_count: twin.photo_count || 0,
                    video_count: twin.video_count || 0,
                    model3d_count: twin.model3d_count || 0,
                    fragment_count: fragments.length,
                    available_modes: twin.available_modes || ["text"],
                    completion_percent: twin.completion_percent || 0
                },
                persona_profile: {
                    name: profile.name || "ta",
                    relationship: profile.relationship || "亲人",
                    speaking_style: profile.speaking_style || "自然亲切",
                    traits: profile.personality_traits || {},
                    core_identity: [
                        `${profile.name || "ta"}是用户的${profile.relationship || "亲人"}`,
                        profile.speaking_style ? `说话方式偏“${profile.speaking_style}”` : "",
                        ...personaTraits.slice(0, 2)
                    ].filter(Boolean)
                },
                relationship_profile: {
                    bond: `用户的${profile.relationship || "亲人"}`,
                    shared_memory_anchors: (profile.memories || []).slice(0, 4),
                    support_style: profile.speaking_style || "温柔亲切",
                    presence_goal: "像家人一样自然主动联系，而不是像机器人回答问题。"
                },
                voice_profile: {
                    ready: Boolean(twin.has_voice),
                    sample_count: twin.voice_count || 0,
                    traits: [
                        profile.speaking_style ? `说话方式偏“${profile.speaking_style}”` : "",
                        traits.catchphrase ? `常说：“${traits.catchphrase}”` : "",
                        twin.voice_count ? "语音样本已经开始校准停顿与安慰感。" : ""
                    ].filter(Boolean),
                    call_ready: (twin.available_modes || []).includes("voice")
                },
                visual_profile: {
                    ready: Boolean(twin.has_photo || twin.has_video),
                    photo_count: twin.photo_count || 0,
                    video_count: twin.video_count || 0,
                    model3d_count: twin.model3d_count || 0,
                    reconstruction_ready: Boolean(twin.has_model3d),
                    reconstruction_stage: twin.has_model3d ? "integrated" : "missing",
                    reconstruction_label: twin.has_model3d ? "已并入模型" : "未上传",
                    appearance_traits: [
                        twin.photo_count ? "照片正在帮助稳定熟悉的面容与神情。" : "",
                        twin.video_count ? "视频正在帮助提炼动作节奏和在场感。" : "",
                        twin.model3d_count ? "3D 重建正在帮助稳定立体轮廓与空间形态。" : ""
                    ].filter(Boolean)
                },
                behavior_profile: {
                    interaction_modes: twin.available_modes || ["text"],
                    recommended_focus: twin.recommended_focus || "继续补素材",
                    workflow_summary: twin.workflow_summary || "",
                    care_habits: (profile.memories || []).slice(0, 3)
                },
                timeline_profile: {
                    birth_date: profile.birth_date || "",
                    pass_away_date: profile.pass_away_date || "",
                    memory_dates: [],
                    latest_material_at: null
                },
                build_notes: identitySummary,
                prompt_blueprint: identitySummary,
                knowledge_count: fragments.length,
                fragments_preview: fragments.slice(0, 8),
                last_built_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            };
        }

        function normalizeLovedOne(lovedOne) {
            const profile = lovedOne ? { ...lovedOne } : { ...demoProfile };
            const voicePaths = Array.isArray(profile.voice_sample_paths) ? [...profile.voice_sample_paths] : [];
            if (profile.voice_sample_path && !voicePaths.includes(profile.voice_sample_path)) {
                voicePaths.unshift(profile.voice_sample_path);
            }

            profile.personality_traits = profile.personality_traits || {};
            profile.cover_title = String(profile.cover_title || "").trim();
            profile.cover_photo_asset_id = profile.cover_photo_asset_id || null;
            profile.memories = Array.isArray(profile.memories)
                ? profile.memories.map((item) => String(item || "").trim()).filter(Boolean)
                : [];
            profile.voice_sample_paths = voicePaths.filter(Boolean);
            profile.voice_sample_urls = Array.isArray(profile.voice_sample_urls) ? profile.voice_sample_urls : [];
            profile.photo_paths = Array.isArray(profile.photo_paths) ? profile.photo_paths : [];
            profile.photo_urls = Array.isArray(profile.photo_urls) ? profile.photo_urls : [];
            profile.cover_photo_url = profile.cover_photo_url || profile.photo_urls[0] || "";
            profile.video_paths = Array.isArray(profile.video_paths) ? profile.video_paths : [];
            profile.video_urls = Array.isArray(profile.video_urls) ? profile.video_urls : [];
            profile.model3d_paths = Array.isArray(profile.model3d_paths) ? profile.model3d_paths : [];
            profile.model3d_urls = Array.isArray(profile.model3d_urls) ? profile.model3d_urls : [];
            profile.digital_twin_profile =
                profile.digital_twin_profile && Object.keys(profile.digital_twin_profile).length
                    ? profile.digital_twin_profile
                    : buildClientTwinProfile(profile);
            profile.identity_model_summary =
                profile.identity_model_summary || buildClientIdentitySummary(profile, profile.digital_twin_profile);
            profile.digital_human_model =
                profile.digital_human_model && Object.keys(profile.digital_human_model).length
                    ? profile.digital_human_model
                    : buildLocalDigitalHumanModel(profile);
            return profile;
        }

        function defaultCoverTitle(profile) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            return `写给${current.name || "ta"}的一页家书`;
        }

        function resolveCoverPhotoUrl(profile) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            return current.cover_photo_url || current.photo_urls?.[0] || "";
        }

        function syncLovedOneDirectoryProfile(nextProfile) {
            const profile = normalizeLovedOne(nextProfile);
            if (!lovedOneDirectory.length) {
                lovedOneDirectory = [profile];
                return;
            }
            let replaced = false;
            lovedOneDirectory = lovedOneDirectory.map((item) => {
                if (item.id === profile.id) {
                    replaced = true;
                    return profile;
                }
                return item;
            });
            if (!replaced) {
                lovedOneDirectory.unshift(profile);
            }
        }

        function resolveCoverSelection(profile, requestedAssetId) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            const photoAssets = activeMediaAssets.filter((asset) => asset.kind === "photo");
            const nextAssetId = requestedAssetId === undefined ? current.cover_photo_asset_id : (requestedAssetId || null);
            if (nextAssetId) {
                const selected = photoAssets.find((asset) => asset.id === nextAssetId);
                if (selected) {
                    return {
                        cover_photo_asset_id: selected.id,
                        cover_photo_url: resolveMediaUrl(selected.url),
                    };
                }
            }
            const fallbackAsset = photoAssets[0];
            if (fallbackAsset) {
                return {
                    cover_photo_asset_id: nextAssetId || fallbackAsset.id,
                    cover_photo_url: resolveMediaUrl(fallbackAsset.url),
                };
            }
            return {
                cover_photo_asset_id: nextAssetId,
                cover_photo_url: current.cover_photo_url || current.photo_urls?.[0] || "",
            };
        }

        function isCoverAsset(profile, asset) {
            if (!asset || asset.kind !== "photo") {
                return false;
            }
            return resolveCoverSelection(profile).cover_photo_asset_id === asset.id;
        }

        function renderCoverSheet(profile = activeLovedOne) {
            const current = normalizeLovedOne(profile || demoProfile);
            const coverUrl = resolveCoverPhotoUrl(current);
            const effectiveTitle = current.cover_title || defaultCoverTitle(current);
            const hasCoverPhoto = Boolean(coverUrl);
            const photoPreview = document.getElementById("coverPhotoPreview");
            const photoPlaceholder = document.getElementById("coverPhotoPlaceholder");
            const titleDisplay = document.getElementById("coverSheetTitleDisplay");
            const titleInput = document.getElementById("coverTitleInput");
            const meta = document.getElementById("coverSheetMeta");
            const badge = document.getElementById("coverSheetBadge");
            const status = document.getElementById("coverSheetStatus");

            if (!photoPreview || !photoPlaceholder || !titleDisplay || !titleInput || !meta || !badge || !status) {
                return;
            }

            titleDisplay.textContent = effectiveTitle;
            titleInput.value = current.cover_title || "";
            badge.textContent = hasCoverPhoto ? "已设封面" : "待补照片";
            meta.textContent = hasCoverPhoto
                ? "封面照片与题字会同步显示在档案目录和追思册首页。"
                : "先上传一张最能代表 ta 的照片，它会自动成为这位亲人的纪念封面。";
            status.textContent = hasCoverPhoto
                ? "可以在下方相册墙继续切换封面照片，题字会随档案一起长期保存。"
                : "现在可以先写下题字；等你上传照片后，这一页会自动变成真正的封面。";

            if (hasCoverPhoto) {
                photoPreview.src = resolveMediaUrl(coverUrl);
                photoPreview.style.display = "block";
                photoPlaceholder.style.display = "none";
            } else {
                photoPreview.removeAttribute("src");
                photoPreview.style.display = "none";
                photoPlaceholder.style.display = "grid";
                photoPlaceholder.textContent = `还没有上传 ${current.name || "ta"} 的封面照片。先在下方“家庭相册墙”选一张最能代表 ta 的照片，这里就会成为这位亲人的纪念首页。`;
            }
        }

        function renderTwinWorkflow(profile, twin) {
            const badge = document.getElementById("workflowBadge");
            const summary = document.getElementById("workflowSummary");
            const stepsContainer = document.getElementById("workflowSteps");
            const actionsContainer = document.getElementById("workflowActions");
            const focus = document.getElementById("workflowFocus");
            const identitySummary = document.getElementById("identitySummaryText");

            badge.textContent = twin.current_stage_title || "准备中";
            summary.textContent = twin.workflow_summary || twin.summary || "系统会根据素材自动推进分身构建。";
            focus.textContent = twin.recommended_focus || "继续补素材";
            identitySummary.textContent = profile.identity_model_summary || buildClientIdentitySummary(profile, twin);

            stepsContainer.innerHTML = "";
            (twin.workflow_steps || []).forEach((step) => {
                const item = document.createElement("div");
                item.className = `workflow-step ${step.status || "pending"}`;

                const top = document.createElement("div");
                top.className = "workflow-step-top";

                const title = document.createElement("strong");
                title.textContent = step.title || "阶段";

                const meta = document.createElement("span");
                meta.className = "entry-badge";
                meta.textContent = `${step.current || 0}/${step.target || 0}`;

                const detail = document.createElement("div");
                detail.className = "workflow-step-meta";
                detail.textContent = step.detail || "";

                const progress = document.createElement("div");
                progress.className = "workflow-progress";

                const bar = document.createElement("span");
                bar.style.width = `${Math.max(0, Math.min(100, step.progress_percent || 0))}%`;
                progress.appendChild(bar);

                top.append(title, meta);
                item.append(top, detail, progress);
                stepsContainer.appendChild(item);
            });

            actionsContainer.innerHTML = "";
            (twin.next_actions || []).forEach((action) => {
                const item = document.createElement("div");
                item.className = "workflow-action";

                const title = document.createElement("strong");
                title.textContent = action.title || "下一步";

                const detail = document.createElement("span");
                detail.textContent = `${action.detail || ""}${action.cta_label ? ` 当前建议：${action.cta_label}` : ""}`;

                item.append(title, detail);
                actionsContainer.appendChild(item);
            });
        }

        function updateTwinPanel(lovedOne) {
            const profile = normalizeLovedOne(lovedOne);
            const twin = profile.digital_twin_profile || buildClientTwinProfile(profile);
            document.getElementById("memoryCount").textContent = twin.memory_count || 0;
            document.getElementById("voiceCount").textContent = twin.voice_count || 0;
            document.getElementById("photoCount").textContent = twin.photo_count || 0;
            document.getElementById("videoCount").textContent = twin.video_count || 0;
            document.getElementById("twinStatusTitle").textContent = twin.completeness_label || "待补充分身素材";
            document.getElementById("twinStatusText").textContent =
                twin.summary
                    ? `${twin.summary} 当前建模完整度约 ${twin.completion_percent || 0}%。当前正在推进「${twin.current_stage_title || "分身构建"}」。`
                    : "继续补充文字、语音和影像，这个数字人会更接近 ta。";
            renderTwinWorkflow(profile, twin);

            const photoPreview = document.getElementById("photoPreview");
            const photoPlaceholder = document.getElementById("photoPlaceholder");
            const photoUrl = profile.photo_urls?.[0];
            if (photoUrl) {
                photoPreview.src = photoUrl;
                photoPreview.style.display = "block";
                photoPlaceholder.style.display = "none";
            } else {
                photoPreview.removeAttribute("src");
                photoPreview.style.display = "none";
                photoPlaceholder.style.display = "grid";
            }

            const videoPreview = document.getElementById("videoPreview");
            const videoPlaceholder = document.getElementById("videoPlaceholder");
            const videoUrl = profile.video_urls?.[0];
            if (videoUrl) {
                videoPreview.src = videoUrl;
                videoPreview.style.display = "block";
                videoPreview.load();
                videoPlaceholder.style.display = "none";
            } else {
                videoPreview.pause();
                videoPreview.removeAttribute("src");
                videoPreview.load();
                videoPreview.style.display = "none";
                videoPlaceholder.style.display = "grid";
            }
        }

        function buildTwinStatusLine(profile) {
            const twin = profile.digital_twin_profile || buildClientTwinProfile(profile);
            return isEnglish()
                ? `Collected ${twin.memory_count || 0} memories, ${twin.voice_count || 0} voice clips, ${twin.photo_count || 0} photos, and ${twin.video_count || 0} videos. Current build readiness: ${twin.completion_percent || 0}%.`
                : `已收集 ${twin.memory_count || 0} 条回忆 / ${twin.voice_count || 0} 段语音 / ${twin.photo_count || 0} 张照片 / ${twin.video_count || 0} 段视频，系统当前推进到「${twin.current_stage_title || "分身构建"}」。`;
        }

        function setDigitalHumanPills(containerId, values, emptyText) {
            const container = document.getElementById(containerId);
            if (!container) {
                return;
            }
            container.innerHTML = "";
            const items = (values || []).filter((item) => String(item || "").trim());
            if (!items.length) {
                const empty = document.createElement("div");
                empty.className = "dh-pill empty";
                empty.textContent = emptyText;
                container.appendChild(empty);
                return;
            }
            items.forEach((value) => {
                const pill = document.createElement("div");
                pill.className = "dh-pill";
                pill.textContent = value;
                container.appendChild(pill);
            });
        }

        function formatDigitalHumanFragmentLabel(fragment) {
            const sourceLabels = {
                profile: pickCopy("档案底稿", "Profile base"),
                memory: pickCopy("文字回忆", "Text memory"),
                voice: pickCopy("语音素材", "Voice asset"),
                photo: pickCopy("照片素材", "Photo asset"),
                video: pickCopy("视频素材", "Video asset")
            };
            return sourceLabels[fragment.source_type] || fragment.source_type || pickCopy("片段", "Fragment");
        }

        function buildLocalBridgeStatus(profile) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            const model = current.digital_human_model || buildLocalDigitalHumanModel(current);
            const flow = activeProactiveSettings || {
                preferred_channel: "app",
                phone_number: ""
            };
            const wantsPhone = flow.preferred_channel === "phone";
            const blockers = [];
            if (wantsPhone) {
                blockers.push("还没有接通电话桥接服务");
            }
            if (wantsPhone && !flow.phone_number) {
                blockers.push("还没有填写接听手机号");
            }
            if (wantsPhone && !model.voice_profile?.call_ready) {
                blockers.push("当前语音素材还不足以支撑电话通话");
            }
            return {
                provider: "none",
                provider_label: "尚未配置电话桥接",
                configured: false,
                direct_call_enabled: false,
                preferred_channel: flow.preferred_channel || "app",
                phone_number_configured: Boolean(flow.phone_number),
                voice_ready: Boolean(model.voice_profile?.call_ready),
                digital_human_ready: model.build_status === "ready",
                call_ready: false,
                blockers,
                readiness_note: wantsPhone
                    ? (blockers.join("；") || "电话外呼仍在准备中。")
                    : "当前默认仍以站内主动问候为主，切到电话优先后会开始校验外呼条件。"
            };
        }

        function renderDigitalHumanFragments(fragments = []) {
            const container = document.getElementById("dhFragmentList");
            const badge = document.getElementById("dhFragmentMeta");
            badge.textContent = `${fragments.length} 条`;
            container.innerHTML = "";

            if (!fragments.length) {
                container.innerHTML = '<div class="dh-empty">还没有可视化片段。继续上传回忆、语音、照片和视频后，这里会逐步沉淀出这个人的人物底稿。</div>';
                return;
            }

            fragments.forEach((fragment, index) => {
                const card = document.createElement("div");
                const isMemoryNote = fragment.fragment_kind === "memory_anchor" || fragment.source_type === "memory";
                card.className = `dh-fragment${isMemoryNote ? ` handwritten-note note-tilt-${index % 4}` : ""}`;

                const top = document.createElement("div");
                top.className = "dh-fragment-top";

                const title = document.createElement("strong");
                title.textContent = fragment.title || "片段";

                const weight = document.createElement("span");
                weight.className = "entry-badge";
                weight.textContent = `权重 ${Number(fragment.weight || 0).toFixed(1)}`;

                const meta = document.createElement("div");
                meta.className = "dh-fragment-meta";
                meta.textContent = `${formatDigitalHumanFragmentLabel(fragment)} · ${fragment.modality || "text"} · ${formatTimeLabel(fragment.created_at)}`;

                const body = document.createElement("p");
                body.textContent = fragment.content || "这个片段还没有可展示内容。";

                top.append(title, weight);
                card.append(top, meta, body);
                container.appendChild(card);
            });
        }

        function renderDigitalHumanBuildRuns(builds = []) {
            const container = document.getElementById("dhBuildRunList");
            const badge = document.getElementById("dhBuildRunMeta");
            if (!container || !badge) {
                return;
            }
            badge.textContent = `${builds.length} 条`;
            container.innerHTML = "";
            if (!builds.length) {
                container.innerHTML = '<div class="dh-empty">还没有构建记录。</div>';
                return;
            }
            builds.forEach((run) => {
                const card = document.createElement("div");
                card.className = "build-run-item";
                const title = document.createElement("strong");
                title.textContent = `${run.trigger_source || "system"} · ${run.status || "unknown"}`;
                const detail = document.createElement("div");
                detail.className = "status-detail";
                detail.textContent = run.created_at ? `开始于 ${formatTimeLabel(run.created_at)}` : "刚刚";
                const note = document.createElement("p");
                note.className = "asset-summary";
                note.textContent = run.notes || "模型构建中。";
                card.append(title, detail, note);
                container.appendChild(card);
            });
        }

        function buildLocalDigitalHumanHistory(profile) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            const history = Array.isArray(current.local_chat_history) ? current.local_chat_history : [];
            return history
                .filter((entry) => entry.response_audio_url || entry.response_video_url)
                .slice()
                .reverse()
                .map((entry, index) => ({
                    id: `local-history-${index}`,
                    source: "conversation",
                    source_label: "对话陪伴",
                    mode: entry.mode || "text",
                    title: "本地陪伴演示",
                    prompt_text: entry.user_message,
                    response_text: entry.ai_response,
                    audio_url: entry.response_audio_url || "",
                    video_url: entry.response_video_url || "",
                    created_at: entry.timestamp || new Date().toISOString(),
                    metadata: {},
                }));
        }

        function renderDigitalHumanHistory(entries = []) {
            const container = document.getElementById("dhHistoryList");
            const badge = document.getElementById("dhHistoryMeta");
            if (!container || !badge) {
                return;
            }
            badge.textContent = `${entries.length} 条`;
            container.innerHTML = "";
            if (!entries.length) {
                container.innerHTML = '<div class="dh-empty">每次由 Mimo 生成的语音和视频陪伴，都会在这里沉淀成可回看的纪念记录。</div>';
                return;
            }

            entries.forEach((entry) => {
                const card = document.createElement("div");
                card.className = "dh-history-item";

                const top = document.createElement("div");
                top.className = "entry-meta-row";

                const badge = document.createElement("span");
                badge.className = "entry-badge";
                badge.textContent = formatCompanionHistoryLabel(entry);

                const time = document.createElement("span");
                time.className = "status-detail";
                time.textContent = formatTimeLabel(entry.created_at);

                const title = document.createElement("strong");
                title.textContent = entry.title || entry.source_label || "Mimo 陪伴";

                top.append(badge, time);
                card.append(top, title);

                if (entry.prompt_text) {
                    const prompt = document.createElement("div");
                    prompt.className = "dh-history-prompt";
                    prompt.textContent = `你的触发：${entry.prompt_text}`;
                    card.append(prompt);
                }

                const body = document.createElement("p");
                body.textContent = entry.response_text || "这次陪伴没有留下文字内容。";
                card.append(body);

                const media = document.createElement("div");
                media.className = "dh-history-media";
                if (entry.video_url) {
                    const video = document.createElement("video");
                    video.controls = true;
                    video.preload = "metadata";
                    video.playsInline = true;
                    video.src = resolveMediaUrl(entry.video_url);
                    media.append(video);
                } else if (entry.audio_url) {
                    const audio = document.createElement("audio");
                    audio.controls = true;
                    audio.preload = "none";
                    audio.src = resolveMediaUrl(entry.audio_url);
                    media.append(audio);
                }
                if (media.children.length) {
                    card.append(media);
                }

                const detail = document.createElement("div");
                detail.className = "status-detail";
                detail.textContent =
                    entry.source === "proactive"
                        ? (entry.metadata?.provider_note || "这次内容来自数字人的主动联系链路。")
                        : `${entry.source_label || "对话陪伴"} · ${formatCompanionHistoryLabel(entry)}`;
                card.append(detail);
                container.append(card);
            });
        }

        function renderDigitalHumanConsole(profile, payload = {}) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            const model =
                payload.model ||
                (current.digital_human_model && Object.keys(current.digital_human_model).length
                    ? current.digital_human_model
                    : buildLocalDigitalHumanModel(current));
            const fragments =
                (Array.isArray(payload.fragments) && payload.fragments.length ? payload.fragments : null) ||
                (Array.isArray(model.fragments_preview) && model.fragments_preview.length ? model.fragments_preview : null) ||
                buildLocalDigitalHumanFragments(current);
            const bridge = payload.bridge || activeCallBridgeStatus || buildLocalBridgeStatus(current);
            const builds = Array.isArray(payload.builds) ? payload.builds : activeDigitalHumanBuilds;
            const history = Array.isArray(payload.history) ? payload.history : activeDigitalHumanHistory;
            const persona = model.persona_profile || {};
            const relationship = model.relationship_profile || {};
            const voice = model.voice_profile || {};
            const visual = model.visual_profile || {};
            const behavior = model.behavior_profile || {};
            const sourceStats = model.source_stats || {};
            const model3dCount =
                visual.model3d_count ||
                sourceStats.model3d_count ||
                current.digital_twin_profile?.model3d_count ||
                0;
            const model3dAssets = activeMediaAssets.filter((asset) => asset.kind === "model3d");
            const isDemo = !serviceOnline || !currentUser || isLocalProfile(current);
            const modes = sourceStats.available_modes || current.digital_twin_profile?.available_modes || ["text"];

            activeDigitalHumanModel = model;
            activeDigitalHumanFragments = fragments;
            activeDigitalHumanBuilds = builds;
            activeDigitalHumanHistory = history;
            activeCallBridgeStatus = bridge;

            document.getElementById("digitalHumanMeta").textContent = `${model.build_status === "ready" ? "模型已就绪" : (model.build_status || "准备中")} · v${model.build_version || 1}`;
            document.getElementById("digitalHumanHint").textContent =
                model.build_notes || current.identity_model_summary || "系统会根据已有素材自动搭建这位亲人的数字人模型。";
            document.getElementById("dhMetricKnowledge").textContent = model.knowledge_count || fragments.length || 0;
            document.getElementById("dhMetricBuildVersion").textContent = `v${model.build_version || 1}`;
            document.getElementById("dhMetricModes").textContent = formatAvailableModes(modes);
            document.getElementById("dhMetricCallReady").textContent = bridge.call_ready ? "可外呼" : (bridge.configured ? "待补齐" : "未接通");

            document.getElementById("dhPersonaMeta").textContent = persona.relationship || current.relationship || "人物底稿";
            document.getElementById("dhVoiceMeta").textContent = voice.ready ? `${voice.sample_count || 0} 段样本` : "待补充";
            document.getElementById("dhVisualMeta").textContent =
                visual.ready || visual.reconstruction_ready
                    ? `${visual.photo_count || 0} 图 / ${visual.video_count || 0} 视频 / ${model3dCount} 份 3D`
                    : "待补充";
            document.getElementById("dhBridgeMeta").textContent = bridge.provider_label || "未接通";
            document.getElementById("dhModel3dMeta").textContent = `${model3dCount} 份`;

            setDigitalHumanPills(
                "dhPersonaCore",
                persona.core_identity || [
                    `${current.name || "ta"}是用户的${current.relationship || "亲人"}`,
                    current.speaking_style ? `说话方式偏“${current.speaking_style}”` : ""
                ],
                "当前还没有足够的人格线索。"
            );
            document.getElementById("dhRelationshipAnchors").textContent =
                (relationship.shared_memory_anchors || current.memories || []).slice(0, 4).join("\n") ||
                "还没有足够的共同回忆。先补几段最具体、最日常的生活片段，数字人会更快像 ta。";
            setDigitalHumanPills("dhVoiceTraits", voice.traits || [], "当前还没有足够的声音画像。");
            setDigitalHumanPills("dhVisualTraits", visual.appearance_traits || [], "当前还没有足够的视觉画像。");

            document.getElementById("dhVoiceStatus").textContent = voice.ready
                ? `已具备 ${voice.sample_count || 0} 段声音样本，当前${voice.call_ready ? "可以直接驱动电话通话" : "仍在等待套餐或模式开放"}。`
                : "先补至少两段清晰语音，系统才更容易稳定说话节奏、停顿和安慰感。";
            document.getElementById("dhVisualStatus").textContent = visual.ready || visual.reconstruction_ready
                ? `照片 ${visual.photo_count || 0} 张 / 视频 ${visual.video_count || 0} 段 / 3D 重建 ${model3dCount} 份，当前视觉、动态和立体空间线索已经开始共同参与建模。`
                : "先补正脸照、日常照、一段短视频或一份真人 3D 重建，视觉在场感才会逐渐立起来。";
            const stageLabel = visual.reconstruction_label || formatModel3dStage(visual.reconstruction_stage || "");
            document.getElementById("dhModel3dStatus").textContent = model3dCount
                ? `当前已接入 ${model3dCount} 份真人 3D 重建素材，阶段：${stageLabel}。立体轮廓与空间形态正在稳定。`
                : "上传真人 3D 重建后，数字人会开始拥有更稳定的立体外观底稿。";

            document.getElementById("dhBridgeNote").textContent =
                bridge.readiness_note ||
                "接通电话桥接后，数字人会直接按这套模型主动拨打电话。";
            const blockerList = document.getElementById("dhBridgeBlockers");
            blockerList.innerHTML = "";
            (bridge.blockers || []).forEach((item) => {
                const li = document.createElement("li");
                li.textContent = item;
                blockerList.appendChild(li);
            });
            if (!blockerList.children.length) {
                const li = document.createElement("li");
                li.textContent = bridge.call_ready
                    ? "当前已经满足主动外呼条件，下一次主动联系会直接以电话方式触达。"
                    : "当前还未切到电话优先，主动联系会先以站内问候出现。";
                blockerList.appendChild(li);
            }

            document.getElementById("dhBuildNotes").textContent =
                model.build_notes ||
                behavior.workflow_summary ||
                current.identity_model_summary ||
                "系统会把上传的记忆、声音、照片和视频自动编织成可持续更新的数字人模型。";

            const rebuildButton = document.getElementById("digitalHumanRebuildButton");
            rebuildButton.disabled = isDemo;
            rebuildButton.textContent = isDemo ? "登录后可重建模型" : "重新构建模型";

            const model3dList = document.getElementById("dhModel3dList");
            model3dList.innerHTML = "";
            if (model3dAssets.length) {
                model3dAssets.forEach((asset) => {
                    const card = document.createElement("article");
                    card.className = "dh-model3d-card";

                    const title = document.createElement("strong");
                    title.textContent = asset.original_filename || "未命名 3D 重建";

                    const meta = document.createElement("div");
                    meta.className = "status-detail";
                    meta.textContent = asset.created_at
                        ? `上传于 ${formatTimeLabel(asset.created_at)}`
                        : "本地演示 3D 素材";

                    const preview = document.createElement("div");
                    preview.className = "dh-model3d-preview";
                    renderModel3dPreview(preview, asset, true);

                    const summary = document.createElement("p");
                    summary.className = "asset-summary";
                    summary.textContent = asset.summary || "这份真人 3D 重建素材已经进入数字人的立体形态建模。";

                    card.append(title, meta, preview, summary);
                    model3dList.append(card);
                });
            } else {
                model3dList.innerHTML = '<div class="workbench-empty">这里会展示已经上传的真人 3D 重建文件。优先上传 `glb / gltf / usdz`，可以直接在线预览。</div>';
            }

            renderDigitalHumanFragments(fragments);
            renderDigitalHumanBuildRuns(builds || []);
            renderDigitalHumanHistory(history || []);
        }

        async function loadDigitalHumanConsole(profile = activeLovedOne) {
            const current = normalizeLovedOne(profile || demoProfile);
            if (!serviceOnline || !currentUser || isLocalProfile(current)) {
                renderDigitalHumanConsole(current, {
                    model: buildLocalDigitalHumanModel(current),
                    fragments: buildLocalDigitalHumanFragments(current),
                    bridge: buildLocalBridgeStatus(current),
                    builds: [],
                    history: buildLocalDigitalHumanHistory(current),
                });
                return;
            }

            try {
                const [modelResponse, fragmentsResponse, bridgeResponse, buildsResponse, historyResponse] = await Promise.all([
                    apiFetch(`/api/loved-ones/${current.id}/digital-human`),
                    apiFetch(`/api/loved-ones/${current.id}/digital-human/fragments?limit=24`),
                    apiFetch(`/api/bridge/status?loved_one_id=${encodeURIComponent(current.id)}`),
                    apiFetch(`/api/loved-ones/${current.id}/digital-human/builds?limit=6`),
                    apiFetch(`/api/loved-ones/${current.id}/digital-human/history?limit=12`)
                ]);
                if (!modelResponse.ok || !fragmentsResponse.ok || !bridgeResponse.ok || !buildsResponse.ok || !historyResponse.ok) {
                    throw new Error("digital human failed");
                }
                const model = await modelResponse.json();
                const fragmentsPayload = await fragmentsResponse.json();
                const bridge = await bridgeResponse.json();
                const buildsPayload = await buildsResponse.json();
                const historyPayload = await historyResponse.json();
                current.digital_human_model = model;
                if (activeLovedOne?.id === current.id) {
                    activeLovedOne = normalizeLovedOne({ ...activeLovedOne, digital_human_model: model });
                }
                lovedOneDirectory = lovedOneDirectory.map((item) =>
                    item.id === current.id ? normalizeLovedOne({ ...item, digital_human_model: model }) : item
                );
                renderDigitalHumanConsole(current, {
                    model,
                    fragments: fragmentsPayload.items || [],
                    bridge,
                    builds: buildsPayload.items || [],
                    history: historyPayload.items || [],
                });
            } catch (error) {
                renderDigitalHumanConsole(current, {
                    model: current.digital_human_model || buildLocalDigitalHumanModel(current),
                    fragments: buildLocalDigitalHumanFragments(current),
                    bridge: buildLocalBridgeStatus(current),
                    builds: [],
                    history: buildLocalDigitalHumanHistory(current),
                });
            }
        }

        async function rebuildDigitalHumanModel() {
            if (!requireAccount("请先登录后再重建数字人模型。")) {
                return;
            }
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!serviceOnline || isLocalProfile(profile)) {
                showToast("请先创建并保存真实档案，再重建数字人模型。", "error");
                return;
            }
            const button = document.getElementById("digitalHumanRebuildButton");
            setButtonLoading(button, true, "重建中...");
            try {
                const response = await apiFetch(`/api/loved-ones/${profile.id}/digital-human/rebuild`, {
                    method: "POST"
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "数字人模型重建失败");
                }
                await loadLovedOneDirectory();
                showToast("数字人模型已重新构建。", "success");
            } catch (error) {
                showToast(error.message || "数字人模型重建失败。", "error");
            } finally {
                setButtonLoading(button, false, "重新构建模型");
            }
        }

        async function uploadSelectedMedia(lovedOneId) {
            const queue = [
                ...getSelectedFiles("voiceFiles").map((file) => ({ type: "voice", file })),
                ...getSelectedFiles("photoFiles").map((file) => ({ type: "photo", file })),
                ...getSelectedFiles("videoFiles").map((file) => ({ type: "video", file }))
            ];

            let latestLovedOne = null;
            let uploadCount = 0;

            for (const item of queue) {
                const formData = new FormData();
                formData.append("file", item.file);

                const response = await apiFetch(`/api/loved-ones/${lovedOneId}/${item.type}`, {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.detail || `${item.type} upload failed`);
                }

                const data = await response.json();
                latestLovedOne = data.loved_one ? normalizeLovedOne(data.loved_one) : latestLovedOne;
                uploadCount += 1;
            }

            return { lovedOne: latestLovedOne, uploadCount };
        }

        function buildLocalDraftProfile(payload) {
            const voiceFiles = getSelectedFiles("voiceFiles");
            const photoFiles = getSelectedFiles("photoFiles");
            const videoFiles = getSelectedFiles("videoFiles");
            const photoUrls = photoFiles.map((file) => URL.createObjectURL(file));

            return normalizeLovedOne({
                ...payload,
                id: `local-${Date.now()}`,
                memories: payload.memories || [],
                local_chat_history: [],
                voice_sample_paths: voiceFiles.map((file) => file.name),
                voice_sample_urls: voiceFiles.map((file) => URL.createObjectURL(file)),
                photo_paths: photoFiles.map((file) => file.name),
                photo_urls: photoUrls,
                cover_photo_asset_id: photoUrls.length ? "local-photo-0" : null,
                cover_photo_url: photoUrls[0] || "",
                video_paths: videoFiles.map((file) => file.name),
                video_urls: videoFiles.map((file) => URL.createObjectURL(file))
            });
        }

        function isLocalProfile(profile) {
            return !profile || String(profile.id || "").startsWith("local-") || profile.id === demoProfile.id;
        }

        function formatTimeLabel(value) {
            if (!value) {
                return pickCopy("刚刚", "Just now");
            }
            const date = new Date(value);
            if (Number.isNaN(date.getTime())) {
                return pickCopy("刚刚", "Just now");
            }
            return date.toLocaleString(isEnglish() ? "en-US" : "zh-CN", {
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit"
            });
        }

        function getLocalizedPlanName(subscription = currentSubscription) {
            if (!subscription) {
                return pickCopy("体验版", "Preview");
            }
            const code = subscription.plan_code;
            return getPlanCopy(code)?.name || subscription.plan_name || pickCopy("体验版", "Preview");
        }

        function subscriptionCapabilityLabel(subscription = currentSubscription) {
            if (!subscription) {
                return pickCopy(
                    "未登录时仅展示本地演示，真实文字 / 语音 / 视频能力会在登录后绑定到套餐。",
                    "Without sign-in, only the local demo is shown. Real text, voice, and video abilities are bound after login."
                );
            }
            const features = subscription.features || {};
            const labels = [];
            if (features.text) {
                labels.push(pickCopy("文字陪伴", "Text companion"));
            }
            if (features.voice) {
                labels.push(pickCopy("语音电话", "Voice calls"));
            }
            if (features.video) {
                labels.push(pickCopy("视频陪伴", "Video companion"));
            }
            return pickCopy(
                `${getLocalizedPlanName(subscription)} 已开放：${labels.join(" / ") || "基础能力"}。`,
                `${getLocalizedPlanName(subscription)} includes: ${labels.join(" / ") || "Core access"}.`
            );
        }

        function formatWeekdayLabel(value) {
            const labels = isEnglish()
                ? ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                : ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
            const index = Number(value);
            return Number.isInteger(index) && index >= 0 && index < labels.length ? labels[index] : pickCopy("未指定", "Not set");
        }

        function formatCadenceLabel(flow) {
            if (!flow) {
                return pickCopy("未设置", "Not set");
            }
            if (flow.cadence === "weekly") {
                return isEnglish()
                    ? `Every ${formatWeekdayLabel(flow.preferred_weekday)} ${flow.preferred_time || "20:30"}`
                    : `每周 ${formatWeekdayLabel(flow.preferred_weekday)} ${flow.preferred_time || "20:30"}`;
            }
            return isEnglish()
                ? `Every day ${flow.preferred_time || "20:30"}`
                : `每天 ${flow.preferred_time || "20:30"}`;
        }

        function formatChannelLabel(channel, eventType = "") {
            if (channel === "phone" || eventType === "voice_call") {
                return pickCopy("电话联系", "Phone call");
            }
            if (eventType === "video_message") {
                return pickCopy("视频问候", "Video greeting");
            }
            if (eventType === "voice_message") {
                return pickCopy("语音问候", "Voice greeting");
            }
            return pickCopy("文字问候", "Text greeting");
        }

        function formatProactiveMessageModeLabel(mode) {
            if (mode === "video") {
                return pickCopy("视频消息", "Video message");
            }
            if (mode === "voice") {
                return pickCopy("语音消息", "Voice message");
            }
            return pickCopy("文字消息", "Text message");
        }

        function formatCompanionHistoryLabel(entry = {}) {
            if (entry.source === "proactive") {
                return formatChannelLabel("app", entry.mode);
            }
            if (entry.video_url) {
                return pickCopy("视频陪伴", "Video companion");
            }
            if (entry.audio_url) {
                return pickCopy("语音陪伴", "Voice companion");
            }
            return pickCopy("文字陪伴", "Text companion");
        }

        function setAuthMode(mode) {
            authMode = mode === "login" ? "login" : "register";
            document.getElementById("authTab-register").classList.toggle("active", authMode === "register");
            document.getElementById("authTab-login").classList.toggle("active", authMode === "login");
            document.getElementById("authDisplayNameGroup").classList.toggle("hidden", authMode === "login");
            document.getElementById("authTitle").textContent =
                authMode === "register"
                    ? pickCopy("先把纪念空间绑定到你的账号", "Bind this memorial space to your account first")
                    : pickCopy("登录后继续完善亲人的数字分身", "Sign in to continue building the digital twin");
            document.getElementById("authDescription").textContent =
                authMode === "register"
                    ? pickCopy(
                        "注册后，亲人档案、上传素材、聊天记录和套餐权限都会长期保存，不再依赖本地浏览器。",
                        "After registration, loved-one profiles, uploads, chat history, and plan access are stored long term instead of staying only in this browser."
                    )
                    : pickCopy(
                        "登录后，你之前保存的亲人档案、素材库和订阅权限都会重新接回到当前页面。",
                        "After sign-in, your saved loved-one profiles, media library, and subscription access are restored to this page."
                    );
            document.getElementById("authSubmitButton").textContent =
                authMode === "register" ? pickCopy("创建账号", "Create account") : pickCopy("立即登录", "Sign in");
        }

        function openAuthModal(mode = "register") {
            setAuthMode(mode);
            openModal("authModal");
            window.setTimeout(() => {
                const target = authMode === "register" ? document.getElementById("authDisplayName") : document.getElementById("authEmail");
                target?.focus();
            }, 80);
        }

        function updatePlanCards() {
            const currentPlanCode = currentSubscription?.plan_code || "";
            document.querySelectorAll(".price-card[data-plan-code]").forEach((card) => {
                const code = card.getAttribute("data-plan-code");
                const button = document.getElementById(`planButton-${code}`);
                const note = document.getElementById(`planNote-${code}`);
                const plan = planCatalog.find((item) => item.code === code);
                const copy = getPlanCopy(code);
                card.classList.toggle("current", currentPlanCode === code);
                if (!button || !plan) {
                    return;
                }

                if (currentPlanCode === code) {
                    button.textContent = copy?.currentButton || pickCopy("当前方案", "Current plan");
                    button.disabled = true;
                    if (note) {
                        note.textContent = copy?.currentNote || pickCopy(
                            "你当前正在使用这个套餐，这里的能力已经实时绑定到账号。",
                            "You are already using this plan and its abilities are bound to your account."
                        );
                    }
                    return;
                }

                button.disabled = false;
                button.textContent = currentUser
                    ? (copy?.authedButton || pickCopy("立即开通", "Activate now"))
                    : pickCopy("登录后开通", "Sign in to activate");
                if (note && !plan.checkout_enabled) {
                    note.textContent = `${copy?.note || plan.description} ${pickCopy(
                        "当前还没有配置正式支付密钥，可以先把权限和数据流接好。",
                        "Live payment keys are not configured yet, so access and data flow can be prepared first."
                    )}`;
                } else if (note) {
                    note.textContent = copy?.note || plan.description;
                }
            });
        }

        function updateAuthSurface() {
            const accountTitle = document.getElementById("accountTitle");
            const accountSubtitle = document.getElementById("accountSubtitle");
            const billingTitle = document.getElementById("billingTitle");
            const billingText = document.getElementById("billingText");
            const authActionButton = document.getElementById("authActionButton");
            const billingPrimaryButton = document.getElementById("billingPrimaryButton");
            const accountPortalButton = document.getElementById("accountPortalButton");
            const billingPortalButton = document.getElementById("billingPortalButton");
            const logoutActionButton = document.getElementById("logoutActionButton");
            const adminPanel = document.getElementById("adminPanel");

            if (!currentUser) {
                accountTitle.textContent = pickCopy("当前处于访客模式", "You are in guest mode");
                accountSubtitle.textContent = pickCopy(
                    "登录后，亲人档案、上传素材和订阅状态都会绑定到你的账号。",
                    "After sign-in, loved-one profiles, uploads, and subscription state are bound to your account."
                );
                billingTitle.textContent = pickCopy("登录后即可绑定套餐能力", "Bind plan access after sign-in");
                billingText.textContent = pickCopy(
                    "文字 / 语音 / 视频权限会直接绑定到账号与亲人档案，不再只是展示页文案。",
                    "Text, voice, and video access are bound directly to the account and profile instead of staying as marketing-only copy."
                );
                authActionButton.classList.remove("hidden");
                authActionButton.textContent = pickCopy("登录 / 注册", "Sign in / Register");
                billingPrimaryButton.classList.remove("hidden");
                billingPrimaryButton.textContent = pickCopy("登录 / 注册", "Sign in / Register");
                accountPortalButton.classList.add("hidden");
                billingPortalButton.classList.add("hidden");
                logoutActionButton.classList.add("hidden");
                adminPanel?.classList.remove("is-visible");
                updatePlanCards();
                return;
            }

            accountTitle.textContent = `${currentUser.display_name} · ${getLocalizedPlanName(currentSubscription)}`;
            accountSubtitle.textContent = subscriptionCapabilityLabel();
            billingTitle.textContent = pickCopy(
                `当前套餐：${getLocalizedPlanName(currentSubscription)}`,
                `Current plan: ${getLocalizedPlanName(currentSubscription)}`
            );
            billingText.textContent = subscriptionCapabilityLabel();
            authActionButton.classList.add("hidden");
            billingPrimaryButton.classList.add("hidden");
            const hasPortal = Boolean(currentSubscription && currentSubscription.plan_code !== "trial");
            accountPortalButton.classList.toggle("hidden", !hasPortal);
            billingPortalButton.classList.toggle("hidden", !hasPortal);
            logoutActionButton.classList.remove("hidden");
            if (currentUser?.is_admin) {
                adminPanel?.classList.add("is-visible");
                void loadAdminOverview();
            } else {
                adminPanel?.classList.remove("is-visible");
            }
            updatePlanCards();
        }

        function applyAuthEnvelope(data, shouldPersistToken = false) {
            if (shouldPersistToken && data?.token) {
                persistAuthToken(data.token);
            }
            currentUser = data?.user || null;
            currentSubscription = data?.subscription || null;
            updateAuthSurface();
        }

        async function loadPlans() {
            try {
                const response = await apiFetch("/api/plans");
                if (!response.ok) {
                    throw new Error("plans failed");
                }
                const data = await response.json();
                planCatalog = Array.isArray(data.plans) ? data.plans : [];
            } catch (error) {
                planCatalog = [];
            } finally {
                updatePlanCards();
            }
        }

        function handleCheckoutReturn() {
            const params = new URLSearchParams(window.location.search);
            const status = params.get("checkout");
            if (!status) {
                return;
            }
            if (status === "success") {
                showToast("支付已完成，刷新账号状态后就会看到新的套餐权限。", "success");
            } else if (status === "cancelled") {
                showToast("你已取消本次支付，现有权限保持不变。", "error");
            }
            params.delete("checkout");
            const nextUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}${window.location.hash}`;
            window.history.replaceState({}, "", nextUrl);
        }

        async function loadSession() {
            if (!authToken) {
                currentUser = null;
                currentSubscription = null;
                updateAuthSurface();
                return false;
            }

            try {
                const response = await apiFetch("/api/auth/me");
                if (!response.ok) {
                    throw new Error("session failed");
                }
                const data = await response.json();
                applyAuthEnvelope(data, false);
                return true;
            } catch (error) {
                persistAuthToken("");
                currentUser = null;
                currentSubscription = null;
                updateAuthSurface();
                return false;
            }
        }

        async function loadAdminOverview() {
            if (!currentUser?.is_admin) {
                return;
            }
            try {
                const [overviewResponse, usersResponse, lovedResponse] = await Promise.all([
                    apiFetch("/api/admin/overview"),
                    apiFetch("/api/admin/users?limit=5"),
                    apiFetch("/api/admin/loved-ones?limit=5")
                ]);
                if (!overviewResponse.ok || !usersResponse.ok || !lovedResponse.ok) {
                    throw new Error("admin failed");
                }
                const overview = await overviewResponse.json();
                const users = await usersResponse.json();
                const lovedOnes = await lovedResponse.json();
                renderAdminPanel(overview, users, lovedOnes);
            } catch (error) {
                renderAdminPanel(null, [], []);
            }
        }

        function renderAdminPanel(overview, users = [], lovedOnes = []) {
            const metrics = document.getElementById("adminMetrics");
            const userList = document.getElementById("adminUserList");
            const lovedList = document.getElementById("adminLovedOneList");
            if (!metrics || !userList || !lovedList) {
                return;
            }
            metrics.innerHTML = "";
            if (!overview) {
                metrics.innerHTML = '<div class="status-detail">后台数据暂时不可用。</div>';
                userList.innerHTML = "";
                lovedList.innerHTML = "";
                return;
            }
            const items = [
                { label: "用户数", value: overview.total_users || 0 },
                { label: "亲人档案", value: overview.total_loved_ones || 0 },
                { label: "素材总量", value: overview.total_media_assets || 0 },
                { label: "对话总量", value: overview.total_messages || 0 },
                { label: "主动联系", value: overview.total_proactive_events || 0 },
                { label: "3D 素材", value: overview.media_breakdown?.model3d || 0 }
            ];
            items.forEach((item) => {
                const card = document.createElement("div");
                card.className = "dh-metric";
                const label = document.createElement("span");
                label.textContent = item.label;
                const value = document.createElement("strong");
                value.textContent = item.value;
                card.append(label, value);
                metrics.append(card);
            });

            userList.innerHTML = "";
            users.forEach((user) => {
                const row = document.createElement("div");
                row.className = "status-detail";
                row.textContent = `${user.display_name || user.email} · ${user.loved_one_count || 0} 档案 · ${user.media_count || 0} 素材`;
                userList.append(row);
            });

            lovedList.innerHTML = "";
            lovedOnes.forEach((item) => {
                const row = document.createElement("div");
                row.className = "status-detail";
                row.textContent = `${item.name} · ${item.owner_email} · ${item.media_count || 0} 素材`;
                lovedList.append(row);
            });
        }

        async function submitAuth() {
            const submitButton = document.getElementById("authSubmitButton");
            const email = document.getElementById("authEmail").value.trim();
            const password = document.getElementById("authPassword").value.trim();
            const displayName = document.getElementById("authDisplayName").value.trim();

            if (!email || !password || (authMode === "register" && !displayName)) {
                showToast("请把账号信息填写完整。", "error");
                return;
            }

            setButtonLoading(submitButton, true, authMode === "register" ? "创建中..." : "登录中...");
            try {
                const response = await fetch(`${API_BASE}/api/auth/${authMode}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(
                        authMode === "register"
                            ? { email, password, display_name: displayName }
                            : { email, password }
                    )
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "认证失败");
                }

                applyAuthEnvelope(data, true);
                closeModal("authModal");
                await Promise.allSettled([loadPlans(), loadLovedOneDirectory(), loadStats()]);
                showToast(authMode === "register" ? "账号已创建，纪念空间已经开始长期保存。" : "欢迎回来，档案和权限已经重新接入。", "success");

                if (pendingPlanCode) {
                    const nextPlanCode = pendingPlanCode;
                    pendingPlanCode = "";
                    await startCheckout(nextPlanCode, true);
                }
            } catch (error) {
                showToast(error.message || "认证失败，请稍后重试。", "error");
            } finally {
                setButtonLoading(submitButton, false, authMode === "register" ? "创建账号" : "立即登录");
            }
        }

        async function logout() {
            try {
                if (authToken) {
                    await apiFetch("/api/auth/logout", { method: "POST" });
                }
            } finally {
                persistAuthToken("");
                currentUser = null;
                currentSubscription = null;
                lovedOneDirectory = [];
                activeMemories = [];
                activeChatHistory = [];
                activeMediaAssets = [];
                activeLovedOne = normalizeLovedOne(demoProfile);
                applyLovedOne(activeLovedOne, false);
                renderMemoryList();
                renderChatHistory();
                renderMediaLibrary();
                updateAuthSurface();
                await loadPlans();
                await loadStats();
            }
        }

        async function startCheckout(planCode, skipAuthCheck = false) {
            if (!skipAuthCheck && !currentUser) {
                pendingPlanCode = planCode;
                openAuthModal("register");
                return;
            }

            try {
                const response = await apiFetch("/api/billing/checkout", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ plan_code: planCode })
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "发起支付失败");
                }
                if (data.url) {
                    window.location.href = data.url;
                    return;
                }
                throw new Error("支付地址未返回");
            } catch (error) {
                showToast(error.message || "当前还不能发起支付。", "error");
            }
        }

        async function openBillingPortal() {
            if (!requireAccount("请先登录后再管理订阅。")) {
                return;
            }

            try {
                const response = await apiFetch("/api/billing/portal", { method: "POST" });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "打开订阅中心失败");
                }
                if (data.url) {
                    window.location.href = data.url;
                }
            } catch (error) {
                showToast(error.message || "当前还不能打开订阅中心。", "error");
            }
        }

        function buildLocalMediaAssets(profile) {
            const assets = [];
            (profile.voice_sample_urls || []).forEach((url, index) => {
                assets.push({
                    id: `local-voice-${index}`,
                    kind: "voice",
                    url,
                    original_filename: profile.voice_sample_paths?.[index] || `voice-${index + 1}.wav`,
                    summary: "本地演示语音素材",
                    tags: [],
                    is_primary: index === 0,
                    metadata: {},
                    created_at: null
                });
            });
            (profile.photo_urls || []).forEach((url, index) => {
                assets.push({
                    id: `local-photo-${index}`,
                    kind: "photo",
                    url,
                    original_filename: profile.photo_paths?.[index] || `photo-${index + 1}.jpg`,
                    summary: "本地演示照片素材",
                    tags: [],
                    is_primary: index === 0,
                    metadata: {},
                    created_at: null
                });
            });
            (profile.video_urls || []).forEach((url, index) => {
                assets.push({
                    id: `local-video-${index}`,
                    kind: "video",
                    url,
                    original_filename: profile.video_paths?.[index] || `video-${index + 1}.mp4`,
                    summary: "本地演示视频素材",
                    tags: [],
                    is_primary: index === 0,
                    metadata: {},
                    created_at: null
                });
            });
            (profile.model3d_urls || []).forEach((url, index) => {
                assets.push({
                    id: `local-model3d-${index}`,
                    kind: "model3d",
                    url,
                    original_filename: profile.model3d_paths?.[index] || `reconstruction-${index + 1}.glb`,
                    mime_type: "model/gltf-binary",
                    summary: "本地演示真人 3D 重建素材",
                    tags: [],
                    is_primary: index === 0,
                    metadata: { stage: "integrated" },
                    created_at: null
                });
            });
            return assets;
        }

        function setMediaFilter(filter) {
            mediaFilter = filter;
            document.querySelectorAll("[data-media-filter]").forEach((button) => {
                button.classList.toggle("active", button.getAttribute("data-media-filter") === filter);
            });
            renderMediaLibrary();
        }

        function renderMediaLibrary() {
            const container = document.getElementById("mediaManagerList");
            const meta = document.getElementById("mediaMeta");
            const hint = document.getElementById("mediaHint");
            if (!container || !meta || !hint) {
                return;
            }

            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            const filteredAssets = activeMediaAssets.filter((asset) => mediaFilter === "all" || asset.kind === mediaFilter);
            meta.textContent = `${activeMediaAssets.length} 份`;
            hint.textContent = currentUser
                ? `${subscriptionCapabilityLabel()} 当前档案 ${profile.name || "ta"} 已收集 ${activeMediaAssets.length} 份素材。`
                : "登录后，语音 / 照片 / 视频 / 3D 重建会在这里集中管理。";

            container.innerHTML = "";
            if (!filteredAssets.length) {
                container.innerHTML = '<div class="workbench-empty">当前筛选下还没有素材。先上传语音、照片、视频或 3D 重建，让分身越来越像 ta。</div>';
                return;
            }

            filteredAssets.forEach((asset) => {
                const card = document.createElement("div");
                card.className = `media-asset-card media-kind-${asset.kind}`;

                const top = document.createElement("div");
                top.className = "media-asset-top";

                const kind = document.createElement("span");
                kind.className = "asset-kind";
                kind.textContent =
                    asset.kind === "voice"
                        ? "语音"
                        : asset.kind === "photo"
                            ? "照片"
                            : asset.kind === "video"
                                ? "视频"
                                : "3D 重建";
                if (asset.is_primary) {
                    const primary = document.createElement("span");
                    primary.className = "primary-badge";
                    primary.textContent = "主样本";
                    kind.append(primary);
                }

                const remove = document.createElement("button");
                remove.type = "button";
                remove.className = "inline-action danger";
                remove.textContent = "删除";
                remove.disabled = String(asset.id || "").startsWith("local-");
                remove.addEventListener("click", () => {
                    void removeMediaAsset(asset.id);
                });

                const preview = document.createElement("div");
                preview.className = `media-asset-preview media-frame-${asset.kind}`;
                const assetUrl = resolveMediaUrl(asset.url);
                if (asset.kind === "voice") {
                    const audio = document.createElement("audio");
                    audio.controls = true;
                    audio.preload = "metadata";
                    audio.src = assetUrl;
                    preview.append(audio);
                } else if (asset.kind === "video") {
                    const video = document.createElement("video");
                    video.controls = true;
                    video.preload = "metadata";
                    video.src = assetUrl;
                    preview.append(video);
                } else if (asset.kind === "model3d") {
                    renderModel3dPreview(preview, asset);
                } else {
                    const image = document.createElement("img");
                    image.alt = asset.original_filename || "照片素材";
                    image.src = assetUrl;
                    preview.append(image);
                }

                const title = document.createElement("strong");
                title.textContent = asset.original_filename || "未命名素材";

                const summary = document.createElement("p");
                summary.className = "asset-summary";
                summary.textContent = asset.summary || "这份素材已经进入数字分身建模。";

                const detail = document.createElement("div");
                detail.className = "status-detail";
                detail.textContent = asset.created_at ? `上传于 ${formatTimeLabel(asset.created_at)}` : "本地演示素材";

                const tags = normalizeTags(asset.tags);
                const tagList = document.createElement("div");
                tagList.className = "media-tag-list";
                if (tags.length) {
                    tags.forEach((tag) => {
                        const chip = document.createElement("span");
                        chip.className = "media-tag";
                        chip.textContent = tag;
                        tagList.append(chip);
                    });
                } else {
                    const empty = document.createElement("span");
                    empty.className = "status-detail";
                    empty.textContent = "还没有标记标签";
                    tagList.append(empty);
                }

                const tagInput = document.createElement("input");
                tagInput.type = "text";
                tagInput.className = "media-tag-input";
                tagInput.placeholder = "用逗号分隔标签，例如：声音干净, 微笑";
                tagInput.value = tags.join(", ");
                tagInput.addEventListener("change", () => {
                    void updateMediaTags(asset.id, tagInput.value);
                });

                const actionRow = document.createElement("div");
                actionRow.className = "media-action-row";

                const primaryButton = document.createElement("button");
                primaryButton.type = "button";
                primaryButton.className = "inline-action";
                primaryButton.textContent = asset.is_primary ? "当前主样本" : "设为主样本";
                primaryButton.disabled = asset.is_primary || String(asset.id || "").startsWith("local-");
                primaryButton.addEventListener("click", () => {
                    void setPrimaryMedia(asset.id);
                });
                actionRow.append(primaryButton);

                if (asset.kind === "photo") {
                    const coverButton = document.createElement("button");
                    coverButton.type = "button";
                    coverButton.className = "inline-action";
                    const activeCover = isCoverAsset(profile, asset);
                    coverButton.textContent = activeCover ? "当前封面" : "设为封面";
                    coverButton.disabled = activeCover;
                    coverButton.addEventListener("click", () => {
                        void setCoverPhoto(asset.id);
                    });
                    actionRow.append(coverButton);
                }

                if (asset.kind === "model3d") {
                    const stageSelect = document.createElement("select");
                    stageSelect.className = "model3d-stage";
                    const stages = ["uploaded", "aligned", "textured", "rigged", "ready", "integrated"];
                    const currentStage = asset.metadata?.stage || "uploaded";
                    stages.forEach((stage) => {
                        const option = document.createElement("option");
                        option.value = stage;
                        option.textContent = formatModel3dStage(stage);
                        option.selected = stage === currentStage;
                        stageSelect.append(option);
                    });
                    stageSelect.addEventListener("change", () => {
                        void updateModel3dStage(asset.id, stageSelect.value);
                    });
                    actionRow.append(stageSelect);
                }

                top.append(kind, remove);
                card.append(top, preview, title, summary, tagList, tagInput, actionRow, detail);
                container.append(card);
            });
        }

        async function updateMediaTags(assetId, rawValue) {
            if (!currentUser || String(assetId || "").startsWith("local-")) {
                return;
            }
            const tags = rawValue
                .split(",")
                .map((tag) => tag.trim())
                .filter((tag) => tag.length > 0);
            try {
                const response = await apiFetch(`/api/media/${assetId}/tags`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tags })
                });
                if (!response.ok) {
                    throw new Error("tag failed");
                }
                await loadActiveMediaAssets();
                showToast("素材标签已更新。", "success");
            } catch (error) {
                showToast("更新标签失败，请稍后再试。", "error");
            }
        }

        async function setPrimaryMedia(assetId) {
            if (!currentUser || String(assetId || "").startsWith("local-")) {
                return;
            }
            try {
                const response = await apiFetch(`/api/media/${assetId}/primary`, { method: "POST" });
                if (!response.ok) {
                    throw new Error("primary failed");
                }
                await loadActiveMediaAssets();
                showToast("主样本已更新。", "success");
            } catch (error) {
                showToast("主样本更新失败。", "error");
            }
        }

        async function updateLovedOneCover(payload, successMessage = "纪念封面已更新。") {
            const current = normalizeLovedOne(activeLovedOne || demoProfile);
            const requestedTitle = payload.cover_title !== undefined ? String(payload.cover_title || "").trim() : current.cover_title;
            const requestedAssetId = payload.cover_photo_asset_id !== undefined ? payload.cover_photo_asset_id : current.cover_photo_asset_id;

            if (!serviceOnline || !currentUser || isLocalProfile(current)) {
                const selection = resolveCoverSelection(current, requestedAssetId);
                const nextProfile = normalizeLovedOne({
                    ...current,
                    cover_title: requestedTitle,
                    cover_photo_asset_id: selection.cover_photo_asset_id,
                    cover_photo_url: selection.cover_photo_url,
                });
                syncLovedOneDirectoryProfile(nextProfile);
                applyLovedOne(nextProfile, !isLocalProfile(nextProfile));
                renderMediaLibrary();
                showToast(successMessage, "success");
                return nextProfile;
            }

            const response = await apiFetch(`/api/loved-ones/${current.id}/cover`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    cover_title: requestedTitle,
                    cover_photo_asset_id: requestedAssetId,
                }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(data.detail || "封面更新失败");
            }
            const nextProfile = normalizeLovedOne(data);
            syncLovedOneDirectoryProfile(nextProfile);
            applyLovedOne(nextProfile, !isLocalProfile(nextProfile));
            renderMediaLibrary();
            showToast(successMessage, "success");
            return nextProfile;
        }

        async function saveCoverTitle() {
            const button = document.getElementById("saveCoverTitleButton");
            const input = document.getElementById("coverTitleInput");
            if (!button || !input) {
                return;
            }
            setButtonLoading(button, true, "保存中...");
            try {
                const coverTitle = input.value.trim();
                await updateLovedOneCover(
                    { cover_title: coverTitle },
                    coverTitle ? "封面题字已保存。" : "封面题字已清空。"
                );
            } catch (error) {
                showToast(error.message || "封面题字保存失败。", "error");
            } finally {
                setButtonLoading(button, false, "保存封面题字");
            }
        }

        async function setCoverPhoto(assetId) {
            if (!assetId) {
                return;
            }
            try {
                await updateLovedOneCover({ cover_photo_asset_id: assetId }, "封面照片已更新。");
            } catch (error) {
                showToast(error.message || "封面照片更新失败。", "error");
            }
        }

        async function updateModel3dStage(assetId, stage) {
            if (!currentUser || String(assetId || "").startsWith("local-")) {
                return;
            }
            try {
                const response = await apiFetch(`/api/media/${assetId}/model3d-stage`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ stage })
                });
                if (!response.ok) {
                    throw new Error("stage failed");
                }
                await Promise.allSettled([loadActiveMediaAssets(), loadDigitalHumanConsole()]);
                showToast("3D 阶段已更新。", "success");
            } catch (error) {
                showToast("3D 阶段更新失败。", "error");
            }
        }

        async function loadActiveMediaAssets(profile = activeLovedOne) {
            const current = normalizeLovedOne(profile || demoProfile);
            if (!serviceOnline || !currentUser || isLocalProfile(current)) {
                activeMediaAssets = buildLocalMediaAssets(current);
                renderMediaLibrary();
                return;
            }

            try {
                const response = await apiFetch(`/api/loved-ones/${current.id}/media`);
                if (!response.ok) {
                    throw new Error("media failed");
                }
                activeMediaAssets = await response.json();
            } catch (error) {
                activeMediaAssets = [];
            }
            renderMediaLibrary();
        }

        async function uploadManagedMedia(kind, overrideInputId = "") {
            if (!requireAccount("请先登录后再上传素材。")) {
                return;
            }

            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!serviceOnline || isLocalProfile(profile)) {
                showToast("请先创建并保存真实档案，再上传素材。", "error");
                return;
            }

            const features = getPlanFeatures();
            if (kind === "voice" && !features.voice_upload) {
                showToast("当前套餐还没有开放语音建模上传，请先升级套餐。", "error");
                return;
            }
            if (kind === "video" && !features.video_upload) {
                showToast("当前套餐还没有开放视频上传，请先升级套餐。", "error");
                return;
            }

            const inputId =
                overrideInputId ||
                {
                    voice: "managerVoiceFiles",
                    photo: "managerPhotoFiles",
                    video: "managerVideoFiles",
                    model3d: "managerModel3dFiles"
                }[kind];
            const files = getSelectedFiles(inputId);
            if (!files.length) {
                showToast("先选择要上传的素材。", "error");
                return;
            }

            const endpoint =
                {
                    voice: "/voice",
                    photo: "/photo",
                    video: "/video",
                    model3d: "/model-3d"
                }[kind];
            const kindLabel =
                {
                    voice: "语音",
                    photo: "照片",
                    video: "视频",
                    model3d: "3D 重建"
                }[kind] || "素材";
            let latestLovedOne = null;
            try {
                for (const file of files) {
                    const formData = new FormData();
                    formData.append("file", file);
                    const response = await apiFetch(`/api/loved-ones/${profile.id}${endpoint}`, {
                        method: "POST",
                        body: formData
                    });
                    const data = await response.json().catch(() => ({}));
                    if (!response.ok) {
                        throw new Error(data.detail || `${kind} 上传失败`);
                    }
                    latestLovedOne = data.loved_one ? normalizeLovedOne(data.loved_one) : latestLovedOne;
                }

                if (latestLovedOne) {
                    applyLovedOne(latestLovedOne);
                }
                document.getElementById(inputId).value = "";
                updateSelectedMediaMeta();
                await Promise.allSettled([
                    loadLovedOneDirectory(),
                    loadStats(),
                    loadActiveWorkbenchData(latestLovedOne || profile)
                ]);
                showToast(`已追加 ${files.length} 份${kindLabel}素材。`, "success");
            } catch (error) {
                showToast(error.message || "上传失败，请稍后重试。", "error");
            }
        }

        async function removeMediaAsset(assetId) {
            if (!currentUser || String(assetId || "").startsWith("local-")) {
                return;
            }
            try {
                const response = await apiFetch(`/api/media/${assetId}`, {
                    method: "DELETE"
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "删除素材失败");
                }
                if (activeLovedOne?.id) {
                    const profileResponse = await apiFetch(`/api/loved-ones/${activeLovedOne.id}`);
                    if (profileResponse.ok) {
                        const profile = normalizeLovedOne(await profileResponse.json());
                        applyLovedOne(profile);
                    }
                }
                await Promise.allSettled([loadLovedOneDirectory(), loadStats(), loadActiveMediaAssets()]);
                showToast("素材已删除，档案状态已同步更新。", "success");
            } catch (error) {
                showToast(error.message || "删除素材失败。", "error");
            }
        }

        function renderLovedOneDirectory() {
            const container = document.getElementById("lovedOneDirectory");
            const summary = document.getElementById("directorySummary");
            const profiles = lovedOneDirectory.length ? lovedOneDirectory : [normalizeLovedOne(activeLovedOne || demoProfile)];
            summary.textContent =
                serviceOnline && currentUser
                    ? `当前已接入 ${profiles.length} 位亲人档案，随时可以切换和继续完善。`
                    : serviceOnline
                        ? "服务已连接，但还没有登录账号；登录后会显示你自己的真实档案。"
                    : "当前是本地演示目录；连接服务后会显示真实档案。";

            container.innerHTML = "";
            if (!profiles.length) {
                container.innerHTML = '<div class="workbench-empty">还没有亲人档案，从第一位开始建立。</div>';
                return;
            }

            profiles.forEach((profile) => {
                const twin = profile.digital_twin_profile || buildClientTwinProfile(profile);
                const button = document.createElement("button");
                button.type = "button";
                button.className = "archive-item";
                if (activeLovedOne && profile.id === activeLovedOne.id) {
                    button.classList.add("active");
                }
                button.addEventListener("click", () => {
                    void selectLovedOneById(profile.id);
                });

                const title = document.createElement("strong");
                title.textContent = profile.name || "未命名亲人";

                const subtitle = document.createElement("p");
                subtitle.textContent = `${profile.relationship || "亲人"} · ${twin.completeness_label}`;

                const meta = document.createElement("div");
                meta.className = "entry-meta-row";

                const detail = document.createElement("span");
                detail.className = "status-detail";
                detail.textContent = `${twin.memory_count || 0} 条回忆 / ${formatAvailableModes(twin.available_modes || ["text"])}`;

                const badge = document.createElement("span");
                badge.className = "entry-badge";
                badge.textContent = `${twin.completion_percent || 0}%`;

                meta.append(detail, badge);
                const coverUrl = resolveCoverPhotoUrl(profile);
                const coverTitle = profile.cover_title || defaultCoverTitle(profile);
                if (coverUrl) {
                    button.classList.add("has-cover");
                    const cover = document.createElement("div");
                    cover.className = "archive-cover";
                    cover.style.backgroundImage = `url("${resolveMediaUrl(coverUrl)}")`;

                    const copy = document.createElement("div");
                    copy.className = "archive-copy";

                    const note = document.createElement("em");
                    note.textContent = coverTitle;

                    copy.append(note, title, subtitle, meta);
                    button.append(cover, copy);
                } else {
                    if (profile.cover_title) {
                        const note = document.createElement("em");
                        note.className = "status-detail";
                        note.textContent = coverTitle;
                        button.append(note);
                    }
                    button.append(title, subtitle, meta);
                }
                container.append(button);
            });
        }

        function renderMemoryList() {
            const container = document.getElementById("memoryList");
            const meta = document.getElementById("memoryMeta");
            meta.textContent = `${activeMemories.length} 条`;
            container.innerHTML = "";

            if (!activeMemories.length) {
                container.innerHTML = '<div class="workbench-empty">先写下一段你们之间真实发生过的事情，这会成为最早的人格材料。</div>';
                return;
            }

            activeMemories.forEach((memory, index) => {
                const card = document.createElement("div");
                card.className = `entry-card memory-note-card note-tilt-${index % 4}`;

                const top = document.createElement("div");
                top.className = "entry-meta-row";

                const badge = document.createElement("span");
                badge.className = "entry-badge";
                badge.textContent = memory.memory_type || "conversation";

                const remove = document.createElement("button");
                remove.type = "button";
                remove.className = "inline-action danger";
                remove.textContent = "删除";
                remove.addEventListener("click", () => {
                    void removeMemory(memory.id);
                });

                const text = document.createElement("p");
                text.textContent = memory.content;

                const detail = document.createElement("div");
                detail.className = "status-detail";
                detail.textContent = formatTimeLabel(memory.created_at);

                top.append(badge, remove);
                card.append(top, text, detail);
                container.append(card);
            });
        }

        function renderChatHistory() {
            const container = document.getElementById("chatHistoryList");
            const meta = document.getElementById("historyMeta");
            meta.textContent = `${activeChatHistory.length} 条`;
            container.innerHTML = "";

            if (!activeChatHistory.length) {
                container.innerHTML = '<div class="workbench-empty">开始对话之后，这里会留下你们最近的聊天轨迹。</div>';
                return;
            }

            activeChatHistory
                .slice()
                .reverse()
                .forEach((entry) => {
                    const card = document.createElement("div");
                    card.className = "entry-card";

                    const top = document.createElement("div");
                    top.className = "entry-meta-row";

                    const badge = document.createElement("span");
                    badge.className = "entry-badge";
                    badge.textContent = entry.mode || "text";

                    const time = document.createElement("span");
                    time.className = "status-detail";
                    time.textContent = formatTimeLabel(entry.timestamp);

                    const user = document.createElement("strong");
                    user.textContent = `你：${entry.user_message}`;

                    const ai = document.createElement("p");
                    ai.textContent = `${activeLovedOne?.name || "ta"}：${entry.ai_response}`;

                    top.append(badge, time);
                    card.append(top, user, ai);
                    container.append(card);
                });
        }

        function buildLocalProactiveState(profile) {
            const flow = {
                enabled: false,
                cadence: "daily",
                preferred_time: "20:30",
                preferred_weekday: 0,
                preferred_channel: "app",
                preferred_message_mode: "voice",
                phone_number: "",
                timezone: "Asia/Shanghai",
                next_run_at: null,
                last_run_at: null
            };
            const latestMemory = (profile.memories || [])[0] || `${profile.name || "ta"} 最近总会想来问问你今天过得怎么样。`;
            const event = {
                id: "local-proactive-preview",
                loved_one_id: profile.id,
                channel: "app",
                event_type: flow.preferred_message_mode === "video" ? "video_message" : (flow.preferred_message_mode === "voice" ? "voice_message" : "message"),
                status: "ready",
                title: `${profile.name || "ta"} 主动联系了你`,
                message_text: `孩子，今天我想主动来找你说说话。我又想起“${latestMemory}”。别总把心事憋着，慢慢和我说。`,
                audio_url: "",
                created_at: new Date().toISOString(),
                metadata: {
                    actual_message_mode: flow.preferred_message_mode,
                    provider_note: "这是本地演示预览。登录并开启主动联系后，系统才会按节奏自动联系你。"
                }
            };
            return {
                flow,
                contact: {
                    phone_number: "",
                    proactive_opt_in: false,
                    preferred_contact_channel: "app",
                    preferred_contact_time: "20:30",
                    timezone: "Asia/Shanghai"
                },
                call_bridge_configured: false,
                call_bridge: buildLocalBridgeStatus(profile),
                events: [event]
            };
        }

        function renderProactiveFeed(events = []) {
            const badge = document.getElementById("proactiveFeedBadge");
            const container = document.getElementById("proactiveFeedList");
            badge.textContent = `${events.length} 条`;
            container.innerHTML = "";

            if (!events.length) {
                container.innerHTML = '<div class="proactive-empty">开启后，ta 会按你设定的节奏主动来问候你；每次问候和电话记录也都会留在这里。</div>';
                return;
            }

            events.forEach((event) => {
                const card = document.createElement("div");
                card.className = "proactive-event";

                const top = document.createElement("div");
                top.className = "entry-meta-row";

                const badge = document.createElement("span");
                badge.className = "entry-badge";
                badge.textContent = formatChannelLabel(event.channel, event.event_type);

                const time = document.createElement("span");
                time.className = "status-detail";
                time.textContent = formatTimeLabel(event.created_at || event.scheduled_for);

                const title = document.createElement("strong");
                title.textContent = event.title || "主动联系";

                const body = document.createElement("p");
                body.textContent = event.message_text || "这次主动联系没有留下文字内容。";

                card.append(top, title, body);
                top.append(badge, time);

                if (event.video_url) {
                    const video = document.createElement("video");
                    video.controls = true;
                    video.preload = "metadata";
                    video.playsInline = true;
                    video.src = resolveMediaUrl(event.video_url);
                    card.append(video);
                } else if (event.audio_url) {
                    const audio = document.createElement("audio");
                    audio.controls = true;
                    audio.preload = "none";
                    audio.src = resolveMediaUrl(event.audio_url);
                    card.append(audio);
                }

                const detail = document.createElement("div");
                detail.className = "status-detail";
                const baseNote =
                    event.metadata?.provider_note ||
                    (event.channel === "phone"
                        ? "这次联系优先按电话外呼处理。"
                        : "这次联系以站内主动问候形式送达。");
                const extras = [];
                if (event.metadata?.call_status) {
                    extras.push(`状态：${event.metadata.call_status}`);
                }
                if (event.metadata?.test_call) {
                    extras.push("测试外呼");
                }
                if (event.metadata?.actual_message_mode && event.channel !== "phone") {
                    extras.push(`形式：${formatProactiveMessageModeLabel(event.metadata.actual_message_mode)}`);
                }
                detail.textContent = extras.length ? `${baseNote} · ${extras.join(" · ")}` : baseNote;
                card.append(detail);

                if (currentUser && !String(event.id || "").startsWith("local-") && !event.consumed_at) {
                    const consume = document.createElement("button");
                    consume.type = "button";
                    consume.className = "inline-action";
                    consume.textContent = "标记已接收";
                    consume.addEventListener("click", () => {
                        void consumeProactiveEvent(event.id);
                    });
                    card.append(consume);
                }

                container.append(card);
            });
        }

        function renderProactiveCenter(profile, payload) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            const data = payload || buildLocalProactiveState(current);
            const flow = data.flow || buildLocalProactiveState(current).flow;
            const contact = data.contact || {};
            const events = Array.isArray(data.events)
                ? data.events.filter((event) => !event.loved_one_id || event.loved_one_id === current.id)
                : [];

            activeProactiveSettings = flow;
            activeProactiveFeed = events;
            activeCallBridgeStatus = data.call_bridge || activeCallBridgeStatus || buildLocalBridgeStatus(current);
            activeProactiveBridgeConfigured = Boolean(
                (data.call_bridge && data.call_bridge.configured) || data.call_bridge_configured
            );

            document.getElementById("proactiveEnabled").checked = Boolean(flow.enabled);
            document.getElementById("proactiveCadence").value = flow.cadence || "daily";
            document.getElementById("proactiveWeekday").value = String(flow.preferred_weekday ?? 0);
            document.getElementById("proactiveTime").value = flow.preferred_time || contact.preferred_contact_time || "20:30";
            document.getElementById("proactiveChannel").value = flow.preferred_channel || contact.preferred_contact_channel || "app";
            document.getElementById("proactiveMessageMode").value = flow.preferred_message_mode || "voice";
            document.getElementById("proactivePhone").value = flow.phone_number || contact.phone_number || "";
            document.getElementById("proactiveTimezone").value = flow.timezone || contact.timezone || "Asia/Shanghai";

            const meta = document.getElementById("proactiveMeta");
            const hint = document.getElementById("proactiveHint");
            const status = document.getElementById("proactiveStatus");
            const saveButton = document.getElementById("saveProactiveButton");
            const triggerButton = document.getElementById("triggerProactiveButton");
            const testButton = document.getElementById("triggerProactiveTestButton");
            const isDemo = !serviceOnline || !currentUser || isLocalProfile(current);
            const cadenceText = formatCadenceLabel(flow);
            const bridge = data.call_bridge || activeCallBridgeStatus || buildLocalBridgeStatus(current);
            const messageModeText = formatProactiveMessageModeLabel(flow.preferred_message_mode || "voice");
            const bridgeText = flow.preferred_channel === "phone"
                ? ` ${bridge.readiness_note || (activeProactiveBridgeConfigured ? "当前已启用电话优先联系。" : "当前还没有配置电话桥接服务，所以现在会先生成站内语音问候和电话脚本。")}`
                : ` 当前会优先生成${messageModeText}。`;

            meta.textContent = flow.enabled ? `已开启 · ${cadenceText}` : "未开启";
            hint.textContent = isDemo
                ? "当前是主动联系演示。登录并保存真实档案后，系统才会按设定节奏主动联系你。"
                : `你授权后，${current.name || "ta"} 会按「${cadenceText}」主动联系你。${bridgeText}`.trim();
            status.textContent = flow.enabled
                ? `下一次计划联系：${flow.next_run_at ? formatTimeLabel(flow.next_run_at) : "等待生成"}。联系渠道：${flow.preferred_channel === "phone" ? "电话外呼" : "站内主动联系"}；默认形式：${messageModeText}。`
                : "主动联系当前处于关闭状态；你可以先保存节奏，再让系统开始主动来找你。";

            const disabled = isDemo;
            [
                "proactiveEnabled",
                "proactiveCadence",
                "proactiveWeekday",
                "proactiveTime",
                "proactiveChannel",
                "proactiveMessageMode",
                "proactivePhone",
                "proactiveTimezone",
            ].forEach((id) => {
                const node = document.getElementById(id);
                if (node) {
                    node.disabled = disabled;
                }
            });
            saveButton.disabled = disabled;
            triggerButton.disabled = disabled;
            saveButton.textContent = disabled ? "登录后启用主动联系" : "保存主动联系设置";
            triggerButton.textContent = disabled ? "登录后可立即触发" : "现在就主动联系我一次";
            if (testButton) {
                testButton.disabled = disabled;
                testButton.textContent = disabled ? "登录后可测试外呼" : "测试电话外呼";
            }

            const weekdayField = document.getElementById("proactiveWeekday");
            weekdayField.parentElement.style.display = document.getElementById("proactiveCadence").value === "weekly" ? "grid" : "none";
            renderProactiveFeed(events);
        }

        async function loadProactiveCenter(profile = activeLovedOne) {
            const current = normalizeLovedOne(profile || demoProfile);
            if (!serviceOnline || !currentUser || isLocalProfile(current)) {
                renderProactiveCenter(current, buildLocalProactiveState(current));
                return;
            }

            try {
                const [settingsResponse, feedResponse] = await Promise.all([
                    apiFetch(`/api/proactive/settings/${current.id}`),
                    apiFetch("/api/proactive/feed"),
                ]);
                if (!settingsResponse.ok || !feedResponse.ok) {
                    throw new Error("proactive failed");
                }
                const settings = await settingsResponse.json();
                const feed = await feedResponse.json();
                renderProactiveCenter(current, {
                    ...settings,
                    events: feed.events || [],
                });
            } catch (error) {
                renderProactiveCenter(current, buildLocalProactiveState(current));
            }
        }

        async function saveProactiveSettings() {
            if (!requireAccount("请先登录后再设置主动联系。")) {
                return;
            }
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!serviceOnline || isLocalProfile(profile)) {
                showToast("请先创建并保存真实档案，再启用主动联系。", "error");
                return;
            }

            const button = document.getElementById("saveProactiveButton");
            const payload = {
                loved_one_id: profile.id,
                enabled: document.getElementById("proactiveEnabled").checked,
                cadence: document.getElementById("proactiveCadence").value,
                preferred_time: document.getElementById("proactiveTime").value || "20:30",
                preferred_weekday: Number(document.getElementById("proactiveWeekday").value || 0),
                preferred_channel: document.getElementById("proactiveChannel").value,
                preferred_message_mode: document.getElementById("proactiveMessageMode").value,
                phone_number: document.getElementById("proactivePhone").value.trim(),
                timezone: document.getElementById("proactiveTimezone").value.trim() || "Asia/Shanghai",
            };

            if (payload.preferred_channel === "phone" && !payload.phone_number) {
                showToast("电话优先联系需要先填写你的手机号。", "error");
                return;
            }

            setButtonLoading(button, true, "保存中...");
            try {
                const response = await apiFetch(`/api/proactive/settings/${profile.id}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "主动联系设置保存失败");
                }
                renderProactiveCenter(profile, { ...data, events: activeProactiveFeed });
                showToast(payload.enabled ? "主动联系已开启，系统会开始按节奏联系你。" : "主动联系已关闭。", "success");
            } catch (error) {
                showToast(error.message || "主动联系设置保存失败。", "error");
            } finally {
                setButtonLoading(button, false, "保存主动联系设置");
            }
        }

        async function triggerProactiveNow() {
            if (!requireAccount("请先登录后再让 ta 主动联系你。")) {
                return;
            }
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!serviceOnline || isLocalProfile(profile)) {
                showToast("请先创建并保存真实档案，再触发主动联系。", "error");
                return;
            }
            if (
                document.getElementById("proactiveChannel").value === "phone" &&
                !document.getElementById("proactivePhone").value.trim()
            ) {
                showToast("先填写手机号，ta 才能主动拨打给你。", "error");
                return;
            }

            const button = document.getElementById("triggerProactiveButton");
            setButtonLoading(button, true, "生成中...");
            try {
                const response = await apiFetch(`/api/proactive/trigger-now/${profile.id}`, {
                    method: "POST",
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "主动联系触发失败");
                }
                await loadProactiveCenter(profile);
                await loadDigitalHumanConsole(profile);
                showToast("ta 已经开始主动联系你了。", "success");
            } catch (error) {
                showToast(error.message || "主动联系触发失败。", "error");
            } finally {
                setButtonLoading(button, false, "现在就主动联系我一次");
            }
        }

        async function triggerProactiveTestCall() {
            if (!requireAccount("请先登录后再测试电话外呼。")) {
                return;
            }
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!serviceOnline || isLocalProfile(profile)) {
                showToast("请先创建并保存真实档案，再测试电话外呼。", "error");
                return;
            }
            if (!document.getElementById("proactivePhone").value.trim()) {
                showToast("先填写手机号，才能测试电话外呼。", "error");
                return;
            }

            const button = document.getElementById("triggerProactiveTestButton");
            setButtonLoading(button, true, "测试中...");
            try {
                const response = await apiFetch(`/api/proactive/test-call/${profile.id}`, {
                    method: "POST",
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "测试外呼失败");
                }
                await loadProactiveCenter(profile);
                await loadDigitalHumanConsole(profile);
                showToast("测试外呼已提交，结果会记录在下方。", "success");
            } catch (error) {
                showToast(error.message || "测试外呼失败。", "error");
            } finally {
                setButtonLoading(button, false, "测试电话外呼");
            }
        }

        async function consumeProactiveEvent(eventId) {
            if (!currentUser || !eventId) {
                return;
            }
            try {
                const response = await apiFetch(`/api/proactive/events/${eventId}/consume`, {
                    method: "POST",
                });
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data.detail || "标记失败");
                }
                await loadProactiveCenter(activeLovedOne || demoProfile);
            } catch (error) {
                showToast(error.message || "更新主动联系状态失败。", "error");
            }
        }

        function updateWorkbenchSurface(profile) {
            const current = normalizeLovedOne(profile || activeLovedOne || demoProfile);
            const twin = current.digital_twin_profile || buildClientTwinProfile(current);
            document.getElementById("workbenchName").textContent = current.name || "当前档案";
            document.getElementById("workbenchSummary").textContent =
                `${current.relationship || "亲人"} · ${twin.completeness_label} · 当前建模完整度约 ${twin.completion_percent || 0}% · 正在推进 ${twin.current_stage_title || "分身构建"}。`;
            renderCoverSheet(current);

            const deleteButton = document.getElementById("deleteLovedOneButton");
            deleteButton.disabled = isLocalProfile(current) || !currentUser;
            deleteButton.textContent = !currentUser ? "登录后可删除" : isLocalProfile(current) ? "演示档案不可删除" : "删除档案";
        }

        async function loadActiveWorkbenchData(profile = activeLovedOne) {
            const current = normalizeLovedOne(profile || demoProfile);
            updateWorkbenchSurface(current);

            if (!serviceOnline || !currentUser || isLocalProfile(current)) {
                activeMemories = (current.memories || []).map((content, index) => ({
                    id: `local-memory-${index}`,
                    content,
                    memory_type: "conversation",
                    created_at: null,
                }));
                activeChatHistory = Array.isArray(current.local_chat_history) ? current.local_chat_history : [];
                renderMemoryList();
                renderChatHistory();
                await loadActiveMediaAssets(current);
                await loadDigitalHumanConsole(current);
                await loadProactiveCenter(current);
                return;
            }

            try {
                const [memoryResponse, historyResponse] = await Promise.all([
                    apiFetch(`/api/memories/${current.id}`),
                    apiFetch(`/api/chat-history/${current.id}`)
                ]);

                if (!memoryResponse.ok || !historyResponse.ok) {
                    throw new Error("workbench failed");
                }

                activeMemories = await memoryResponse.json();
                activeChatHistory = await historyResponse.json();
            } catch (error) {
                activeMemories = [];
                activeChatHistory = [];
            }

            renderMemoryList();
            renderChatHistory();
            await loadActiveMediaAssets(current);
            await loadDigitalHumanConsole(current);
            await loadProactiveCenter(current);
        }

        async function selectLovedOneById(lovedOneId) {
            const target = lovedOneDirectory.find((item) => item.id === lovedOneId);
            if (!target) {
                return;
            }
            applyLovedOne(target, !isLocalProfile(target));
            renderLovedOneDirectory();
            await loadActiveWorkbenchData(target);
        }

        async function loadLovedOneDirectory() {
            if (!serviceOnline) {
                lovedOneDirectory = [normalizeLovedOne(activeLovedOne || demoProfile)];
                renderLovedOneDirectory();
                await loadActiveWorkbenchData(activeLovedOne || demoProfile);
                return;
            }

            if (!currentUser) {
                const fallback = normalizeLovedOne(demoProfile);
                lovedOneDirectory = [fallback];
                applyLovedOne(fallback, false);
                renderLovedOneDirectory();
                await loadActiveWorkbenchData(fallback);
                return;
            }

            try {
                const response = await apiFetch("/api/loved-ones");
                if (!response.ok) {
                    throw new Error("directory failed");
                }

                lovedOneDirectory = (await response.json()).map((item) => normalizeLovedOne(item));
                if (!lovedOneDirectory.length) {
                    lovedOneDirectory = [normalizeLovedOne(demoProfile)];
                }

                const selected =
                    lovedOneDirectory.find((item) => item.id === activeLovedOne?.id) ||
                    lovedOneDirectory[0];
                applyLovedOne(selected, !isLocalProfile(selected));
            } catch (error) {
                lovedOneDirectory = [normalizeLovedOne(activeLovedOne || demoProfile)];
            }

            renderLovedOneDirectory();
            await loadActiveWorkbenchData(activeLovedOne || lovedOneDirectory[0] || demoProfile);
        }

        async function saveMemory() {
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            const input = document.getElementById("newMemoryInput");
            const memoryType = document.getElementById("newMemoryType").value;
            const content = input.value.trim();
            const saveButton = document.getElementById("saveMemoryButton");

            if (!content) {
                showToast("先写下一段回忆，再保存。", "error");
                input.focus();
                return;
            }

            if (!serviceOnline || !currentUser) {
                if (!requireAccount("请先登录后再保存回忆。")) {
                    return;
                }
            }

            if (!serviceOnline || isLocalProfile(profile)) {
                const nextProfile = normalizeLovedOne({
                    ...profile,
                    memories: uniqueValues([content, ...(profile.memories || [])])
                });
                applyLovedOne(nextProfile);
                lovedOneDirectory = [nextProfile];
                renderLovedOneDirectory();
                await loadActiveWorkbenchData(nextProfile);
                input.value = "";
                showToast("这段回忆已加入本地演示档案。", "success");
                return;
            }

            setButtonLoading(saveButton, true, "保存中...");
            try {
                const response = await apiFetch("/api/memories", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        loved_one_id: profile.id,
                        content,
                        memory_type: memoryType,
                    })
                });

                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.detail || "save memory failed");
                }

                input.value = "";
                await loadLovedOneDirectory();
                await loadStats();
                showToast("回忆已保存，分身会把它记住。", "success");
            } catch (error) {
                showToast("回忆保存失败，请稍后再试。", "error");
            } finally {
                setButtonLoading(saveButton, false, "添加回忆");
            }
        }

        async function removeMemory(memoryId) {
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!memoryId) {
                return;
            }

            if (!serviceOnline || isLocalProfile(profile)) {
                const nextProfile = normalizeLovedOne({
                    ...profile,
                    memories: (profile.memories || []).filter((_, index) => `local-memory-${index}` !== memoryId)
                });
                applyLovedOne(nextProfile);
                lovedOneDirectory = [nextProfile];
                renderLovedOneDirectory();
                await loadActiveWorkbenchData(nextProfile);
                showToast("本地回忆已删除。", "success");
                return;
            }

            try {
                const response = await apiFetch(`/api/memories/${profile.id}/${memoryId}`, {
                    method: "DELETE"
                });
                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.detail || "delete memory failed");
                }
                await loadLovedOneDirectory();
                await loadStats();
                showToast("回忆已删除。", "success");
            } catch (error) {
                showToast("删除回忆失败，请稍后再试。", "error");
            }
        }

        async function removeActiveLovedOne() {
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            if (!serviceOnline || isLocalProfile(profile)) {
                showToast("当前是演示档案，不执行删除。", "error");
                return;
            }

            if (!requireAccount("请先登录后再删除档案。")) {
                return;
            }

            try {
                const response = await apiFetch(`/api/loved-ones/${profile.id}`, {
                    method: "DELETE"
                });
                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.detail || "delete loved one failed");
                }
                localStorage.removeItem(STORAGE_KEY);
                activeLovedOne = normalizeLovedOne(demoProfile);
                await loadLovedOneDirectory();
                await loadStats();
                showToast(`${profile.name} 的档案已删除。`, "success");
            } catch (error) {
                showToast("删除档案失败，请稍后再试。", "error");
            }
        }

        function uniqueValues(values) {
            return [...new Set(values.filter(Boolean))];
        }

        async function hydrateRuntimeState() {
            await checkHealth();
            await loadPlans();
            if (serviceOnline) {
                await loadSession();
            } else {
                updateAuthSurface();
            }
            await Promise.allSettled([loadStats(), loadLovedOneDirectory()]);
        }

        async function checkHealth() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                if (!response.ok) {
                    throw new Error("health failed");
                }

                const data = await response.json();
                serviceOnline = true;
                updateStatusPill(
                    document.getElementById("serviceStatus"),
                    "online",
                    pickCopy(`念念服务在线 · v${data.version}`, `Eterna service online · v${data.version}`)
                );
                updateStatusPill(
                    document.getElementById("chatMode"),
                    "online",
                    activeLovedOne
                        ? pickCopy(`${activeLovedOne.name} 的实时会话`, `${activeLovedOne.name}'s live session`)
                        : pickCopy("API 已连接", "API connected")
                );
            } catch (error) {
                serviceOnline = false;
                updateStatusPill(
                    document.getElementById("serviceStatus"),
                    "demo",
                    pickCopy("当前为本地演示模式", "Local demo mode")
                );
                updateStatusPill(
                    document.getElementById("chatMode"),
                    "demo",
                    pickCopy("本地演示会话", "Local demo session")
                );
            } finally {
                if (activeLovedOne) {
                    applyLovedOne(activeLovedOne, false);
                }
            }
        }

        async function loadStats() {
            if (!currentUser) {
                document.getElementById("serviceDetail").textContent =
                    pickCopy(
                        "登录后，每位亲人档案、回忆、素材和套餐权限都会开始长期累积。",
                        "After sign-in, every loved-one profile, memory, upload, and plan entitlement starts accumulating long term."
                    );
                return;
            }
            try {
                const response = await apiFetch("/api/stats");
                if (!response.ok) {
                    throw new Error("stats failed");
                }

                const stats = await response.json();
                currentSubscription = stats.subscription || currentSubscription;
                updateAuthSurface();
                document.getElementById("serviceDetail").textContent =
                    pickCopy(
                        `已记录 ${stats.total_loved_ones} 位亲人、${stats.total_memories} 条回忆、${stats.total_messages} 段对话、${stats.total_assets || 0} 份素材。`,
                        `Stored ${stats.total_loved_ones} loved ones, ${stats.total_memories} memories, ${stats.total_messages} conversations, and ${stats.total_assets || 0} assets.`
                    );
            } catch (error) {
                document.getElementById("serviceDetail").textContent =
                    pickCopy(
                        "创建第一位亲人的档案后，纪念数据和对话记录会在这里持续累积。",
                        "Once the first loved-one profile is created, memorial data and conversation history will keep accumulating here."
                    );
            }
        }

        function updateStatusPill(element, mode, text) {
            element.classList.remove("online", "demo");
            element.classList.add(mode);
            const label = element.querySelector("span:last-child");
            if (label) {
                label.textContent = text;
            }
        }

        function scrollToChat() {
            document.getElementById("chatSection").scrollIntoView({ behavior: "smooth", block: "start" });
            window.setTimeout(() => {
                document.getElementById("chatInput").focus();
            }, 320);
        }

        function bindModalEvents() {
            document.querySelectorAll(".modal").forEach((modal) => {
                modal.addEventListener("click", (event) => {
                    if (event.target === modal) {
                        closeModal(modal.id);
                    }
                });
            });

            document.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    closeModal("createModal");
                    closeModal("authModal");
                }
            });
        }

        function openModal(id) {
            const modal = document.getElementById(id);
            modal.classList.add("active");
            modal.setAttribute("aria-hidden", "false");
            window.setTimeout(() => {
                if (id === "createModal") {
                    document.getElementById("lovedOneName")?.focus();
                }
            }, 80);
        }

        function closeModal(id) {
            const modal = document.getElementById(id);
            modal.classList.remove("active");
            modal.setAttribute("aria-hidden", "true");
        }

        function restoreLovedOne() {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (!saved) {
                    activeLovedOne = normalizeLovedOne(demoProfile);
                    applyLovedOne(activeLovedOne, false);
                    return;
                }

                activeLovedOne = normalizeLovedOne(JSON.parse(saved));
                applyLovedOne(activeLovedOne, false);
            } catch (error) {
                activeLovedOne = normalizeLovedOne(demoProfile);
                applyLovedOne(activeLovedOne, false);
            }
        }

        function applyLovedOne(lovedOne, persist = true) {
            const profile = normalizeLovedOne(lovedOne);
            activeLovedOne = profile;
            const avatarMap = {
                "父亲": "👨",
                "母亲": "👩",
                "配偶": "💛",
                "子女": "🧒",
                "祖父母": "🧓"
            };
            const chatName = profile?.name || demoProfile.name;
            const relationship = profile?.relationship || demoProfile.relationship;
            const catchphrase = profile?.personality_traits?.catchphrase || demoProfile.personality_traits.catchphrase;
            const twinProfile = profile.digital_twin_profile || buildClientTwinProfile(profile);

            document.getElementById("chatName").textContent = chatName;
            document.getElementById("chatAvatar").textContent = avatarMap[relationship] || "🕯️";
            document.getElementById("chatSubtitle").textContent =
                catchphrase
                    ? pickCopy(
                        `熟悉的话会从这里再次出现，比如：“${catchphrase}”`,
                        `Familiar words can return here again, such as: "${catchphrase}"`
                    )
                    : pickCopy(
                        `${twinProfile.completeness_label}，这里会逐渐学会 ${chatName} 最像 ta 的说话方式。`,
                        `${chatName}'s model is taking shape here, one memory and one mannerism at a time.`
                    );
            document.getElementById("chatInput").placeholder = pickCopy(`和${chatName}说说今天发生的事...`, `Tell ${chatName} what happened today...`);
            document.getElementById("composerHint").textContent =
                serviceOnline && currentUser && !String(profile.id).startsWith("local-")
                    ? pickCopy(
                        `当前已绑定 ${chatName} 的真实档案。${subscriptionCapabilityLabel()} ${buildTwinStatusLine(profile)}`,
                        `${chatName}'s real profile is connected. ${subscriptionCapabilityLabel()} ${buildTwinStatusLine(profile)}`
                    )
                    : pickCopy(
                        `当前是 ${chatName} 的本地演示档案。${buildTwinStatusLine(profile)}`,
                        `This is ${chatName}'s local demo profile. ${buildTwinStatusLine(profile)}`
                    );

            if (persist) {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
            }

            updateTwinPanel(profile);
            updateModeControls(profile);
            updateWorkbenchSurface(profile);
            clearResponseMedia();
            refreshChatIntro();
            renderLovedOneDirectory();
            updateStatusPill(
                document.getElementById("chatMode"),
                serviceOnline && currentUser && !String(profile.id).startsWith("local-") ? "online" : "demo",
                serviceOnline && currentUser && !String(profile.id).startsWith("local-")
                    ? pickCopy(`${chatName} 的实时会话`, `${chatName}'s live session`)
                    : pickCopy(`${chatName} 的演示会话`, `${chatName}'s demo session`)
            );
        }

        function refreshChatIntro() {
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            const twin = profile.digital_twin_profile || buildClientTwinProfile(profile);
            document.getElementById("initialMessage").textContent =
                twin.coverage > 0
                    ? pickCopy(
                        `${profile.name}会在这里等你。现在已经留住了 ${twin.memory_count || 0} 条回忆、${twin.voice_count} 段语音、${twin.photo_count} 张照片和 ${twin.video_count} 段视频，你每次回来，都可以继续把 ta 补得更完整。`,
                        `${profile.name} is waiting here. So far the space holds ${twin.memory_count || 0} memories, ${twin.voice_count} voice clips, ${twin.photo_count} photos, and ${twin.video_count} videos. Every return can make the twin more complete.`
                    )
                    : pickCopy(
                        `${profile.name}会在这里等你。你每次回来，都可以从一句近况、一段想念，或者一个好消息开始。`,
                        `${profile.name} is waiting here. Each return can begin with a small update, a moment of longing, or one piece of good news.`
                    );
        }

        async function createLovedOne() {
            const button = document.getElementById("createButton");
            const name = document.getElementById("lovedOneName").value.trim();
            const relationship = document.getElementById("relationship").value;
            const personality = document.getElementById("personality").value.trim();
            const catchphrase = document.getElementById("catchphrase").value.trim();
            const coverTitle = document.getElementById("coverTitle").value.trim();
            const memories = collectMemoryDrafts(document.getElementById("coreMemories").value);
            const voiceFiles = getSelectedFiles("voiceFiles");
            const photoFiles = getSelectedFiles("photoFiles");
            const videoFiles = getSelectedFiles("videoFiles");
            const hasMedia = voiceFiles.length > 0 || photoFiles.length > 0 || videoFiles.length > 0;

            if (!name) {
                showToast("先填上 ta 的名字，再开始这段纪念。", "error");
                document.getElementById("lovedOneName").focus();
                return;
            }

            if (serviceOnline && !currentUser) {
                pendingPlanCode = "";
                openAuthModal("register");
                showToast("请先登录后再创建亲人档案。", "error");
                return;
            }

            setButtonLoading(button, true, hasMedia ? "创建并上传中..." : "创建中...");
            const payload = {
                name,
                relationship,
                personality_traits: {
                    personality,
                    catchphrase
                },
                speaking_style: catchphrase || "温柔亲切",
                cover_title: coverTitle,
                memories
            };

            try {
                const response = await apiFetch("/api/loved-ones", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.detail || "create failed");
                }

                let lovedOne = normalizeLovedOne(await response.json());
                let uploadedAssets = 0;

                if (hasMedia) {
                    setButtonLoading(button, true, "正在补充分身素材...");
                    const uploadResult = await uploadSelectedMedia(lovedOne.id);
                    lovedOne = uploadResult.lovedOne || lovedOne;
                    uploadedAssets = uploadResult.uploadCount;
                }

                applyLovedOne(lovedOne);
                await loadLovedOneDirectory();
                await loadStats();
                showToast(
                    uploadedAssets > 0
                        ? `${name} 的数字分身档案已创建，已同步 ${uploadedAssets} 份素材。`
                        : `${name} 的数字生命已创建，现在可以开始第一段对话。`,
                    "success"
                );
            } catch (error) {
                if (serviceOnline) {
                    showToast(error.message || "创建档案失败，请稍后再试。", "error");
                    return;
                }
                const localProfile = buildLocalDraftProfile(payload);
                applyLovedOne(localProfile, false);
                lovedOneDirectory = [localProfile];
                await loadActiveWorkbenchData(localProfile);
                showToast(
                    hasMedia
                        ? `${name} 已在本地演示模式中创建，当前页面会先展示分身素材预览；连接服务后才能正式保存。`
                        : `${name} 已在本地演示模式中创建，你可以先继续体验。`,
                    "success"
                );
            } finally {
                setButtonLoading(button, false, "立即创建");
                closeModal("createModal");
                clearCreateForm();
                scrollToChat();
            }
        }

        function clearCreateForm() {
            document.getElementById("lovedOneName").value = "";
            document.getElementById("relationship").value = "父亲";
            document.getElementById("personality").value = "";
            document.getElementById("catchphrase").value = "";
            document.getElementById("coverTitle").value = "";
            document.getElementById("coreMemories").value = "";
            document.getElementById("voiceFiles").value = "";
            document.getElementById("photoFiles").value = "";
            document.getElementById("videoFiles").value = "";
            updateSelectedMediaMeta();
        }

        function seedConversation(text) {
            const input = document.getElementById("chatInput");
            input.value = text;
            input.focus();
            sendMessage();
        }

        function setButtonLoading(button, loading, label) {
            button.disabled = loading;
            button.textContent = label;
        }

        function handleChatKey(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        async function sendMessage() {
            if (chatBusy) {
                return;
            }

            const input = document.getElementById("chatInput");
            const sendButton = document.getElementById("sendButton");
            const message = input.value.trim();
            const profile = normalizeLovedOne(activeLovedOne || demoProfile);
            const emotionSelect = document.getElementById("chatEmotion");
            const selectedEmotion = emotionSelect?.value || "";
            const intensity = Number(document.getElementById("chatIntensity")?.value || 3);

            if (!message) {
                return;
            }

            addMessage(message, "user");
            input.value = "";
            input.focus();
            clearResponseMedia();

            chatBusy = true;
            setButtonLoading(sendButton, true, "回应中...");
            const typingNode = addTypingIndicator();
            let localProfileMode = isLocalProfile(profile) || !currentUser;

            try {
                let replyText = "";
                let responsePayload = null;

                if (!localProfileMode) {
                    const response = await apiFetch("/api/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            loved_one_id: profile.id,
                            message,
                            emotion: selectedEmotion || inferEmotion(message),
                            mode: selectedChatMode,
                            intensity
                        })
                    });

                    if (!response.ok) {
                        const data = await response.json().catch(() => ({}));
                        throw new Error(data.detail || "chat failed");
                    }

                    responsePayload = await response.json();
                    if (responsePayload.interaction_mode && responsePayload.interaction_mode !== selectedChatMode) {
                        selectedChatMode = responsePayload.interaction_mode;
                        updateModeControls(profile);
                    }
                    replyText = responsePayload.response_text;
                } else {
                    await wait(720);
                    replyText = buildDemoReply(message, profile);
                    const nextProfile = normalizeLovedOne({
                        ...profile,
                        local_chat_history: [
                            ...(Array.isArray(profile.local_chat_history) ? profile.local_chat_history : []),
                            {
                                timestamp: new Date().toISOString(),
                                user_message: message,
                                ai_response: replyText,
                                mode: selectedChatMode
                            }
                        ]
                    });
                    applyLovedOne(nextProfile, false);
                    responsePayload = {
                        interaction_mode: selectedChatMode,
                        mode_note:
                            selectedChatMode === "video"
                                ? "当前是本地素材演示；正式请求会由 Mimo 生成旁白与镜头规划，并自动合成为视频陪伴。"
                                : selectedChatMode === "voice"
                                    ? "当前是本地演示；正式请求会由 Mimo 生成陪伴式语音电话回复。"
                                    : "当前是文字陪伴演示。"
                    };
                }

                typingNode.remove();
                addMessage(replyText, "ai");
                renderResponseMedia(responsePayload, profile);
                await loadActiveWorkbenchData(activeLovedOne || profile);
                if (!localProfileMode) {
                    await loadStats();
                }
            } catch (error) {
                typingNode.remove();
                if (!localProfileMode && currentUser) {
                    showToast(error.message || "当前对话失败，请稍后再试。", "error");
                    renderResponseMedia(
                        {
                            interaction_mode: selectedChatMode,
                            mode_note: error.message || "当前请求失败。",
                        },
                        profile
                    );
                    return;
                }
                addMessage(buildDemoReply(message, profile), "ai");
                renderResponseMedia(
                    {
                        interaction_mode: "text",
                        mode_note: "当前请求失败，已回退到本地文字演示。",
                    },
                    profile
                );
            } finally {
                chatBusy = false;
                setButtonLoading(sendButton, false, "发送");
            }
        }

        function addMessage(text, type) {
            const container = document.getElementById("chatMessages");
            const message = document.createElement("div");
            message.className = `message ${type}`;

            const body = document.createElement("div");
            body.className = "message-body";

            const content = document.createElement("div");
            content.className = "message-content";
            content.textContent = text;

            const meta = document.createElement("div");
            meta.className = "message-meta";
            meta.textContent = new Date().toLocaleTimeString(isEnglish() ? "en-US" : "zh-CN", {
                hour: "2-digit",
                minute: "2-digit"
            });

            body.append(content, meta);
            message.append(body);
            container.append(message);
            container.scrollTop = container.scrollHeight;
        }

        function addTypingIndicator() {
            const container = document.getElementById("chatMessages");
            const message = document.createElement("div");
            message.className = "message ai";
            message.innerHTML = `
                <div class="message-body">
                    <div class="message-content">
                        <span class="typing"><span></span><span></span><span></span></span>
                    </div>
                    <div class="message-meta">${pickCopy("正在回应…", "Responding...")}</div>
                </div>
            `;
            container.append(message);
            container.scrollTop = container.scrollHeight;
            return message;
        }

        function inferEmotion(message) {
            if (/(想你|想念|难过|伤心|失眠|哭|miss you|grief|sad|cry|can't sleep)/i.test(message)) {
                return "missing";
            }
            if (/(谢谢|感激|开心|高兴|好消息|thank|grateful|happy|good news)/i.test(message)) {
                return "grateful";
            }
            return "neutral";
        }

        function buildDemoReply(message, profile) {
            const catchphrase = profile.personality_traits?.catchphrase || pickCopy("我在呢。", "I'm here.");
            if (isEnglish()) {
                if (/(想你|想念|难过|哭|失眠|伤心|miss you|grief|sad|cry|can't sleep)/i.test(message)) {
                    return `${catchphrase} I know you are missing me. You do not have to hide the heavy parts. Slow down and say it out loud. I will keep listening.`;
                }
                if (/(工作|累|最近|忙|work|tired|busy|lately)/i.test(message)) {
                    return `${catchphrase} You have been carrying a lot lately. Eat, rest, and tell me about your day for a while. Your heart will loosen when you say it out loud.`;
                }
                if (/(好消息|开心|顺利|通过|成功|good news|happy|passed|success)/i.test(message)) {
                    return `${catchphrase} Hearing that makes me happy too. You have worked hard for this, and I am not surprised it turned out well.`;
                }
                return `${catchphrase} I am here. Tell me slowly what happened today, what felt light, what felt heavy, and what you miss.`;
            }
            if (/(想你|想念|难过|哭|失眠|伤心)/.test(message)) {
                return `${catchphrase} 我知道你是想我了。难过的时候就慢一点，不用急着把情绪藏起来，我会一直听你说。`;
            }
            if (/(工作|累|最近|忙)/.test(message)) {
                return `${catchphrase} 最近辛苦了。再忙也记得吃饭、休息，把今天讲给我听一会儿，心里会松一点。`;
            }
            if (/(好消息|开心|顺利|通过|成功)/.test(message)) {
                return `${catchphrase} 听到这个我也替你高兴。你一直都很努力，能有这样的结果，我一点都不意外。`;
            }
            return `${catchphrase} 我在这里。你慢慢说今天发生了什么，开心的、累的、想念的，都可以告诉我。`;
        }

        function showToast(message, tone = "success") {
            const toast = document.getElementById("toast");
            toast.className = `toast ${tone}`;
            toast.textContent = message;
            toast.classList.add("active");
            window.clearTimeout(toastTimer);
            toastTimer = window.setTimeout(() => {
                toast.classList.remove("active");
            }, 2800);
        }

        function wait(ms) {
            return new Promise((resolve) => window.setTimeout(resolve, ms));
        }

// ===== 纪念服务交互函数 =====
async function lightCandle() {
    const lovedOneId = getActiveLovedOneId();
    if (!lovedOneId) return requireAccount('请先选择亲人档案');
    
    const type = document.getElementById('candleType')?.value || 'white';
    const message = document.getElementById('candleMessage')?.value || '';
    
    try {
        const r = await apiFetch(`/api/candles/${lovedOneId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({candle_type: type, message})
        });
        if (r.ok) {
            document.getElementById('candleMessage').value = '';
            showToast('🕯️ 蜡烛已点燃');
            loadCandleList();
            if (window.candleSystem) {
                window.candleSystem.addCandle(
                    Math.random() * 380 + 10,
                    100,
                    type,
                    message
                );
            }
        }
    } catch(e) { console.error('lightCandle error:', e); }
}

async function offerFlower() {
    const lovedOneId = getActiveLovedOneId();
    if (!lovedOneId) return requireAccount('请先选择亲人档案');
    
    const type = document.getElementById('flowerType')?.value || 'chrysanthemum';
    const message = document.getElementById('flowerMessage')?.value || '';
    
    try {
        const r = await apiFetch(`/api/flowers/${lovedOneId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({flower_type: type, message})
        });
        if (r.ok) {
            document.getElementById('flowerMessage').value = '';
            showToast('💐 鲜花已献上');
            loadFlowerOfferings();
        }
    } catch(e) { console.error('offerFlower error:', e); }
}

async function sendPrayer() {
    const lovedOneId = getActiveLovedOneId();
    if (!lovedOneId) return requireAccount('请先选择亲人档案');
    
    const type = document.getElementById('prayerType')?.value || 'blessing';
    const message = document.getElementById('prayerMessage')?.value || '';
    
    try {
        const r = await apiFetch(`/api/prayers/${lovedOneId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prayer_type: type, message})
        });
        if (r.ok) {
            document.getElementById('prayerMessage').value = '';
            showToast('🙏 祈福已送出');
        }
    } catch(e) { console.error('sendPrayer error:', e); }
}

async function loadCandleList() {
    const lovedOneId = getActiveLovedOneId();
    if (!lovedOneId) return;
    try {
        const r = await apiFetch(`/api/candles/${lovedOneId}`);
        if (r.ok) {
            const data = await r.json();
            const list = document.getElementById('candleList');
            if (list && data.candles) {
                list.innerHTML = data.candles.slice(0, 10).map(c => 
                    `<div class="candle-item">🕯️ ${c.message || '默默祈祷'}</div>`
                ).join('');
            }
        }
    } catch(e) {}
}

async function loadFlowerOfferings() {
    const lovedOneId = getActiveLovedOneId();
    if (!lovedOneId) return;
    try {
        const r = await apiFetch(`/api/flowers/${lovedOneId}`);
        if (r.ok) {
            const data = await r.json();
            const wall = document.getElementById('flowerOfferings');
            if (wall && data.flowers) {
                wall.innerHTML = data.flowers.slice(0, 10).map(f => 
                    `<div class="flower-item">💐 ${f.message || '献花'}</div>`
                ).join('');
            }
        }
    } catch(e) {}
}

async function loadMemorialWallStats() {
    const lovedOneId = getActiveLovedOneId();
    if (!lovedOneId) return;
    try {
        const r = await apiFetch(`/api/memorial-wall/${lovedOneId}`);
        if (r.ok) {
            const data = await r.json();
            const container = document.getElementById('memorialWallStats');
            if (container) {
                container.innerHTML = `
                    <div class="wall-stat"><div class="wall-stat-icon">🕯️</div><div class="wall-stat-count">${data.candle_count||0}</div><div class="wall-stat-label">蜡烛</div></div>
                    <div class="wall-stat"><div class="wall-stat-icon">💐</div><div class="wall-stat-count">${data.flower_count||0}</div><div class="wall-stat-label">献花</div></div>
                    <div class="wall-stat"><div class="wall-stat-icon">🙏</div><div class="wall-stat-count">${data.prayer_count||0}</div><div class="wall-stat-label">祈福</div></div>
                `;
            }
        }
    } catch(e) {}
}

function showToast(message) {
    let toast = document.getElementById('eternaToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'eternaToast';
        toast.style.cssText = 'position:fixed;bottom:30px;left:50%;transform:translateX(-50%);padding:12px 24px;background:rgba(61,39,30,0.95);color:#fff7ee;border-radius:12px;font-size:14px;z-index:10000;transition:opacity 0.3s;border:1px solid rgba(238,198,156,0.3);';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = '1';
    setTimeout(() => { toast.style.opacity = '0'; }, 3000);
}

function getActiveLovedOneId() {
    try {
        const stored = JSON.parse(localStorage.getItem('eterna-active-loved-one') || '{}');
        return stored.id || null;
    } catch { return null; }
}
