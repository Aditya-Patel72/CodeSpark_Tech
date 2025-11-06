-- ============================================
-- DATABASE: PeerCommunity
-- Purpose: Health-Tech Peer Support Community
-- ============================================

CREATE DATABASE IF NOT EXISTS peercommunity
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE peercommunity;

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(60) UNIQUE NOT NULL,
  display_name VARCHAR(120),
  email VARCHAR(120),
  password_hash VARCHAR(255),
  bio TEXT,
  role ENUM('member','moderator','admin') DEFAULT 'member',
  status ENUM('active','banned','suspended') DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================
-- GROUPS / FORUMS TABLE
-- =========================
CREATE TABLE groups (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) UNIQUE NOT NULL,
  description TEXT,
  icon VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- POSTS TABLE
-- =========================
CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  username VARCHAR(60),
  group_id INT,
  group_name VARCHAR(120),
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  type ENUM('story','question','poll','resource') DEFAULT 'story',
  thank_count INT DEFAULT 0,
  inform_count INT DEFAULT 0,
  flagged BOOLEAN DEFAULT FALSE,
  pinned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL
);

-- =========================
-- COMMENTS TABLE
-- =========================
CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT,
  user_id INT,
  username VARCHAR(60),
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- =========================
-- REACTIONS TABLE
-- =========================
CREATE TABLE reactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT,
  user_id INT,
  type ENUM('thank','hug','inform','thinking') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- =========================
-- BADGES TABLE
-- =========================
CREATE TABLE badges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  name VARCHAR(120),
  description TEXT,
  icon VARCHAR(255),
  awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================
-- MODERATION LOGS TABLE
-- =========================
CREATE TABLE moderation_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  moderator_id INT,
  post_id INT,
  action ENUM('flag','approve','remove','ban_user','warn_user') NOT NULL,
  reason TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (moderator_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- =========================
-- NOTIFICATIONS TABLE
-- =========================
CREATE TABLE notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  message TEXT,
  link VARCHAR(255),
  read_status BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================
-- FOLLOW RELATIONSHIPS
-- =========================
CREATE TABLE follows (
  id INT AUTO_INCREMENT PRIMARY KEY,
  follower_id INT,
  followed_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================
-- SEED INITIAL GROUPS
-- =========================
INSERT IGNORE INTO groups (name, description, icon) VALUES
('Diabetes Type 2', 'Support for people living with Type 2 Diabetes', '🩸'),
('Migraines', 'Tips, triggers, and management stories about migraines', '💊'),
('Mental Health', 'Peer support for mental well-being and stress', '🧠'),
('Nutrition & Diet', 'Discuss diets, meal plans, and recipes', '🥗'),
('Fitness & Recovery', 'Talk about exercises, physiotherapy, and healthy habits', '🏋️‍♂️');

-- =========================
-- MEDICAL DISCLAIMER (SYSTEM POST)
-- =========================
INSERT INTO posts (username, title, content, group_name)
VALUES (
  'System',
  'Medical Disclaimer',
  '⚠️ This community is for informational and emotional support only. Do NOT share personal medical data or treat any advice here as a substitute for professional diagnosis or treatment. In an emergency, contact a licensed medical provider or local helpline immediately.',
  'General'
);
