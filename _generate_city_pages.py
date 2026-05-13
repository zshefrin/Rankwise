#!/usr/bin/env python3
"""Generate city-specific HVAC and Plumbing marketing pages for Rankwise."""
import os

CITIES = [
    {
        "name": "Vancouver",
        "slug": "vancouver-hvac-marketing",
        "eyebrow": "HVAC marketing agency · Vancouver, BC",
        "h1_city": "Vancouver.",
        "meta_title": "HVAC Marketing Agency in Vancouver | Rankwise",
        "meta_desc": "HVAC marketing for Vancouver contractors — Kitsilano, Mount Pleasant, Kerrisdale, and Marpole. Map Pack optimization and Google Business Profile management. One HVAC contractor per city.",
        "og_desc": "HVAC marketing for Vancouver contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "HVAC marketing in Vancouver: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Kitsilano, Mount Pleasant, Kerrisdale, and Marpole each have distinct search demand for furnace repair and heat pump installation.",
            "<strong>Google Business Profile activity</strong> — weekly posts with real job photos, responses to every review, and an accurate primary category tell Google your business is active and relevant.",
            "<strong>Review velocity</strong> — Vancouver contractors holding top-3 Map Pack positions carry a median of 275 reviews; contractors below 50 reviews are rarely competitive for high-intent queries.",
            "<strong>City-specific landing pages</strong> — one page per service area lets Google match your website to neighbourhood-level searches for furnace repair, AC installation, and heat pump service.",
        ],
        "hero_copy": "Your crew does great work. The opportunity is getting the dispatch line busier. We build the local search engine around your company so Vancouver homeowners find you first, trust you faster, and call before they call someone else.",
        "problem_stat": "In Vancouver, the median contractor holding a top-3 Map Pack position has 275 reviews — most new entrants have fewer than 30.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Vancouver — wherever high-intent homeowners are searching for furnace repair, AC installation, or heat pump service.",
        "cta_h2": "See your Vancouver Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Vancouver Map Pack data before the call so you can see exactly which calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one HVAC contractor per city — that's a hard rule. If Vancouver is open when you book the audit, your local competitors can't hire Rankwise while you're a client. It also means every strategy I build is built for your Vancouver market, not split across five contractors competing for the same jobs.",
        "utm_city": "vancouver",
    },
    {
        "name": "Burnaby",
        "slug": "burnaby-hvac-marketing",
        "eyebrow": "HVAC marketing agency · Burnaby, BC",
        "h1_city": "Burnaby.",
        "meta_title": "HVAC Marketing Agency in Burnaby | Rankwise",
        "meta_desc": "HVAC marketing for Burnaby contractors — Brentwood, Metrotown, and Lougheed. Map Pack and Google Business Profile management for furnace repair and HVAC service. One contractor per city.",
        "og_desc": "HVAC marketing for Burnaby contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "HVAC marketing in Burnaby: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Brentwood, Metrotown, and Lougheed are Burnaby's densest residential zones for furnace repair and HVAC installation searches.",
            "<strong>Google Business Profile activity</strong> — weekly posts with real job photos and consistent review responses signal an active, trustworthy business to Google and to homeowners reading your profile.",
            "<strong>Review velocity</strong> — Burnaby contractors with fewer than 30 reviews rarely appear in competitive Map Pack results for high-intent furnace repair and heating contractor queries.",
            "<strong>City-specific landing pages</strong> — a Burnaby-specific page lets Google match your business to neighbourhood-level searches for furnace repair, HVAC installation, and emergency heating service.",
        ],
        "hero_copy": "Burnaby homeowners search for furnace repair and HVAC help on Google every day. The opportunity is making sure they find your company first. We build the local search presence around your business so you get the call before a competitor does.",
        "problem_stat": "In Burnaby, furnace repair and near-me HVAC queries drive consistent year-round search volume — and most of those calls go to the contractors who appear in the top 3 Google Map Pack results.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Burnaby — wherever homeowners are searching for furnace repair, HVAC installation, or emergency heating service.",
        "cta_h2": "See your Burnaby Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Burnaby Map Pack data before the call so you can see exactly which calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one HVAC contractor per city — that's a hard rule. If Burnaby is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Burnaby market specifically.",
        "utm_city": "burnaby",
    },
    {
        "name": "Surrey",
        "slug": "surrey-hvac-marketing",
        "eyebrow": "HVAC marketing agency · Surrey, BC",
        "h1_city": "Surrey.",
        "meta_title": "HVAC Marketing Agency in Surrey | Rankwise",
        "meta_desc": "HVAC marketing for Surrey contractors — Cloverdale, Newton, Fleetwood, South Surrey. Local SEO and GBP management for BC's largest city. One HVAC contractor per city.",
        "og_desc": "HVAC marketing for Surrey contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "HVAC marketing in Surrey: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Cloverdale, Newton, Fleetwood, and South Surrey drive high HVAC installation search volume as BC's largest city (~600,000 population) with active new-build development.",
            "<strong>Google Business Profile activity</strong> — consistent weekly posting and review responses maintain visibility as Surrey's rapid growth drives heat pump and HVAC installation searches year-round.",
            "<strong>Review velocity</strong> — Surrey's competitive HVAC market rewards contractors with strong review velocity; new-build areas like Fleetwood and South Surrey generate disproportionate search volume for heat pump installation.",
            "<strong>City-specific landing pages</strong> — Surrey neighbourhood pages capture installation and furnace replacement searches from homeowners in new-build developments who are actively looking to book.",
        ],
        "hero_copy": "Surrey is one of Metro Vancouver's fastest-growing markets for HVAC installation and service. The contractors winning the most calls aren't the biggest — they're the ones Google shows first. We build that visibility around your business.",
        "problem_stat": "Surrey HVAC installation and residential service queries are among the highest-volume in Metro Vancouver — but most of those searches resolve to the same 2–3 contractors showing up in the Map Pack.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Surrey — wherever homeowners are searching for HVAC installation, furnace replacement, or air conditioning service.",
        "cta_h2": "See your Surrey Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Surrey Map Pack data before the call so you can see exactly which calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one HVAC contractor per city — that's a hard rule. If Surrey is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Surrey market specifically.",
        "utm_city": "surrey",
    },
    {
        "name": "Richmond",
        "slug": "richmond-hvac-marketing",
        "eyebrow": "HVAC marketing agency · Richmond, BC",
        "h1_city": "Richmond.",
        "meta_title": "HVAC Marketing Agency in Richmond | Rankwise",
        "meta_desc": "HVAC marketing for Richmond contractors — Steveston, Brighouse, Hamilton. Map Pack and GBP management for AC repair, heat pump, and furnace service. One contractor per city.",
        "og_desc": "HVAC marketing for Richmond contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "HVAC marketing in Richmond: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Steveston, Brighouse, and Hamilton are Richmond's densest residential zones, with year-round demand for AC repair, heat pump installation, and furnace service.",
            "<strong>Google Business Profile activity</strong> — active GBP with frequent job photos and review responses signals relevance for Richmond homeowners searching for HVAC service.",
            "<strong>Review velocity</strong> — Richmond's top-3 Map Pack positions are typically held by contractors with 30–60 reviews and a consistent response pattern; below 20 reviews it is difficult to appear for competitive queries.",
            "<strong>City-specific landing pages</strong> — Richmond-specific pages target city-level searches for AC repair, heat pump installation, and furnace service from a dense, high-intent residential market.",
        ],
        "hero_copy": "Richmond homeowners search for AC repair, heat pump service, and furnace work year-round. We build the local search presence that puts your company in front of those searches — before a competitor gets the call.",
        "problem_stat": "Richmond's dense residential market means high HVAC search volume, but most of those searches convert to the same handful of contractors who dominate the local Map Pack.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Richmond — wherever homeowners are searching for AC repair, heat pump installation, or furnace service.",
        "cta_h2": "See your Richmond Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Richmond Map Pack data before the call so you can see exactly which calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one HVAC contractor per city — that's a hard rule. If Richmond is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Richmond market specifically.",
        "utm_city": "richmond",
    },
    {
        "name": "North Vancouver",
        "slug": "north-vancouver-hvac-marketing",
        "eyebrow": "HVAC marketing agency · North Vancouver, BC",
        "h1_city": "North Vancouver.",
        "meta_title": "HVAC Marketing Agency in North Vancouver | Rankwise",
        "meta_desc": "HVAC marketing for North Vancouver contractors — Lonsdale, Lynn Valley, Deep Cove, Capilano. Map Pack and GBP for furnace repair and heat pump installation. One contractor per city.",
        "og_desc": "HVAC marketing for North Vancouver contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "HVAC marketing in North Vancouver: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Lonsdale, Lynn Valley, Deep Cove, and Capilano each have distinct search demand; North Vancouver has higher average job values and strong heat pump installation intent compared to most Metro Vancouver markets.",
            "<strong>Google Business Profile activity</strong> — North Vancouver homeowners expect well-maintained listings and prompt responses; active GBP management is essential for building credibility in a market where trust matters.",
            "<strong>Review velocity</strong> — North Vancouver furnace repair and heat pump searches route almost entirely to the top-3 Map Pack results; contractors below that visibility threshold see very few inbound calls from organic search.",
            "<strong>City-specific landing pages</strong> — North Vancouver city pages capture distinct search intent across neighbourhoods, including heat pump installation searches from Lynn Valley and Capilano homeowners considering electrification upgrades.",
        ],
        "hero_copy": "North Vancouver homeowners call HVAC contractors year-round — furnace work in winter, AC and heat pump service in summer. We make sure your company is the one they find when they search.",
        "problem_stat": "North Vancouver HVAC searches — especially for furnace repair and heating contractors — consistently flow to the top 3 Map Pack results. Most contractors below that threshold get very few organic calls.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across North Vancouver — wherever homeowners are searching for furnace repair, heating contractors, or HVAC service.",
        "cta_h2": "See your North Vancouver Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live North Vancouver Map Pack data before the call so you can see exactly which calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one HVAC contractor per city — that's a hard rule. If North Vancouver is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your North Vancouver market specifically.",
        "utm_city": "north-vancouver",
    },
    {
        "name": "Coquitlam",
        "slug": "coquitlam-hvac-marketing",
        "eyebrow": "HVAC marketing agency · Coquitlam, BC",
        "h1_city": "Coquitlam.",
        "meta_title": "HVAC Marketing Agency in Coquitlam | Rankwise",
        "meta_desc": "HVAC marketing for Coquitlam contractors — Town Centre, Burke Mountain, Westwood Plateau. Heat pump and furnace Map Pack optimization. One HVAC contractor per city.",
        "og_desc": "HVAC marketing for Coquitlam contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "HVAC marketing in Coquitlam: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Town Centre, Burke Mountain, and Westwood Plateau are fast-growing residential areas with strong demand for heat pump installation and ductless retrofit work.",
            "<strong>Google Business Profile activity</strong> — Coquitlam's growing suburban neighbourhoods drive consistent new HVAC installation searches; active GBP with job photos from local installs builds trust and ranking authority.",
            "<strong>Review velocity</strong> — Coquitlam heating contractor searches route almost entirely to the top-3 local Map Pack positions; contractors without a strong review profile see very few organic inbound calls.",
            "<strong>City-specific landing pages</strong> — Coquitlam pages capture heat pump installation and ductless retrofit searches from homeowners in Burke Mountain and Westwood Plateau new developments, where installations are at a premium.",
        ],
        "hero_copy": "Coquitlam homeowners searching for heating contractors and HVAC service are booking from the top of Google Maps. We build the visibility that puts your company in those results — and keeps competitors out.",
        "problem_stat": "Coquitlam heating contractor and HVAC service searches route almost entirely to contractors in the top 3 local Map Pack positions. Visibility below that threshold means very few inbound calls.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Coquitlam — wherever homeowners are searching for heating contractors, furnace repair, or HVAC installation.",
        "cta_h2": "See your Coquitlam Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Coquitlam Map Pack data before the call so you can see exactly which calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one HVAC contractor per city — that's a hard rule. If Coquitlam is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Coquitlam market specifically.",
        "utm_city": "coquitlam",
    },
]

PLUMBING_CITIES = [
    {
        "name": "Vancouver",
        "slug": "vancouver-plumbing-marketing",
        "eyebrow": "Plumbing marketing agency · Vancouver, BC",
        "h1_city": "Vancouver.",
        "meta_title": "Plumbing Marketing Agency in Vancouver | Rankwise",
        "meta_desc": "Plumbing marketing for Vancouver contractors — Kitsilano, Mount Pleasant, Kerrisdale, and Marpole. Map Pack optimization and GBP management for drain cleaning and water heater replacement. One plumbing contractor per city.",
        "og_desc": "Plumbing marketing for Vancouver contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "Plumbing marketing in Vancouver: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Kitsilano, Mount Pleasant, Kerrisdale, and Marpole each generate high search demand for drain cleaning and water heater replacement, driven by Vancouver's median housing build year of 1975 and an ageing cast-iron drain stock.",
            "<strong>Google Business Profile activity</strong> — weekly posts with real job photos of water heater swaps and drain work, responses to every review, and an accurate primary category tell Google your business is active and relevant.",
            "<strong>Review velocity</strong> — Vancouver plumbing contractors holding top-3 Map Pack positions consistently carry strong review profiles; contractors with fewer than 30 reviews rarely appear for high-intent drain and water heater queries.",
            "<strong>City-specific landing pages</strong> — neighbourhood-level pages let Google match your website to searches for drain cleaning, water heater replacement, and sewer line repair across Vancouver's distinct service areas.",
        ],
        "hero_copy": "Vancouver's housing stock — most of it built before 1980 — means cast-iron drains failing and water heaters hitting end-of-life are a consistent call driver all year. We build the local search presence that puts your plumbing company in front of those homeowners before they dial a competitor.",
        "problem_stat": "In Vancouver, ageing cast-iron drains and end-of-life water heaters in pre-1980 homes generate year-round plumbing search volume — and most of those calls resolve to the contractors who dominate the local Map Pack.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Vancouver — wherever homeowners are searching for drain cleaning, water heater replacement, or sewer line repair.",
        "cta_h2": "See your Vancouver Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Vancouver Map Pack data before the call so you can see exactly which drain and water heater calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one plumbing contractor per city — that's a hard rule. If Vancouver is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Vancouver market, not split across multiple contractors competing for the same drain and water heater calls.",
        "utm_city": "plumbing-vancouver",
        "trade_label": "Plumbing",
    },
    {
        "name": "Burnaby",
        "slug": "burnaby-plumbing-marketing",
        "eyebrow": "Plumbing marketing agency · Burnaby, BC",
        "h1_city": "Burnaby.",
        "meta_title": "Plumbing Marketing Agency in Burnaby | Rankwise",
        "meta_desc": "Plumbing marketing for Burnaby contractors — Brentwood, Metrotown, Lougheed. Map Pack and GBP management for drain cleaning and water heater replacement. One plumbing contractor per city.",
        "og_desc": "Plumbing marketing for Burnaby contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "Plumbing marketing in Burnaby: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Brentwood, Metrotown, and Lougheed are Burnaby's densest residential zones, with a mix of pre-1980 condos and townhomes driving consistent drain cleaning and water heater call volume year-round.",
            "<strong>Google Business Profile activity</strong> — regular posts featuring local water heater installations and drain jobs, paired with prompt review responses, signal an active and trustworthy business to both Google and homeowners.",
            "<strong>Review velocity</strong> — Burnaby plumbing contractors with fewer than 25 reviews rarely appear in competitive Map Pack results for high-intent drain and water heater replacement queries.",
            "<strong>City-specific landing pages</strong> — Burnaby-specific pages let Google match your business to neighbourhood-level searches for hot water tank replacement, drain cleaning, and emergency plumbing service.",
        ],
        "hero_copy": "Burnaby's pre-1980 condo and townhome stock keeps drain cleaning and water heater replacement calls steady all year. We build the local search presence that puts your plumbing company at the top of those searches — before a competitor picks up the phone.",
        "problem_stat": "In Burnaby, drain cleaning and water heater replacement searches driven by the city's ageing pre-1980 condo stock flow almost entirely to plumbing contractors in the top 3 Map Pack positions.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Burnaby — wherever homeowners are searching for drain cleaning, hot water tank replacement, or emergency plumbing service.",
        "cta_h2": "See your Burnaby Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Burnaby Map Pack data before the call so you can see exactly which drain and water heater calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one plumbing contractor per city — that's a hard rule. If Burnaby is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Burnaby market specifically.",
        "utm_city": "plumbing-burnaby",
        "trade_label": "Plumbing",
    },
    {
        "name": "Surrey",
        "slug": "surrey-plumbing-marketing",
        "eyebrow": "Plumbing marketing agency · Surrey, BC",
        "h1_city": "Surrey.",
        "meta_title": "Plumbing Marketing Agency in Surrey | Rankwise",
        "meta_desc": "Plumbing marketing for Surrey contractors — Cloverdale, Newton, Fleetwood, South Surrey. Local SEO and GBP management for water heater installation and drain service. One plumbing contractor per city.",
        "og_desc": "Plumbing marketing for Surrey contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "Plumbing marketing in Surrey: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Cloverdale, Newton, Fleetwood, and South Surrey drive high plumbing installation search volume; as BC's fastest-growing city, new builds in Surrey generate disproportionate water heater installation demand.",
            "<strong>Google Business Profile activity</strong> — consistent weekly posting with water heater installation photos and review responses keeps your listing visible as Surrey's rapid growth drives new plumbing search volume year-round.",
            "<strong>Review velocity</strong> — Surrey's competitive plumbing market rewards contractors with strong review velocity; new-build areas like Fleetwood and South Surrey generate high search volume for water heater installation and drain connection work.",
            "<strong>City-specific landing pages</strong> — Surrey neighbourhood pages capture water heater installation and drain service searches from homeowners in new developments who are actively ready to book.",
        ],
        "hero_copy": "Surrey's rapid growth means new-build water heater installations and drain connection work are constant. At the same time, older Newton and Cloverdale neighbourhoods keep sewer line and drain cleaning calls coming year-round. We make sure your plumbing company captures both.",
        "problem_stat": "Surrey water heater installation and residential plumbing queries are among the highest-volume in Metro Vancouver — but most of those searches resolve to the same handful of contractors in the local Map Pack.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Surrey — wherever homeowners are searching for water heater installation, drain cleaning, or sewer line repair.",
        "cta_h2": "See your Surrey Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Surrey Map Pack data before the call so you can see exactly which water heater and drain calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one plumbing contractor per city — that's a hard rule. If Surrey is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Surrey market specifically.",
        "utm_city": "plumbing-surrey",
        "trade_label": "Plumbing",
    },
    {
        "name": "Richmond",
        "slug": "richmond-plumbing-marketing",
        "eyebrow": "Plumbing marketing agency · Richmond, BC",
        "h1_city": "Richmond.",
        "meta_title": "Plumbing Marketing Agency in Richmond | Rankwise",
        "meta_desc": "Plumbing marketing for Richmond contractors — Steveston, Brighouse, Hamilton. Map Pack and GBP management for water heater replacement and drain service. One plumbing contractor per city.",
        "og_desc": "Plumbing marketing for Richmond contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "Plumbing marketing in Richmond: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Steveston, Brighouse, and Hamilton are Richmond's densest residential zones, with a high proportion of 20–30 year old water heaters approaching end of life driving a consistent replacement call cycle.",
            "<strong>Google Business Profile activity</strong> — active GBP with frequent water heater and drain job photos, and prompt review responses, signals relevance for Richmond homeowners searching for plumbing service.",
            "<strong>Review velocity</strong> — Richmond's top-3 Map Pack positions are typically held by plumbing contractors with a consistent review history; below 20 reviews it is difficult to appear for competitive hot water tank replacement queries.",
            "<strong>City-specific landing pages</strong> — Richmond-specific pages target city-level searches for water heater replacement, drain cleaning, and sewer line repair from a dense, high-intent residential market.",
        ],
        "hero_copy": "Richmond's dense residential neighbourhoods — Steveston, Brighouse, Hamilton — are home to a large stock of water heaters now 20 to 30 years old. That means end-of-life replacement calls are a reliable, recurring revenue driver. We make sure your plumbing company owns those searches.",
        "problem_stat": "Richmond's high proportion of 20–30 year old residential water heaters creates consistent end-of-life replacement search volume — but most of those calls go to the contractors who dominate the local Map Pack.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Richmond — wherever homeowners are searching for water heater replacement, drain cleaning, or sewer line repair.",
        "cta_h2": "See your Richmond Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Richmond Map Pack data before the call so you can see exactly which water heater and drain calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one plumbing contractor per city — that's a hard rule. If Richmond is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Richmond market specifically.",
        "utm_city": "plumbing-richmond",
        "trade_label": "Plumbing",
    },
    {
        "name": "North Vancouver",
        "slug": "north-vancouver-plumbing-marketing",
        "eyebrow": "Plumbing marketing agency · North Vancouver, BC",
        "h1_city": "North Vancouver.",
        "meta_title": "Plumbing Marketing Agency in North Vancouver | Rankwise",
        "meta_desc": "Plumbing marketing for North Vancouver contractors — Lonsdale, Lynn Valley, Deep Cove. Map Pack and GBP for drain cleaning, sewer line repair, and water heater replacement. One plumbing contractor per city.",
        "og_desc": "Plumbing marketing for North Vancouver contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "Plumbing marketing in North Vancouver: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Lonsdale, Lynn Valley, and Deep Cove each generate distinct plumbing search demand; North Vancouver's older detached housing stock drives above-average job values for sewer line repair and drain work.",
            "<strong>Google Business Profile activity</strong> — North Vancouver homeowners research carefully before booking; active GBP management with sewer line and drain job photos and prompt review responses builds the credibility that converts searches into calls.",
            "<strong>Review velocity</strong> — North Vancouver plumbing searches route almost entirely to the top-3 Map Pack results; contractors without a strong review profile and active listing see very few inbound calls from organic search.",
            "<strong>City-specific landing pages</strong> — North Vancouver city pages capture distinct search intent, including sewer line repair searches from Lynn Valley and Deep Cove homeowners dealing with older drain infrastructure.",
        ],
        "hero_copy": "North Vancouver's older detached housing stock — Lonsdale, Lynn Valley, Deep Cove — means sewer line issues, ageing drain systems, and end-of-life water heaters are a constant call driver. We build the local search presence that puts your plumbing company in front of those high-value jobs first.",
        "problem_stat": "North Vancouver plumbing searches — especially for sewer line repair and drain cleaning — consistently flow to the top 3 Map Pack results. Most plumbing contractors below that threshold see very few organic calls.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across North Vancouver — wherever homeowners are searching for drain cleaning, sewer line repair, or water heater replacement.",
        "cta_h2": "See your North Vancouver Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live North Vancouver Map Pack data before the call so you can see exactly which drain and sewer calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one plumbing contractor per city — that's a hard rule. If North Vancouver is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your North Vancouver market specifically.",
        "utm_city": "plumbing-north-vancouver",
        "trade_label": "Plumbing",
    },
    {
        "name": "Coquitlam",
        "slug": "coquitlam-plumbing-marketing",
        "eyebrow": "Plumbing marketing agency · Coquitlam, BC",
        "h1_city": "Coquitlam.",
        "meta_title": "Plumbing Marketing Agency in Coquitlam | Rankwise",
        "meta_desc": "Plumbing marketing for Coquitlam contractors — Town Centre, Burke Mountain, Westwood Plateau. Map Pack optimization for water heater installation and drain service. One plumbing contractor per city.",
        "og_desc": "Plumbing marketing for Coquitlam contractors. One client per city. Month-to-month, results guaranteed.",
        "aio_heading": "Plumbing marketing in Coquitlam: four signals that decide who gets the call",
        "aio_items": [
            "<strong>Google Map Pack coverage</strong> across your service area — Town Centre, Burke Mountain, and Westwood Plateau are fast-growing residential areas with strong demand for water heater installation and drain connection work driven by rapid new development.",
            "<strong>Google Business Profile activity</strong> — Coquitlam's expanding suburban neighbourhoods drive consistent new plumbing installation searches; active GBP with water heater and drain job photos from local installs builds trust and ranking authority.",
            "<strong>Review velocity</strong> — Coquitlam plumbing searches route almost entirely to the top-3 local Map Pack positions; contractors without a strong review profile see very few organic inbound calls from new homeowners.",
            "<strong>City-specific landing pages</strong> — Coquitlam pages capture water heater installation and drain connection searches from homeowners in Burke Mountain and Westwood Plateau new developments, where first-time plumbing service demand is high.",
        ],
        "hero_copy": "Coquitlam's rapid development — Burke Mountain, Westwood Plateau, Town Centre — means water heater installations and new drain connections are a consistent high-volume call driver. We build the local search visibility that puts your plumbing company at the top of those searches and keeps competitors out.",
        "problem_stat": "Coquitlam plumbing searches — especially for water heater installation and drain connection work in new developments — route almost entirely to contractors in the top 3 local Map Pack positions.",
        "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Coquitlam — wherever homeowners are searching for water heater installation, drain cleaning, or plumbing service.",
        "cta_h2": "See your Coquitlam Map Pack standing in 15 minutes.",
        "cta_sub": "We pull your live Coquitlam Map Pack data before the call so you can see exactly which water heater and drain calls are going to competitors — and what it would take to change that.",
        "faq_exclusivity": "No. I take one plumbing contractor per city — that's a hard rule. If Coquitlam is open when you book the audit, your local competitors can't hire Rankwise while you're a client. Every strategy I build is built for your Coquitlam market specifically.",
        "utm_city": "plumbing-coquitlam",
        "trade_label": "Plumbing",
    },
]

PLUMBING_LANDING = {
    "name": "Metro Vancouver",
    "slug": "plumbing",
    "eyebrow": "Plumbing marketing agency · Metro Vancouver, BC",
    "h1_city": "Metro Vancouver.",
    "meta_title": "Plumbing Marketing Agency in Metro Vancouver | Rankwise",
    "meta_desc": "Plumbing marketing for Metro Vancouver contractors — drain cleaning, water heater replacement, and sewer line repair. GBP and Map Pack management. One contractor per city.",
    "og_desc": "Plumbing marketing for Metro Vancouver contractors. One client per city. Month-to-month, results guaranteed.",
    "aio_heading": "Plumbing marketing in Metro Vancouver: four signals that decide who gets the call",
    "aio_items": [
        "<strong>Google Map Pack placement</strong> is where most plumbing calls originate — homeowners searching for drain cleaning or a water heater replacement tap the first three results on the map, rarely scrolling further. Ranking in that pack is not optional if you want consistent inbound volume.",
        "<strong>Google Business Profile activity</strong> drives Map Pack ranking and conversion together — regular posts with real job photos, responses to every review, and an accurate service area tell Google your business is active and trusted in Metro Vancouver.",
        "<strong>Review velocity and recency</strong> separate the contractors who win calls from the ones who don't — Metro Vancouver plumbing contractors holding top-3 positions consistently show recent reviews; a stagnant review profile signals inactivity to both Google and homeowners.",
        "<strong>City-specific landing pages</strong> let Google match your website to high-intent neighbourhood-level searches — a homeowner in Steveston searching for water heater replacement near me should land on a page built for Richmond, not a generic Metro Vancouver page.",
    ],
    "hero_copy": "Metro Vancouver's mix of ageing housing stock and rapid new development creates consistent, year-round plumbing call volume — drain cleaning in older Vancouver and Burnaby neighbourhoods, water heater installations in new Surrey and Coquitlam builds, sewer line work in North Vancouver's older detached homes. We build the local search presence that routes those calls to your company.",
    "problem_stat": "Across Metro Vancouver, most plumbing searches — drain cleaning, water heater replacement, sewer line repair — resolve to the same 2–3 contractors showing up in the Map Pack. Visibility below that threshold means very few organic calls.",
    "services_copy": "We tighten your Google Business Profile and local SEO structure so your company shows up across Metro Vancouver — wherever homeowners are searching for drain cleaning, water heater replacement, or sewer line repair.",
    "cta_h2": "See your Metro Vancouver Map Pack standing in 15 minutes.",
    "cta_sub": "We pull your live Metro Vancouver Map Pack data before the call so you can see exactly which drain cleaning and water heater calls are going to competitors — and what it would take to change that.",
    "faq_exclusivity": "No. I take one plumbing contractor per city across Metro Vancouver — that's a hard rule. If your city is open when you book the audit, your local competitors can't hire Rankwise while you're a client.",
    "utm_city": "plumbing-landing",
    "trade_label": "Plumbing",
}

CSS = open(os.path.join(os.path.dirname(__file__), "index.html")).read().split("<style>")[1].split("</style>")[0]

CITY_EXTRA_CSS = """
.city-intel{padding:48px 52px;background:rgba(255,255,255,0.025);border-top:1px solid var(--line)}
.city-intel-inner{max-width:780px;margin:0 auto}
.city-intel-h{font-family:var(--display);font-size:clamp(17px,1.8vw,21px);font-weight:700;color:var(--ink);margin-bottom:18px;line-height:1.3}
.city-intel-list{padding-left:22px;display:flex;flex-direction:column;gap:10px;margin:0}
.city-intel-list li{font-size:15px;color:var(--ink-soft);line-height:1.68}
.city-intel-list li strong{color:var(--ink);font-weight:600}
.city-links{padding:28px 52px;border-top:1px solid var(--line)}
.city-links .container{max-width:1150px;margin:0 auto}
.city-links-label{font-family:var(--display);font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:12px}
.city-links-list{display:flex;flex-wrap:wrap;gap:10px}
.city-links-list a{font-size:13px;color:var(--ink-soft);text-decoration:none;font-weight:600;padding:6px 14px;border:1px solid var(--line);border-radius:999px;transition:color .15s,border-color .15s}
.city-links-list a:hover{color:var(--ink);border-color:var(--line-strong)}
@media(max-width:700px){.city-intel{padding:36px 20px}.city-links{padding:24px 20px}}
"""


def _city_links_html(current_slug: str, cities_list: list, tl: str = "HVAC") -> str:
    others = [c for c in cities_list if c["slug"] != current_slug]
    links = "\n      ".join(
        f'<a href="/{c["slug"]}/">{c["name"]} {tl} marketing</a>' for c in others
    )
    return f"""<section class="city-links">
  <div class="container">
    <p class="city-links-label">We also serve</p>
    <div class="city-links-list">
      {links}
    </div>
  </div>
</section>"""


def _aio_section_html(c: dict) -> str:
    items_html = "\n        ".join(
        f"<li>{item}</li>" for item in c["aio_items"]
    )
    return f"""<section class="city-intel">
  <div class="city-intel-inner reveal in">
    <h2 class="city-intel-h">{c['aio_heading']}</h2>
    <ol class="city-intel-list">
        {items_html}
    </ol>
  </div>
</section>"""


def build_page(c, cities_list):
    tl = c.get("trade_label", "HVAC")
    slug = c["slug"]
    name = c["name"]
    utm = c["utm_city"]
    canonical = f"https://rankwise.ca/{slug}/"

    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{c["meta_title"]}</title>
<meta name="description" content="{c["meta_desc"]}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{c["meta_title"]}">
<meta property="og:description" content="{c["og_desc"]}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{c["meta_title"]}">
<meta name="twitter:description" content="{c["og_desc"]}">
<meta name="robots" content="index, follow">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-LRX309H9CH"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());var _rwInt=document.cookie.split(';').some(function(c){{return c.trim()==='internal_traffic=true';}});gtag('config','G-LRX309H9CH',_rwInt?{{traffic_type:'internal'}}:{{}});</script>
<link rel="preconnect" href="https://app.cal.com" crossorigin>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Rankwise",
  "description": "{tl} marketing agency serving {name}, BC — one contractor per city, no exceptions. Local SEO and Google Business Profile management for heating and cooling contractors.",
  "url": "https://rankwise.ca",
  "image": "https://rankwise.ca/rankwise-icon.svg.png",
  "email": "zshef@rankwise.ca",
  "address": {{
    "@type": "PostalAddress",
    "addressLocality": "Metro Vancouver",
    "addressRegion": "BC",
    "addressCountry": "CA"
  }},
  "areaServed": [{{"@type": "City", "name": "{name}", "containedInPlace": {{"@type": "AdministrativeArea", "name": "British Columbia"}}}}],
  "knowsAbout": ["Local SEO", "Google Business Profile Management", "Content Marketing", "{tl} Marketing", "Search Engine Optimization", "Map Pack Optimization", "Review Management"],
  "priceRange": "$$",
  "telephone": "+1-778-887-0311",
  "openingHoursSpecification": {{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "opens": "09:00",
    "closes": "18:00"
  }},
  "founder": {{
    "@type": "Person",
    "name": "Zackary Shefrin",
    "sameAs": "https://www.wikidata.org/wiki/Q139590851"
  }}
}}
</script>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type":"Question","name":"How much of my time does this take?","acceptedAnswer":{{"@type":"Answer","text":"About 30 minutes upfront for a quick onboarding call where we get access to your Google listing and learn about your business. After that, we just need you to send us job photos when you finish installs — a quick phone pic works fine. That's it. We handle everything else."}}}},
    {{"@type":"Question","name":"What if it doesn't work?","acceptedAnswer":{{"@type":"Answer","text":"We set specific, measurable targets with you every month. If we don't hit the agreed target at the end of the month, you get your money back for that month. No arguing about it, no fine print."}}}},
    {{"@type":"Question","name":"Am I locked into a contract?","acceptedAnswer":{{"@type":"Answer","text":"No long-term contracts. It's month-to-month — if you want to stop, give us 30 days notice and that's it."}}}},
    {{"@type":"Question","name":"Do you work with other {tl} contractors in {name}?","acceptedAnswer":{{"@type":"Answer","text":"{c["faq_exclusivity"]}"}}}}
  ]
}}
</script>

<style>{CSS}{CITY_EXTRA_CSS}</style>
</head>
<body>
<nav>
  <a href="/" class="logo">Rank<span>wise</span></a>
  <ul class="nav-links">
    <li><a href="/#services">What we do</a></li>
    <li><a href="/#how">How it works</a></li>
    <li><a href="/#results">Results</a></li>
    <li><a href="/#faq">FAQ</a></li>
    <li><a href="/blog/">Blog</a></li>
    <li><a href="/lab/">Lab</a></li>
  </ul>
  <a href="/audit/?utm_source={utm}&amp;utm_medium=cta&amp;utm_content=nav" class="nav-cta">Book free audit</a>
</nav>

<section class="hero">
  <div class="container hero-grid">
    <div class="hero-left reveal in">
      <div class="eyebrow">{c["eyebrow"]}</div>
      <h1>Get more booked<br>{tl} jobs in <span class="serif">{c["h1_city"]}</span></h1>
      <div class="hero-lock">
        <div>No contracts.<br>Month to month.</div>
        <div>One {tl} contractor<br>per city.</div>
        <div>If we miss targets,<br>you do not pay for that month.</div>
      </div>
      <p class="hero-copy">{c["hero_copy"]}</p>
      <div class="hero-actions">
        <a href="/audit/?utm_source={utm}&amp;utm_medium=cta&amp;utm_content=hero" class="btn-primary">Book my free {tl} audit</a>
        <a href="/#services" class="btn-secondary">See how it works</a>
      </div>
    </div>
    <aside class="hero-right reveal in">
      <h3>What you get on the call</h3>
      <div class="mini">
        <strong>Live map pack breakdown</strong>
        <span>See who outranks you and why in your {name} service area.</span>
      </div>
      <div class="mini">
        <strong>Call volume upside</strong>
        <span>An estimate of the calls you're leaving on the table each month in {name} — and what they're worth in jobs.</span>
      </div>
      <div class="mini">
        <strong>90-day action plan</strong>
        <span>Clear first moves for GBP, SEO, and lead conversion in your market.</span>
      </div>
    </aside>
  </div>
</section>

{_aio_section_html(c)}

<section>
  <div class="container">
    <div class="section-head reveal in">
      <div class="label">The gap we fix</div>
      <h2>Solid install team,<br>weak <span class="serif">inbound flow.</span></h2>
      <p class="sub">Most {tl} owners in {name} already run solid businesses. The opportunity is turning more Google search demand into booked calls each week.</p>
    </div>
    <div class="problem-grid">
      <article class="problem-card reveal in">
        <h3>Feast-or-famine calendar</h3>
        <p>Referrals keep you alive, but they do not create predictable weeks for your crew or your cash flow.</p>
      </article>
      <article class="problem-card reveal in">
        <h3>Great work, quiet Google</h3>
        <p>{c["problem_stat"]}</p>
      </article>
      <article class="problem-card reveal in">
        <h3>No time for marketing ops</h3>
        <p>You are running service calls, estimates, and team logistics. You should not also be babysitting search systems.</p>
      </article>
    </div>
  </div>
</section>

<section class="services" id="services">
  <div class="container">
    <div class="section-head reveal in">
      <div class="label">What we do</div>
      <h2>One operator.<br>Three engines.<br><span class="serif">One outcome.</span></h2>
      <p class="sub">Everything points to one metric that matters: more qualified calls from {name} homeowners ready to book.</p>
    </div>
    <div class="services-grid">
      <article class="service-card reveal in">
        <h3>Your Google listing</h3>
        <p>{c["services_copy"]}</p>
        <div class="service-list">
          <div>GBP optimization and posting cadence</div>
          <div>City-level service page structure</div>
          <div>Review velocity and response support</div>
        </div>
      </article>
      <article class="service-card reveal in">
        <h3>Turning searches into calls</h3>
        <p>Ranking is step one. Our {tl} lead generation layer tightens page clarity, proof, and calls to action so clicks become booked conversations.</p>
        <div class="service-list">
          <div>Landing page and audit funnel positioning</div>
          <div>Offer framing for contractor buyers</div>
          <div>Lead journey tracking from click to booking</div>
        </div>
      </article>
      <article class="service-card reveal in">
        <h3>Weekly results signal</h3>
        <p>You get a clean weekly signal loop so we can cut what does not work and double down on what produces calls.</p>
        <div class="service-list">
          <div>GA4 event and key-event tracking</div>
          <div>GSC and ranking movement snapshots</div>
          <div>Action-first weekly scorecard</div>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="how" id="how">
  <div class="container">
    <div class="section-head reveal in">
      <div class="label">How it works</div>
      <h2>You stay on jobs.<br>We keep the <span class="serif">calls coming in.</span></h2>
      <p class="sub">Simple operating model. You keep the field running. We keep inbound momentum running.</p>
    </div>
    <div class="how-grid">
      <article class="step reveal in">
        <div class="step-num">STEP 01</div>
        <h3>Diagnostic audit</h3>
        <p>We compare your current visibility against local {name} competitors and identify the fastest opportunities by service intent.</p>
      </article>
      <article class="step reveal in">
        <div class="step-num">STEP 02</div>
        <h3>System build and launch</h3>
        <p>We set up positioning, content, and conversion assets so your brand looks like the clear trusted option in {name}.</p>
      </article>
      <article class="step reveal in">
        <div class="step-num">STEP 03</div>
        <h3>Weekly optimization loop</h3>
        <p>Every week we review traffic quality, booking events, and ranking movement, then adjust the next sprint so momentum compounds.</p>
      </article>
    </div>
  </div>
</section>

<section class="results" id="results">
  <div class="container">
    <div class="section-head reveal in">
      <div class="label">What to expect</div>
      <h2>Real timeline.<br>Real tradeoffs.<br><span class="serif">No fake promises.</span></h2>
    </div>
    <div class="results-grid">
      <article class="result-main reveal in">
        <h3>Ramp window most contractors see</h3>
        <div class="timeline">
          <div><strong>First 30 days</strong>Profile quality and local visibility improve. More discovery events, cleaner lead path.</div>
          <div><strong>Days 30 to 90</strong>Rank movement compounds. Calls from non-referral homeowners start to rise.</div>
          <div><strong>After month 3</strong>Pipeline becomes more stable, less dependent on random referral timing.</div>
        </div>
      </article>
      <article class="result-side reveal in">
        <h3>How we protect your position in {name}</h3>
        <p>We do not work with multiple {tl} companies in {name}. That keeps your market message focused and your growth plan clean.</p>
        <p style="margin-top:10px">If a move does not help call quality or booking volume, we do not keep it in the system.</p>
      </article>
    </div>
  </div>
</section>

<section class="cta" id="contact">
  <div class="container">
    <div class="section-head reveal in">
      <div class="label">Free {tl} audit</div>
      <h2>{c["cta_h2"]}</h2>
      <p class="sub">{c["cta_sub"]}</p>
    </div>
    <div class="cta-promise reveal in">
      <div>No contracts. Month to month.</div>
      <div>One {tl} contractor per city.</div>
      <div>If we miss targets, you do not pay for that month.</div>
    </div>
    <a href="/audit/?utm_source={utm}&amp;utm_medium=cta&amp;utm_content=founder-card" class="founder-card reveal in">
      <div class="founder-avatar">ZS</div>
      <div class="founder-text">
        <strong>Zack Shefrin — Founder, Rankwise</strong>
        <span>Every audit lands in my inbox, not a team's. I work with {tl} contractors only, one per city, and I review the numbers myself before every call.</span>
      </div>
    </a>
    <div class="reveal in" id="cal-embed"></div>
    <p class="cta-note reveal in">{name} only · Results guarantee included</p>
  </div>
</section>

<section class="faq" id="faq">
  <div class="container faq-wrap">
    <div class="section-head reveal in">
      <div class="label">FAQ</div>
      <h2>Questions we get a lot.</h2>
    </div>
    <div class="faq-item reveal in" onclick="toggleFaq(this)">
      <div class="faq-q">How much of my time does this take?<span class="faq-icon">+</span></div>
      <div class="faq-a">About 30 minutes upfront for a quick onboarding call where we get access to your Google listing and learn about your business. After that, we just need you to send us job photos when you finish installs — a quick phone pic works fine. That's it. We handle everything else. You'll get a monthly report and a check-in call, but the day-to-day work is all on us.</div>
    </div>
    <div class="faq-item reveal in" onclick="toggleFaq(this)">
      <div class="faq-q">What if it doesn't work?<span class="faq-icon">+</span></div>
      <div class="faq-a">We set specific, measurable targets with you every month — things like search appearances, ranking positions, and calls from Google. If we don't hit the agreed target at the end of the month, you get your money back for that month. No arguing about it, no fine print.</div>
    </div>
    <div class="faq-item reveal in" onclick="toggleFaq(this)">
      <div class="faq-q">Am I locked into a contract?<span class="faq-icon">+</span></div>
      <div class="faq-a">No long-term contracts. It's month-to-month — if you want to stop, give us 30 days notice and that's it. We don't believe in trapping people. The results keep you around, not a contract.</div>
    </div>
    <div class="faq-item reveal in" onclick="toggleFaq(this)">
      <div class="faq-q">How much does it cost?<span class="faq-icon">+</span></div>
      <div class="faq-a">Depends on your market and what you need. Book the free audit — we'll look at your {name} market specifically, show you the opportunity, and give you a straight answer on cost.</div>
    </div>
    <div class="faq-item reveal in" onclick="toggleFaq(this)">
      <div class="faq-q">How fast will I see results?<span class="faq-icon">+</span></div>
      <div class="faq-a">Google Business Profile improvements show up within 30 days — more people seeing your listing, more clicks to your profile. Actual ranking improvements for search terms typically take 60–90 days. The full effect compounds over 6+ months.</div>
    </div>
    <div class="faq-item reveal in" onclick="toggleFaq(this)">
      <div class="faq-q">Do you work with other {tl} contractors in {name}?<span class="faq-icon">+</span></div>
      <div class="faq-a">{c["faq_exclusivity"]}</div>
    </div>
  </div>
</section>

{_city_links_html(slug, cities_list, tl)}

<footer>
  <div class="footer-wrap">
    <div class="flogo">Rank<span>wise</span></div>
    <div class="flinks">
      <a href="/#services">What we do</a>
      <a href="/#how">How it works</a>
      <a href="/#results">Results</a>
      <a href="/#faq">FAQ</a>
      <a href="/blog/">Blog</a>
      <a href="/lab/">Rankwise Lab</a>
      <a href="/audit/?utm_source={utm}&amp;utm_medium=cta&amp;utm_content=footer">Free audit</a>
      <a href="https://www.linkedin.com/in/zackary-shefrin-8a1a87406/" target="_blank" rel="noopener">LinkedIn</a>
    </div>
    <div class="fcopy">© 2026 Rankwise · {tl} marketing · {name}, BC</div>
  </div>
</footer>

<a class="mobile-sticky-cta" href="/audit/?utm_source={utm}&amp;utm_medium=cta&amp;utm_content=mobile-sticky">Book Free {tl} Audit</a>

<script>
const obs=new IntersectionObserver(e=>{{e.forEach(x=>{{if(x.isIntersecting)x.target.classList.add('in')}});}},{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
function toggleFaq(item){{const o=item.classList.contains('open');document.querySelectorAll('.faq-item').forEach(i=>i.classList.remove('open'));if(!o)item.classList.add('open');}}
</script>

<script type="text/javascript">
(function(){{
  var params = new URLSearchParams(window.location.search);
  var cfg = {{"layout":"month_view","useSlotsViewOnSmallScreen":"true"}};
  var embedEl = document.getElementById("cal-embed");
  var started = false;
  ["utm_source","utm_medium","utm_campaign","utm_term","utm_content"].forEach(function(k){{
    var v = params.get(k); if(v) cfg[k] = v;
  }});
  if (!embedEl) return;
  var _conversionFired = false;
  function fireAuditConversion(e){{
    if (_conversionFired || typeof gtag !== "function") return;
    _conversionFired = true;
    var bookingUid =
      (e && e.detail && e.detail.data && e.detail.data.booking && e.detail.data.booking.uid) ||
      (e && e.detail && e.detail.data && e.detail.data.uid) ||
      "cal_com";
    gtag("event","audit_request_submitted",{{
      event_category:"lead",
      event_label: bookingUid,
      utm_source: params.get("utm_source") || "{utm}",
      utm_campaign: params.get("utm_campaign") || "city-page"
    }});
  }}
  function loadCal(){{
    if (started) return;
    started = true;
    (function(C,A,L){{
      var p=function(a,ar){{a.q.push(ar);}};
      C.Cal=C.Cal||function(){{
        var cal=C.Cal,ar=arguments;
        if(!cal.loaded){{
          cal.ns={{}};cal.q=cal.q||[];
          var s=document.createElement("script");
          s.src=A;s.async=true;
          s.onerror=function(){{
            embedEl.innerHTML='<div class="cal-fallback">Calendar not loading? <a href="/audit/?utm_source={utm}&utm_medium=cta&utm_content=calendar-fallback">Open the booking page directly</a>.</div>';
          }};
          document.head.appendChild(s);
          cal.loaded=1;
        }}
        if(ar[0]===L){{
          var api=function(){{p(api,arguments);}};var namespace=ar[1];
          api.q=api.q||[];
          if(typeof namespace==="string"){{cal.ns[namespace]=cal.ns[namespace]||api;p(cal.ns[namespace],ar);p(cal,[L,namespace,api]);}}
          else p(cal,ar);
          return;
        }}
        p(cal,ar);
      }};
    }})(window,"https://app.cal.com/embed/embed.js","init");
    Cal("init","15min",{{origin:"https://app.cal.com"}});
    Cal.ns["15min"]("inline",{{elementOrSelector:"#cal-embed",config:cfg,calLink:"zackary-shefrin-oy63zv/15min"}});
    Cal.ns["15min"]("ui",{{"theme":"dark","hideEventTypeDetails":true,"layout":"month_view","cssVarsPerTheme":{{"dark":{{"cal-brand":"#F5B731"}}}}}});
    Cal.ns["15min"]("on",{{action:"bookingSuccessful",callback:fireAuditConversion}});
    Cal.ns["15min"]("on",{{action:"bookingSuccessfulV2",callback:fireAuditConversion}});
  }}
  if ("IntersectionObserver" in window) {{
    var observer = new IntersectionObserver(function(entries){{
      entries.forEach(function(entry){{
        if (entry.isIntersecting) {{ loadCal(); observer.disconnect(); }}
      }});
    }}, {{rootMargin:"200px 0px"}});
    observer.observe(embedEl);
  }} else {{
    loadCal();
  }}
}})();
</script>
</body></html>'''


base = os.path.dirname(os.path.abspath(__file__))

# HVAC city pages
for c in CITIES:
    out_dir = os.path.join(base, c["slug"])
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(build_page(c, CITIES))
    print(f"✓ {c['slug']}/index.html")

# Plumbing pages — archived 2026-05-12, will re-enable after first paying HVAC client.
# Data definitions (PLUMBING_CITIES, PLUMBING_LANDING) kept above so this block can be
# uncommented when the Trade Expansion Plan Phase 1 trigger fires.
# Old generated output preserved at _archive/plumbing-pages-2026-05-12/

# for c in PLUMBING_CITIES:
#     out_dir = os.path.join(base, c["slug"])
#     os.makedirs(out_dir, exist_ok=True)
#     with open(os.path.join(out_dir, "index.html"), "w") as f:
#         f.write(build_page(c, PLUMBING_CITIES))
#     print(f"✓ {c['slug']}/index.html")
#
# out_dir = os.path.join(base, PLUMBING_LANDING["slug"])
# os.makedirs(out_dir, exist_ok=True)
# with open(os.path.join(out_dir, "index.html"), "w") as f:
#     f.write(build_page(PLUMBING_LANDING, PLUMBING_CITIES))
# print(f"✓ {PLUMBING_LANDING['slug']}/index.html")
