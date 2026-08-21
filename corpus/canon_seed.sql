-- SceneMedic — ClickHouse continuity DB seed
-- Show bible: "St. Anne's" — a fictional ER drama

CREATE DATABASE IF NOT EXISTS scenemedic;

CREATE TABLE IF NOT EXISTS scenemedic.patient_canon (
    name        String,
    age         UInt8,
    sex         String,
    diagnoses   Array(String),
    medications Array(String),
    last_labs   Map(String, String),
    notes       String,
    updated_at  DateTime DEFAULT now()
) ENGINE = MergeTree
ORDER BY name;

INSERT INTO scenemedic.patient_canon
(name, age, sex, diagnoses, medications, last_labs, notes) VALUES
(
    'Maya Chen', 34, 'F',
    ['Type 1 diabetes mellitus', 'Non-ischemic cardiomyopathy (LVEF 30%)',
     'Chronic kidney disease stage 3a'],
    ['carvedilol 12.5 mg BID', 'empagliflozin 10 mg daily',
     'insulin glargine 22 U qHS', 'insulin aspart per sliding scale',
     'lisinopril 10 mg daily'],
    map('A1c', '8.2', 'BNP', '820', 'Cr', '1.4', 'K', '4.1'),
    'Recurring patient. Third code this arc. Do NOT push standard-dose '
    'ACE-I with hyperkalemia; watch potassium with empagliflozin.'
),
(
    'Marcus Bell', 58, 'M',
    ['Coronary artery disease s/p CABG x3 (2022)', 'Hypertension',
     'Hyperlipidemia'],
    ['aspirin 81 mg', 'atorvastatin 80 mg', 'metoprolol succinate 50 mg',
     'lisinopril 20 mg'],
    map('LDL', '68', 'Troponin', '<0.01', 'K', '4.3'),
    'Season 2 antagonist. History of MI. Vagal-averse in dialogue.'
),
(
    'Priya Rao', 8, 'F',
    ['Acute lymphoblastic leukemia — remission',
     'Prior tunneled central line infection'],
    ['maintenance mercaptopurine', 'methotrexate weekly'],
    map('ANC', '1800', 'Plt', '210', 'Hgb', '11.2'),
    'Pediatric patient. Any febrile presentation is neutropenic-fever '
    'protocol until proven otherwise.'
);

CREATE TABLE IF NOT EXISTS scenemedic.episodes (
    show       String,
    season     UInt8,
    episode    UInt8,
    title      String,
    aired_date Date,
    logline    String,
    PRIMARY KEY (show, season, episode)
) ENGINE = MergeTree
ORDER BY (show, season, episode);

INSERT INTO scenemedic.episodes VALUES
('St. Anne''s', 3, 7, 'Outliers', '2026-11-14',
 'Maya''s third code forces Elena to confront the limits of her protocols.');
