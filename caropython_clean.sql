-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `caropython`
--

CREATE DATABASE IF NOT EXISTS `caropython` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `caropython`;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` varchar(10) NOT NULL,
  `displayName` varchar(50) NOT NULL CHECK (char_length(`displayName`) between 3 and 50),
  `avatar` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `displayName`, `avatar`) VALUES
('mAPpT4CPbT', 'Din', NULL),
('user1', 'Nguyễn Văn An', '/static/images/default_avatar.png'),
('user10', 'Lý Thị Khánh', '/static/images/default_avatar.png'),
('user11', 'Hồ Văn Lộc', '/static/images/avatar1.png'),
('user12', 'Mai Thị Minh', '/static/images/avatar2.png'),
('user13', 'Đỗ Văn Năm', '/static/images/default_avatar.png'),
('user14', 'Huỳnh Thị Oanh', '/static/images/avatar2.png'),
('user15', 'Phan Văn Phúc', '/static/images/avatar1.png'),
('user16', 'Trương Thị Quỳnh', '/static/images/default_avatar.png'),
('user17', 'Dương Văn Rồng', '/static/images/avatar1.png'),
('user18', 'Võ Thị Sen', '/static/images/avatar2.png'),
('user19', 'Đinh Văn Tâm', '/static/images/default_avatar.png'),
('user2', 'Trần Thị Bình', '/static/images/avatar2.png'),
('user20', 'Nguyễn Thị Uyên', '/static/images/avatar2.png'),
('user3', 'Lê Văn Cường', '/static/images/avatar1.png'),
('user4', 'Phạm Thị Dung', '/static/images/default_avatar.png'),
('user5', 'Hoàng Văn Em', '/static/images/avatar1.png'),
('user6', 'Ngô Thị Phương', '/static/images/avatar2.png'),
('user7', 'Vũ Văn Giàu', '/static/images/default_avatar.png'),
('user8', 'Đặng Thị Hồng', '/static/images/avatar2.png'),
('user9', 'Bùi Văn Inox', '/static/images/avatar1.png');

-- --------------------------------------------------------

--
-- Table structure for table `games`
--

CREATE TABLE `games` (
  `game_id` int(11) NOT NULL,
  `room_code` varchar(10) NOT NULL,
  `player1_id` varchar(10) DEFAULT NULL,
  `player2_id` varchar(10) DEFAULT NULL,
  `winner_id` varchar(10) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'ongoing',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `move`
--

CREATE TABLE `move` (
  `move_id` int(11) NOT NULL,
  `game_id` int(11) DEFAULT NULL,
  `player_id` varchar(10) DEFAULT NULL,
  `position` varchar(10) NOT NULL,
  `move_order` int(11) DEFAULT 0,
  `position_x` int(11) DEFAULT NULL,
  `position_y` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `avatar`
--

CREATE TABLE `avatar` (
  `avatar_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `price` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `skin`
--

CREATE TABLE `skin` (
  `skin_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `price` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_avatar`
--

CREATE TABLE `user_avatar` (
  `id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `avatar_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_skin`
--

CREATE TABLE `user_skin` (
  `id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `skin_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `leaderboard`
--

CREATE TABLE `leaderboard` (
  `rank_id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `wins` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `leaderboard`
--

INSERT INTO `leaderboard` (`rank_id`, `user_id`, `wins`) VALUES
(21, 'user1', 40),
(22, 'user2', 23),
(23, 'user3', 19),
(24, 'user4', 64),
(25, 'user5', 47),
(26, 'user6', 67),
(27, 'user7', 74),
(28, 'user8', 50),
(29, 'user9', 43),
(30, 'user10', 40),
(31, 'user11', 7),
(32, 'user12', 93),
(33, 'user13', 6),
(34, 'user14', 92),
(35, 'user15', 85),
(36, 'user16', 88),
(37, 'user17', 58),
(38, 'user18', 97),
(39, 'user19', 98),
(40, 'user20', 72);

-- --------------------------------------------------------

--
-- Table structure for table `replay_request`
--

CREATE TABLE `replay_request` (
  `request_id` int(11) NOT NULL,
  `game_id` int(11) DEFAULT NULL,
  `player_id` varchar(10) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `games`
--
ALTER TABLE `games`
  ADD PRIMARY KEY (`game_id`),
  ADD UNIQUE KEY `room_code` (`room_code`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `move`
--
ALTER TABLE `move`
  ADD PRIMARY KEY (`move_id`),
  ADD KEY `game_id` (`game_id`),
  ADD KEY `player_id` (`player_id`),
  ADD KEY `idx_move_order` (`move_order`);

--
-- Indexes for table `avatar`
--
ALTER TABLE `avatar`
  ADD PRIMARY KEY (`avatar_id`);

--
-- Indexes for table `skin`
--
ALTER TABLE `skin`
  ADD PRIMARY KEY (`skin_id`);

--
-- Indexes for table `user_avatar`
--
ALTER TABLE `user_avatar`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `avatar_id` (`avatar_id`);

--
-- Indexes for table `user_skin`
--
ALTER TABLE `user_skin`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `skin_id` (`skin_id`);

--
-- Indexes for table `leaderboard`
--
ALTER TABLE `leaderboard`
  ADD PRIMARY KEY (`rank_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `idx_wins` (`wins`);

--
-- Indexes for table `replay_request`
--
ALTER TABLE `replay_request`
  ADD PRIMARY KEY (`request_id`),
  ADD KEY `game_id` (`game_id`),
  ADD KEY `player_id` (`player_id`);

-- --------------------------------------------------------

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `games`
--
ALTER TABLE `games`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `move`
--
ALTER TABLE `move`
  MODIFY `move_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `avatar`
--
ALTER TABLE `avatar`
  MODIFY `avatar_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `skin`
--
ALTER TABLE `skin`
  MODIFY `skin_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_avatar`
--
ALTER TABLE `user_avatar`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_skin`
--
ALTER TABLE `user_skin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `leaderboard`
--
ALTER TABLE `leaderboard`
  MODIFY `rank_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `replay_request`
--
ALTER TABLE `replay_request`
  MODIFY `request_id` int(11) NOT NULL AUTO_INCREMENT;

-- --------------------------------------------------------

--
-- Constraints for dumped tables
--

--
-- Constraints for table `games`
--
ALTER TABLE `games`
  ADD CONSTRAINT `fk_games_player1` FOREIGN KEY (`player1_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_games_player2` FOREIGN KEY (`player2_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_games_winner` FOREIGN KEY (`winner_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints for table `move`
--
ALTER TABLE `move`
  ADD CONSTRAINT `fk_move_game` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_move_player` FOREIGN KEY (`player_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_avatar`
--
ALTER TABLE `user_avatar`
  ADD CONSTRAINT `fk_user_avatar_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user_avatar_avatar` FOREIGN KEY (`avatar_id`) REFERENCES `avatar` (`avatar_id`) ON DELETE CASCADE;

--
-- Constraints for table `user_skin`
--
ALTER TABLE `user_skin`
  ADD CONSTRAINT `fk_user_skin_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_user_skin_skin` FOREIGN KEY (`skin_id`) REFERENCES `skin` (`skin_id`) ON DELETE CASCADE;

--
-- Constraints for table `leaderboard`
--
ALTER TABLE `leaderboard`
  ADD CONSTRAINT `fk_leaderboard_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `replay_request`
--
ALTER TABLE `replay_request`
  ADD CONSTRAINT `fk_replay_game` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_replay_player` FOREIGN KEY (`player_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */; 