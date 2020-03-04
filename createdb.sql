CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    daily_limit INTEGER DEFAULT 1000
);

CREATE TABLE categories (
    codename VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    is_base_expense BOOLEAN,
    aliases TEXT
);

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount INTEGER,
    created DATETIME,
    category_codename INTEGER,
    raw_text TEXT,
    FOREIGN KEY(category_codename) REFERENCES categories(codename)
);

INSERT INTO categories (codename, name, is_base_expense, aliases)
VALUES
    ("products", "продукты", true, "еда"),
    ("coffee", "кофе", true, ""),
    ("dinner", "обед", true, "столовая, ланч, бизнес-ланч, бизнес ланч"),
    ("cafe", "кафе", true, "ресторан, рест, мак, макдональдс, макдак, kfc, ilpatio, il patio"),
    ("transport", "общ. транспорт", false, "метро, автобус, metro"),
    ("taxi", "такси", false, "яндекс такси, yandex taxi"),
    ("phone", "телефон", false, "теле2, связь"),
    ("books", "книги", false, "литература, литра, лит-ра"),
    ("internet", "интернет", false, "инет, inet"),
    ("subscriptions", "подписки", false, "подписка"),
    ("other", "прочее", true, "");