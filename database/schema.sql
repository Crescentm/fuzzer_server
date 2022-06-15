CREATE TABLE `transactions` (
    `transaction_hash` varchar(128) PRIMARY KEY,
    `pc` longtext,
    `cost` longtext NOT NULL,
    `status` varchar(32) NOT NULL,
)

CREATE TABLE `jobs` (
    `id` int AUTO_INCREMENT PRIMARY KEY,
    `name` varchar(128) NOT NULL,
    `abi_path` varchar(128) NOT NULL,
    `bin_path` varchar(128) NOT NULL
);

CREATE TABLE `crashes` (
    `id` int AUTO_INCREMENT PRIMARY KEY,
    `job_id` int NOT NULL,
    `type` varchar(64) NOT NULL,
    `backtrace` longtext NOT NULL
);

CREATE TABLE `corpuses` (
    `id` int AUTO_INCREMENT PRIMARY KEY,
    `name` varchar(64) NOT NULL,
    `job_id` int NOT NULL,
    `file_path` varchar(128) NOT NULL,
    `size` varchar(128) NOT NULL,
    `update_time` datetime NOT NULL
);