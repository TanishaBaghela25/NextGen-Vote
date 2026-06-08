-- =============================================
--  SMART VOTING SYSTEM — DATABASE SETUP
--  Run this in MySQL Workbench or terminal
-- =============================================

CREATE DATABASE IF NOT EXISTS online_voting
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE online_voting;

-- ─────────────────────────────────────────
--  TABLE 1: REGISTERED VOTERS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS voters (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    aadhaar       VARCHAR(12)  NOT NULL UNIQUE,
    epic_id       VARCHAR(20)  NOT NULL UNIQUE,
    mobile        VARCHAR(10)  NOT NULL,
    email         VARCHAR(100) DEFAULT NULL,
    full_name     VARCHAR(100) NOT NULL,
    dob           DATE         DEFAULT NULL,
    gender        VARCHAR(10)  DEFAULT NULL,
    state         VARCHAR(50)  DEFAULT NULL,
    registered_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
    is_active     TINYINT(1)   DEFAULT 1
);

-- ─────────────────────────────────────────
--  TABLE 2: VOTES CAST
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS votes (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    aadhaar  VARCHAR(12) NOT NULL UNIQUE,
    party    VARCHAR(50) NOT NULL,
    voted_at DATETIME    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (aadhaar) REFERENCES voters(aadhaar)
);

-- ─────────────────────────────────────────
--  TABLE 3: ADMIN USERS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admins (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(64)  NOT NULL,
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
--  DEFAULT ADMIN (password: Admin@123)
--  SHA256 of "Admin@123"
-- ─────────────────────────────────────────
INSERT INTO admins (username, password) VALUES (
    'admin',
    '0b14d501a594442a01c6859541b44b54f62ae7a71f84ef01aa13e8a2d87eb1b3'
)
ON DUPLICATE KEY UPDATE username=username;

-- ─────────────────────────────────────────
--  INDEXES FOR PERFORMANCE
-- ─────────────────────────────────────────
CREATE INDEX idx_voters_aadhaar ON voters(aadhaar);
CREATE INDEX idx_voters_epic    ON voters(epic_id);
CREATE INDEX idx_votes_aadhaar  ON votes(aadhaar);
CREATE INDEX idx_votes_party    ON votes(party);
