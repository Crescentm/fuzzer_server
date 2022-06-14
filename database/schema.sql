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