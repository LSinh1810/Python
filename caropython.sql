-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th3 31, 2025 lúc 05:58 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `caropython`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `avatar`
--

CREATE TABLE `avatar` (
  `avatar_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `price` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `avatars`
--

CREATE TABLE `avatars` (
  `avatar_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `price` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `games`
--

CREATE TABLE `games` (
  `game_id` int(11) NOT NULL,
  `player1_id` varchar(10) DEFAULT NULL,
  `player2_id` varchar(10) DEFAULT NULL,
  `winner_id` varchar(10) DEFAULT NULL,
  `room_code` varchar(50) DEFAULT NULL,
  `status` enum('ongoing','finished','cancelled') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `leaderboard`
--

CREATE TABLE `leaderboard` (
  `rank_id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `wins` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `leaderboard`
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
-- Cấu trúc bảng cho bảng `move`
--

CREATE TABLE `move` (
  `move_id` int(11) NOT NULL,
  `game_id` int(11) DEFAULT NULL,
  `player_id` varchar(10) DEFAULT NULL,
  `position` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `moves`
--

CREATE TABLE `moves` (
  `move_id` int(11) NOT NULL,
  `game_id` int(11) DEFAULT NULL,
  `player_id` varchar(10) DEFAULT NULL,
  `move_order` int(11) DEFAULT NULL,
  `position_x` int(11) NOT NULL,
  `position_y` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `replay_request`
--

CREATE TABLE `replay_request` (
  `request_id` int(11) NOT NULL,
  `game_id` int(11) DEFAULT NULL,
  `player_id` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `skin`
--

CREATE TABLE `skin` (
  `skin_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `price` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `skins`
--

CREATE TABLE `skins` (
  `skin_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `price` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user`
--

CREATE TABLE `user` (
  `user_id` varchar(10) NOT NULL,
  `displayName` varchar(50) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `user`
--

INSERT INTO `user` (`user_id`, `displayName`, `avatar`) VALUES
('mAPpT4CPbT', 'Din', NULL),
('user1', 'Nguyễn Văn An', '/static/images/default_avatar.png');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `user_id` varchar(10) NOT NULL,
  `displayName` varchar(50) NOT NULL CHECK (char_length(`displayName`) between 3 and 50),
  `avatar` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
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
-- Cấu trúc bảng cho bảng `user_avatar`
--

CREATE TABLE `user_avatar` (
  `id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `avatar_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_avatars`
--

CREATE TABLE `user_avatars` (
  `id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `avatar_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_skin`
--

CREATE TABLE `user_skin` (
  `id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `skin_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_skins`
--

CREATE TABLE `user_skins` (
  `id` int(11) NOT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `skin_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `avatar`
--
ALTER TABLE `avatar`
  ADD PRIMARY KEY (`avatar_id`);

--
-- Chỉ mục cho bảng `avatars`
--
ALTER TABLE `avatars`
  ADD PRIMARY KEY (`avatar_id`);

--
-- Chỉ mục cho bảng `games`
--
ALTER TABLE `games`
  ADD PRIMARY KEY (`game_id`),
  ADD KEY `player1_id` (`player1_id`),
  ADD KEY `player2_id` (`player2_id`),
  ADD KEY `winner_id` (`winner_id`);

--
-- Chỉ mục cho bảng `leaderboard`
--
ALTER TABLE `leaderboard`
  ADD PRIMARY KEY (`rank_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Chỉ mục cho bảng `move`
--
ALTER TABLE `move`
  ADD PRIMARY KEY (`move_id`),
  ADD KEY `game_id` (`game_id`),
  ADD KEY `player_id` (`player_id`);

--
-- Chỉ mục cho bảng `moves`
--
ALTER TABLE `moves`
  ADD PRIMARY KEY (`move_id`),
  ADD KEY `game_id` (`game_id`),
  ADD KEY `player_id` (`player_id`);

--
-- Chỉ mục cho bảng `replay_request`
--
ALTER TABLE `replay_request`
  ADD PRIMARY KEY (`request_id`),
  ADD KEY `game_id` (`game_id`),
  ADD KEY `player_id` (`player_id`);

--
-- Chỉ mục cho bảng `skin`
--
ALTER TABLE `skin`
  ADD PRIMARY KEY (`skin_id`);

--
-- Chỉ mục cho bảng `skins`
--
ALTER TABLE `skins`
  ADD PRIMARY KEY (`skin_id`);

--
-- Chỉ mục cho bảng `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- Chỉ mục cho bảng `user_avatar`
--
ALTER TABLE `user_avatar`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `avatar_id` (`avatar_id`);

--
-- Chỉ mục cho bảng `user_avatars`
--
ALTER TABLE `user_avatars`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `avatar_id` (`avatar_id`);

--
-- Chỉ mục cho bảng `user_skin`
--
ALTER TABLE `user_skin`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `skin_id` (`skin_id`);

--
-- Chỉ mục cho bảng `user_skins`
--
ALTER TABLE `user_skins`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `skin_id` (`skin_id`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `avatar`
--
ALTER TABLE `avatar`
  MODIFY `avatar_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `avatars`
--
ALTER TABLE `avatars`
  MODIFY `avatar_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `games`
--
ALTER TABLE `games`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `leaderboard`
--
ALTER TABLE `leaderboard`
  MODIFY `rank_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT cho bảng `move`
--
ALTER TABLE `move`
  MODIFY `move_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `moves`
--
ALTER TABLE `moves`
  MODIFY `move_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `replay_request`
--
ALTER TABLE `replay_request`
  MODIFY `request_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `skin`
--
ALTER TABLE `skin`
  MODIFY `skin_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `skins`
--
ALTER TABLE `skins`
  MODIFY `skin_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_avatar`
--
ALTER TABLE `user_avatar`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_avatars`
--
ALTER TABLE `user_avatars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_skin`
--
ALTER TABLE `user_skin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_skins`
--
ALTER TABLE `user_skins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `games`
--
ALTER TABLE `games`
  ADD CONSTRAINT `games_ibfk_1` FOREIGN KEY (`player1_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `games_ibfk_2` FOREIGN KEY (`player2_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `games_ibfk_3` FOREIGN KEY (`winner_id`) REFERENCES `users` (`user_id`);

--
-- Các ràng buộc cho bảng `leaderboard`
--
ALTER TABLE `leaderboard`
  ADD CONSTRAINT `leaderboard_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Các ràng buộc cho bảng `move`
--
ALTER TABLE `move`
  ADD CONSTRAINT `move_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`),
  ADD CONSTRAINT `move_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `users` (`user_id`);

--
-- Các ràng buộc cho bảng `moves`
--
ALTER TABLE `moves`
  ADD CONSTRAINT `moves_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `moves_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `users` (`user_id`);

--
-- Các ràng buộc cho bảng `replay_request`
--
ALTER TABLE `replay_request`
  ADD CONSTRAINT `replay_request_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`),
  ADD CONSTRAINT `replay_request_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `users` (`user_id`);

--
-- Các ràng buộc cho bảng `user_avatar`
--
ALTER TABLE `user_avatar`
  ADD CONSTRAINT `user_avatar_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `user_avatar_ibfk_2` FOREIGN KEY (`avatar_id`) REFERENCES `avatar` (`avatar_id`);

--
-- Các ràng buộc cho bảng `user_avatars`
--
ALTER TABLE `user_avatars`
  ADD CONSTRAINT `user_avatars_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_avatars_ibfk_2` FOREIGN KEY (`avatar_id`) REFERENCES `avatars` (`avatar_id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `user_skin`
--
ALTER TABLE `user_skin`
  ADD CONSTRAINT `user_skin_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `user_skin_ibfk_2` FOREIGN KEY (`skin_id`) REFERENCES `skin` (`skin_id`);

--
-- Các ràng buộc cho bảng `user_skins`
--
ALTER TABLE `user_skins`
  ADD CONSTRAINT `user_skins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_skins_ibfk_2` FOREIGN KEY (`skin_id`) REFERENCES `skins` (`skin_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
