--
-- Table structure for table `admin_user`
--

CREATE TABLE `admin_user` (
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `admin_user`:
--   `user_id`
--       `app_user` -> `user_id`
--

--
-- Triggers `admin_user`
--
DELIMITER $$
CREATE TRIGGER `trg_admin_role_chk` BEFORE INSERT ON `admin_user` FOR EACH ROW BEGIN
  DECLARE v_role VARCHAR(10);

  SELECT role INTO v_role
  FROM app_user
  WHERE user_id = NEW.user_id;

  IF v_role <> 'ADMIN' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'User must have role ADMIN to appear in ADMIN_USER.';
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `app_user`
--

CREATE TABLE `app_user` (
  `user_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `role` varchar(10) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_superuser` tinyint(1) DEFAULT 0,
  `is_staff` tinyint(1) DEFAULT 0,
  `date_joined` datetime DEFAULT current_timestamp(),
  `last_login` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ;

--
-- RELATIONSHIPS FOR TABLE `app_user`:
--

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `django_migrations`:
--

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `django_session`:
--

-- --------------------------------------------------------

--
-- Table structure for table `game`
--

CREATE TABLE `game` (
  `game_id` int(11) NOT NULL,
  `player1` int(11) NOT NULL,
  `player2` int(11) NOT NULL,
  `outcome` int(11) DEFAULT NULL,
  `played_at` datetime NOT NULL DEFAULT current_timestamp()
) ;

--
-- RELATIONSHIPS FOR TABLE `game`:
--   `outcome`
--       `player` -> `user_id`
--   `player1`
--       `player` -> `user_id`
--   `player2`
--       `player` -> `user_id`
--

-- --------------------------------------------------------

--
-- Table structure for table `player`
--

CREATE TABLE `player` (
  `user_id` int(11) NOT NULL,
  `elo` decimal(10,3) DEFAULT NULL,
  `glicko` decimal(10,3) DEFAULT NULL,
  `glicko_rd` decimal(10,3) NOT NULL DEFAULT 350.000,
  `volatility` decimal(10,5) NOT NULL DEFAULT 0.06000,
  `tries` int(11) NOT NULL DEFAULT 0,
  `last_game_date` datetime DEFAULT NULL,
  `gamecount` bigint(20) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `player`:
--   `user_id`
--       `app_user` -> `user_id`
--

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_user`
--
ALTER TABLE `admin_user`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `app_user`
--
ALTER TABLE `app_user`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_idx` (`expire_date`);

--
-- Indexes for table `game`
--
ALTER TABLE `game`
  ADD PRIMARY KEY (`game_id`),
  ADD KEY `idx_game_p1` (`player1`),
  ADD KEY `idx_game_p2` (`player2`),
  ADD KEY `idx_game_outcome` (`outcome`),
  ADD KEY `idx_game_playedat` (`played_at`);

--
-- Indexes for table `player`
--
ALTER TABLE `player`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `app_user`
--
ALTER TABLE `app_user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `game`
--
ALTER TABLE `game`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin_user`
--
ALTER TABLE `admin_user`
  ADD CONSTRAINT `fk_admin_user` FOREIGN KEY (`user_id`) REFERENCES `app_user` (`user_id`);

--
-- Constraints for table `game`
--
ALTER TABLE `game`
  ADD CONSTRAINT `fk_game_outcome` FOREIGN KEY (`outcome`) REFERENCES `player` (`user_id`),
  ADD CONSTRAINT `fk_game_p1` FOREIGN KEY (`player1`) REFERENCES `player` (`user_id`),
  ADD CONSTRAINT `fk_game_p2` FOREIGN KEY (`player2`) REFERENCES `player` (`user_id`);

--
-- Constraints for table `player`
--
ALTER TABLE `player`
  ADD CONSTRAINT `fk_player_user` FOREIGN KEY (`user_id`) REFERENCES `app_user` (`user_id`);
COMMIT;

-- ==================================================================================================
-- CREATE A DEFAULT ADMIN USER FOR EASY SETUP. DELETE IF NECESSARY, OR IF YOU WANT TO CREATE YOUR OWN ADMIN USER.
-- ==================================================================================================

-- Default credentials:
-- Username: Admin
-- Password: admin123

INSERT INTO `app_user` (`user_id`, `name`, `role`, `password_hash`, `is_superuser`, `is_staff`, `is_active`) 
VALUES (
    1,
    'Admin',
    'ADMIN',
    'pbkdf2_sha256$1200000$rhwr6YkguCSVADyvKqHhgR$vhP1phNdJzCHP333WoDuwhG5c8TghlNX3rh5YWXeCIU=',  -- PASSWORD HASHED BY DJANGO BY DEFAULT.
    1,
    1,
    1
);

INSERT INTO `admin_user` (`user_id`) VALUES (1);