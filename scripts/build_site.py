#!/usr/bin/env python3
import csv
import html
import json
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "nationalparkcam_export"
DIST = ROOT / "docs"
PAGES_OUT = DIST / "parks"
ASSETS_OUT = DIST / "assets"
SITE_URL = "https://www.national-parks.us"
CUSTOM_DOMAIN = "www.national-parks.us"
NATIONALPARKCAM_SITE_URL = "https://www.nationalparkcam.com"
GOOGLE_ANALYTICS_ID = "G-Y64NX1DFKX"
INFO_PAGE_SLUGS = {"about", "contact", "privacy-policy"}
ACTIVE_HERO_YOUTUBE_IDS = {
    "OteVW3af3BU",
    "OAJF1Ie1m_Q",
    "f5Rjm5tiEkU",
    "OtbWimuJQ_A",
    "rnTsOesC6hE",
    "XhBUrjhJm1A",
    "o4fKtgPVpoU",
    "6IaMqotNF_s",
    "Tz5tPqRRv1Y",
    "FVdmnpJ2kM0",
    "gXKuUyKt8mc",
    "C0e8bpZ-5WY",
}
BLOCKED_YOUTUBE_IDS = {
    "5LFLhZ_h91A",
    "BWnloy8r0qU",
}


SECTION_TITLES = {
    "Introduction",
    "Day Hikes",
    "Top Hikes and Climbs",
    "Hiking and Backpacking",
    "Backpacking",
    "Camping and Lodging",
    "Camping",
    "Lodging",
    "Fishing",
    "Wildlife Viewing",
    "Biking",
    "Climbing",
    "Accommodations",
    "Food & Groceries",
    "Getting Around - Transportation",
    "External Links",
    "Short History of the National Park",
}

WEBCAM_PARK_NAMES = {
    "acadia-webcam": "Acadia National Park",
    "arches-webcam": "Arches National Park",
    "big-bend-webcam": "Big Bend National Park",
    "black-canyon-of-the-gunnison-webcam": "Black Canyon of the Gunnison National Park",
    "bryce-canyon-webcam": "Bryce Canyon National Park",
    "channel-islands-webcam": "Channel Islands National Park",
    "colorado-national-monument-webcam": "Colorado National Monument",
    "crater-lake-webcam": "Crater Lake National Park",
    "denali-webcam": "Denali National Park",
    "dinosaur-national-monument-webcam": "Dinosaur National Monument",
    "everglades-webcam": "Everglades National Park",
    "florissant-fossil-beds-national-monument-webcam": "Florissant Fossil Beds National Monument",
    "glacier-bay-webcam": "Glacier Bay National Park",
    "glacier-webcam": "Glacier National Park",
    "grand-canyon-parashant-national-monument-webcam": "Grand Canyon-Parashant National Monument",
    "grand-canyon-webcam": "Grand Canyon National Park",
    "grand-tetons-webcam": "Grand Teton National Park",
    "great-smoky-mountains-webcam": "Great Smoky Mountains National Park",
    "guadalupe-mountains-webcam": "Guadalupe Mountains National Park",
    "haleakala-webcam": "Haleakala National Park",
    "hawaii-volcanoes-webcam": "Hawaii Volcanoes National Park",
    "isle-royale-national-park-webcam": "Isle Royale National Park",
    "john-day-fossil-beds-national-monument-webcam": "John Day Fossil Beds National Monument",
    "joshua-tree-webcam": "Joshua Tree National Park",
    "katmai-webcam": "Katmai National Park",
    "kings-canyon-webcam": "Sequoia and Kings Canyon National Parks",
    "lassen-volcano-webcam": "Lassen Volcanic National Park",
    "mammoth-cave-webcam": "Mammoth Cave National Park",
    "mount-rainier-webcam": "Mount Rainier National Park",
    "new-river-gorge-webcam": "New River Gorge National Park",
    "north-cascades-webcam": "North Cascades National Park",
    "olympic-webcam": "Olympic National Park",
    "petrified-forest-webcam": "Petrified Forest National Park",
    "redwood-national-park": "Redwood National and State Parks",
    "rocky-mountain-webcam": "Rocky Mountain National Park",
    "shenandoah-webcam": "Shenandoah National Park",
    "theodore-roosevelt-webcam": "Theodore Roosevelt National Park",
    "virgin-islands-webcam": "Virgin Islands National Park",
    "wrangell-st-elias-webcam": "Wrangell-St. Elias National Park",
    "yellowstone-webcam": "Yellowstone National Park",
    "yosemite-webcam": "Yosemite National Park",
    "zion-webcam": "Zion National Park",
}

NO_CAMERA_PARK_NAMES = {
    "badlands-national-park": "Badlands National Park",
    "biscayne-national-park": "Biscayne National Park",
    "canyonlands-national-park": "Canyonlands National Park",
    "capitol-reef-national-park": "Capitol Reef National Park",
    "carlsbad-caverns-national-park": "Carlsbad Caverns National Park",
    "congaree-national-park": "Congaree National Park",
    "cuyahoga-valley-national-park": "Cuyahoga Valley National Park",
    "death-valley-national-park": "Death Valley National Park",
    "dry-tortugas-national-park": "Dry Tortugas National Park",
    "gates-of-the-arctic-national-park": "Gates of the Arctic National Park and Preserve",
    "gateway-arch-national-park": "Gateway Arch National Park",
    "great-basin-national-park": "Great Basin National Park",
    "great-sand-dunes-national-park": "Great Sand Dunes National Park and Preserve",
    "hot-springs-national-park": "Hot Springs National Park",
    "indiana-dunes-national-park": "Indiana Dunes National Park",
    "kenai-fjords-national-park": "Kenai Fjords National Park",
    "kobuk-valley-national-park": "Kobuk Valley National Park",
    "lake-clark-national-park": "Lake Clark National Park",
    "mesa-verde-national-park": "Mesa Verde National Park",
    "national-park-of-american-samoa": "National Park of American Samoa",
    "pinnacles-national-park": "Pinnacles National Park",
    "saguaro-national-park": "Saguaro National Park",
    "voyageurs-national-park": "Voyageurs National Park",
    "white-sands-national-park": "White Sands National Park",
    "wind-cave-national-park": "Wind Cave National Park",
}

PARK_NAMES = {
    **WEBCAM_PARK_NAMES,
    **NO_CAMERA_PARK_NAMES,
}

PARK_COORDS = {
    "acadia-webcam": [44.3386, -68.2733],
    "arches-webcam": [38.7331, -109.5925],
    "big-bend-webcam": [29.1275, -103.2425],
    "black-canyon-of-the-gunnison-webcam": [38.5754, -107.7416],
    "bryce-canyon-webcam": [37.593, -112.1871],
    "channel-islands-webcam": [34.0069, -119.7785],
    "colorado-national-monument-webcam": [39.0538, -108.7147],
    "crater-lake-webcam": [42.9446, -122.109],
    "denali-webcam": [63.1148, -151.1926],
    "dinosaur-national-monument-webcam": [40.4416, -109.3047],
    "everglades-webcam": [25.2866, -80.8987],
    "florissant-fossil-beds-national-monument-webcam": [38.9126, -105.2803],
    "glacier-bay-webcam": [58.6658, -136.9002],
    "glacier-webcam": [48.7596, -113.787],
    "grand-canyon-parashant-national-monument-webcam": [36.3911, -113.6877],
    "grand-canyon-webcam": [36.1069, -112.1129],
    "grand-tetons-webcam": [43.7904, -110.6818],
    "great-smoky-mountains-webcam": [35.6118, -83.4895],
    "guadalupe-mountains-webcam": [31.923, -104.87],
    "haleakala-webcam": [20.7204, -156.1552],
    "hawaii-volcanoes-webcam": [19.4194, -155.2885],
    "isle-royale-national-park-webcam": [48.011, -88.8278],
    "john-day-fossil-beds-national-monument-webcam": [44.6257, -119.8811],
    "joshua-tree-webcam": [33.8734, -115.901],
    "katmai-webcam": [58.5975, -154.6939],
    "kings-canyon-webcam": [36.8879, -118.5551],
    "lassen-volcano-webcam": [40.4977, -121.4207],
    "mammoth-cave-webcam": [37.1862, -86.1005],
    "mesa-verde-national-park": [37.2309, -108.4618],
    "mount-rainier-webcam": [46.8523, -121.7603],
    "new-river-gorge-webcam": [37.8683, -80.9996],
    "north-cascades-webcam": [48.7718, -121.2985],
    "olympic-webcam": [47.8021, -123.6044],
    "petrified-forest-webcam": [35.0659, -109.781],
    "pinnacles-national-park": [36.4915, -121.1972],
    "redwood-national-park": [41.2132, -124.0046],
    "rocky-mountain-webcam": [40.3428, -105.6836],
    "shenandoah-webcam": [38.5339, -78.35],
    "theodore-roosevelt-webcam": [46.979, -103.5387],
    "virgin-islands-webcam": [18.3424, -64.7486],
    "wrangell-st-elias-webcam": [61.7104, -142.9857],
    "yellowstone-webcam": [44.6, -110.5],
    "yosemite-webcam": [37.8651, -119.5383],
    "zion-webcam": [37.2982, -113.0263],
    "badlands-national-park": [43.8554, -102.3397],
    "biscayne-national-park": [25.4824, -80.2083],
    "canyonlands-national-park": [38.3269, -109.8783],
    "capitol-reef-national-park": [38.0877, -111.1355],
    "carlsbad-caverns-national-park": [32.1479, -104.5567],
    "congaree-national-park": [33.7919, -80.7487],
    "cuyahoga-valley-national-park": [41.2808, -81.5678],
    "death-valley-national-park": [36.5323, -116.9325],
    "dry-tortugas-national-park": [24.6285, -82.8732],
    "gates-of-the-arctic-national-park": [67.78, -153.3],
    "gateway-arch-national-park": [38.6247, -90.1848],
    "great-basin-national-park": [38.9833, -114.3],
    "great-sand-dunes-national-park": [37.7916, -105.5943],
    "hot-springs-national-park": [34.5215, -93.0422],
    "indiana-dunes-national-park": [41.6533, -87.0524],
    "kenai-fjords-national-park": [59.818, -150.1066],
    "kobuk-valley-national-park": [67.3356, -159.1281],
    "lake-clark-national-park": [60.4127, -154.3235],
    "national-park-of-american-samoa": [-14.2583, -170.6833],
    "saguaro-national-park": [32.25, -110.5],
    "voyageurs-national-park": [48.5, -92.88],
    "white-sands-national-park": [32.78, -106.17],
    "wind-cave-national-park": [43.57, -103.48],
}

CAMPING_LINK_ALIASES = {
    "acadia-webcam": {
        "official NPS camping page": "https://www.nps.gov/acad/planyourvisit/camping.htm",
    },
    "badlands-national-park": {
        "Cedar Pass Campground": "https://www.nps.gov/badl/planyourvisit/eatingsleeping.htm",
        "Sage Creek Campground": "https://www.nps.gov/badl/planyourvisit/eatingsleeping.htm",
    },
    "biscayne-national-park": {
        "Boca Chita Key": "https://www.nps.gov/bisc/planyourvisit/camping.htm",
        "Elliott Key": "https://www.nps.gov/bisc/planyourvisit/camping.htm",
    },
    "capitol-reef-national-park": {
        "Fruita Campground": "https://www.nps.gov/care/planyourvisit/campinga.htm",
    },
    "canyonlands-national-park": {
        "Island in the Sky Campground": "https://www.nps.gov/cany/planyourvisit/camping.htm",
        "The Needles Campground": "https://www.nps.gov/cany/planyourvisit/camping.htm",
    },
    "congaree-national-park": {
        "Longleaf Campground": "https://www.nps.gov/cong/planyourvisit/camping.htm",
        "Bluff Campground": "https://www.nps.gov/cong/planyourvisit/camping.htm",
    },
    "death-valley-national-park": {
        "Furnace Creek Campground": "https://www.nps.gov/deva/planyourvisit/camping-in-death-valley.htm",
    },
    "dry-tortugas-national-park": {
        "Garden Key": "https://www.nps.gov/drto/planyourvisit/camping.htm",
    },
    "great-basin-national-park": {
        "developed campgrounds": "https://www.nps.gov/grba/planyourvisit/camping.htm",
    },
    "great-sand-dunes-national-park": {
        "Pinon Flats Campground": "https://www.nps.gov/grsa/planyourvisit/camping.htm",
    },
    "hot-springs-national-park": {
        "Gulpha Gorge Campground": "https://www.nps.gov/hosp/planyourvisit/campground.htm",
    },
    "indiana-dunes-national-park": {
        "Dunewood Campground": "https://www.nps.gov/indu/planyourvisit/campgrounds.htm",
    },
    "pinnacles-national-park": {
        "Pinnacles Campground": "https://www.nps.gov/pinn/planyourvisit/camp.htm",
    },
    "wind-cave-national-park": {
        "Elk Mountain Campground": "https://www.nps.gov/wica/planyourvisit/campgrounds.htm",
    },
    "mesa-verde-national-park": {
        "Morefield Campground": "https://www.nps.gov/meve/planyourvisit/camping.htm",
    },
    "voyageurs-national-park": {
        "Most campsites": "https://www.nps.gov/voya/planyourvisit/camping.htm",
        "frontcountry, backcountry, and houseboat sites": "https://www.nps.gov/voya/planyourvisit/camping.htm",
    },
    "redwood-national-park": {
        "Jedediah Smith Campground": "https://www.nps.gov/redw/planyourvisit/jedediah-smith-campground.htm",
        "Mill Creek Campground": "https://www.nps.gov/redw/planyourvisit/mill-creek-campground.htm",
        "Gold Bluffs Beach Campground": "https://www.nps.gov/redw/planyourvisit/gold-bluffs-beach-campground.htm",
        "Elk Prairie Campground": "https://www.nps.gov/redw/planyourvisit/elk-prairie-campground.htm",
    },
}

WEATHER_COORDS = {
    "national-park-of-american-samoa": [-14.2756, -170.702],
}

WEATHER_LOCATION_LABELS = {
    "national-park-of-american-samoa": "Forecast near Pago Pago, American Samoa",
}

GUIDE_SEO = {
    "badlands-national-park": {
        "title": "Badlands National Park Guide | Hiking, Map & Weather",
        "description": "Plan Badlands National Park with hiking trails, Badlands Loop Road stops, camping notes, weather, map links, wildlife viewing, and official NPS resources.",
    },
    "biscayne-national-park": {
        "title": "Biscayne National Park Guide | Snorkeling, Map & Weather",
        "description": "Plan Biscayne National Park with snorkeling, boat tours, paddling, fishing, island camping, weather, maps, and official NPS planning links.",
    },
    "canyonlands-national-park": {
        "title": "Canyonlands National Park Guide | Hiking, Map & Weather",
        "description": "Plan Canyonlands National Park with Island in the Sky, The Needles, hiking, scenic drives, river trips, camping, weather, maps, and NPS links.",
    },
    "capitol-reef-national-park": {
        "title": "Capitol Reef National Park Guide | Hiking, Map & Weather",
        "description": "Plan Capitol Reef National Park with Fruita, Scenic Drive, hiking trails, camping, weather, maps, backcountry notes, and official NPS resources.",
    },
    "carlsbad-caverns-national-park": {
        "title": "Carlsbad Caverns Guide | Cave Tours, Map & Weather",
        "description": "Plan Carlsbad Caverns National Park with cave tours, Big Room route, bat flight programs, desert hiking, weather, maps, and NPS links.",
    },
    "congaree-national-park": {
        "title": "Congaree National Park Guide | Boardwalk, Map & Weather",
        "description": "Plan Congaree National Park with Boardwalk Loop, Cedar Creek paddling, hiking, camping, flood notes, weather, maps, and official NPS resources.",
    },
    "cuyahoga-valley-national-park": {
        "title": "Cuyahoga Valley Guide | Hiking, Biking, Map & Weather",
        "description": "Plan Cuyahoga Valley National Park with Towpath Trail biking, Brandywine Falls, hiking, Scenic Railroad, weather, maps, and NPS links.",
    },
    "death-valley-national-park": {
        "title": "Death Valley National Park Guide | Map, Weather & Hikes",
        "description": "Plan Death Valley National Park with Badwater Basin, Zabriskie Point, scenic drives, hiking, camping, safety notes, weather, maps, and NPS links.",
    },
    "dry-tortugas-national-park": {
        "title": "Dry Tortugas Guide | Fort Jefferson, Camping & Weather",
        "description": "Plan Dry Tortugas National Park with Fort Jefferson, snorkeling, ferry access, Garden Key camping, birding, weather, maps, and NPS resources.",
    },
    "gates-of-the-arctic-national-park": {
        "title": "Gates of the Arctic Guide | Backpacking, Map & Weather",
        "description": "Plan Gates of the Arctic National Park and Preserve with backpacking, rafting, flight access, camping, weather, maps, and wilderness safety links.",
    },
    "gateway-arch-national-park": {
        "title": "Gateway Arch National Park Guide | Tickets, Map & Weather",
        "description": "Plan Gateway Arch National Park with tram tickets, museum visits, Old Courthouse history, riverfront walks, weather, maps, and official links.",
    },
    "great-basin-national-park": {
        "title": "Great Basin National Park Guide | Caves, Map & Weather",
        "description": "Plan Great Basin National Park with Lehman Caves, Wheeler Peak, bristlecone pine hikes, camping, stargazing, weather, maps, and NPS links.",
    },
    "great-sand-dunes-national-park": {
        "title": "Great Sand Dunes Guide | Hiking, Sledding & Weather",
        "description": "Plan Great Sand Dunes National Park and Preserve with dune hikes, sand sledding, Medano Creek, camping, weather, maps, and NPS resources.",
    },
    "hot-springs-national-park": {
        "title": "Hot Springs National Park Guide | Trails, Map & Weather",
        "description": "Plan Hot Springs National Park with Bathhouse Row, thermal springs, hiking trails, Gulpha Gorge camping, weather, maps, and NPS links.",
    },
    "indiana-dunes-national-park": {
        "title": "Indiana Dunes Guide | Beaches, Hiking, Map & Weather",
        "description": "Plan Indiana Dunes National Park with Lake Michigan beaches, hiking trails, birding, Dunewood camping, weather, maps, and NPS resources.",
    },
    "kenai-fjords-national-park": {
        "title": "Kenai Fjords National Park Guide | Glaciers & Weather",
        "description": "Plan Kenai Fjords National Park with Exit Glacier, Harding Icefield Trail, boat tours, wildlife viewing, weather, maps, and official NPS links.",
    },
    "kobuk-valley-national-park": {
        "title": "Kobuk Valley Guide | Sand Dunes, Map & Weather",
        "description": "Plan Kobuk Valley National Park with Great Kobuk Sand Dunes, backpacking, river trips, camping, weather, maps, and NPS wilderness resources.",
    },
    "lake-clark-national-park": {
        "title": "Lake Clark National Park Guide | Bears, Map & Weather",
        "description": "Plan Lake Clark National Park and Preserve with bear viewing, Twin Lakes, Port Alsworth, backpacking, fishing, weather, maps, and NPS links.",
    },
    "mesa-verde-national-park": {
        "title": "Mesa Verde National Park Guide | Tours, Map & Weather",
        "description": "Plan Mesa Verde National Park with cliff dwelling tours, Mesa Top Loop, hiking, Morefield Campground, weather, maps, and NPS resources.",
    },
    "national-park-of-american-samoa": {
        "title": "National Park of American Samoa Guide | Trails & Weather",
        "description": "Plan the National Park of American Samoa with Tutuila, Ofu, Ta'u, hiking trails, snorkeling, village visits, weather, maps, and NPS links.",
    },
    "pinnacles-national-park": {
        "title": "Pinnacles National Park Guide | Hiking, Caves & Weather",
        "description": "Plan Pinnacles National Park with High Peaks hiking, Bear Gulch Cave, Balconies Cave, condor viewing, camping, weather, maps, and NPS links.",
    },
    "saguaro-national-park": {
        "title": "Saguaro National Park Guide | Hiking, Map & Weather",
        "description": "Plan Saguaro National Park with Tucson Mountain and Rincon districts, hiking trails, scenic drives, camping notes, weather, maps, and NPS links.",
    },
    "voyageurs-national-park": {
        "title": "Voyageurs National Park Guide | Boating, Map & Weather",
        "description": "Plan Voyageurs National Park with boating, paddling, fishing, houseboats, camping, winter routes, weather, maps, and official NPS resources.",
    },
    "white-sands-national-park": {
        "title": "White Sands National Park Guide | Sledding, Map & Weather",
        "description": "Plan White Sands National Park with Dunes Drive, Alkali Flat Trail, sledding, sunset photography, weather, maps, and official NPS links.",
    },
    "wind-cave-national-park": {
        "title": "Wind Cave National Park Guide | Cave Tours & Weather",
        "description": "Plan Wind Cave National Park with cave tours, hiking trails, bison viewing, Elk Mountain camping, weather, maps, and official NPS resources.",
    },
}

GUIDE_TOPICS = {
    "badlands-national-park": {"hiking", "desert", "wildlife", "scenic-drives", "camping"},
    "biscayne-national-park": {"water", "beaches", "paddling", "fishing", "camping"},
    "canyonlands-national-park": {"hiking", "desert", "scenic-drives", "backpacking", "paddling", "camping"},
    "capitol-reef-national-park": {"hiking", "desert", "scenic-drives", "backpacking", "history", "camping"},
    "carlsbad-caverns-national-park": {"caves", "desert", "hiking", "wildlife"},
    "congaree-national-park": {"hiking", "paddling", "wildlife", "camping", "forests"},
    "cuyahoga-valley-national-park": {"hiking", "biking", "waterfalls", "history", "family"},
    "death-valley-national-park": {"hiking", "desert", "scenic-drives", "backpacking", "stargazing", "camping"},
    "dry-tortugas-national-park": {"water", "beaches", "snorkeling", "history", "camping", "wildlife"},
    "gates-of-the-arctic-national-park": {"alaska", "backpacking", "wildlife", "paddling", "camping"},
    "gateway-arch-national-park": {"history", "family", "urban", "museums"},
    "great-basin-national-park": {"caves", "hiking", "stargazing", "scenic-drives", "camping"},
    "great-sand-dunes-national-park": {"hiking", "desert", "sledding", "stargazing", "camping"},
    "hot-springs-national-park": {"hiking", "history", "family", "camping"},
    "indiana-dunes-national-park": {"beaches", "hiking", "wildlife", "biking", "camping"},
    "kenai-fjords-national-park": {"alaska", "glaciers", "hiking", "water", "wildlife"},
    "kobuk-valley-national-park": {"alaska", "desert", "backpacking", "paddling", "wildlife", "camping"},
    "lake-clark-national-park": {"alaska", "water", "backpacking", "wildlife", "fishing", "camping"},
    "mesa-verde-national-park": {"history", "hiking", "scenic-drives", "camping"},
    "national-park-of-american-samoa": {"water", "beaches", "snorkeling", "hiking", "culture"},
    "pinnacles-national-park": {"hiking", "caves", "wildlife", "climbing", "camping"},
    "saguaro-national-park": {"hiking", "desert", "scenic-drives", "wildlife", "backpacking"},
    "voyageurs-national-park": {"water", "paddling", "fishing", "camping", "wildlife"},
    "white-sands-national-park": {"hiking", "desert", "sledding", "scenic-drives", "stargazing"},
    "wind-cave-national-park": {"caves", "hiking", "wildlife", "scenic-drives", "camping"},
}

TOPIC_LABELS = {
    "alaska": "Alaska parks",
    "backpacking": "backpacking",
    "beaches": "beaches",
    "biking": "biking",
    "camping": "camping",
    "caves": "cave tours",
    "climbing": "climbing",
    "culture": "culture",
    "desert": "desert parks",
    "family": "family trips",
    "fishing": "fishing",
    "forests": "forests",
    "glaciers": "glaciers",
    "hiking": "hiking",
    "history": "history",
    "museums": "museums",
    "paddling": "paddling",
    "scenic-drives": "scenic drives",
    "sledding": "sand sledding",
    "snorkeling": "snorkeling",
    "stargazing": "stargazing",
    "urban": "city parks",
    "water": "water parks",
    "waterfalls": "waterfalls",
    "wildlife": "wildlife",
}

GUIDE_FAQ_ACTIVITIES = {
    "badlands-national-park": "Drive Badlands Loop Road, hike Door, Window, Notch, Castle, and Saddle Pass trails, watch sunrise or sunset along the Wall, and look for prairie wildlife.",
    "biscayne-national-park": "Boat tours, snorkeling, diving, paddling, fishing, island walks, and visits to Boca Chita Key, Elliott Key, Jones Lagoon, and the Maritime Heritage Trail are the main activities.",
    "canyonlands-national-park": "Top activities include Mesa Arch, Grand View Point, Upheaval Dome, Chesler Park, Elephant Hill, White Rim Road, backcountry hiking, and river trips.",
    "capitol-reef-national-park": "Explore Fruita, Scenic Drive, Grand Wash, Capitol Gorge, Hickman Bridge, Cassidy Arch, Cathedral Valley, orchards, petroglyphs, and backcountry routes.",
    "carlsbad-caverns-national-park": "The Big Room, Natural Entrance route, ranger-guided cave tours, seasonal bat flight programs, desert trails, and cave photography are the main highlights.",
    "congaree-national-park": "Walk the Boardwalk Loop, hike Weston Lake Loop or Kingsnake Trail, paddle Cedar Creek, watch wildlife, and check seasonal firefly viewing dates.",
    "cuyahoga-valley-national-park": "Popular activities include Brandywine Falls, the Ledges Trail, Towpath Trail biking, Beaver Marsh, the Scenic Railroad, historic farms, and short waterfall hikes.",
    "death-valley-national-park": "Plan for Badwater Basin, Zabriskie Point, Dante View, Mesquite Flat Sand Dunes, Golden Canyon, Artist Drive, Ubehebe Crater, stargazing, and desert hiking.",
    "dry-tortugas-national-park": "Tour Fort Jefferson, snorkel around the moat wall, watch birds, swim, paddle, photograph Garden Key, and camp overnight if you can secure transport.",
    "gates-of-the-arctic-national-park": "Most trips focus on backpacking, rafting, basecamp wilderness travel, flightseeing, fishing, photography, wildlife viewing, and Brooks Range scenery.",
    "gateway-arch-national-park": "Ride the tram to the top of the Arch, visit the museum, walk the riverfront grounds, photograph the skyline, and explore the Old Courthouse area.",
    "great-basin-national-park": "Reserve a Lehman Caves tour, drive Wheeler Peak Scenic Drive, hike to bristlecone pines or alpine lakes, summit Wheeler Peak, camp, and stargaze.",
    "great-sand-dunes-national-park": "Climb the dunes, try sand sledding, visit Medano Creek in season, hike Mosca Pass, camp at Pinon Flats, photograph sunset, and stargaze.",
    "hot-springs-national-park": "Walk Bathhouse Row, tour Fordyce Bathhouse, hike Hot Springs Mountain trails, fill bottles at thermal fountains, camp at Gulpha Gorge, and explore downtown.",
    "indiana-dunes-national-park": "Visit Lake Michigan beaches, hike Cowles Bog, West Beach, Great Marsh, and Heron Rookery, go birding, tour historic farm sites, and camp at Dunewood.",
    "kenai-fjords-national-park": "Visit Exit Glacier, hike the Harding Icefield Trail, take a wildlife and glacier boat tour, watch marine wildlife, kayak, and explore Seward-area scenery.",
    "kobuk-valley-national-park": "The Great Kobuk Sand Dunes, Onion Portage, backpacking, Kobuk River floating, flightseeing, wildlife viewing, and remote camping are the main draws.",
    "lake-clark-national-park": "Top activities include bear viewing, Twin Lakes, Port Alsworth, Tanalian Falls, kayaking, fishing, flightseeing, backpacking, and visiting the Proenneke cabin area.",
    "mesa-verde-national-park": "Plan for cliff dwelling tours, Mesa Top Loop Road, Far View Sites, Chapin Mesa Archeological Museum, Petroglyph Point Trail, overlooks, and Morefield Campground.",
    "national-park-of-american-samoa": "Explore Tutuila, Ofu, and Ta'u with hiking, snorkeling, reef viewing, village scenery, Mount Alava, Lower Sauma Ridge, Pola Island views, and beaches.",
    "pinnacles-national-park": "Hike High Peaks, Bear Gulch Cave, Balconies Cave, Condor Gulch, Moses Spring, and west-side trails, watch for condors, and consider rock climbing.",
    "saguaro-national-park": "Drive Bajada Loop and Cactus Forest Drive, hike desert trails, visit Signal Hill petroglyphs, photograph saguaros at sunset, watch wildlife, and backpack in the Rincon District.",
    "voyageurs-national-park": "Boating, paddling, fishing, houseboating, lakeside camping, Kettle Falls, Ellsworth Rock Gardens, winter ice roads, snowshoeing, and northern lights are signature activities.",
    "white-sands-national-park": "Drive Dunes Drive, hike Alkali Flat or shorter dune trails, try sledding, photograph sunset, join ranger programs, and prepare for bright sun and heat.",
    "wind-cave-national-park": "Take a cave tour, hike Rankin Ridge or Wind Cave Canyon, watch bison and prairie dogs, drive scenic park roads, and camp at Elk Mountain.",
}

GUIDE_FAQ_CAMPING = {
    "badlands-national-park": "Yes. Cedar Pass Campground and Sage Creek Campground are the main in-park options, and backcountry camping is possible with careful planning.",
    "biscayne-national-park": "Yes, but camping is boat-access only on Boca Chita Key and Elliott Key. Campers need to bring water, food, and weather-ready supplies.",
    "canyonlands-national-park": "Yes. Island in the Sky and The Needles have frontcountry campgrounds, and many backcountry trips require permits and advanced planning.",
    "capitol-reef-national-park": "Yes. Fruita Campground is the main developed campground, with primitive and backcountry options available in more remote areas.",
    "carlsbad-caverns-national-park": "There is no developed campground inside the park. Backcountry camping may be available by permit, and most visitors use nearby lodging or campgrounds.",
    "congaree-national-park": "Yes. Longleaf and Bluff campgrounds require reservations, and backcountry camping is available by permit.",
    "cuyahoga-valley-national-park": "There is no standard NPS campground inside Cuyahoga Valley National Park, so visitors usually use nearby lodging or regional campgrounds.",
    "death-valley-national-park": "Yes. Death Valley has several campgrounds, including Furnace Creek, but heat, water, services, and seasonal conditions are critical planning factors.",
    "dry-tortugas-national-park": "Yes. Primitive camping is available on Garden Key, but campers must bring all supplies and plan around ferry or private boat access.",
    "gates-of-the-arctic-national-park": "Yes, but it is undeveloped wilderness camping. Visitors must be self-sufficient and prepared for bears, weather, rivers, and remote travel.",
    "gateway-arch-national-park": "No. Gateway Arch is an urban national park without camping; visitors use hotels or campgrounds around the St. Louis region.",
    "great-basin-national-park": "Yes. Great Basin has developed campgrounds at several elevations, plus backcountry options for prepared visitors.",
    "great-sand-dunes-national-park": "Yes. Pinon Flats Campground is the main developed campground, and permitted backcountry camping may be available in dune or mountain zones.",
    "hot-springs-national-park": "Yes. Gulpha Gorge Campground is the in-park campground and offers convenient access to trails and downtown Hot Springs.",
    "indiana-dunes-national-park": "Yes. Dunewood Campground is the main national park campground, with additional nearby options outside the park.",
    "kenai-fjords-national-park": "Camping is limited and often primitive. Most visitors use Seward lodging or campgrounds while planning Exit Glacier, boat tours, or backcountry trips.",
    "kobuk-valley-national-park": "Yes, but all camping is undeveloped backcountry camping reached by air taxi, river travel, or remote wilderness routes.",
    "lake-clark-national-park": "Yes. Camping is mostly undeveloped backcountry camping, with lodges and services concentrated around Port Alsworth and select access points.",
    "mesa-verde-national-park": "Yes. Morefield Campground is the main in-park campground and generally operates seasonally.",
    "national-park-of-american-samoa": "There is no standard developed campground. Visitors should arrange lodging and local logistics before traveling between islands.",
    "pinnacles-national-park": "Yes. Pinnacles Campground is on the east side of the park, and visitors should plan around the separate east and west entrances.",
    "saguaro-national-park": "There is no vehicle camping in Saguaro. Overnight camping is limited to designated backcountry sites in the Rincon Mountain District with permits.",
    "voyageurs-national-park": "Yes. Campsites are mostly boat-access, and reservations or permits are needed for frontcountry, backcountry, and houseboat sites.",
    "white-sands-national-park": "Backcountry camping has historically existed, but availability can change. Check current NPS conditions before planning an overnight stay.",
    "wind-cave-national-park": "Yes. Elk Mountain Campground is the main in-park campground and is generally first come, first served.",
}

GUIDE_IMAGES = {
    "badlands-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/C4524107-A9DF-29E3-80B8554266867C06.jpg",
        "alt": "Badlands formations and prairie landscape in Badlands National Park",
    },
    "biscayne-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/1FCA9BB2-C027-31FF-D77F060FFA94ABBD.jpg",
        "alt": "Turquoise water and islands in Biscayne National Park",
    },
    "canyonlands-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/0B5242D9-A949-CDF9-39AAC40183326ECB.jpg",
        "alt": "Canyon country and mesa views in Canyonlands National Park",
    },
    "capitol-reef-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/4278897C-E561-2333-807608024BC97BFB.jpg",
        "alt": "Red rock cliffs and desert scenery in Capitol Reef National Park",
    },
    "carlsbad-caverns-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/07CA762D-1DD8-B71B-0B5263929F1AEAC2.jpg",
        "alt": "Cave formations inside Carlsbad Caverns National Park",
    },
    "congaree-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/F2511AA6-077D-1523-A9C2D6E72A8D2E97.jpg",
        "alt": "Bottomland hardwood forest in Congaree National Park",
    },
    "cuyahoga-valley-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/0259096B-0813-0FE6-5855DC86EA709ACA.jpg",
        "alt": "Waterfall and forest scenery in Cuyahoga Valley National Park",
    },
    "death-valley-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/pwr/homepage/8A274E4D-C9F5-C45C-4AB2CDD4FA838583.jpg",
        "alt": "Desert basin and mountain scenery in Death Valley National Park",
    },
    "dry-tortugas-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/B8CF5C7E-1DD8-B71B-0B62F152705DCACA.jpg",
        "alt": "Fort Jefferson and blue water in Dry Tortugas National Park",
    },
    "gates-of-the-arctic-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/80BF2CBB-1DD8-B71B-0B0EE177F0BF9659.jpg",
        "alt": "Brooks Range wilderness in Gates of the Arctic National Park and Preserve",
    },
    "gateway-arch-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/3B27D537-A6DF-9DFC-50E6FFA69B702157.jpg",
        "alt": "Gateway Arch and St. Louis riverfront in Gateway Arch National Park",
    },
    "great-basin-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/pwr/homepage/201FE384-F8DF-7A67-F799282C9034E8B1.jpg",
        "alt": "Mountain and high desert scenery in Great Basin National Park",
    },
    "great-sand-dunes-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/40B6A775-D31E-2E17-A3D01E8D5D05BFD5.jpeg",
        "alt": "Tall dunes and mountain backdrop in Great Sand Dunes National Park and Preserve",
    },
    "hot-springs-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/EC804E3D-DA2E-8D80-414AD1E55DF95EE6.jpg",
        "alt": "Bathhouse Row and forested hills in Hot Springs National Park",
    },
    "indiana-dunes-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/D861DCC5-D20D-94B1-BF92E14EA155A584.jpg",
        "alt": "Lake Michigan beach and dunes in Indiana Dunes National Park",
    },
    "kenai-fjords-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/479F536C-0578-CA8B-EA9306523C814E70.jpg",
        "alt": "Glacier and coastal mountain scenery in Kenai Fjords National Park",
    },
    "kobuk-valley-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/3AA12CC6-E6E6-9F7D-79DA7C33936C11AC.jpg",
        "alt": "Great Kobuk Sand Dunes in Kobuk Valley National Park",
    },
    "lake-clark-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/akr/homepage/9D511285-1DD8-B71B-0B39C127CBF6FD5D.jpg",
        "alt": "Lake and mountain wilderness in Lake Clark National Park and Preserve",
    },
    "mesa-verde-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/E06DAC3A-F89E-05AC-8383F3AF5699EBB8.jpg",
        "alt": "Cliff dwelling and canyon landscape in Mesa Verde National Park",
    },
    "national-park-of-american-samoa": {
        "url": "https://www.nps.gov/common/uploads/banner_image/pwr/homepage/25FAA5B5-1DD8-B71B-0B96C6CD4CEB4517.jpg",
        "alt": "Tropical coastline in the National Park of American Samoa",
    },
    "pinnacles-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/pwr/homepage/2913AF89-1DD8-B71B-0B428CC0594DA1F3.jpg",
        "alt": "Rock formations and hiking landscape in Pinnacles National Park",
    },
    "saguaro-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/C2699B98-0653-5E91-0E8E24B25E753D7F.jpg",
        "alt": "Saguaro cactus forest near Tucson in Saguaro National Park",
    },
    "voyageurs-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/5DDB3FB1-97AC-9F8B-B1513749B1E2565F.jpg",
        "alt": "Lake and forest scenery in Voyageurs National Park",
    },
    "white-sands-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/imr/homepage/A16AAF73-C278-1129-5EB3056BED7BA85C.jpg",
        "alt": "White gypsum dunes in White Sands National Park",
    },
    "wind-cave-national-park": {
        "url": "https://www.nps.gov/common/uploads/banner_image/mwr/homepage/CC25AAB0-1DD8-B71B-0B48DF48A0B8DE84.JPG",
        "alt": "Prairie and wildlife habitat in Wind Cave National Park",
    },
}

PAGE_SOURCE_EMBEDS = {
    "https://video-monitoring.com/everglades/royalpalm/": {
        "kind": "image",
        "url": "https://video-monitoring.com/everglades/royalpalm/sstn/s1.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=81B46712-1DD8-B71B-0B4B99EDA0AE3CFC": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-glba/BartlettDock.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=81B4672D-1DD8-B71B-0B04336F55ECDD47": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-glba/LowerBay.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=81B46B99-1DD8-B71B-0B124A40CC3384CE": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-shen/bvc2.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=51F606E1-BAF1-472B-2BC7D21ED4CDA08E": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-wrst/KennecottNorth.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=5224B014-CBDE-5E14-DEF34EBF65E78E88": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-wrst/KennecottSouth.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=F91F11B2-C421-28C4-16C717FF1FF2CB72": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-wrst/HQVC.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=B28D5845-C504-BBA5-17748BFF1C6CC716": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-turtleback/latest.jpg",
        "status": "Current webcam image",
        "description": "Located on a dome near the Wawona Tunnel, this webcam provides a view of Yosemite Valley.",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=1148077C-F06F-CD3A-969692F6BC0481AC": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-sentinel/latest.jpg",
        "status": "Current webcam image",
        "description": "This webcam looks across Yosemite's high country toward Half Dome and the surrounding peaks.",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=EAA24FCD-BC0D-C360-19BF30B462D0ACE8": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-halfdome/latest.jpg",
        "status": "Current webcam image",
        "description": "This webcam shows Half Dome and the surrounding Yosemite Valley landscape.",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=3E81EC42-BB62-0A59-E30ABB8F1646322E": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-yosfalls/latest.jpg",
        "status": "Current webcam image",
        "description": "This webcam shows the upper section of Yosemite Falls.",
    },
}


def clean_site_text(text):
    nps_attribution = "(" + "U.S. National " + "Park Service" + ")"
    text = text.replace(f" {nps_attribution}", "")
    text = text.replace(nps_attribution, "")
    text = re.sub(r"(?:&lt;|<)\s*br\s*/?\s*(?:&gt;|>)", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    repeated_park_name = re.compile(
        r"^(.+?\b(?:National Park(?: & Preserve)?|National Parks(?: & Preserve)?|National and State Parks))\s+\1\b"
    )
    while repeated_park_name.search(text):
        text = repeated_park_name.sub(r"\1", text, count=1)
    return text


def clean_title(title):
    title = title.replace("Liv e", "Live").replace("Glacie r", "Glacier")
    title = title.replace("G rand", "Grand").replace("Gr eat", "Great")
    title = title.replace("G uadalupe", "Guadalupe").replace("H awaii", "Hawaii")
    title = title.replace("Y osemite", "Yosemite")
    return clean_site_text(title)


def decode_url(url):
    parsed = urlparse(url)
    if parsed.netloc == "www.google.com" and parsed.path == "/url":
        q = parse_qs(parsed.query).get("q")
        if q:
            return q[0]
    return url


def portable_embed_url(url):
    parsed = urlparse(url)
    if parsed.netloc in {"www.youtube.com", "youtube.com"} and parsed.path.startswith("/embed/"):
        allowed = {
            key: value
            for key, value in parse_qs(parsed.query).items()
            if key
            not in {
                "embed_config",
                "errorlinks",
            }
        }
        query = urlencode(allowed, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", query, ""))
    return url


def page_href(row):
    if row["slug"] == "national-park-webcam-home":
        return "index.html"
    return f"parks/{row['slug']}.html"


def nationalparkcam_park_url(slug):
    return f"{NATIONALPARKCAM_SITE_URL}/parks/{slug}"


def is_no_camera_page(slug):
    return slug in NO_CAMERA_PARK_NAMES


def page_target_href(page, depth=0, absolute=False):
    if is_no_camera_page(page["slug"]):
        if absolute:
            return sitemap_loc(page)
        target = page_href(page)
        return rel_from_page(target, "park-detail") if depth else target
    return nationalparkcam_park_url(page["slug"])


def sitemap_loc(row):
    if row["slug"] == "national-park-webcam-home":
        return f"{SITE_URL}/"
    if row["slug"] in INFO_PAGE_SLUGS:
        return f"{SITE_URL}/{row['slug']}"
    return f"{SITE_URL}/parks/{row['slug']}"


def build_sitemap(pages):
    lastmod = date.today().isoformat()
    urls = "\n".join(
        "\n".join(
            [
                "  <url>",
                f"    <loc>{html.escape(sitemap_loc(page))}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "  </url>",
            ]
        )
        for page in pages
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""


def build_robots_txt():
    return f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""


def rel_from_page(target, page_slug):
    if page_slug == "national-park-webcam-home":
        return target
    if target.startswith("parks/"):
        return target.split("/", 1)[1]
    return f"../{target}"


def load_pages():
    pages = []
    with (EXPORT / "index.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = dict(row)
            row["title"] = clean_title(row["title"])
            row["line_count"] = int(row["line_count"])
            row["link_count"] = int(row["link_count"])
            row["image_count"] = int(row["image_count"])
            row["embed_count"] = int(row.get("embed_count") or 0)
            if row["slug"] in WEBCAM_PARK_NAMES:
                row["title"] = f"{WEBCAM_PARK_NAMES[row['slug']]} Webcams"
            elif row["slug"] in NO_CAMERA_PARK_NAMES:
                row["title"] = f"{NO_CAMERA_PARK_NAMES[row['slug']]} Guide"
            pages.append(row)
    return pages


def load_resources():
    resources = defaultdict(list)
    with (EXPORT / "resources.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = dict(row)
            row["page"] = clean_title(row["page"])
            row["url"] = portable_embed_url(decode_url(row["url"]))
            resources[row["page_url"]].append(row)
    return resources


def load_webcam_sources():
    path = EXPORT / "webcam_sources.csv"
    sources = defaultdict(list)
    if not path.exists():
        return sources
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            replacement = PAGE_SOURCE_EMBEDS.get(row["url"])
            if replacement:
                row.update(replacement)
                row["status"] = row["status"].replace("page", "embed")
            sources[row["slug"]].append(dict(row))
    return sources


def parse_markdown(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip()
    source = ""
    body = []
    in_resource = False
    for line in lines[1:]:
        if line.startswith("Source:"):
            source = line.replace("Source:", "", 1).strip()
            continue
        if line.startswith("## Images") or line.startswith("## Embeds") or line.startswith("## Links"):
            in_resource = True
        if in_resource:
            continue
        text = line.strip()
        if text:
            body.append(clean_site_text(text))
    return clean_title(title), source, body


def display_title(page, parsed_title):
    if page["slug"] in WEBCAM_PARK_NAMES:
        return f"{WEBCAM_PARK_NAMES[page['slug']]} Webcams"
    if page["slug"] in NO_CAMERA_PARK_NAMES:
        return f"{NO_CAMERA_PARK_NAMES[page['slug']]} Guide"
    return parsed_title


def first_image(resources):
    candidates = []
    for item in resources:
        if item["type"] != "image":
            continue
        url = item["url"]
        label = item["label"].lower()
        if "email" in label or "sociallinks" in url or "sheets_32dp" in url:
            continue
        candidates.append(url)
    return candidates[0] if candidates else ""


def clean_summary_text(text):
    text = html.unescape(text)
    text = re.sub(r"<\s*br\s*/?\s*>", " ", text, flags=re.IGNORECASE)
    return clean_site_text(text)


def official_nps_summary(resources, fallback_title, fallback_description=""):
    for item in resources:
        if item["type"] != "link":
            continue
        parsed = urlparse(item["url"])
        if not parsed.netloc.endswith("nps.gov"):
            continue
        if not parsed.path.endswith("/index.htm"):
            continue
        label = clean_title(item["label"])
        title = clean_summary_text(fallback_title)
        description = clean_summary_text(fallback_description)
        marker = "(" + "U.S. National " + "Park Service" + ")"
        if marker in label:
            title_part, description_part = label.split(marker, 1)
            title = clean_summary_text(title_part)
            description = clean_summary_text(description_part) or clean_summary_text(fallback_description)
        return {
            "url": item["url"],
            "title": title,
            "description": description,
        }
    return {
        "url": "",
        "title": clean_summary_text(fallback_title),
        "description": clean_summary_text(fallback_description),
    }


def intro_from_body(body):
    for line in body:
        if len(line) > 90 and not line.startswith("Image:"):
            return line
    return body[0] if body else ""


def is_internal_nav_link(url, page_urls):
    parsed = urlparse(url)
    if parsed.netloc != "www.nationalparkcam.com":
        return False
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
    return normalized in page_urls


def resource_groups(resources, page_urls):
    links, embeds, images = [], [], []
    seen = set()
    for item in resources:
        url = item["url"]
        label = clean_title(item["label"]).strip() or item["type"].title()
        key = (item["type"], label, url)
        if key in seen:
            continue
        seen.add(key)
        if item["type"] == "link":
            if is_internal_nav_link(url, page_urls):
                continue
            if url.startswith("mailto:"):
                continue
            links.append({**item, "label": label})
        elif item["type"] == "embed":
            embeds.append({**item, "label": label})
        elif item["type"] == "image":
            if "email" in label.lower() or "sociallinks" in url or "sheets_32dp" in url:
                continue
            images.append({**item, "label": label})
    return links, embeds, images


def is_map_embed(embed):
    return "maps-api-ssl.google.com" in embed["url"]


def rendered_embed_count(embeds):
    return sum(1 for embed in embeds if "youtube.com/embed/" in embed["url"])


def first_webcam_image(webcam_sources):
    for source in webcam_sources:
        if source.get("kind") == "image" and source.get("url") and "nps.gov" in source["url"]:
            return source["url"]
    for source in webcam_sources:
        if source.get("kind") == "image" and source.get("url"):
            return source["url"]
    return ""


def section_has_body(section):
    return any(not line.startswith("Image:") for line in section["paragraphs"])


def inline_link_candidates(links):
    grouped = {}
    candidates = []

    def add_candidate(label, url, copies=1):
        label = clean_title(label).strip().rstrip(".")
        if not label or url.startswith("mailto:"):
            return
        if label.startswith(("http://", "https://")):
            return
        if len(label) > 80:
            return
        if label not in grouped:
            grouped[label] = {"label": label, "urls": []}
            candidates.append(grouped[label])
        grouped[label]["urls"].extend([url] * copies)

    for link in links:
        label = clean_title(link["label"]).strip()
        url = link["url"]
        parsed = urlparse(url)
        if parsed.netloc.endswith("nps.gov") and re.fullmatch(r"/[^/]+/index\.htm", parsed.path):
            add_candidate("official NPS page", url)
            add_candidate("official NPS site", url)
            add_candidate("current alerts", url)
        path_lower = parsed.path.lower()
        basename = path_lower.rsplit("/", 1)[-1]
        label_lower = label.lower()
        is_general_camping_link = (
            label_lower in {
                "camp",
                "camping",
                "campgrounds",
                "nps camping page",
                "nps campground page",
                "nps camping information",
                "nps campground information",
                "nps site",
                "nps website",
            }
            or label_lower.endswith(" campgrounds")
            or basename in {"camp.htm", "camping.htm", "campgrounds.htm", "campinga.htm", "campground.htm", "campingbcdv.htm"}
        )
        if parsed.netloc.endswith("nps.gov") and "camp" in path_lower and is_general_camping_link:
            add_candidate("official NPS campground page", url)
            add_candidate("official NPS camping page", url)
            add_candidate("NPS campground page", url)
            add_candidate("NPS camping page", url)
            add_candidate("NPS campground information", url)
            add_candidate("NPS camping information", url)
            add_candidate("campground information", url)
            add_candidate("camping information", url)
            add_candidate("campground page", url)
            add_candidate("camping page", url)
        if label.lower() == "maps":
            add_candidate("park map", url)
            add_candidate("maps", url)
            continue
        if label.lower() == "hiking":
            add_candidate("NPS Hiking page", url)
            add_candidate("official NPS Hiking page", url)
            add_candidate(label, url)
            continue
        if label.lower() == "camping":
            add_candidate("NPS Camping details", url)
            add_candidate("NPS Camping information", url)
            add_candidate("NPS Camping page", url)
            add_candidate("official NPS Camping page", url)
            add_candidate(label, url)
            continue
        if label.lower() in {"recreation.gov", "reservations"}:
            add_candidate("reservation links", url)
            add_candidate("reservations", url)
            add_candidate(label, url)
            continue
        if label.lower() == "bike":
            add_candidate("Bike riding", url)
            add_candidate("Biking", url)
            continue
        add_candidate(label, url)
        if "wikipedia.org" in url:
            for alias in ("Wikipedia website", "Wikipedia site", "Wikipedia page", "Wikipedia", "wikipedia website", "wikipedia site", "wikipedia page", "wikipedia"):
                add_candidate(alias, url)

            parsed_name = urlparse(url).path.rsplit("/", 1)[-1].replace("_", " ")
            parsed_name = re.sub(r"%[0-9A-Fa-f]{2}", "", parsed_name).strip()
            if parsed_name:
                short_name = re.sub(r"\s+National\s+Park.*$", "", parsed_name).strip()
                if short_name:
                    add_candidate(f"{short_name} Wikipedia website", url)
                    add_candidate(f"{short_name} Wikipedia site", url)
    candidates.sort(key=lambda item: len(item["label"]), reverse=True)
    return candidates


def park_inline_link_candidates(page_slug, links):
    candidates = inline_link_candidates(links)
    aliases = CAMPING_LINK_ALIASES.get(page_slug, {})
    for label, url in aliases.items():
        candidates.append({"label": label, "urls": [url] * 4})
    nps = official_nps_url(links)
    if nps:
        candidates.append({"label": "official NPS page", "urls": [nps] * 12})
    wiki = wikipedia_url(links)
    if wiki:
        candidates.append({"label": "Wikipedia page", "urls": [wiki] * 12})
    candidates.sort(key=lambda item: len(item["label"]), reverse=True)
    return candidates


def official_nps_url(links):
    for link in links:
        parsed = urlparse(link["url"])
        if parsed.netloc.endswith("nps.gov") and re.fullmatch(r"/[^/]+/index\.htm", parsed.path):
            return link["url"]
    return ""


def wikipedia_url(links):
    for link in links:
        if "wikipedia.org" in link["url"]:
            return link["url"]
    return ""


def linked_paragraph(line, inline_links=None):
    inline_links = inline_links or []
    escaped = html.escape(line)
    for link in inline_links:
        if not link["urls"]:
            continue
        label = html.escape(link["label"])
        pattern = re.compile(rf"(?<![\w/]){re.escape(label)}(?![\w/])", flags=re.IGNORECASE)
        if not pattern.search(escaped):
            continue

        url = html.escape(link["urls"].pop(0))
        parts = re.split(r"(<a\b[^>]*>.*?</a>)", escaped, flags=re.IGNORECASE)
        replaced = False
        for index, part in enumerate(parts):
            if replaced or part.lower().startswith("<a "):
                continue
            if pattern.search(part):
                parts[index] = pattern.sub(
                    lambda match: f'<a href="{url}" target="_blank" rel="noopener">{match.group(0)}</a>',
                    part,
                    count=1,
                )
                replaced = True
        if replaced:
            escaped = "".join(parts)
        else:
            link["urls"].insert(0, html.unescape(url))
    return escaped


def inline_formatting(rendered):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)


BOLD_LEAD_LABELS = {
    "Camping",
    "Hotel/Lodge",
    "Restaurants",
    "Grocery Stores",
    "Food and groceries",
    "Food and Groceries",
    "Riding the River",
    "Biking",
}

BOLD_LEAD_STOPWORDS = {
    "A",
    "All",
    "Also",
    "For",
    "Here",
    "However",
    "If",
    "In",
    "It",
    "Please",
    "The",
    "There",
    "These",
    "This",
    "Visitors",
    "We",
}


def title_like_words(text):
    words = text.replace("&", " ").split()
    if not words:
        return False
    title_words = 0
    for word in words:
        stripped = word.strip(".,:;()[]")
        if not stripped or stripped.lower() in {"and", "of", "the", "to", "at", "from"}:
            continue
        if stripped[0].isupper() or stripped[0].isdigit():
            title_words += 1
        else:
            return False
    return title_words > 0


def detect_bold_lead(line):
    for label in sorted(BOLD_LEAD_LABELS, key=len, reverse=True):
        if line.startswith(label + " "):
            return label

    first_word = line.split(" ", 1)[0].strip(".,:;")
    if first_word in BOLD_LEAD_STOPWORDS:
        return ""

    for marker in (" This ", " The campground ", " The trail ", " The lodge "):
        if marker in line:
            lead = line.split(marker, 1)[0].strip()
            if 1 <= len(lead.split()) <= 7 and title_like_words(lead):
                return lead

    match = re.match(
        r"^(.{2,70}?)(?=\s+(?:is|are|has|have|offers|provides|takes|runs|allows|will|can|:)\b)",
        line,
    )
    if match:
        lead = match.group(1).strip()
        if 1 <= len(lead.split()) <= 7 and title_like_words(lead):
            return lead
    return ""


def bold_lead_text(rendered, line):
    if rendered.startswith("<strong>"):
        return rendered

    anchor = re.match(r"^(<a\b[^>]*>.*?</a>)(\s*)", rendered, flags=re.IGNORECASE)
    if anchor:
        return f"<strong>{anchor.group(1)}</strong>{anchor.group(2)}{rendered[anchor.end():]}"

    lead = detect_bold_lead(line)
    if not lead:
        return rendered

    escaped_lead = html.escape(lead)
    if rendered.startswith(escaped_lead):
        return f"<strong>{escaped_lead}</strong>{rendered[len(escaped_lead):]}"
    return rendered


def park_heading_name(page_slug, title):
    return PARK_NAMES.get(page_slug) or title.replace(" Webcams", "").replace(" Guide", "").strip()


def seo_section_heading(section_title, page_slug="", page_title=""):
    if not section_title or not page_slug:
        return section_title
    park_name = park_heading_name(page_slug, page_title)
    short = short_name(page_title)
    lower = section_title.lower()
    if park_name.lower() in lower or short.lower() in lower:
        return section_title
    exact_headings = {
        "introduction": f"{park_name} Overview",
        "planning highlights": f"Things to Do in {park_name}",
        "official resources": f"Official {park_name} Resources",
        "hiking": f"{park_name} Hiking Trails",
        "backpacking": f"{park_name} Backpacking",
        "camping": f"{park_name} Camping",
        "lodging": f"{park_name} Lodging",
        "camping and lodging": f"{park_name} Camping and Lodging",
        "camping / lodging": f"{park_name} Camping and Lodging",
        "cave tours": f"{park_name} Cave Tours",
        "planning a visit": f"Planning a Visit to {park_name}",
    }
    if lower in exact_headings:
        return exact_headings[lower]
    if lower == "hiking and backpacking":
        return f"{park_name} Hiking and Backpacking"
    if lower in {"walking and historic sites", "walking, snorkeling, and camping", "boating, paddling, and island walks"}:
        return f"{section_title} in {park_name}"
    if "camping" in lower or "lodging" in lower or "backpacking" in lower or "hiking" in lower:
        return f"{section_title} in {park_name}"
    return section_title


def text_to_html(body, inline_links=None, page_slug="", page_title="", wikipedia_link="", nps_link=""):
    inline_links = inline_links or []
    sections = []
    current = {"title": "", "paragraphs": []}
    for line in body:
        if line.startswith("Image:"):
            continue
        if line in SECTION_TITLES or (len(line) <= 46 and not line.endswith((".", ",")) and len(line.split()) <= 7):
            if current["title"] or section_has_body(current):
                sections.append(current)
            current = {"title": line, "paragraphs": []}
        else:
            current["paragraphs"].append(line)
    if current["title"] or section_has_body(current):
        sections.append(current)

    out = []
    for section in sections:
        if not section_has_body(section):
            continue
        section_title = seo_section_heading(section["title"], page_slug, page_title)
        heading = f"<h2>{inline_formatting(html.escape(section_title))}</h2>" if section_title else ""
        section_paragraphs = list(section["paragraphs"])
        if section["title"] == "Introduction" and wikipedia_link:
            section_paragraphs = [
                line
                for line in section_paragraphs
                if not (
                    "wikipedia" in line.lower()
                    and line.strip().lower().startswith(
                        (
                            "for more information",
                            "for more on",
                            "visit the wikipedia",
                            "please visit the wikipedia",
                            "see wikipedia",
                        )
                    )
                )
            ]
            section_paragraphs.append(
                "For more information see the park's Wikipedia page."
            )
        if section["title"] == "Introduction" and nps_link:
            section_paragraphs.append(
                "For official park information, visit the official NPS page."
            )
        paragraphs = "".join(
            f"<p>{bold_lead_text(inline_formatting(linked_paragraph(line, inline_links)), line)}</p>"
            for line in section_paragraphs
        )
        out.append(f'<section class="content-section">{heading}{paragraphs}</section>')
    return "\n".join(out)


def official_resources_body(body, page, title, links):
    has_reservations = any(
        clean_title(link["label"]).strip().lower() in {"recreation.gov", "reservations"} or "recreation.gov" in link["url"]
        for link in links
    )
    replacement = f"Use the official NPS page, park map, and current alerts"
    if has_reservations:
        replacement += ", plus reservation links"
    park_name = NO_CAMERA_PARK_NAMES.get(page["slug"]) or WEBCAM_PARK_NAMES.get(page["slug"]) or title
    replacement += f" when planning a trip to {park_name}."
    return [
        replacement
        if line.startswith("Use the official NPS page, park map, current alerts, and reservation links below when planning a trip to ")
        else line
        for line in body
    ]


def youtube_id(url):
    match = re.search(r"/embed/([^?&/]+)", url)
    return match.group(1) if match else ""


def is_webcam_heading(line):
    normalized = re.sub(r"\s+", " ", line.lower())
    return "webcam" in normalized or "web cam" in normalized or "web c am" in normalized


def webcam_caption_lines(body):
    try:
        intro_index = body.index("Introduction")
    except ValueError:
        return []
    start = next((index + 1 for index, line in enumerate(body[:intro_index]) if is_webcam_heading(line)), -1)
    if start < 0:
        return []
    captions = []
    for line in body[start:intro_index]:
        if not is_webcam_heading(line) and len(line) <= 180:
            captions.append(line)
    return captions


def strip_webcam_caption_block(body):
    captions = webcam_caption_lines(body)
    if not captions:
        return body
    intro_index = body.index("Introduction")
    start = next((index for index, line in enumerate(body[:intro_index]) if is_webcam_heading(line)), -1)
    if start < 0:
        return body
    return body[:start] + body[intro_index:]


def strip_body_lead_for_page(page_slug, body):
    if page_slug in {"big-bend-webcam", "grand-tetons-webcam", "lassen-volcano-webcam", "mammoth-cave-webcam", "mount-rainier-webcam", "new-river-gorge-webcam", "north-cascades-webcam", "olympic-webcam", "petrified-forest-webcam", "redwood-national-park", "rocky-mountain-webcam", "shenandoah-webcam", "theodore-roosevelt-webcam", "virgin-islands-webcam", "wrangell-st-elias-webcam", "yellowstone-webcam"} and body and "Introduction" in body:
        if body[0] == "Introduction":
            return body
        return body[1:]
    return body


def caption_for_label(label, captions):
    label_key = re.sub(r"[^a-z0-9]+", " ", html.unescape(label).lower())
    best_index = -1
    best_score = 0
    for index, caption in enumerate(captions):
        caption_key = re.sub(r"[^a-z0-9]+", " ", caption.lower())
        words = {word for word in caption_key.split() if len(word) > 3}
        score = sum(1 for word in words if word in label_key)
        if score > best_score:
            best_index = index
            best_score = score
    if best_index < 0 or best_score == 0:
        return ""
    caption = captions.pop(best_index)
    if " - " in caption:
        prefix, detail = caption.split(" - ", 1)
        if prefix.lower() in html.unescape(label).lower():
            return detail
    return caption


def webcam_description(source, captions):
    description = source.get("description", "").strip()
    if not description:
        description = caption_for_label(source.get("title", ""), captions)
    if description and description != source.get("status", ""):
        return f"<p>{html.escape(description)}</p>"
    return ""


def youtube_video_id(url):
    match = re.search(r"youtube\.com/embed/([^?&#/]+)", html.unescape(url))
    return match.group(1) if match else ""


def render_video_frame(src, title):
    video_id = youtube_video_id(src)
    if not video_id:
        return f'<div class="embed-frame"><iframe src="{src}" title="{title}" loading="lazy" allowfullscreen></iframe></div>'
    thumbnail = html.escape(f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
    thumbnail_alt = html.escape(f"{html.unescape(title)} video thumbnail")
    srcdoc = html.escape(
        f"""
        <style>
          body {{ margin: 0; }}
          a {{ display: grid; place-items: center; position: relative; height: 100vh; overflow: hidden; background: #111; color: white; text-decoration: none; }}
          img {{ width: 100%; height: 100%; object-fit: cover; }}
          span {{ position: absolute; display: grid; place-items: center; width: 68px; height: 48px; border-radius: 8px; background: rgba(0,0,0,.74); }}
          span::before {{ content: ""; width: 0; height: 0; margin-left: 4px; border-top: 11px solid transparent; border-bottom: 11px solid transparent; border-left: 18px solid white; }}
        </style>
        <a href="{html.unescape(src)}" aria-label="Play {html.unescape(title)}">
          <img src="{thumbnail}" alt="{thumbnail_alt}">
          <span></span>
        </a>
        """,
        quote=True,
    )
    return f'<div class="embed-frame"><iframe src="{src}" srcdoc="{srcdoc}" title="{title}" loading="lazy" allowfullscreen></iframe></div>'


def render_hls_frame(src, title, video_id=""):
    video_id = video_id or "hls-" + re.sub(r"[^a-z0-9]+", "-", html.unescape(title).lower()).strip("-")
    escaped_src = html.escape(src)
    escaped_title = html.escape(html.unescape(title))
    return f"""
                  <div class="embed-frame">
                    <video id="{video_id}" class="webcam-hls-video" autoplay muted playsinline controls aria-label="{escaped_title}">
                      <source src="{escaped_src}" type="application/x-mpegURL">
                    </video>
                  </div>
                  <script src="https://cdn.jsdelivr.net/npm/hls.js@1" defer></script>
                  <script>
                    window.addEventListener("load", function () {{
                      var video = document.getElementById("{video_id}");
                      var src = "{escaped_src}";
                      if (!video) return;
                      if (video.canPlayType("application/vnd.apple.mpegurl")) {{
                        video.src = src;
                      }} else if (window.Hls && window.Hls.isSupported()) {{
                        var hls = new Hls();
                        hls.loadSource(src);
                        hls.attachMedia(video);
                      }}
                      video.muted = true;
                      video.play().catch(function () {{}});
                    }});
                  </script>
    """


def render_webcam_source_cards(webcam_sources, captions=None, page_slug=""):
    captions = captions or []
    cards = []
    nationalparkcam_url = html.escape(nationalparkcam_park_url(page_slug)) if page_slug else ""
    nationalparkcam_link = (
        f'<a class="source-link" href="{nationalparkcam_url}" target="_blank" rel="noopener">View this webcam on NationalParkCam.com</a>'
        if nationalparkcam_url
        else ""
    )
    for source in webcam_sources:
        title = html.escape(source["title"])
        url = html.escape(source["url"])
        page_url = html.escape(source["page_url"])
        provider = html.escape(source["provider"])
        status = html.escape(source["status"])
        description = webcam_description(source, captions)
        kind = source.get("kind")
        if kind == "hls":
            cards.append(
                f"""
                <article class="embed-card video-card">
                  {render_hls_frame(source["url"], title)}
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        elif kind == "iframe":
            cards.append(
                f"""
                <article class="embed-card video-card">
                  {render_video_frame(url, title)}
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        elif kind == "page":
            cards.append(
                f"""
                <article class="embed-card video-card webcam-page-card">
                  <div class="embed-frame"><iframe src="{url}" title="{title}" loading="lazy" allowfullscreen></iframe></div>
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        elif kind == "inactive":
            cards.append(
                f"""
                <article class="embed-card webcam-unavailable-card">
                  <div class="webcam-unavailable-media" role="img" aria-label="{title} is temporarily unavailable">
                    <span>Webcam temporarily unavailable</span>
                  </div>
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        else:
            cards.append(
                f"""
                <article class="embed-card webcam-image-card">
                  <div class="webcam-image-media" data-full-src="{url}" data-title="{title}" data-nationalparkcam-url="{nationalparkcam_url}">
                    <img src="{url}" data-refresh-src="{url}" alt="{title}" loading="lazy" onerror="this.closest('.webcam-image-card').classList.add('image-missing'); this.remove();">
                  </div>
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
    return cards


def render_park_map_card(page_slug):
    coords = PARK_COORDS.get(page_slug)
    if not coords:
        return ""
    lat, lng = coords
    return f"""
                <article class="embed-card park-location-card">
                  <div class="embed-frame map park-location-map" data-park-map data-lat="{lat}" data-lng="{lng}"></div>
                  <div class="embed-meta"><strong>Park location</strong></div>
                </article>
                """


def render_guide_image_card(page_slug, title):
    image = GUIDE_IMAGES.get(page_slug)
    if not image:
        return ""
    return f"""
                <article class="embed-card guide-image-card">
                  <div class="guide-image-media" data-full-src="{html.escape(image["url"])}" data-title="{html.escape(image["alt"])}">
                    <img src="{html.escape(image["url"])}" alt="{html.escape(image["alt"])}" loading="lazy">
                  </div>
                  <div class="embed-meta"><strong>{html.escape(park_heading_name(page_slug, title))}</strong><p>Official park image from the National Park Service.</p></div>
                </article>
                """


def render_embed_cards(embeds, webcam_sources=None, captions=None, page_slug=""):
    webcam_sources = webcam_sources or []
    captions = list(captions or [])
    cards = []
    missing = []
    has_map = False
    for embed in embeds:
        url = embed["url"]
        raw_label = embed["label"]
        label = html.escape(raw_label)
        if "youtube.com/embed/" in url:
            if youtube_id(url) in BLOCKED_YOUTUBE_IDS:
                continue
            src = html.escape(url)
            caption = caption_for_label(raw_label, captions)
            caption_html = f"<p>{html.escape(caption)}</p>" if caption else ""
            cards.append(
                f"""
                <article class="embed-card video-card">
                  {render_video_frame(src, label)}
                  <div class="embed-meta"><span>Live video</span><strong>{html.escape(clean_embed_label(raw_label))}</strong>{caption_html}</div>
                </article>
                """
            )
        elif "maps-api-ssl.google.com" in url:
            has_map = True
        elif url.startswith("google-sites-frame:"):
            missing.append((label, html.escape(url.replace("google-sites-frame:", ""))))
    if has_map:
        cards.append(render_park_map_card(page_slug))
    cards.extend(render_webcam_source_cards(webcam_sources, captions, page_slug))
    return "\n".join(cards)


def render_link_list(links):
    useful = links[:28]
    items = []
    for link in useful:
        items.append(
            f'<li><a href="{html.escape(link["url"])}" target="_blank" rel="noopener">{html.escape(link["label"])}</a></li>'
        )
    return "\n".join(items)


def clean_embed_label(label):
    return label.replace("YouTube Video, ", "").strip()


def popular_streams(resources_by_url, pages, webcam_sources_by_slug=None):
    webcam_sources_by_slug = webcam_sources_by_slug or {}
    seen_video_ids = set()
    streams = []
    yellowstone = next((page for page in pages if page["slug"] == "yellowstone-webcam"), None)
    if yellowstone:
        yellowstone_hls = next(
            (
                source
                for source in webcam_sources_by_slug.get("yellowstone-webcam", [])
                if source.get("kind") == "hls"
            ),
            None,
        )
        if yellowstone_hls:
            streams.append(
                {
                    "park": short_name(yellowstone["title"]),
                    "label": yellowstone_hls["title"],
                    "url": yellowstone_hls["url"],
                    "href": nationalparkcam_park_url(yellowstone["slug"]),
                    "kind": "hls",
                }
            )
    for page in pages:
        for item in resources_by_url[page["url"]]:
            if item["type"] != "embed" or "youtube.com/embed/" not in item["url"]:
                continue
            video_id = youtube_id(item["url"])
            if not video_id or video_id in BLOCKED_YOUTUBE_IDS or video_id in seen_video_ids or video_id not in ACTIVE_HERO_YOUTUBE_IDS:
                continue
            seen_video_ids.add(video_id)
            streams.append(
                {
                    "park": short_name(page["title"]),
                    "label": clean_embed_label(clean_title(item["label"])),
                    "url": item["url"],
                    "href": nationalparkcam_park_url(page["slug"]),
                    "kind": "youtube",
                }
            )
    return streams


def youtube_autoplay_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query.update(
        {
            "autoplay": ["1"],
            "mute": ["1"],
            "playsinline": ["1"],
            "rel": ["0"],
        }
    )
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def render_popular_streams(streams):
    if not streams:
        return ""
    initial = streams[0]
    stream_json = html.escape(json.dumps(streams), quote=False)
    if initial.get("kind") == "hls":
        player = render_hls_frame(initial["url"], initial["label"], "hero-live-video")
    else:
        initial_src = youtube_autoplay_url(initial["url"])
        player = f"""
            <iframe
              id="hero-video-iframe"
              src="{html.escape(initial_src)}"
              title="{html.escape(initial['label'])}"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen></iframe>
        """
    return f"""
        <div class="hero-video-player" data-random-hero-video>
          <script type="application/json" id="hero-video-data">{stream_json}</script>
          <div class="hero-video-frame">
            {player}
          </div>
          <div class="hero-video-meta">
            <span id="hero-video-park">{html.escape(initial['park'])}</span>
            <strong id="hero-video-title">{html.escape(initial['label'])}</strong>
            <a id="hero-video-link" href="{html.escape(initial['href'])}" target="_blank" rel="noopener">View on NationalParkCam.com</a>
          </div>
        </div>
    """


def render_nav(pages, current_slug, depth):
    prefix = "" if depth == 0 else "../"
    links = [
        f'<a href="{prefix}index.html">Home</a>',
        f'<a href="{prefix}index.html#parks">Parks</a>',
    ]
    if current_slug not in {"national-park-webcam-home", "resources"}:
        current = next((p for p in pages if p["slug"] == current_slug), None)
        if current:
            links.append(f'<a aria-current="page" href="{prefix}parks/{current["slug"]}.html">{html.escape(short_name(current["title"]))}</a>')
    return "\n".join(links)


def render_breadcrumbs(title, page_slug, depth):
    if page_slug == "national-park-webcam-home":
        return ""
    prefix = "" if depth == 0 else "../"
    if page_slug in INFO_PAGE_SLUGS:
        crumbs = [
            (f"{prefix}index.html", "Home"),
            ("", title),
        ]
    else:
        crumbs = [
            (f"{prefix}index.html", "Home"),
            (f"{prefix}index.html#parks", "Park Directory"),
            ("", title),
        ]
    items = []
    for href, label in crumbs:
        if href:
            items.append(f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>')
        else:
            items.append(f'<li aria-current="page">{html.escape(label)}</li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def render_header_search(pages, depth):
    entries = []
    for page in pages:
        if page["slug"] == "national-park-webcam-home":
            continue
        label = short_name(page["title"])
        full_title = page["title"].replace(" Webcams", "").replace(" Guide", "").strip()
        entries.append(
            {
                "slug": page["slug"],
                "label": label,
                "title": full_title,
                "href": page_target_href(page, depth=depth),
                "external": not is_no_camera_page(page["slug"]),
                "type": "Guide" if is_no_camera_page(page["slug"]) else "Live cams",
            }
        )
    data = html.escape(json.dumps(entries, ensure_ascii=False), quote=False)
    return f"""
      <form class="header-search" role="search" autocomplete="off">
        <label class="sr-only" for="header-park-search">Search national parks</label>
        <input id="header-park-search" type="search" placeholder="Search parks" aria-label="Search national parks" aria-controls="header-search-results" aria-expanded="false">
        <div class="header-search-results" id="header-search-results" role="listbox" hidden></div>
        <script type="application/json" id="header-search-data">{data}</script>
      </form>
    """


def short_name(title):
    if title.startswith("National Park of American Samoa"):
        return "American Samoa"
    title = title.replace("National and State Parks Webcams", "")
    title = title.replace("National Parks Webcams", "")
    title = title.replace("National Park Webcams", "")
    title = title.replace("National Park", "")
    title = title.replace("Webcams", "")
    title = title.replace("Guide", "")
    return re.sub(r"\s+", " ", title).strip(" -.") or title


def hero_intro(title, intro):
    park_name = title.replace(" Webcams", "").strip()
    if intro.startswith(f"{park_name} "):
        return intro[len(park_name):].strip()
    return intro


def related_park_links(current_page, pages, count=6):
    current_coords = PARK_COORDS.get(current_page["slug"])
    if not current_coords:
        return ""
    local_guides = []
    live_cam_parks = []
    for page in pages:
        coords = PARK_COORDS.get(page["slug"])
        if not coords or page["slug"] == current_page["slug"]:
            continue
        distance = (coords[0] - current_coords[0]) ** 2 + (coords[1] - current_coords[1]) ** 2
        if is_no_camera_page(page["slug"]):
            local_guides.append((distance, page))
        else:
            live_cam_parks.append((distance, page))
    local_guides.sort(key=lambda item: item[0])
    live_cam_parks.sort(key=lambda item: item[0])

    selected = []
    selected.extend(local_guides[:3])
    remaining = count - len(selected)
    selected.extend(live_cam_parks[:remaining])
    if len(selected) < count:
        used = {page["slug"] for _, page in selected}
        selected.extend(item for item in local_guides[3:] + live_cam_parks[remaining:] if item[1]["slug"] not in used)
    selected = selected[:count]

    cards = []
    for _, page in selected:
        title = short_name(page["title"])
        href = page_target_href(page, depth=1)
        local_page = is_no_camera_page(page["slug"])
        action = "Read park guide" if local_page else "View live cams on NationalParkCam.com"
        target_attrs = "" if is_no_camera_page(page["slug"]) else ' target="_blank" rel="noopener"'
        cards.append(
            f"""
            <a class="related-park-card" href="{html.escape(href)}"{target_attrs}>
              <span>{html.escape(title)}</span>
              <strong>{html.escape(action)}</strong>
            </a>
            """
        )
    if not cards:
        return ""
    return f"""
    <section class="related-parks-section" aria-labelledby="related-parks-heading">
      <div class="section-heading">
        <div>
          <span class="eyebrow">More parks</span>
          <h2 id="related-parks-heading">More National Park Guides</h2>
          <p class="section-note">Continue planning with nearby park guides on this site or open live camera pages on NationalParkCam.com.</p>
        </div>
      </div>
      <div class="related-park-grid">{''.join(cards)}</div>
    </section>
"""


def related_guide_links(current_page, pages, count=8):
    current_slug = current_page["slug"]
    if not is_no_camera_page(current_slug):
        return ""
    current_topics = GUIDE_TOPICS.get(current_slug, set())
    if not current_topics:
        return ""

    current_coords = PARK_COORDS.get(current_slug)
    candidates = []
    for page in pages:
        slug = page["slug"]
        if slug == current_slug or not is_no_camera_page(slug):
            continue
        shared = current_topics & GUIDE_TOPICS.get(slug, set())
        if not shared:
            continue
        coords = PARK_COORDS.get(slug)
        distance = 9999
        if current_coords and coords:
            distance = (coords[0] - current_coords[0]) ** 2 + (coords[1] - current_coords[1]) ** 2
        candidates.append((-len(shared), distance, page, shared))
    candidates.sort(key=lambda item: (item[0], item[1], short_name(item[2]["title"])))

    cards = []
    for _, _, page, shared in candidates[:count]:
        labels = [TOPIC_LABELS.get(topic, topic) for topic in sorted(shared)]
        topic_text = ", ".join(labels[:3])
        cards.append(
            f"""
            <a class="related-park-card internal-guide-card" href="{html.escape(page_target_href(page, depth=1))}">
              <span>{html.escape(short_name(page["title"]))}</span>
              <p>Related: {html.escape(topic_text)}</p>
              <strong>Read park guide</strong>
            </a>
            """
        )
    if not cards:
        return ""

    current_topic_labels = [TOPIC_LABELS.get(topic, topic) for topic in sorted(current_topics)]
    topic_summary = ", ".join(current_topic_labels[:5])
    return f"""
    <section class="related-parks-section internal-guides-section" aria-labelledby="internal-guides-heading">
      <div class="section-heading">
        <div>
          <span class="eyebrow">Related guides</span>
          <h2 id="internal-guides-heading">Related National Park Guides</h2>
          <p class="section-note">Continue planning with local guide pages connected by {html.escape(topic_summary)}.</p>
        </div>
      </div>
      <div class="related-park-grid">{''.join(cards)}</div>
    </section>
"""


def guide_faqs(page_slug, title):
    if not is_no_camera_page(page_slug):
        return []
    park_name = NO_CAMERA_PARK_NAMES.get(page_slug, title.replace(" Guide", ""))
    return [
        {
            "question": f"What are the best things to do in {park_name}?",
            "answer": GUIDE_FAQ_ACTIVITIES.get(
                page_slug,
                f"Use this {park_name} guide to compare hiking, scenic stops, camping notes, weather, maps, and official NPS planning resources.",
            ),
        },
        {
            "question": f"Can you camp in {park_name}?",
            "answer": GUIDE_FAQ_CAMPING.get(
                page_slug,
                f"Camping options vary by season and location. Check the official NPS camping information for current rules, reservations, and closures before planning an overnight trip to {park_name}.",
            ),
        },
        {
            "question": f"Are there live webcams in {park_name}?",
            "answer": f"This guide page does not host a current webcam page for {park_name}. For live views from other national parks, use NationalParkCam.com and compare active park camera pages.",
        },
        {
            "question": f"What should I check before visiting {park_name}?",
            "answer": f"Check current NPS alerts, weather, maps, road or trail conditions, permits, campground status, and seasonal closures before visiting {park_name}.",
        },
    ]


def render_guide_faq_section(page_slug, title):
    faqs = guide_faqs(page_slug, title)
    if not faqs:
        return ""
    items = []
    for faq in faqs:
        items.append(
            f"""
            <article class="faq-item">
              <h3>{html.escape(faq["question"])}</h3>
              <p>{html.escape(faq["answer"])}</p>
            </article>
            """
        )
    return f"""
    <section class="faq-section" aria-labelledby="park-faq-heading">
      <div class="section-heading">
        <div>
          <span class="eyebrow">Park FAQ</span>
          <h2 id="park-faq-heading">Frequently Asked Questions</h2>
        </div>
      </div>
      <div class="faq-grid">{''.join(items)}</div>
    </section>
"""


def structured_data(title, page_slug, description, canonical_url):
    site_name = "National Parks and Monuments Guide" if page_slug == "national-park-webcam-home" or is_no_camera_page(page_slug) else "National Parks Webcams"
    website_node = {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "name": "National Parks and Monuments Guide",
        "alternateName": "National Parks US",
        "url": SITE_URL,
        "description": "Browse national park, monument, and public-land guides with maps, weather, official resources, and live camera links.",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }
    if page_slug == "national-park-webcam-home":
        graph = {
            "@context": "https://schema.org",
            "@graph": [
                website_node,
                {
                    "@type": "CollectionPage",
                    "@id": f"{canonical_url}/#webpage",
                    "name": title,
                    "url": canonical_url,
                    "description": description,
                    "isPartOf": {"@id": f"{SITE_URL}/#website"},
                    "mainEntity": {
                        "@type": "ItemList",
                        "name": "National parks, monuments, and public land guide directory",
                        "itemListOrder": "https://schema.org/ItemListOrderAscending",
                    },
                },
            ],
        }
    else:
        park_name = PARK_NAMES.get(page_slug, title.replace(" Webcams", "").replace(" Guide", ""))
        page_type = "CollectionPage" if page_slug in INFO_PAGE_SLUGS else "WebPage"
        breadcrumb_items = [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": SITE_URL,
            }
        ]
        if page_slug in INFO_PAGE_SLUGS:
            breadcrumb_items.append(
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": title,
                    "item": canonical_url,
                }
            )
        else:
            breadcrumb_items.extend(
                [
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Park Directory",
                        "item": f"{SITE_URL}/#parks",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": title,
                        "item": canonical_url,
                    },
                ]
            )
        graph = {
            "@context": "https://schema.org",
            "@graph": [
                website_node,
                {
                "@type": "WebPage",
                "@id": f"{canonical_url}#webpage",
                "name": title,
                "url": canonical_url,
                "description": description,
                "isPartOf": {"@id": f"{SITE_URL}/#website"},
                "breadcrumb": {"@id": f"{canonical_url}#breadcrumb"},
                "about": {
                    "@type": "TouristAttraction",
                    "name": park_name,
                    "url": canonical_url,
                }
                if page_slug not in INFO_PAGE_SLUGS
                else None,
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": breadcrumb_items,
            },
            ],
        }
        if page_slug in INFO_PAGE_SLUGS:
            graph["@graph"][1]["@type"] = page_type
            graph["@graph"][1].pop("about", None)
        faqs = guide_faqs(page_slug, title)
        if faqs:
            graph["@graph"].append(
                {
                    "@type": "FAQPage",
                    "@id": f"{canonical_url}#faq",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": faq["question"],
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": faq["answer"],
                            },
                        }
                        for faq in faqs
                    ],
                }
            )
    return json.dumps(graph, ensure_ascii=False)


def seo_page_title(title, page_slug):
    if page_slug == "national-park-webcam-home":
        return "National Park Guide | Parks, Monuments, Maps & Weather"
    if page_slug in INFO_PAGE_SLUGS:
        return f"{title} | National Parks Webcams"
    if is_no_camera_page(page_slug):
        custom = GUIDE_SEO.get(page_slug, {}).get("title")
        if custom:
            return custom
        park_name = NO_CAMERA_PARK_NAMES.get(page_slug, title.replace(" Guide", ""))
        seo_title = f"{park_name} Guide | Weather, Map & Planning"
        if len(seo_title) > 70:
            seo_title = f"{park_name} Guide | Park Map & Weather"
        if len(seo_title) > 70:
            seo_title = f"{short_name(title)} Guide | Weather & Map"
        return seo_title
    park_name = WEBCAM_PARK_NAMES.get(page_slug, title.replace(" Webcams", ""))
    seo_title = f"{park_name} Webcams | Live Cams, Weather & Map"
    if len(seo_title) > 70:
        seo_title = f"{park_name} Cams | Weather & Map"
    if len(seo_title) > 70:
        seo_title = f"{short_name(title)} Cams | Weather & Map"
    return seo_title


def seo_description(title, page_slug, description):
    if is_no_camera_page(page_slug):
        custom = GUIDE_SEO.get(page_slug, {}).get("description")
        if custom:
            return custom
        park_name = NO_CAMERA_PARK_NAMES.get(page_slug, title.replace(" Guide", ""))
        meta = (
            f"{park_name} guide with weather, map, activities, camping and lodging notes, "
            "NPS links, visitor stats, acreage, and park history."
        )
        if len(meta) > 155:
            meta = f"{park_name} guide with weather, map, activities, camping, lodging, NPS links, and park history."
        return meta
    return description


def truncate_meta(text, limit):
    clean = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if len(clean) <= limit:
        return clean
    clipped = clean[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,.;:-")
    while re.search(r"\b(?:and|or|the|of|in|with|to|from|for)$", clipped, flags=re.IGNORECASE):
        clipped = clipped.rsplit(" ", 1)[0].rstrip(" ,.;:-")
    return clipped


def google_analytics_tag():
    measurement_id = html.escape(GOOGLE_ANALYTICS_ID)
    return f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{measurement_id}');
  </script>"""


def page_shell(title, body, page_slug, pages, description, image="", depth=0):
    prefix = "" if depth == 0 else "../"
    image_meta = f'<meta property="og:image" content="{html.escape(image)}">' if image else ""
    twitter_image_meta = f'<meta name="twitter:image" content="{html.escape(image)}">' if image else ""
    if page_slug == "national-park-webcam-home":
        canonical_url = SITE_URL
    elif page_slug in INFO_PAGE_SLUGS:
        canonical_url = f"{SITE_URL}/{page_slug}"
    else:
        canonical_url = f"{SITE_URL}/parks/{page_slug}"
    seo_title = seo_page_title(title, page_slug)
    page_description = seo_description(title, page_slug, description)
    meta_description = truncate_meta(page_description, 155)
    social_description = truncate_meta(page_description, 180)
    json_ld = structured_data(title, page_slug, page_description, canonical_url).replace("</", "<\\/")
    data_attrs = f' data-page-slug="{html.escape(page_slug)}" data-page-title="{html.escape(title)}" data-page-depth="{depth}"'
    brand_label = "National Parks and Monuments Guide home" if page_slug == "national-park-webcam-home" or is_no_camera_page(page_slug) else "National Parks Webcams home"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(seo_title)}</title>
  <meta name="description" content="{html.escape(meta_description)}">
  <meta property="og:title" content="{html.escape(seo_title)}">
  <meta property="og:description" content="{html.escape(social_description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{html.escape(canonical_url)}">
  {image_meta}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(seo_title)}">
  <meta name="twitter:description" content="{html.escape(social_description)}">
  <meta name="twitter:url" content="{html.escape(canonical_url)}">
  {twitter_image_meta}
  <link rel="canonical" href="{html.escape(canonical_url)}">
  <link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/favicon-32x32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="{prefix}assets/apple-touch-icon.png">
  <script type="application/ld+json">{json_ld}</script>
{google_analytics_tag()}
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body{data_attrs}>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html" aria-label="{html.escape(brand_label)}">
      <img class="brand-logo" src="{prefix}assets/npsLogo.png" alt="National Park Cam logo">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <div class="header-nav-group">
      {render_header_search(pages, depth)}
      <nav class="recent-parks" id="recent-parks" aria-label="Recently viewed parks"></nav>
      <nav class="site-nav" id="site-nav">{render_nav(pages, page_slug, depth)}</nav>
    </div>
  </header>
  {body}
  <section class="footer-contact" aria-label="Contact">
    <p>For questions or comments, email <a href="mailto:npcam012@gmail.com">npcam012@gmail.com</a></p>
    <nav class="footer-links" aria-label="Site information">
      <a href="{prefix}about.html">About</a>
      <a href="{prefix}contact.html">Contact</a>
      <a href="{prefix}privacy-policy.html">Privacy Policy</a>
    </nav>
  </section>
  <footer class="site-footer"></footer>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="{prefix}assets/app.js?v=20260518-live-video-preview"></script>
</body>
</html>
"""


def build_home(pages, content_by_url, resources_by_url, webcam_sources_by_slug):
    home = next(p for p in pages if p["slug"] == "national-park-webcam-home")
    park_pages = sorted(
        (p for p in pages if p["slug"] != "national-park-webcam-home"),
        key=lambda page: page["title"].removesuffix(" Webcams").removesuffix(" Guide").lower(),
    )
    cards = []
    for page in park_pages:
        parsed_title, _, body = content_by_url[page["url"]]
        title = display_title(page, parsed_title)
        res = resources_by_url[page["url"]]
        links, embeds, images = resource_groups(res, {p["url"].rstrip("/") for p in pages})
        cam_count = rendered_embed_count(embeds) + len(webcam_sources_by_slug.get(page["slug"], []))
        intro = intro_from_body(body)
        nps = official_nps_summary(res, PARK_NAMES.get(page["slug"], short_name(title)), intro)
        href = page_target_href(page)
        target_attrs = "" if is_no_camera_page(page["slug"]) else ' target="_blank" rel="noopener"'
        aria_action = "Open" if is_no_camera_page(page["slug"]) else "Open on NationalParkCam.com"
        card_action = "Read park guide" if is_no_camera_page(page["slug"]) else "View live cams on NationalParkCam.com"
        map_count = max(0, len(embeds) - rendered_embed_count(embeds))
        nps_link = (
            f'<a class="official-link" href="{html.escape(nps["url"])}" target="_blank" rel="noopener">Official NPS page</a>'
            if nps["url"]
            else ""
        )
        cards.append(
            f"""
            <article class="park-card" data-title="{html.escape(title.lower())}">
              <a href="{html.escape(href)}"{target_attrs} aria-label="{html.escape(aria_action)} {html.escape(title)}">
                <div class="park-card-body">
                  <h2>{html.escape(nps["title"])}</h2>
                  <p>{html.escape(nps["description"])}</p>
                  <strong class="card-action">{html.escape(card_action)}</strong>
                </div>
              </a>
              {nps_link}
            </article>
            """
        )
    _, _, home_body = content_by_url[home["url"]]
    hero_source = next((p for p in park_pages if p["slug"] == "glacier-webcam"), park_pages[0])
    hero_image = first_image(resources_by_url[hero_source["url"]]) or first_image(resources_by_url[home["url"]])
    description = intro_from_body(home_body)
    page_urls = {p["url"].rstrip("/") for p in pages}
    hero_streams = popular_streams(resources_by_url, park_pages, webcam_sources_by_slug)
    map_points = []
    for page in park_pages:
        links, embeds, _ = resource_groups(resources_by_url[page["url"]], page_urls)
        cam_count = rendered_embed_count(embeds) + len(webcam_sources_by_slug.get(page["slug"], []))
        coords = PARK_COORDS.get(page["slug"])
        if not coords:
            continue
        map_points.append(
            {
                "slug": page["slug"],
                "title": short_name(page["title"]),
                "fullTitle": page["title"],
                "href": page_target_href(page),
                "lat": coords[0],
                "lng": coords[1],
                "cams": cam_count,
                "embeds": len(embeds),
                "links": len(links),
            }
        )
    map_json = html.escape(json.dumps(map_points), quote=False)
    body = f"""
  <main>
    <section class="home-hero">
      <div class="hero-copy">
        <span class="eyebrow">Park and monument webcams, maps, and planning links</span>
        <h1>National Parks & Monuments Guide</h1>
        <p>{html.escape(description)}</p>
      </div>
      <div class="hero-streams" aria-label="Popular live streams">
        {render_popular_streams(hero_streams)}
      </div>
    </section>
    <section class="park-browser" id="parks">
      <div class="section-heading">
        <div>
          <span class="eyebrow">Browse by location</span>
          <h2>Map</h2>
        </div>
        <label class="search-box">
          <span>Search</span>
          <input type="search" id="park-search" placeholder="Yellowstone, Acadia, Zion...">
        </label>
      </div>
      <div class="map-explorer">
        <div id="webcam-map" class="webcam-map" aria-label="Interactive national park webcam map"></div>
        <aside class="map-side">
          <span class="eyebrow">Featured live cams</span>
          <h3 id="map-active-title">Select a park</h3>
          <p id="map-active-meta">Choose a marker or a page below to open the park, monument, or public-land webcam guide.</p>
          <a id="map-active-link" class="button primary" href="#parks" target="_blank" rel="noopener">Open park cams</a>
          <div class="map-list" id="map-list"></div>
        </aside>
      </div>
      <script type="application/json" id="park-map-data">{map_json}</script>
      <div class="section-heading park-grid-heading">
        <div>
          <span class="eyebrow">All park pages</span>
          <h2>Park Directory</h2>
        </div>
      </div>
      <div class="park-grid" id="park-grid">{''.join(cards)}</div>
    </section>
  </main>
"""
    return page_shell("National Parks & Monuments Guide", body, home["slug"], pages, description, hero_image, 0)


def build_park_page(page, pages, content, resources, page_urls, webcam_sources):
    parsed_title, source, body = content
    title = display_title(page, parsed_title)
    links, embeds, images = resource_groups(resources, page_urls)
    cam_count = rendered_embed_count(embeds) + len(webcam_sources)
    map_count = max(0, len(embeds) - rendered_embed_count(embeds))
    intro = intro_from_body(body)
    captions = webcam_caption_lines(body)
    article_body = strip_body_lead_for_page(page["slug"], strip_webcam_caption_block(body))
    article_body = official_resources_body(article_body, page, title, links)
    nps = official_nps_summary(resources, PARK_NAMES.get(page["slug"], short_name(title)), intro)
    planning_url = nps["url"] or (links[0]["url"] if links else source)
    nationalparkcam_url = nationalparkcam_park_url(page["slug"])
    no_camera_page = is_no_camera_page(page["slug"])
    park_name = park_heading_name(page["slug"], title)
    coords = PARK_COORDS.get(page["slug"], ["", ""])
    weather_coords = WEATHER_COORDS.get(page["slug"], coords)
    weather_attrs = f'data-lat="{weather_coords[0]}" data-lng="{weather_coords[1]}"' if weather_coords[0] != "" else ""
    weather_note = WEATHER_LOCATION_LABELS.get(page["slug"], "")
    cam_notice = ""
    if page["slug"] == "black-canyon-of-the-gunnison-webcam":
        cam_notice = '<p class="section-note">The Black Canyon webcams are currently inactive. The park map remains available below.</p>'
    if no_camera_page:
        primary_cta = f'<a class="button primary" href="{html.escape(NATIONALPARKCAM_SITE_URL)}" target="_blank" rel="noopener">View cameras from other national parks</a>'
        hero_actions = ""
        bottom_actions = f"""
    <section class="bottom-page-actions" aria-label="More park resources">
      <div class="page-actions">
        {primary_cta}
        <a class="button" href="{html.escape(planning_url)}" target="_blank" rel="noopener">Visit park website</a>
      </div>
    </section>
"""
        live_section = f"""
    <section class="resource-section guide-visual-section" id="park-map">
      <div class="embed-grid">{render_guide_image_card(page["slug"], title)}{render_park_map_card(page["slug"])}</div>
    </section>
"""
    else:
        primary_cta = f'<a class="button primary" href="{html.escape(nationalparkcam_url)}" target="_blank" rel="noopener">View webcams on NationalParkCam.com</a>'
        hero_actions = f"""
        <div class="page-actions">
          {primary_cta}
          <a class="button" href="{html.escape(planning_url)}" target="_blank" rel="noopener">Visit park website</a>
        </div>"""
        bottom_actions = ""
        live_section = f"""
    <section class="resource-section live-first" id="live-cams">
      <div class="section-heading">
        <div><h2>{html.escape(park_name)} Live Cams and Map</h2></div>
      </div>
      {cam_notice}
      <div class="embed-grid">{render_embed_cards(embeds, webcam_sources, captions, page["slug"])}</div>
    </section>
"""
    hero_summary = "" if no_camera_page else f"<p>{html.escape(hero_intro(title, intro))}</p>"
    body_html = f"""
  <main>
    <section class="page-hero">
      <div class="page-hero-copy">
        {render_breadcrumbs(title, page["slug"], 1)}
        <h1>{html.escape(title)}</h1>
        {hero_summary}
        {hero_actions}
      </div>
    </section>
    {live_section}
    <section class="weather-section" {weather_attrs}>
      <div class="section-heading">
        <div><h2>{html.escape(park_name)} Weather</h2>{f'<p class="section-note">{html.escape(weather_note)}</p>' if weather_note else ''}</div>
      </div>
      <div class="weather-layout">
        <article class="weather-card">
          <h3>Next 12 hours</h3>
          <div class="hourly-weather" data-weather-hourly>Loading hourly forecast...</div>
        </article>
        <article class="weather-card">
          <h3>7 day outlook</h3>
          <div class="daily-weather" data-weather-daily>Loading forecast...</div>
        </article>
      </div>
    </section>
    <div class="page-layout">
      <article class="page-content">{text_to_html(article_body, park_inline_link_candidates(page["slug"], links), page["slug"], title, wikipedia_url(links), official_nps_url(links) if no_camera_page else "")}</article>
    </div>
    {render_guide_faq_section(page["slug"], title)}
    {related_guide_links(page, pages)}
    {related_park_links(page, pages)}
    {bottom_actions}
  </main>
"""
    page_image = GUIDE_IMAGES.get(page["slug"], {}).get("url", "") if no_camera_page else first_image(resources)
    return page_shell(title, body_html, page["slug"], pages, intro, page_image, 1)


def build_info_page(slug, title, description, sections, pages):
    section_html = []
    for heading, paragraphs in sections:
        section_html.append(f'<section class="content-section"><h2>{html.escape(heading)}</h2>')
        for paragraph in paragraphs:
            section_html.append(f"<p>{paragraph}</p>")
        section_html.append("</section>")
    body_html = f"""
  <main>
    <section class="park-hero">
      {render_breadcrumbs(title, slug, 0)}
      <div class="park-hero-grid">
        <div>
          <span class="eyebrow">National Parks Webcams</span>
          <h1>{html.escape(title)}</h1>
          <p>{html.escape(description)}</p>
        </div>
      </div>
    </section>
    <div class="page-layout">
      <article class="page-content">{''.join(section_html)}</article>
    </div>
  </main>
"""
    return page_shell(title, body_html, slug, pages, description, "", 0)


def info_pages():
    email = '<a href="mailto:npcam012@gmail.com">npcam012@gmail.com</a>'
    return [
        {
            "slug": "about",
            "title": "About National Parks Webcams",
            "description": "Learn about National Parks Webcams, an independent guide to official park and monument webcams, maps, weather, and visitor planning resources.",
            "sections": [
                (
                    "Our Purpose",
                    [
                        "National Parks Webcams is an independent visitor guide that helps people find official webcams, maps, weather, and planning resources for national parks, national monuments, and other public land units.",
                        "The goal is simple: make it easier to check current conditions, explore public-land views, and plan better visits using official sources whenever possible.",
                    ],
                ),
                (
                    "Sources",
                    [
                        "Whenever possible, this site links to official National Park Service pages, official webcam sources, Recreation.gov, and other public agency or public-land resources.",
                        "National Parks Webcams is not affiliated with, endorsed by, or operated by the National Park Service.",
                    ],
                ),
            ],
        },
        {
            "slug": "contact",
            "title": "Contact National Parks Webcams",
            "description": "Contact National Parks Webcams about broken webcam links, incorrect park information, suggestions, or general questions.",
            "sections": [
                (
                    "Email",
                    [
                        f"For questions, corrections, broken webcam links, or suggestions, email {email}.",
                        "Please note that this is an independent website. For official park rules, closures, reservations, permits, or emergency information, contact the National Park Service or the relevant public land agency directly.",
                    ],
                ),
            ],
        },
        {
            "slug": "privacy-policy",
            "title": "Privacy Policy",
            "description": "Privacy Policy for National Parks Webcams, including Google Analytics, cookies, third-party services, and contact information.",
            "sections": [
                (
                    "Overview",
                    [
                        "National Parks Webcams does not directly create user accounts, collect form submissions, sell personal information, or process payments.",
                        "This site is a public visitor guide. It may collect limited technical information through third-party services used for analytics, performance, security, advertising, or embedded content.",
                    ],
                ),
                (
                    "Google Analytics",
                    [
                        "This site uses Google Analytics to understand general traffic patterns, popular pages, referring websites, approximate location, device type, and similar usage information.",
                        "Google Analytics may use cookies or similar technologies to collect and process this information. The data helps improve the site and understand how visitors use it.",
                    ],
                ),
                (
                    "Cookies",
                    [
                        "National Parks Webcams does not currently provide user accounts or site-specific preference settings that require first-party cookies.",
                        "Third-party services, including Google Analytics and any future advertising services such as Google AdSense, may use cookies or similar technologies to measure traffic, prevent abuse, personalize services, or measure advertising performance.",
                    ],
                ),
                (
                    "Managing Cookies",
                    [
                        "Visitors can manage, block, or delete cookies through their browser settings. Most browsers allow you to block cookies, delete existing cookies, or receive a warning before cookies are stored.",
                        'Visitors can also manage Google ad personalization through <a href="https://adssettings.google.com/" target="_blank" rel="noopener">Google Ad Settings</a> and learn how Google uses information from sites and apps at <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">Google Partner Sites</a>.',
                    ],
                ),
                (
                    "Third-Party Links and Embeds",
                    [
                        "This site links to third-party websites such as National Park Service pages, Recreation.gov, YouTube, map providers, webcam providers, and other public resources.",
                        "Those third-party websites and embedded services may have their own privacy practices and cookie policies. National Parks Webcams is not responsible for the privacy practices of those external websites.",
                    ],
                ),
                (
                    "Contact",
                    [
                        f"For privacy questions or site questions, email {email}.",
                    ],
                ),
            ],
        },
    ]


def main():
    pages = load_pages()
    resources_by_url = load_resources()
    webcam_sources_by_slug = load_webcam_sources()
    page_urls = {p["url"].rstrip("/") for p in pages}
    content_by_url = {}
    for page in pages:
        content_by_url[page["url"]] = parse_markdown(EXPORT / page["markdown"])

    if DIST.exists():
        shutil.rmtree(DIST)
    PAGES_OUT.mkdir(parents=True)
    ASSETS_OUT.mkdir(parents=True)
    shutil.copy(ROOT / "assets" / "styles.css", ASSETS_OUT / "styles.css")
    shutil.copy(ROOT / "assets" / "app.js", ASSETS_OUT / "app.js")
    shutil.copy(ROOT / "assets" / "npsLogo.png", ASSETS_OUT / "npsLogo.png")
    shutil.copy(ROOT / "assets" / "favicon-32x32.png", ASSETS_OUT / "favicon-32x32.png")
    shutil.copy(ROOT / "assets" / "apple-touch-icon.png", ASSETS_OUT / "apple-touch-icon.png")

    (DIST / "index.html").write_text(build_home(pages, content_by_url, resources_by_url, webcam_sources_by_slug), encoding="utf-8")
    info = info_pages()
    sitemap_pages = pages + [{"slug": item["slug"]} for item in info]
    (DIST / "CNAME").write_text(f"{CUSTOM_DOMAIN}\n", encoding="utf-8")
    sitemap_xml = build_sitemap(sitemap_pages)
    robots_txt = build_robots_txt()
    (DIST / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (DIST / "robots.txt").write_text(robots_txt, encoding="utf-8")
    # Root fallbacks help if a host is accidentally pointed at the repo root
    # instead of the generated docs/ directory.
    (ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots_txt, encoding="utf-8")
    for item in info:
        (DIST / f"{item['slug']}.html").write_text(
            build_info_page(item["slug"], item["title"], item["description"], item["sections"], pages),
            encoding="utf-8",
        )
    for page in pages:
        if page["slug"] == "national-park-webcam-home":
            continue
        html_out = build_park_page(
            page,
            pages,
            content_by_url[page["url"]],
            resources_by_url[page["url"]],
            page_urls,
            webcam_sources_by_slug.get(page["slug"], []),
        )
        (PAGES_OUT / f"{page['slug']}.html").write_text(html_out, encoding="utf-8")
    print(f"Built {len(pages)} pages into {DIST}")


if __name__ == "__main__":
    main()
