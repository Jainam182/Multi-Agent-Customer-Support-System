BEGIN TRANSACTION;

CREATE TABLE Customer (
    CustomerId INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT,
    Email TEXT,
    Phone TEXT,
    Location TEXT
);

CREATE TABLE ProductCategory (
    CategoryId INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL
);

CREATE TABLE Product (
    ProductId INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryId INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Description TEXT,
    Price NUMERIC,
    StockQuantity INTEGER NOT NULL,
    FOREIGN KEY(CategoryId) REFERENCES ProductCategory(CategoryId)
);

CREATE TABLE Employee (
    EmployeeId INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Title TEXT,
    Email TEXT
);

CREATE TABLE Orders (
    OrderId INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerId INTEGER NOT NULL,
    EmployeeId INTEGER,
    OrderDate DATETIME NOT NULL,
    Status TEXT NOT NULL,
    TotalAmount NUMERIC,
    FOREIGN KEY(CustomerId) REFERENCES Customer(CustomerId),
    FOREIGN KEY(EmployeeId) REFERENCES Employee(EmployeeId)
);

CREATE TABLE OrderLine (
    OrderLineId INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderId INTEGER NOT NULL,
    ProductId INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    UnitPrice NUMERIC NOT NULL,
    FOREIGN KEY(OrderId) REFERENCES Orders(OrderId),
    FOREIGN KEY(ProductId) REFERENCES Product(ProductId)
);

-- Insert dummy data
INSERT INTO Employee (EmployeeId, FirstName, LastName, Title, Email) VALUES (1, 'Aditi', 'Sharma', 'Sales Representative', 'aditi.sharma@arihant.com');
INSERT INTO Employee (EmployeeId, FirstName, LastName, Title, Email) VALUES (2, 'Rahul', 'Verma', 'Support Specialist', 'rahul.verma@arihant.com');

INSERT INTO Customer (CustomerId, FirstName, LastName, Email, Phone, Location) VALUES (5, 'Rajesh', 'Kumar', 'rajesh.k@example.com', '9876543210', 'Mumbai');
INSERT INTO Customer (CustomerId, FirstName, LastName, Email, Phone, Location) VALUES (10, 'Sneha', 'Patil', 'sneha.patil@example.com', '+919988776655', 'Pune');

INSERT INTO ProductCategory (CategoryId, Name) VALUES (1, 'Respiratory Equipment');
INSERT INTO ProductCategory (CategoryId, Name) VALUES (2, 'Hospital & ICU Equipment');
INSERT INTO ProductCategory (CategoryId, Name) VALUES (3, 'Consumables & Disposables');

INSERT INTO Product (ProductId, CategoryId, Name, Description, Price, StockQuantity) VALUES (1, 1, 'Oxygen Concentrator 5L', 'Provides continuous oxygen up to 5 Liters per minute.', 35000, 15);
INSERT INTO Product (ProductId, CategoryId, Name, Description, Price, StockQuantity) VALUES (2, 1, 'BiPAP Machine', 'Non-invasive ventilation device for sleep apnea.', 45000, 8);
INSERT INTO Product (ProductId, CategoryId, Name, Description, Price, StockQuantity) VALUES (3, 1, 'CPAP Machine', 'Continuous positive airway pressure machine.', 28000, 12);
INSERT INTO Product (ProductId, CategoryId, Name, Description, Price, StockQuantity) VALUES (4, 2, 'ICU Bed (Motorized)', '5-function motorized ICU bed with mattress.', 65000, 5);
INSERT INTO Product (ProductId, CategoryId, Name, Description, Price, StockQuantity) VALUES (5, 3, 'Surgical Gloves (Box of 100)', 'Latex examination gloves.', 450, 150);
INSERT INTO Product (ProductId, CategoryId, Name, Description, Price, StockQuantity) VALUES (6, 3, 'N95 Masks (Pack of 50)', 'High-efficiency particulate air masks.', 1500, 200);

INSERT INTO Orders (OrderId, CustomerId, EmployeeId, OrderDate, Status, TotalAmount) VALUES (101, 5, 1, '2023-10-15 10:00:00', 'Delivered', 35000);
INSERT INTO OrderLine (OrderLineId, OrderId, ProductId, Quantity, UnitPrice) VALUES (1, 101, 1, 1, 35000);

INSERT INTO Orders (OrderId, CustomerId, EmployeeId, OrderDate, Status, TotalAmount) VALUES (102, 10, 2, '2023-11-01 14:30:00', 'In Progress', 45000);
INSERT INTO OrderLine (OrderLineId, OrderId, ProductId, Quantity, UnitPrice) VALUES (2, 102, 2, 1, 45000);

COMMIT;
